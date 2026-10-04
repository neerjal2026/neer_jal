import frappe


EMPLOYEE_FIELDS = [
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
	if not frappe.db.exists("DocType", "Neer Jal Employee"):
		return
	if not frappe.db.table_exists("Neer Jal Employee Migration"):
		return

	employees = frappe.db.sql(
		"select * from `tabNeer Jal Employee Migration`",
		as_dict=True,
	)
	for employee in employees:
		if frappe.db.exists("Neer Jal Employee", employee.name):
			continue

		doc = {"doctype": "Neer Jal Employee", "name": employee.name}
		for field in EMPLOYEE_FIELDS:
			if field in employee:
				doc[field] = employee[field]
		if doc.get("role") == "Sales Person":
			doc["role"] = "Driver"
		frappe.get_doc(doc).insert(ignore_permissions=True)

	frappe.db.sql("delete from `tabNeer Jal Employee Migration`")
