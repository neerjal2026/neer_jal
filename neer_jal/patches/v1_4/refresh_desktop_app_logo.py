import frappe


LOGO_URL = "/assets/neer_jal/favicon.svg"


def execute():
	if not frappe.db.exists("DocType", "Desktop Icon"):
		return
	if not frappe.db.has_column("Desktop Icon", "logo_url"):
		return

	filters = {"icon_type": "App"}
	if frappe.db.has_column("Desktop Icon", "app"):
		filters["app"] = "neer_jal"
	else:
		filters["label"] = frappe.get_hooks("app_title", app_name="neer_jal")[0]

	icon_names = frappe.get_all("Desktop Icon", filters=filters, pluck="name")
	for name in icon_names:
		frappe.db.set_value("Desktop Icon", name, "logo_url", LOGO_URL, update_modified=False)
