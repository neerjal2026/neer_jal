import frappe

from neer_jal.api.permission import has_app_permission

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = f"/login?redirect-to={frappe.local.request.path}"
		raise frappe.Redirect

	if not has_app_permission():
		frappe.throw("You are not permitted to access this page", frappe.PermissionError)

	context.csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosemgrep
	return context


@frappe.whitelist(allow_guest=True)
def get_context_for_dev():
	if not frappe.conf.developer_mode:
		frappe.throw("This method is only meant for developer mode")
	return {"csrf_token": frappe.sessions.get_csrf_token()}
