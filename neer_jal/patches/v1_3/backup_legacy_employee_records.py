import frappe


EMPLOYEE_FIELDS = [
	"name",
	"employee_code",
	"employee_name",
	"dob",
	"gender",
	"phone",
	"email",
	"role",
	"user",
	"disabled",
	"hourly_wage",
	"joining_date",
	"relieving_date",
	"employment_type",
	"status",
	"designation",
	"current_address",
	"permanent_address",
	"pincode",
	"state",
	"id_number",
	"emergency_contact",
	"education",
	"bank_name",
	"account_no",
	"ifsc_code",
	"other_bank_details",
	"notes",
]


def execute():
	if not frappe.db.has_column("Employee", "employee_code"):
		return
	if frappe.db.table_exists("Neer Jal Employee Migration"):
		return

	available_fields = [field for field in EMPLOYEE_FIELDS if frappe.db.has_column("Employee", field)]
	fields_sql = ", ".join(f"`{field}`" for field in available_fields)
	frappe.db.sql(
		f"""
		create table `tabNeer Jal Employee Migration` as
		select {fields_sql}
		from `tabEmployee`
		where ifnull(employee_code, '') != ''
		"""
	)
