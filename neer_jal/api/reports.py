import frappe
from frappe.utils import flt, getdate, now_datetime
from frappe.utils.pdf import get_pdf

from neer_jal.api.permission import MANAGER_ROLES


def _ensure_manager():
	if not (MANAGER_ROLES & set(frappe.get_roles())):
		frappe.throw("Not permitted", frappe.PermissionError)


def _get_user_full_names(user_ids):
	if not user_ids:
		return {}
	users = frappe.get_all("User", filters={"name": ["in", list(user_ids)]}, fields=["name", "full_name"])
	return {user.name: user.full_name for user in users}


def _get_trip_sheet(from_date, to_date, driver=None):
	from_date = getdate(from_date)
	to_date = getdate(to_date)
	if from_date > to_date:
		frappe.throw("From date cannot be after To date")

	filters = {"start_time": ["between", [f"{from_date} 00:00:00", f"{to_date} 23:59:59"]]}
	if driver:
		filters["driver"] = driver

	trips = frappe.get_all(
		"Trip",
		filters=filters,
		fields=[
			"name", "driver", "vehicle", "trip_route", "route_price", "driver_credit",
			"status", "start_time", "end_time", "start_km", "end_km", "distance_km", "notes",
		],
		order_by="start_time asc, driver asc",
	)

	driver_names = _get_user_full_names({trip.driver for trip in trips if trip.driver})
	route_ids = {trip.trip_route for trip in trips if trip.trip_route}
	route_names = {
		row.name: row.route_name
		for row in frappe.get_all(
			"Trip Route", filters={"name": ["in", list(route_ids)]}, fields=["name", "route_name"]
		)
	}
	for trip in trips:
		trip.driver_name = driver_names.get(trip.driver, trip.driver)
		trip.route_name = route_names.get(trip.trip_route, trip.trip_route or "-")

	return {
		"trips": trips,
		"totals": {
			"trip_count": len(trips),
			"completed_count": sum(1 for trip in trips if trip.status == "Completed"),
			"route_price": sum(flt(trip.route_price) for trip in trips),
			"driver_credit": sum(flt(trip.driver_credit) for trip in trips),
		},
	}


@frappe.whitelist()
def get_trip_sheet(from_date, to_date, driver=None):
	_ensure_manager()
	return _get_trip_sheet(from_date, to_date, driver)


def _build_trip_sheet_html(from_date, to_date, data, driver=None):
	driver_name = _get_user_full_names({driver}).get(driver, driver) if driver else "All Drivers"
	rows = []
	for trip in data["trips"]:
		end_km = f"{flt(trip.end_km):g}" if trip.end_km is not None else "-"
		distance = f"{flt(trip.distance_km):g}" if trip.distance_km is not None else "-"
		rows.append(
			f"""
		<tr>
			<td>{frappe.utils.format_datetime(trip.start_time)}</td>
			<td>{frappe.utils.escape_html(trip.driver_name or "-")}</td>
			<td>{frappe.utils.escape_html(trip.vehicle or "-")}</td>
			<td>{frappe.utils.escape_html(trip.route_name or "-")}</td>
			<td style="text-align:right">{flt(trip.start_km):g}</td>
			<td style="text-align:right">{end_km}</td>
			<td style="text-align:right">{distance}</td>
			<td>{frappe.utils.escape_html(trip.status)}</td>
			<td style="text-align:right">{flt(trip.route_price):.2f}</td>
			<td style="text-align:right">{flt(trip.driver_credit):.2f}</td>
			<td>{frappe.utils.escape_html(trip.notes or "-")}</td>
		</tr>
		"""
		)
	rows = "".join(rows)
	totals = data["totals"]
	return f"""
	<html>
	<head>
		<style>
			body {{ font-family: Arial, sans-serif; font-size: 12px; color: #111827; }}
			h2 {{ margin-bottom: 0; }}
			.subtitle {{ color: #6b7280; margin: 4px 0 16px; }}
			table {{ width: 100%; border-collapse: collapse; }}
			th, td {{ border: 1px solid #d1d5db; padding: 6px 7px; font-size: 9px; }}
			th {{ background-color: #eff6ff; text-align: left; }}
			.total td {{ font-weight: bold; background-color: #f9fafb; }}
		</style>
	</head>
	<body>
		<h2>Neer Jal - Driver Trip Sheet</h2>
		<p class="subtitle">{frappe.utils.format_date(from_date)} to {frappe.utils.format_date(to_date)} &middot; {frappe.utils.escape_html(driver_name)} &middot; Generated {frappe.utils.format_datetime(now_datetime())}</p>
		<table>
			<thead><tr><th>Started</th><th>Driver</th><th>Vehicle</th><th>Route</th><th>Start KM</th><th>End KM</th><th>Distance</th><th>Status</th><th>Route Price</th><th>Driver Credit</th><th>Notes</th></tr></thead>
			<tbody>
				{rows or '<tr><td colspan="11" style="text-align:center">No trips found</td></tr>'}
				<tr class="total"><td colspan="7">Totals ({totals['trip_count']} trips, {totals['completed_count']} completed)</td><td></td><td style="text-align:right">{totals['route_price']:.2f}</td><td style="text-align:right">{totals['driver_credit']:.2f}</td><td></td></tr>
			</tbody>
		</table>
	</body>
	</html>
	"""


@frappe.whitelist()
def download_trip_sheet_pdf(from_date, to_date, driver=None):
	_ensure_manager()
	data = _get_trip_sheet(from_date, to_date, driver)
	html = _build_trip_sheet_html(from_date, to_date, data, driver)
	frappe.local.response.filename = f"driver-trip-sheet-{getdate(from_date)}-to-{getdate(to_date)}.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": "Landscape"})
	frappe.local.response.type = "pdf"


def _ensure_trip_access(trip):
	if MANAGER_ROLES & set(frappe.get_roles()):
		return
	if trip.driver == frappe.session.user:
		return
	frappe.throw("Not permitted", frappe.PermissionError)


@frappe.whitelist()
def download_trip_report_pdf(trip):
	trip_doc = frappe.get_doc("Trip", trip)
	_ensure_trip_access(trip_doc)
	trip_sheet = _get_trip_sheet(trip_doc.start_time.date(), trip_doc.start_time.date(), trip_doc.driver)
	trip_sheet["trips"] = [row for row in trip_sheet["trips"] if row.name == trip_doc.name]
	trip_sheet["totals"] = {
		"trip_count": len(trip_sheet["trips"]),
		"completed_count": sum(1 for row in trip_sheet["trips"] if row.status == "Completed"),
		"route_price": sum(flt(row.route_price) for row in trip_sheet["trips"]),
		"driver_credit": sum(flt(row.driver_credit) for row in trip_sheet["trips"]),
	}
	html = _build_trip_sheet_html(trip_doc.start_time.date(), trip_doc.start_time.date(), trip_sheet, trip_doc.driver)
	frappe.local.response.filename = f"trip-report-{trip_doc.name}.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": "Landscape"})
	frappe.local.response.type = "pdf"
