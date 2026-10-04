import frappe


def execute():
	if not frappe.db.exists("DocType", "Neer Jal Vehicle"):
		return

	if not frappe.db.table_exists("Neer Jal Vehicle Migration"):
		return

	vehicles = frappe.db.sql(
		"""
		select vehicle_number, model, mileage, disabled
		from `tabNeer Jal Vehicle Migration`
		""",
		as_dict=True,
	)
	for vehicle in vehicles:
		if frappe.db.exists("Neer Jal Vehicle", vehicle.vehicle_number):
			continue
		frappe.get_doc(
			{
				"doctype": "Neer Jal Vehicle",
				"vehicle_number": vehicle.vehicle_number,
				"model": vehicle.model,
				"mileage": vehicle.mileage,
				"disabled": vehicle.disabled,
			}
		).insert(ignore_permissions=True)

	frappe.db.sql("delete from `tabNeer Jal Vehicle Migration`")
