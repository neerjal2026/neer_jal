<template>
  <div class="mx-auto max-w-3xl p-4 sm:p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Time Clock</h1>
      <p class="text-sm text-gray-500">Record when each employee starts and finishes work</p>
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
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Button, Badge, FormControl, createResource } from 'frappe-ui'
import { showError } from '@/utils/toast'

const actionLoading = ref(null)
const search = ref('')

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

const clockIn = createResource({ url: 'neer_jal.api.employees.clock_in' })
const clockOut = createResource({ url: 'neer_jal.api.employees.clock_out' })

function toggle(row) {
  actionLoading.value = row.name
  const action = row.clocked_in ? clockOut : clockIn
  action.submit(
    { employee: row.name },
    {
      onSuccess() {
        actionLoading.value = null
        employees.reload()
      },
      onError(error) {
        actionLoading.value = null
        showError(error, 'Could not update time clock')
      },
    },
  )
}
</script>
