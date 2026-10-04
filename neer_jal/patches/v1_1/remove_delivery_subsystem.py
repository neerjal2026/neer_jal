import frappe
from frappe.utils import flt, getdate


def execute():
	if frappe.db.has_column("Trip", "sales_person") and frappe.db.has_column("Trip", "driver"):
		frappe.db.sql(
			"""
			update `tabTrip`
			set driver = sales_person
			where ifnull(driver, '') = '' and ifnull(sales_person, '') != ''
			"""
		)

	if frappe.db.has_column("Neer Jal Employee", "role"):
		frappe.db.sql(
			"update `tabNeer Jal Employee` set role = 'Driver' where role = 'Sales Person'"
		)

	if frappe.db.exists("DocType", "Driver Credit"):
		trips = frappe.get_all(
			"Trip",
			filters={"status": "Completed", "trip_route": ["is", "set"]},
			fields=["name", "driver", "end_time", "driver_credit"],
		)
		for trip in trips:
			if not trip.driver or frappe.db.exists("Driver Credit", {"trip": trip.name}):
				continue
			frappe.get_doc(
				{
					"doctype": "Driver Credit",
					"driver": trip.driver,
					"trip": trip.name,
					"credit_date": getdate(trip.end_time),
					"amount": flt(trip.driver_credit),
				}
			).insert(ignore_permissions=True)

	for doctype in ("Sales Entry", "Payment Entry", "Customer", "Sales Settings", "Driver"):
		if frappe.db.exists("DocType", doctype):
			frappe.delete_doc("DocType", doctype, force=True, ignore_missing=True)
