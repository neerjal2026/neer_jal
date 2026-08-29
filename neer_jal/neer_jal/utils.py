import re

import frappe
from frappe.utils import flt


def validate_phone_number(phone, label="Phone"):
	"""Strip formatting and require exactly 10 digits. Returns the cleaned digits-only
	value, or the original falsy value (None/"") unchanged if nothing was entered."""
	if not phone:
		return phone

	digits = re.sub(r"\D", "", phone)
	if len(digits) != 10:
		frappe.throw(f"{label} must be exactly 10 digits")

	return digits


def update_customer_balance(customer):
	totals = frappe.db.sql(
		"""
		select
			coalesce(sum(cans_given), 0) as given,
			coalesce(sum(cans_returned), 0) as returned,
			coalesce(sum(case when payment_mode = 'Pending' then amount else 0 end), 0) as due
		from `tabSales Entry`
		where customer = %s
		""",
		customer,
		as_dict=True,
	)[0]

	frappe.db.set_value(
		"Customer",
		customer,
		{
			"cans_pending": flt(totals.given) - flt(totals.returned),
			"amount_due": flt(totals.due),
		},
	)


def update_trip_cans_delivered(trip):
	if not trip:
		return

	delivered = frappe.db.sql(
		"""
		select coalesce(sum(cans_given), 0)
		from `tabSales Entry`
		where trip = %s
		""",
		trip,
	)[0][0]

	doc = frappe.get_doc("Trip", trip)
	doc.cans_delivered = flt(delivered)
	doc.save(ignore_permissions=True)
