import frappe


def execute():
	if not frappe.db.has_column("Vehicle", "vehicle_number"):
		return

	frappe.db.sql(
		"""
		create table if not exists `tabNeer Jal Vehicle Migration` as
		select vehicle_number, model, mileage, disabled
		from `tabVehicle`
		where ifnull(vehicle_number, '') != ''
		"""
	)
