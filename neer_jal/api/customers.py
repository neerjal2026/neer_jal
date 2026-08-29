import frappe
from frappe.utils import cint


@frappe.whitelist()
def search_customers(search=None, only_pending=False, start=0, page_length=10):
	conditions = []
	values = {}

	if search:
		conditions.append("(customer_code like %(search)s or customer_name like %(search)s)")
		values["search"] = f"%{search}%"

	if cint(only_pending):
		conditions.append("(amount_due > 0 or cans_pending > 0)")

	where_clause = f"where {' and '.join(conditions)}" if conditions else ""

	values["page_length"] = cint(page_length) + 1
	values["start"] = cint(start)

	return frappe.db.sql(
		f"""
		select name, customer_code, customer_name, phone, city, disabled, cans_pending, amount_due
		from `tabCustomer`
		{where_clause}
		order by modified desc
		limit %(page_length)s offset %(start)s
		""",
		values,
		as_dict=True,
	)
