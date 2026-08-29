import zxcvbn from 'zxcvbn'
import { createResource, frappeRequest } from 'frappe-ui'

// Mirrors Frappe's own backend password policy (frappe.utils.password_strength,
// which is built on zxcvbn) so the frontend rejects exactly what the backend would.
export const passwordPolicy = createResource({
  url: 'neer_jal.api.users.get_password_policy',
  auto: true,
  initialData: { enabled: true, minimum_score: 2 },
  resourceFetcher: frappeRequest,
})

export function checkPasswordStrength(password, { inputs = [] } = {}) {
  const pwd = password || ''
  if (!pwd) return null

  const policy = passwordPolicy.data || { enabled: true, minimum_score: 2 }
  if (!policy.enabled) return null

  const result = zxcvbn(pwd, inputs.filter(Boolean))
  if (result.score < policy.minimum_score) {
    return (
      result.feedback?.warning ||
      result.feedback?.suggestions?.[0] ||
      'This password is too weak. Please choose a stronger one.'
    )
  }
  return null
}
