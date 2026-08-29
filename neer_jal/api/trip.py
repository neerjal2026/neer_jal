import frappe


@frappe.whitelist()
def get_active_trip():
	name = frappe.db.get_value(
		"Trip", {"sales_person": frappe.session.user, "status": "Active"}, "name"
	)
	if not name:
		return None
	return frappe.get_doc("Trip", name).as_dict()
