<template>
  <div class="mx-auto max-w-3xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Time Clock</h1>
        <p class="text-sm text-gray-500">Record when each employee starts and finishes work</p>
      </div>
      <Button v-if="isHrManager" theme="blue" variant="outline" class="w-full sm:w-auto" @click="showManualDialog = true">
        Add Past Time Log
      </Button>
    </div>

    <FormControl
      class="mb-4"
      label="Search"
      placeholder="Search by name or employee ID"
      v-model="search"
    />

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[560px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Employee ID</th>
            <th class="px-4 py-3 font-medium">Employee</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium">Since</th>
            <th class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredEmployees" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 text-gray-600">{{ row.employee_code }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.employee_name }}</td>
            <td class="px-4 py-3">
              <Badge :theme="row.clocked_in ? 'green' : 'gray'" variant="subtle">
                {{ row.clocked_in ? 'Clocked In' : 'Clocked Out' }}
              </Badge>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ row.clocked_in ? row.time_in : '-' }}</td>
            <td class="px-4 py-3">
              <Button
                :theme="row.clocked_in ? 'red' : 'blue'"
                variant="solid"
                :loading="actionLoading === row.name"
                @click="toggle(row)"
              >
                {{ row.clocked_in ? 'Time Out' : 'Time In' }}
              </Button>
            </td>
          </tr>
          <tr v-if="!employees.loading && !filteredEmployees.length">
            <td colspan="5" class="px-4 py-10 text-center text-gray-400">
              {{ search ? 'No employees match your search' : 'No active employees' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Dialog v-model="showConfirmDialog" :options="{ title: pendingRow?.clocked_in ? 'Confirm Time Out' : 'Confirm Time In', size: 'sm' }">
      <template #body-content>
        <p class="text-sm text-gray-600">
          {{ pendingRow?.clocked_in ? 'Are you sure you want to record time out for' : 'Are you sure you want to record time in for' }}
          <span class="font-medium text-gray-900">{{ pendingRow?.employee_name }}</span>?
        </p>
      </template>
      <template #actions>
        <Button
          :theme="pendingRow?.clocked_in ? 'red' : 'blue'"
          variant="solid"
          class="w-full"
          :loading="actionLoading === pendingRow?.name"
          @click="confirmToggle"
        >
          {{ pendingRow?.clocked_in ? 'Confirm Time Out' : 'Confirm Time In' }}
        </Button>
      </template>
    </Dialog>

    <Dialog
      v-model="showManualDialog"
      :options="{ title: 'Add Past Time Log', size: 'sm' }"
      disable-outside-click-to-close
    >
      <template #body>
        <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
          <div class="mb-6 flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900">Add Past Time Log</h3>
            <button
              type="button"
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              aria-label="Close dialog"
              @click="showManualDialog = false"
            >
              <FeatherIcon name="x" class="h-5 w-5" />
            </button>
          </div>
          <div class="boxed-fields grid grid-cols-1 gap-4">
            <div>
              <FormControl label="Search Employee" placeholder="Search by ID or name" v-model="employeeSearch" />
              <div v-if="employeeSearch.trim() && !manualForm.employee" class="mt-2 max-h-40 overflow-y-auto rounded border bg-white">
                <button
                  v-for="employee in searchedEmployees"
                  :key="employee.name"
                  type="button"
                  class="block w-full border-b px-3 py-2 text-left text-sm last:border-0 hover:bg-blue-50"
                  @click="selectEmployee(employee)"
                >
                  <span class="font-medium text-gray-900">{{ employee.employee_name }}</span>
                  <span class="ml-2 text-gray-500">{{ employee.employee_code }}</span>
                </button>
                <p v-if="!searchedEmployees.length" class="px-3 py-2 text-sm text-gray-500">
                  No employees found
                </p>
              </div>
              <div v-if="manualForm.employee" class="mt-2 flex items-center justify-between rounded border bg-gray-50 px-3 py-2 text-sm">
                <span class="text-gray-700">{{ selectedEmployee?.employee_name }} ({{ selectedEmployee?.employee_code }})</span>
                <button type="button" class="text-gray-500 hover:text-gray-900" @click="clearEmployee">Change</button>
              </div>
            </div>
            <FormControl type="datetime-local" label="Time In" required v-model="manualForm.time_in" />
            <FormControl type="datetime-local" label="Time Out" required v-model="manualForm.time_out" />
          </div>
          <ErrorMessage class="mt-3 block" :message="manualLog.error" />
        </div>
        <div class="px-4 pb-7 pt-4 sm:px-6">
          <Button theme="blue" variant="solid" class="w-full" :loading="manualLog.loading" @click="submitManualLog">
            Add Time Log
          </Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Button, Badge, Dialog, ErrorMessage, FeatherIcon, FormControl, createResource } from 'frappe-ui'
import { isHrManager } from '@/utils/session'
import { showError, showSuccess } from '@/utils/toast'

const actionLoading = ref(null)
const pendingRow = ref(null)
const showConfirmDialog = ref(false)
const showManualDialog = ref(false)
const search = ref('')
const employeeSearch = ref('')
const manualForm = reactive({ employee: '', time_in: '', time_out: '' })

const employees = createResource({
  url: 'neer_jal.api.employees.get_employees_with_status',
  auto: true,
  initialData: [],
})

const filteredEmployees = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return employees.data || []
  return (employees.data || []).filter(
    (row) =>
      row.employee_name?.toLowerCase().includes(term) || row.employee_code?.toLowerCase().includes(term),
  )
})

const searchedEmployees = computed(() => {
  const term = employeeSearch.value.trim().toLowerCase()
  return (employees.data || []).filter(
    (row) =>
      row.employee_name?.toLowerCase().includes(term) || row.employee_code?.toLowerCase().includes(term),
  )
})

const selectedEmployee = computed(() => (employees.data || []).find((row) => row.name === manualForm.employee))

const clockIn = createResource({ url: 'neer_jal.api.employees.clock_in' })
const clockOut = createResource({ url: 'neer_jal.api.employees.clock_out' })
const manualLog = createResource({ url: 'neer_jal.api.employees.add_past_time_log' })

watch(showManualDialog, (value) => {
  if (value) {
    Object.assign(manualForm, { employee: '', time_in: '', time_out: '' })
    employeeSearch.value = ''
  }
})

function toggle(row) {
  pendingRow.value = row
  showConfirmDialog.value = true
}

function confirmToggle() {
  const row = pendingRow.value
  if (!row) return

  actionLoading.value = row.name
  const action = row.clocked_in ? clockOut : clockIn
  action.submit(
    { employee: row.name },
    {
      onSuccess() {
        actionLoading.value = null
        showConfirmDialog.value = false
        pendingRow.value = null
        employees.reload()
      },
      onError(error) {
        actionLoading.value = null
        showError(error, 'Could not update time clock')
      },
    },
  )
}

function submitManualLog() {
  if (!manualForm.employee || !manualForm.time_in || !manualForm.time_out) {
    showError('Select an employee and enter both times')
    return
  }

  manualLog.submit(manualForm, {
    onSuccess() {
      showSuccess('Past time log added')
      showManualDialog.value = false
      employees.reload()
    },
    onError(error) {
      showError(error, 'Could not add past time log')
    },
  })
}

function selectEmployee(employee) {
  manualForm.employee = employee.name
  employeeSearch.value = ''
}

function clearEmployee() {
  manualForm.employee = ''
  employeeSearch.value = ''
}
</script>
