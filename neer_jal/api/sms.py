import frappe
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.utils import flt


def queue_delivery_sms(sales_entry_name):
	frappe.enqueue(
		"neer_jal.api.sms.send_delivery_sms",
		queue="short",
		sales_entry_name=sales_entry_name,
	)


def send_delivery_sms(sales_entry_name):
	try:
		_send_delivery_sms(sales_entry_name)
	except Exception:
		frappe.log_error(title="Delivery SMS failed", message=frappe.get_traceback())


def _send_delivery_sms(sales_entry_name):
	if not frappe.db.get_single_value("Sales Settings", "enable_sms_notifications"):
		return

	entry = frappe.db.get_value(
		"Sales Entry",
		sales_entry_name,
		["customer", "cans_given", "cans_returned", "amount", "payment_mode"],
		as_dict=True,
	)
	if not entry:
		return

	customer = frappe.db.get_value(
		"Customer", entry.customer, ["customer_name", "phone", "sms_enabled", "owner"], as_dict=True
	)
	if not customer or not customer.sms_enabled:
		return

	message = (
		f"Neer Jal: Delivered {flt(entry.cans_given):g} can(s) to {customer.customer_name}. "
		f"Refill collected: {flt(entry.cans_returned):g}. Amount: Rs.{flt(entry.amount):.2f} "
		f"({entry.payment_mode}). Thank you!"
	)

	receivers = []
	if customer.phone:
		receivers.append(customer.phone)

	manager_mobile = frappe.db.get_value("User", customer.owner, "mobile_no")
	if manager_mobile and manager_mobile not in receivers:
		receivers.append(manager_mobile)

	if not receivers:
		return

	send_sms(receivers, message, success_msg=False)
