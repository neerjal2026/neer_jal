import frappe
from frappe.utils import flt, getdate, now_datetime
from frappe.utils.pdf import get_pdf

from neer_jal.api.permission import HR_ROLES, MANAGER_ROLES
from neer_jal.api.users import SALES_USER_EMAIL_DOMAIN, USERNAME_PATTERN, _ensure_username_login_enabled
from neer_jal.neer_jal.utils import validate_phone_number

# UI label -> the actual Frappe Role granted to the login created for that employee.
# "Sales Person" maps to the pre-existing "Sales User" role so it plugs into all
# existing sales/trip permission checks unchanged.
ROLE_MAP = {
	"Sales Person": "Sales User",
	"Office Staff": "Office Staff",
}


def _ensure_manager():
	if not (MANAGER_ROLES & set(frappe.get_roles())):
		frappe.throw("Not permitted", frappe.PermissionError)


def _ensure_hr_manager():
	if not (HR_ROLES & set(frappe.get_roles())):
		frappe.throw("Not permitted", frappe.PermissionError)


# Extra profile fields that are simply passed straight through onto the Employee
# doc (format/validity checks for these, e.g. pincode/email, live in the doctype's
# own validate() so they're enforced the same way regardless of caller).
EXTRA_EMPLOYEE_FIELDS = [
	"dob",
	"gender",
	"email",
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
]


@frappe.whitelist()
def create_employee(
	employee_name,
	role=None,
	phone=None,
	hourly_wage=0,
	notes=None,
	username=None,
	password=None,
	dob=None,
	gender=None,
	email=None,
	employment_type=None,
	status=None,
	designation=None,
	current_address=None,
	permanent_address=None,
	pincode=None,
	state=None,
	id_number=None,
	emergency_contact=None,
	education=None,
	bank_name=None,
	account_no=None,
	ifsc_code=None,
	other_bank_details=None,
):
	_ensure_manager()
	employee_name = (employee_name or "").strip()
	if not employee_name:
		frappe.throw("Employee name is required")

	role = (role or "").strip()
	if role and role not in ROLE_MAP:
		frappe.throw("Invalid role")

	phone = validate_phone_number(phone, "Phone") if phone else None

	user_name = None
	if role:
		user_name = _create_login(employee_name, role, phone, username, password)

	extra_values = {k: v for k, v in locals().items() if k in EXTRA_EMPLOYEE_FIELDS}

	employee = frappe.get_doc(
		{
			"doctype": "Employee",
			"employee_name": employee_name,
			"phone": phone,
			"role": role,
			"user": user_name,
			"hourly_wage": flt(hourly_wage),
			"notes": notes,
			**extra_values,
		}
	)
	employee.insert(ignore_permissions=True)
	return employee.as_dict()


def _create_login(employee_name, role, phone, username, password):
	username = (username or "").strip().lower()
	if not username or not password:
		frappe.throw("Username and password are required to create a login for this role")
	if not USERNAME_PATTERN.match(username):
		frappe.throw("Username can only contain lowercase letters, numbers, dots, underscores and hyphens")
	if frappe.db.exists("User", {"username": username}):
		frappe.throw(f"Username {username} is already taken")

	email = f"{username}@{SALES_USER_EMAIL_DOMAIN}"
	if frappe.db.exists("User", email):
		frappe.throw(f"Username {username} is already taken")

	_ensure_username_login_enabled()

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"username": username,
			"full_name": employee_name,
			"first_name": employee_name,
			"mobile_no": phone,
			"send_welcome_email": 0,
			"user_type": "System User",
			"new_password": password,
			"roles": [{"role": ROLE_MAP[role]}],
		}
	)
	user.flags.no_welcome_mail = True
	user.insert(ignore_permissions=True)
	return user.name


@frappe.whitelist()
def update_employee(
	name,
	phone=None,
	hourly_wage=None,
	notes=None,
	disabled=None,
	relieving_date=None,
	dob=None,
	gender=None,
	email=None,
	employment_type=None,
	status=None,
	designation=None,
	current_address=None,
	permanent_address=None,
	pincode=None,
	state=None,
	id_number=None,
	emergency_contact=None,
	education=None,
	bank_name=None,
	account_no=None,
	ifsc_code=None,
	other_bank_details=None,
):
	_ensure_manager()
	employee = frappe.get_doc("Employee", name)
	if phone is not None:
		employee.phone = validate_phone_number(phone, "Phone") if phone else None
	if hourly_wage is not None:
		employee.hourly_wage = flt(hourly_wage)
	if notes is not None:
		employee.notes = notes
	if relieving_date is not None:
		employee.relieving_date = relieving_date or None

	extra_values = locals()
	for fieldname in EXTRA_EMPLOYEE_FIELDS:
		if extra_values[fieldname] is not None:
			employee.set(fieldname, extra_values[fieldname])

	if disabled is not None:
		employee.disabled = int(disabled)
		if employee.user:
			frappe.db.set_value("User", employee.user, "enabled", 0 if employee.disabled else 1)
	employee.save(ignore_permissions=True)
	return employee.as_dict()


@frappe.whitelist()
def get_employees_with_status():
	_ensure_hr_manager()
	employees = frappe.get_all(
		"Employee",
		filters={"disabled": 0},
		fields=["name", "employee_code", "employee_name", "role", "hourly_wage"],
		order_by="employee_name asc",
	)
	open_logs = frappe.get_all(
		"Time Log",
		filters={"time_out": ["is", "not set"]},
		fields=["name", "employee", "time_in"],
	)
	open_by_employee = {log.employee: log for log in open_logs}

	for employee in employees:
		open_log = open_by_employee.get(employee.name)
		employee["clocked_in"] = bool(open_log)
		employee["time_in"] = open_log.time_in if open_log else None

	return employees


@frappe.whitelist()
def clock_in(employee):
	_ensure_hr_manager()
	if frappe.db.exists("Time Log", {"employee": employee, "time_out": ["is", "not set"]}):
		frappe.throw("This employee is already clocked in")

	log = frappe.get_doc(
		{"doctype": "Time Log", "employee": employee, "time_in": now_datetime()}
	)
	log.insert(ignore_permissions=True)
	return log.as_dict()


@frappe.whitelist()
def clock_out(employee):
	_ensure_hr_manager()
	open_name = frappe.db.exists("Time Log", {"employee": employee, "time_out": ["is", "not set"]})
	if not open_name:
		frappe.throw("This employee is not currently clocked in")

	log = frappe.get_doc("Time Log", open_name)
	log.time_out = now_datetime()
	log.save(ignore_permissions=True)
	return log.as_dict()


def _date_range_bounds(from_date, to_date):
	return f"{getdate(from_date)} 00:00:00", f"{getdate(to_date)} 23:59:59"


def _calculate_pay(hourly_wage, total_hours):
	# Pay is prorated to the exact minute rather than rounded to the hour.
	total_minutes = round(flt(total_hours) * 60)
	pay = flt(hourly_wage) / 60 * total_minutes
	hours_display = f"{total_minutes // 60}h {total_minutes % 60}m"
	return total_minutes, hours_display, flt(pay, 2)


@frappe.whitelist()
def run_payroll(from_date, to_date):
	_ensure_hr_manager()
	# An overnight shift (time in one day, time out the next) is attributed to
	# the day it started, so we filter on time_in falling in the selected range.
	from_dt, to_dt = _date_range_bounds(from_date, to_date)

	logs = frappe.get_all(
		"Time Log",
		filters={"time_out": ["is", "set"], "time_in": ["between", [from_dt, to_dt]]},
		fields=["employee", "hours"],
	)

	total_hours_by_employee = {}
	for log in logs:
		total_hours_by_employee[log.employee] = total_hours_by_employee.get(log.employee, 0) + flt(
			log.hours
		)

	if not total_hours_by_employee:
		return []

	employees = frappe.get_all(
		"Employee",
		filters={"name": ["in", list(total_hours_by_employee.keys())]},
		fields=["name", "employee_name", "hourly_wage"],
	)

	result = []
	for employee in employees:
		total_hours = total_hours_by_employee.get(employee.name, 0)
		_, hours_display, total_pay = _calculate_pay(employee.hourly_wage, total_hours)
		result.append(
			{
				"employee": employee.name,
				"employee_name": employee.employee_name,
				"hourly_wage": employee.hourly_wage,
				"total_hours": flt(total_hours, 2),
				"hours_display": hours_display,
				"total_pay": total_pay,
			}
		)

	result.sort(key=lambda r: r["employee_name"])
	return result


def _build_payslip_html(employee, from_date, to_date, logs, hours_display, total_pay):
	rows = "".join(
		f"""
		<tr>
			<td>{frappe.utils.format_datetime(log.time_in)}</td>
			<td>{frappe.utils.format_datetime(log.time_out)}</td>
			<td style="text-align:right">{flt(log.hours):.2f}</td>
		</tr>
		"""
		for log in logs
	)

	return f"""
	<html>
	<head>
		<style>
			body {{ font-family: Arial, sans-serif; font-size: 12px; color: #111827; }}
			h2 {{ margin-bottom: 0; }}
			.subtitle {{ color: #6b7280; margin-top: 4px; margin-bottom: 16px; }}
			table {{ width: 100%; border-collapse: collapse; }}
			th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; font-size: 11px; }}
			th {{ background-color: #eff6ff; text-align: left; }}
			.totals-row td {{ font-weight: bold; background-color: #f9fafb; }}
			.summary {{ margin-top: 16px; width: 260px; margin-left: auto; }}
			.summary td {{ border: none; padding: 4px 0; }}
			.summary tr:last-child td {{ font-weight: bold; border-top: 1px solid #d1d5db; padding-top: 8px; }}
		</style>
	</head>
	<body>
		<h2>Neer Jal - Payslip</h2>
		<p class="subtitle">
			{frappe.utils.escape_html(employee.employee_name)}
			&middot; {frappe.utils.format_date(from_date)} to {frappe.utils.format_date(to_date)}
			&middot; Generated on {frappe.utils.format_datetime(now_datetime())}
		</p>
		<table>
			<thead>
				<tr>
					<th>Time In</th>
					<th>Time Out</th>
					<th style="text-align:right">Hours</th>
				</tr>
			</thead>
			<tbody>
				{rows or '<tr><td colspan="3" style="text-align:center">No time logs found</td></tr>'}
				<tr class="totals-row">
					<td colspan="2">Total ({len(logs)} entries)</td>
					<td style="text-align:right">{hours_display}</td>
				</tr>
			</tbody>
		</table>
		<table class="summary">
			<tr><td>Hourly Wage</td><td style="text-align:right">{flt(employee.hourly_wage):.2f}</td></tr>
			<tr><td>Total Hours</td><td style="text-align:right">{hours_display}</td></tr>
			<tr><td>Total Pay</td><td style="text-align:right">{total_pay:.2f}</td></tr>
		</table>
	</body>
	</html>
	"""


@frappe.whitelist()
def download_payslip_pdf(employee, from_date, to_date):
	_ensure_hr_manager()
	emp = frappe.db.get_value("Employee", employee, ["name", "employee_name", "hourly_wage"], as_dict=True)
	if not emp:
		frappe.throw("Employee not found")

	from_dt, to_dt = _date_range_bounds(from_date, to_date)
	logs = frappe.get_all(
		"Time Log",
		filters={"employee": employee, "time_out": ["is", "set"], "time_in": ["between", [from_dt, to_dt]]},
		fields=["time_in", "time_out", "hours"],
		order_by="time_in asc",
	)

	total_hours = sum(flt(log.hours) for log in logs)
	_, hours_display, total_pay = _calculate_pay(emp.hourly_wage, total_hours)

	html = _build_payslip_html(emp, from_date, to_date, logs, hours_display, total_pay)

	frappe.local.response.filename = f"payslip-{emp.name}-{getdate(from_date)}-to-{getdate(to_date)}.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": "Portrait"})
	frappe.local.response.type = "pdf"
