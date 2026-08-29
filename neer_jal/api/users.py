import re

import frappe
from frappe.utils import cint

MANAGER_ROLES = {"System Manager", "Sales Manager"}
SALES_USER_EMAIL_DOMAIN = "neerjal.com"
USERNAME_PATTERN = re.compile(r"^[a-z0-9._-]+$")


def _ensure_manager():
	if not (MANAGER_ROLES & set(frappe.get_roles())):
		frappe.throw("Not permitted", frappe.PermissionError)


def _ensure_employee_login(user):
	if not ({"Sales User", "Office Staff"} & set(frappe.get_roles(user))):
		frappe.throw("This user does not have an employee login")


@frappe.whitelist()
def get_password_policy():
	return {
		"enabled": bool(frappe.get_system_settings("enable_password_policy")),
		"minimum_score": cint(frappe.get_system_settings("minimum_password_score") or 2),
	}


@frappe.whitelist()
def list_sales_users(start=0, page_length=10):
	_ensure_manager()
	user_names = frappe.get_all(
		"Has Role",
		filters={"role": "Sales User", "parenttype": "User"},
		pluck="parent",
	)
	if not user_names:
		return []
	return frappe.get_all(
		"User",
		filters={"name": ["in", user_names]},
		fields=["name", "username", "full_name", "mobile_no", "enabled"],
		order_by="full_name asc",
		start=cint(start),
		# fetch one extra row so the frontend can tell whether a next page exists
		page_length=cint(page_length) + 1,
	)


def _ensure_username_login_enabled():
	if not cint(frappe.db.get_single_value("System Settings", "allow_login_using_user_name")):
		frappe.db.set_single_value("System Settings", "allow_login_using_user_name", 1)


@frappe.whitelist()
def reset_sales_user_password(user, new_password):
	_ensure_manager()
	_ensure_employee_login(user)

	doc = frappe.get_doc("User", user)
	doc.new_password = new_password
	doc.save(ignore_permissions=True)
