// Mirrors the backend's validate_phone_number() (my_app/utils.py) so obviously
// invalid phone numbers are caught instantly, without a round trip to the server.
export function checkPhoneNumber(phone, label = 'Phone') {
  if (!phone) return null

  const digits = String(phone).replace(/\D/g, '')
  if (digits.length !== 10) {
    return `${label} must be exactly 10 digits`
  }
  return null
}
