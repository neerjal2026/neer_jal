import frappe
from frappe.utils import flt, today

from neer_jal.api.permission import MANAGER_ROLES
from neer_jal.neer_jal.utils import update_customer_balance


def _ensure_manager():
	if not (MANAGER_ROLES & set(frappe.get_roles())):
		frappe.throw("Not permitted", frappe.PermissionError)


@frappe.whitelist()
def settle_customer_dues(customer, payment_mode, payment_date=None, notes=None):
	if payment_mode not in ("Cash", "UPI"):
		frappe.throw("Payment mode must be Cash or UPI")

	if not frappe.has_permission("Sales Entry", "write") or not frappe.has_permission(
		"Payment Entry", "create"
	):
		frappe.throw("Not permitted to settle dues", frappe.PermissionError)

	pending = frappe.get_all(
		"Sales Entry",
		filters={"customer": customer, "payment_mode": "Pending"},
		fields=["name", "amount"],
	)
	if not pending:
		frappe.throw("This customer has no pending dues to settle")

	total = 0.0
	for entry in pending:
		frappe.db.set_value("Sales Entry", entry.name, "payment_mode", payment_mode)
		total += flt(entry.amount)

	payment = frappe.get_doc(
		{
			"doctype": "Payment Entry",
			"customer": customer,
			"amount": total,
			"payment_mode": payment_mode,
			"payment_date": payment_date or today(),
			"received_by": frappe.session.user,
			"notes": notes,
		}
	).insert()

	update_customer_balance(customer)

	return {"settled_count": len(pending), "amount": total, "payment_entry": payment.name}


@frappe.whitelist()
def get_lcr_summary():
	"""Outstanding LCR amount per (sales person, customer) - money a sales person
	personally took responsibility for collecting from a customer, and hasn't yet
	remitted back to the company."""
	_ensure_manager()
	return frappe.db.sql(
		"""
		select sales_person, customer, customer_name, sum(amount) as amount
		from `tabSales Entry`
		where payment_mode = 'LCR'
		group by sales_person, customer, customer_name
		having sum(amount) > 0
		order by sales_person asc, customer_name asc
		""",
		as_dict=True,
	)


@frappe.whitelist()
def get_lcr_due(sales_person, customer):
	_ensure_manager()
	amount = frappe.db.sql(
		"""
		select coalesce(sum(amount), 0)
		from `tabSales Entry`
		where payment_mode = 'LCR' and sales_person = %s and customer = %s
		""",
		(sales_person, customer),
	)[0][0]
	return {"amount": flt(amount)}


@frappe.whitelist()
def settle_lcr(sales_person, customer, payment_mode, payment_date=None, notes=None):
	_ensure_manager()
	if payment_mode not in ("Cash", "UPI"):
		frappe.throw("Payment mode must be Cash or UPI")

	pending = frappe.get_all(
		"Sales Entry",
		filters={"customer": customer, "sales_person": sales_person, "payment_mode": "LCR"},
		fields=["name", "amount"],
	)
	if not pending:
		frappe.throw("This sales person has no pending LCR for this customer")

	total = 0.0
	for entry in pending:
		frappe.db.set_value("Sales Entry", entry.name, "payment_mode", payment_mode)
		total += flt(entry.amount)

	payment = frappe.get_doc(
		{
			"doctype": "Payment Entry",
			"customer": customer,
			"sales_person": sales_person,
			"amount": total,
			"payment_mode": payment_mode,
			"payment_date": payment_date or today(),
			"received_by": frappe.session.user,
			"notes": notes,
		}
	).insert()

	update_customer_balance(customer)

	return {"settled_count": len(pending), "amount": total, "payment_entry": payment.name}
