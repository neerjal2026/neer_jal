<template>
  <div class="mx-auto max-w-4xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Salary Advances</h1>
        <p class="text-sm text-gray-500">Record advances that will be deducted from monthly payroll</p>
      </div>
      <Button theme="blue" variant="solid" class="w-full sm:w-auto" @click="showAddDialog = true">
        Add Salary Advance
      </Button>
    </div>

    <div class="boxed-fields mb-6 flex flex-col gap-4 rounded-lg border bg-white p-5 sm:flex-row sm:items-end sm:justify-between">
      <FormControl type="month" label="Month" v-model="month" />
      <Button theme="blue" variant="outline" :loading="advances.loading" @click="loadAdvances">Load Advances</Button>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[720px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Employee</th>
            <th class="px-4 py-3 font-medium">Date</th>
            <th class="px-4 py-3 font-medium">Amount</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium">Notes</th>
            <th class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="advance in advances.data?.advances || []" :key="advance.name" class="border-b last:border-0">
            <td class="px-4 py-3 font-medium text-gray-900">
              {{ advance.employee_name }}
              <span class="ml-1 text-xs text-gray-500">{{ advance.employee_code }}</span>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ advance.advance_date }}</td>
            <td class="px-4 py-3 text-gray-900">{{ formatCurrency(advance.amount) }}</td>
            <td class="px-4 py-3">
              <Badge :theme="advance.status === 'Unpaid' ? 'orange' : 'gray'" variant="subtle">{{ advance.status }}</Badge>
            </td>
            <td class="max-w-xs truncate px-4 py-3 text-gray-600">{{ advance.notes || '-' }}</td>
            <td class="px-4 py-3 text-right">
              <Button
                v-if="advance.status === 'Unpaid'"
                theme="red"
                variant="outline"
                :loading="cancelLoading === advance.name"
                @click="openCancelDialog(advance)"
              >
                Cancel
              </Button>
            </td>
          </tr>
          <tr v-if="!advances.loading && !(advances.data?.advances || []).length">
            <td colspan="6" class="px-4 py-10 text-center text-gray-400">No salary advances found for this month</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="advances.data?.total_pages > 1" class="mt-4 flex items-center justify-center gap-3">
      <Button theme="blue" variant="outline" :disabled="page <= 1 || advances.loading" @click="changePage(page - 1)">
        Previous
      </Button>
      <span class="text-sm text-gray-500">Page {{ page }} of {{ advances.data.total_pages }}</span>
      <Button
        theme="blue"
        variant="outline"
        :disabled="page >= advances.data.total_pages || advances.loading"
        @click="changePage(page + 1)"
      >
        Next
      </Button>
    </div>

    <Dialog v-model="showAddDialog" :options="{ title: 'Add Salary Advance', size: 'sm' }" disable-outside-click-to-close>
      <template #body>
        <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
          <div class="mb-6 flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900">Add Salary Advance</h3>
            <button type="button" class="flex h-8 w-8 items-center justify-center rounded text-gray-600 hover:bg-gray-100" aria-label="Close dialog" @click="showAddDialog = false">
              <FeatherIcon name="x" class="h-5 w-5" />
            </button>
          </div>
          <div class="boxed-fields grid grid-cols-1 gap-4">
            <div>
              <FormControl label="Search Employee" placeholder="Search by ID or name" v-model="employeeSearch" />
              <div v-if="employeeSearch.trim() && !form.employee" class="mt-2 max-h-40 overflow-y-auto rounded border bg-white">
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
                <p v-if="!searchedEmployees.length" class="px-3 py-2 text-sm text-gray-500">No employees found</p>
              </div>
              <div v-if="form.employee" class="mt-2 flex items-center justify-between rounded border bg-gray-50 px-3 py-2 text-sm">
                <span class="text-gray-700">{{ selectedEmployee?.employee_name }} ({{ selectedEmployee?.employee_code }})</span>
                <button type="button" class="text-gray-500 hover:text-gray-900" @click="clearEmployee">Change</button>
              </div>
            </div>
            <FormControl type="date" label="Advance Date" required v-model="form.advance_date" />
            <FormControl type="number" label="Amount" required v-model="form.amount" />
            <FormControl type="textarea" label="Notes" v-model="form.notes" />
          </div>
          <ErrorMessage class="mt-3 block" :message="createAdvance.error" />
        </div>
        <div class="px-4 pb-7 pt-4 sm:px-6">
          <Button theme="blue" variant="solid" class="w-full" :loading="createAdvance.loading" @click="submitAdvance">
            Add Advance
          </Button>
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showCancelDialog" :options="{ title: 'Cancel Salary Advance', size: 'sm' }">
      <template #body-content>
        <p class="text-sm text-gray-600">Cancel this salary advance? It will no longer be deducted from payroll.</p>
      </template>
      <template #actions>
        <Button theme="red" variant="solid" class="w-full" :loading="cancelLoading === selectedAdvance?.name" @click="confirmCancel">
          Cancel Salary Advance
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Badge, Button, Dialog, ErrorMessage, FeatherIcon, FormControl, createResource } from 'frappe-ui'
import { showError, showSuccess } from '@/utils/toast'

function currentMonth() {
  const date = new Date()
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

const month = ref(currentMonth())
const page = ref(1)
const showAddDialog = ref(false)
const showCancelDialog = ref(false)
const employeeSearch = ref('')
const selectedAdvance = ref(null)
const cancelLoading = ref(null)
const form = reactive({ employee: '', advance_date: today(), amount: '', notes: '' })

const employees = createResource({
  url: 'neer_jal.api.employees.get_employees_with_status',
  auto: true,
  initialData: [],
})

const advances = createResource({
  url: 'neer_jal.api.employees.get_salary_advances',
  auto: true,
  params: { month: month.value, page: 1, page_length: 10 },
})

const createAdvance = createResource({ url: 'neer_jal.api.employees.create_salary_advance' })
const cancelAdvance = createResource({ url: 'neer_jal.api.employees.cancel_salary_advance' })

const searchedEmployees = computed(() => {
  const term = employeeSearch.value.trim().toLowerCase()
  return (employees.data || []).filter(
    (employee) =>
      employee.employee_name?.toLowerCase().includes(term) || employee.employee_code?.toLowerCase().includes(term),
  )
})

const selectedEmployee = computed(() => (employees.data || []).find((employee) => employee.name === form.employee))

function loadAdvances() {
  page.value = 1
  advances.submit({ month: month.value, page: 1, page_length: 10 })
}

function changePage(nextPage) {
  page.value = nextPage
  advances.submit({ month: month.value, page: nextPage, page_length: 10 })
}

watch(month, loadAdvances)
watch(showAddDialog, (value) => {
  if (value) {
    Object.assign(form, { employee: '', advance_date: today(), amount: '', notes: '' })
    employeeSearch.value = ''
  }
})

function selectEmployee(employee) {
  form.employee = employee.name
  employeeSearch.value = ''
}

function clearEmployee() {
  form.employee = ''
  employeeSearch.value = ''
}

function submitAdvance() {
  if (!form.employee || !form.advance_date || !form.amount) {
    showError('Select an employee, date, and amount')
    return
  }
  createAdvance.submit(form, {
    onSuccess() {
      showSuccess('Salary advance added')
      showAddDialog.value = false
      loadAdvances()
    },
    onError(error) {
      showError(error, 'Could not add salary advance')
    },
  })
}

function openCancelDialog(advance) {
  selectedAdvance.value = advance
  showCancelDialog.value = true
}

function confirmCancel() {
  if (!selectedAdvance.value) return
  cancelLoading.value = selectedAdvance.value.name
  cancelAdvance.submit(
    { name: selectedAdvance.value.name },
    {
      onSuccess() {
        cancelLoading.value = null
        showCancelDialog.value = false
        selectedAdvance.value = null
        showSuccess('Salary advance cancelled')
        loadAdvances()
      },
      onError(error) {
        cancelLoading.value = null
        showError(error, 'Could not cancel salary advance')
      },
    },
  )
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
