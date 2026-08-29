import { toast } from 'frappe-ui'

export function showSuccess(title) {
  toast({ title, icon: 'check-circle', iconClasses: 'text-green-600', timeout: 3 })
}

// Accepts either a plain string, or the Error object frappe-ui passes to onError
// handlers (which carries the actual backend validation message in `.messages`).
// Falling back to a generic message only when no specific one is available.
export function showError(errorOrMessage, fallback = 'Something went wrong') {
  let title = fallback
  if (typeof errorOrMessage === 'string' && errorOrMessage) {
    title = errorOrMessage
  } else if (errorOrMessage && typeof errorOrMessage === 'object') {
    title = errorOrMessage.messages?.[0] || errorOrMessage.message || fallback
  }
  toast({ title, icon: 'alert-circle', iconClasses: 'text-red-600', timeout: 5 })
}
