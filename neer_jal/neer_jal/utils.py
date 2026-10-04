import re

import frappe


def validate_phone_number(phone, label="Phone"):
	"""Strip formatting and require exactly 10 digits. Returns the cleaned digits-only
	value, or the original falsy value (None/"") unchanged if nothing was entered."""
	if not phone:
		return phone

	digits = re.sub(r"\D", "", phone)
	if len(digits) != 10:
		frappe.throw(f"{label} must be exactly 10 digits")

	return digits


