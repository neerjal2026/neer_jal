import frappe


def execute():
	if frappe.db.has_column("Trip", "driver") and frappe.db.has_column("Trip", "sales_person"):
		frappe.db.sql(
			"""
			update `tabTrip`
			set driver = sales_person
			where ifnull(sales_person, '') != ''
			"""
		)

	if frappe.db.has_column("Neer Jal Employee", "role"):
		frappe.db.sql(
			"""
			update `tabNeer Jal Employee`
			set role = 'Driver'
			where role = 'Sales Person'
			"""
		)
