<template>
  <div class="mx-auto max-w-4xl p-4 sm:p-6">
    <div class="mb-6">
      <button class="mb-2 text-sm text-gray-500 hover:text-gray-900" @click="router.back()">
        &larr; Back to Time Clock
      </button>
      <h1 class="text-2xl font-semibold text-gray-900">{{ logs.data?.employee?.employee_name || 'Employee Time Logs' }}</h1>
      <p class="text-sm text-gray-500">{{ logs.data?.employee?.employee_code || employee }}</p>
    </div>

    <div class="boxed-fields mb-6 flex flex-col gap-4 rounded-lg border bg-white p-5 sm:flex-row sm:items-end sm:justify-between">
      <FormControl type="month" label="Month" v-model="month" />
      <Button theme="blue" variant="solid" :loading="logs.loading" @click="loadLogs">Load Logs</Button>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[640px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Time In</th>
            <th class="px-4 py-3 font-medium">Time Out</th>
            <th class="px-4 py-3 font-medium">Hours</th>
            <th class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs.data?.logs || []" :key="log.name" class="border-b last:border-0">
            <td class="px-4 py-3 text-gray-700">{{ log.time_in }}</td>
            <td class="px-4 py-3 text-gray-700">{{ log.time_out || 'Still open' }}</td>
            <td class="px-4 py-3 text-gray-700">{{ log.hours || 0 }}</td>
            <td class="px-4 py-3 text-right">
              <Button theme="red" variant="outline" :loading="deleteLoading === log.name" @click="openDeleteDialog(log)">
                Delete
              </Button>
            </td>
          </tr>
          <tr v-if="!logs.loading && !(logs.data?.logs || []).length">
            <td colspan="4" class="px-4 py-10 text-center text-gray-400">No time logs found for this month</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="logs.data?.total_pages > 1" class="mt-4 flex items-center justify-center gap-3">
      <Button theme="blue" variant="outline" :disabled="page <= 1 || logs.loading" @click="changePage(page - 1)">
        Previous
      </Button>
      <span class="text-sm text-gray-500">Page {{ page }} of {{ logs.data.total_pages }}</span>
      <Button
        theme="blue"
        variant="outline"
        :disabled="page >= logs.data.total_pages || logs.loading"
        @click="changePage(page + 1)"
      >
        Next
      </Button>
    </div>

    <Dialog v-model="showDeleteDialog" :options="{ title: 'Delete Time Log', size: 'sm' }">
      <template #body-content>
        <p class="text-sm text-gray-600">Delete this time log permanently? This will remove it from payroll calculations.</p>
      </template>
      <template #actions>
        <Button theme="red" variant="solid" class="w-full" :loading="deleteLoading === selectedLog?.name" @click="confirmDelete">
          Delete Time Log
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog, FormControl, createResource } from 'frappe-ui'
import { showError, showSuccess } from '@/utils/toast'

const props = defineProps({
  employee: { type: String, required: true },
})

function currentMonth() {
  const date = new Date()
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

const router = useRouter()
const month = ref(currentMonth())
const page = ref(1)
const selectedLog = ref(null)
const showDeleteDialog = ref(false)
const deleteLoading = ref(null)

const logs = createResource({
  url: 'neer_jal.api.employees.get_employee_time_logs',
  auto: true,
  params: { employee: props.employee, month: month.value, page: 1, page_length: 10 },
})

const deleteLog = createResource({ url: 'neer_jal.api.employees.delete_time_log' })

function loadLogs() {
  page.value = 1
  logs.submit({ employee: props.employee, month: month.value, page: 1, page_length: 10 })
}

function changePage(nextPage) {
  page.value = nextPage
  logs.submit({ employee: props.employee, month: month.value, page: nextPage, page_length: 10 })
}

watch(month, loadLogs)

function openDeleteDialog(log) {
  selectedLog.value = log
  showDeleteDialog.value = true
}

function confirmDelete() {
  if (!selectedLog.value) return
  deleteLoading.value = selectedLog.value.name
  deleteLog.submit(
    { name: selectedLog.value.name },
    {
      onSuccess() {
        deleteLoading.value = null
        showDeleteDialog.value = false
        selectedLog.value = null
        showSuccess('Time log deleted')
        loadLogs()
      },
      onError(error) {
        deleteLoading.value = null
        showError(error, 'Could not delete time log')
      },
    },
  )
}
</script>
