import frappe
from frappe.utils import flt, getdate, now_datetime
from frappe.utils.pdf import get_pdf

from neer_jal.api.permission import MANAGER_ROLES


def _ensure_manager():
	if not (MANAGER_ROLES & set(frappe.get_roles())):
		frappe.throw("Not permitted", frappe.PermissionError)


def _get_payment_modes():
	options = frappe.get_meta("Sales Entry").get_field("payment_mode").options or ""
	return [mode for mode in options.split("\n") if mode]


def _get_filtered_entries(from_date, to_date, customer=None, sales_person=None):
	filters = {"sales_date": ["between", [getdate(from_date), getdate(to_date)]]}
	if customer:
		filters["customer"] = customer
	if sales_person:
		filters["sales_person"] = sales_person

	entries = frappe.get_all(
		"Sales Entry",
		filters=filters,
		fields=[
			"name",
			"sales_date",
			"customer",
			"customer_name",
			"sales_person",
			"cans_given",
			"cans_returned",
			"rate_per_can",
			"amount",
			"payment_mode",
			"trip",
		],
		order_by="sales_date asc, creation asc",
	)

	sales_person_ids = {e.sales_person for e in entries if e.sales_person}
	names = _get_user_full_names(sales_person_ids)
	for e in entries:
		e.sales_person_name = names.get(e.sales_person, e.sales_person)

	return entries


def _get_user_full_names(user_ids):
	if not user_ids:
		return {}
	users = frappe.get_all("User", filters={"name": ["in", list(user_ids)]}, fields=["name", "full_name"])
	return {u.name: u.full_name for u in users}


def _get_customer_label(customer):
	return frappe.db.get_value("Customer", customer, "customer_name") or customer


def _get_totals(entries, payment_modes):
	by_payment_mode = {mode: 0 for mode in payment_modes}
	for e in entries:
		by_payment_mode[e.payment_mode] = by_payment_mode.get(e.payment_mode, 0) + flt(e.amount)

	return {
		"cans_given": sum(flt(e.cans_given) for e in entries),
		"cans_returned": sum(flt(e.cans_returned) for e in entries),
		"amount": sum(flt(e.amount) for e in entries),
		"by_payment_mode": by_payment_mode,
	}


@frappe.whitelist()
def get_delivery_report(from_date, to_date, customer=None, sales_person=None):
	_ensure_manager()
	entries = _get_filtered_entries(from_date, to_date, customer, sales_person)
	payment_modes = _get_payment_modes()
	totals = _get_totals(entries, payment_modes)
	return {"entries": entries, "totals": totals, "payment_modes": payment_modes}


def _build_report_html(from_date, to_date, customer, sales_person, entries, totals, payment_modes):
	customer_label = _get_customer_label(customer) if customer else "All Customers"
	sales_person_label = _get_user_full_names({sales_person}).get(sales_person, sales_person) if sales_person else "All Sales Persons"

	payment_headers = "".join(f'<th style="text-align:right">{mode}</th>' for mode in payment_modes)

	rows = "".join(
		f"""
		<tr>
			<td>{frappe.utils.format_date(e.sales_date)}</td>
			<td>{frappe.utils.escape_html(e.customer_name or e.customer)}</td>
			<td>{frappe.utils.escape_html(e.sales_person_name or e.sales_person)}</td>
			<td style="text-align:right">{flt(e.cans_given):g}</td>
			<td style="text-align:right">{flt(e.cans_returned):g}</td>
			{"".join(
				f'<td style="text-align:right">{flt(e.amount):.2f}</td>'
				if e.payment_mode == mode
				else '<td style="text-align:right">-</td>'
				for mode in payment_modes
			)}
		</tr>
		"""
		for e in entries
	)

	payment_totals = "".join(
		f'<td style="text-align:right">{totals["by_payment_mode"].get(mode, 0):.2f}</td>' for mode in payment_modes
	)

	col_count = 5 + len(payment_modes)

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
		</style>
	</head>
	<body>
		<h2>Neer Jal - Delivery Report</h2>
		<p class="subtitle">
			{frappe.utils.format_date(from_date)} to {frappe.utils.format_date(to_date)}
			&middot; Customer: {frappe.utils.escape_html(customer_label)}
			&middot; Sales Person: {frappe.utils.escape_html(sales_person_label)}
			&middot; Generated on {frappe.utils.format_datetime(now_datetime())}
		</p>
		<table>
			<thead>
				<tr>
					<th>Date</th>
					<th>Customer</th>
					<th>Sales Person</th>
					<th style="text-align:right">Given</th>
					<th style="text-align:right">Refill</th>
					{payment_headers}
				</tr>
			</thead>
			<tbody>
				{rows or f'<tr><td colspan="{col_count}" style="text-align:center">No deliveries found</td></tr>'}
				<tr class="totals-row">
					<td colspan="3">Total ({len(entries)} deliveries)</td>
					<td style="text-align:right">{totals['cans_given']:g}</td>
					<td style="text-align:right">{totals['cans_returned']:g}</td>
					{payment_totals}
				</tr>
				<tr class="totals-row">
					<td colspan="{col_count - 1}">Grand Total</td>
					<td style="text-align:right">{totals['amount']:.2f}</td>
				</tr>
			</tbody>
		</table>
	</body>
	</html>
	"""


@frappe.whitelist()
def download_delivery_report_pdf(from_date, to_date, customer=None, sales_person=None):
	_ensure_manager()
	entries = _get_filtered_entries(from_date, to_date, customer, sales_person)
	payment_modes = _get_payment_modes()
	totals = _get_totals(entries, payment_modes)
	html = _build_report_html(from_date, to_date, customer, sales_person, entries, totals, payment_modes)

	frappe.local.response.filename = (
		f"delivery-report-{getdate(from_date)}-to-{getdate(to_date)}.pdf"
	)
	frappe.local.response.filecontent = get_pdf(html, {"orientation": "Landscape"})
	frappe.local.response.type = "pdf"


def _ensure_trip_access(trip_doc):
	if MANAGER_ROLES & set(frappe.get_roles()):
		return
	if trip_doc.sales_person == frappe.session.user:
		return
	frappe.throw("Not permitted", frappe.PermissionError)


def _get_trip_entries(trip):
	entries = frappe.get_all(
		"Sales Entry",
		filters={"trip": trip},
		fields=[
			"name",
			"sales_date",
			"customer",
			"customer_name",
			"cans_given",
			"cans_returned",
			"amount",
			"payment_mode",
		],
		order_by="sales_date asc, creation asc",
	)
	return entries


def _build_trip_report_html(trip_doc, driver_name, sales_person_name, entries, totals, payment_modes):
	payment_headers = "".join(f'<th style="text-align:right">{mode}</th>' for mode in payment_modes)

	rows = "".join(
		f"""
		<tr>
			<td>{frappe.utils.format_date(e.sales_date)}</td>
			<td>{frappe.utils.escape_html(e.customer_name or e.customer)}</td>
			<td style="text-align:right">{flt(e.cans_given):g}</td>
			<td style="text-align:right">{flt(e.cans_returned):g}</td>
			{"".join(
				f'<td style="text-align:right">{flt(e.amount):.2f}</td>'
				if e.payment_mode == mode
				else '<td style="text-align:right">-</td>'
				for mode in payment_modes
			)}
		</tr>
		"""
		for e in entries
	)

	payment_totals = "".join(
		f'<td style="text-align:right">{totals["by_payment_mode"].get(mode, 0):.2f}</td>' for mode in payment_modes
	)

	col_count = 4 + len(payment_modes)

	def detail(label, value):
		return f'<div class="detail"><span class="label">{label}</span><span class="value">{value}</span></div>'

	details = "".join(
		[
			detail("Vehicle", trip_doc.vehicle or "-"),
			detail("Driver", frappe.utils.escape_html(driver_name or trip_doc.driver or "-")),
			detail("Sales Person", frappe.utils.escape_html(sales_person_name or trip_doc.sales_person or "-")),
			detail("Status", trip_doc.status),
			detail("Start Time", trip_doc.start_time or "-"),
			detail("End Time", trip_doc.end_time or "-"),
			detail("Start KM", trip_doc.start_km if trip_doc.start_km is not None else "-"),
			detail("End KM", trip_doc.end_km or "-"),
			detail("Distance", f"{trip_doc.distance_km} km" if trip_doc.distance_km else "-"),
			detail("Cans Loaded", trip_doc.cans_loaded or 0),
			detail("Cans Delivered", trip_doc.cans_delivered or 0),
			detail("Cans Damaged", trip_doc.cans_damaged or 0),
			detail(
				"Cans Remaining (Good)",
				trip_doc.cans_remaining if trip_doc.status == "Completed" else "-",
			),
		]
	)

	return f"""
	<html>
	<head>
		<style>
			body {{ font-family: Arial, sans-serif; font-size: 12px; color: #111827; }}
			h2 {{ margin-bottom: 0; }}
			.subtitle {{ color: #6b7280; margin-top: 4px; margin-bottom: 16px; }}
			/* wkhtmltopdf's flexbox support is unreliable, so this uses a plain
			   float-based grid instead - it renders correctly in PDF output. */
			.details {{ overflow: hidden; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #e5e7eb; }}
			.detail {{ float: left; width: 25%; box-sizing: border-box; padding-right: 12px; margin-bottom: 12px; }}
			.detail .label {{ display: block; font-size: 10px; text-transform: uppercase; color: #6b7280; margin-bottom: 3px; }}
			.detail .value {{ display: block; font-size: 13px; font-weight: bold; }}
			table {{ width: 100%; border-collapse: collapse; }}
			th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; font-size: 11px; }}
			th {{ background-color: #eff6ff; text-align: left; }}
			.totals-row td {{ font-weight: bold; background-color: #f9fafb; }}
		</style>
	</head>
	<body>
		<h2>Neer Jal - Trip Report</h2>
		<p class="subtitle">
			{trip_doc.name} &middot; Generated on {frappe.utils.format_datetime(now_datetime())}
		</p>
		<div class="details">{details}</div>
		<table>
			<thead>
				<tr>
					<th>Date</th>
					<th>Customer</th>
					<th style="text-align:right">Given</th>
					<th style="text-align:right">Refill</th>
					{payment_headers}
				</tr>
			</thead>
			<tbody>
				{rows or f'<tr><td colspan="{col_count}" style="text-align:center">No deliveries recorded on this trip</td></tr>'}
				<tr class="totals-row">
					<td colspan="2">Total ({len(entries)} deliveries)</td>
					<td style="text-align:right">{totals['cans_given']:g}</td>
					<td style="text-align:right">{totals['cans_returned']:g}</td>
					{payment_totals}
				</tr>
				<tr class="totals-row">
					<td colspan="{col_count - 1}">Grand Total</td>
					<td style="text-align:right">{totals['amount']:.2f}</td>
				</tr>
			</tbody>
		</table>
	</body>
	</html>
	"""


@frappe.whitelist()
def download_trip_report_pdf(trip):
	trip_doc = frappe.get_doc("Trip", trip)
	_ensure_trip_access(trip_doc)

	entries = _get_trip_entries(trip)
	payment_modes = _get_payment_modes()
	totals = _get_totals(entries, payment_modes)

	names = _get_user_full_names({trip_doc.sales_person} if trip_doc.sales_person else set())
	sales_person_name = names.get(trip_doc.sales_person)
	driver_name = frappe.db.get_value("Driver", trip_doc.driver, "driver_name") if trip_doc.driver else None

	html = _build_trip_report_html(trip_doc, driver_name, sales_person_name, entries, totals, payment_modes)

	frappe.local.response.filename = f"trip-report-{trip_doc.name}.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": "Landscape"})
	frappe.local.response.type = "pdf"
