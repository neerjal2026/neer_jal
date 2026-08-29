import { computed } from 'vue'
import { createResource, frappeRequest } from 'frappe-ui'

export const session = createResource({
  url: 'neer_jal.api.permission.get_my_roles',
  auto: true,
  initialData: { roles: [], is_manager: false, is_hr_manager: false },
  resourceFetcher: frappeRequest,
})

export const isManager = computed(() => !!session.data?.is_manager)
export const isHrManager = computed(() => !!session.data?.is_hr_manager)
