<template>
  <div class="mx-auto max-w-4xl p-4 sm:p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Payroll</h1>
      <p class="text-sm text-gray-500">Run payroll for a date range based on recorded time logs</p>
    </div>

    <div class="boxed-fields mb-6 grid grid-cols-1 gap-4 rounded-lg border bg-white p-5 sm:grid-cols-2 lg:grid-cols-4">
      <FormControl type="date" label="From Date" v-model="filters.from_date" />
      <FormControl type="date" label="To Date" v-model="filters.to_date" />
      <div class="flex items-end sm:col-span-2 lg:col-span-2">
        <Button theme="blue" variant="solid" :loading="payroll.loading" @click="run">
          Run Payroll
        </Button>
      </div>
    </div>

    <div v-if="payroll.data" class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[560px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Employee</th>
            <th class="px-4 py-3 font-medium">Hourly Wage</th>
            <th class="px-4 py-3 font-medium">Hours Worked</th>
            <th class="px-4 py-3 font-medium">Total Pay</th>
            <th class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in payroll.data" :key="row.employee" class="border-b last:border-0">
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.employee_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ formatCurrency(row.hourly_wage) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.hours_display }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ formatCurrency(row.total_pay) }}</td>
            <td class="px-4 py-3">
              <Button
                theme="blue"
                variant="outline"
                :loading="payslipLoading === row.employee"
                @click="downloadPayslip(row)"
              >
                Payslip
              </Button>
            </td>
          </tr>
          <tr v-if="!payroll.data.length">
            <td colspan="5" class="px-4 py-10 text-center text-gray-400">
              No time logs found for this date range
            </td>
          </tr>
        </tbody>
        <tfoot v-if="payroll.data.length">
          <tr class="border-t bg-gray-50 font-semibold text-gray-900">
            <td class="px-4 py-3" colspan="3">Total</td>
            <td class="px-4 py-3" colspan="2">{{ formatCurrency(grandTotal) }}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Button, FormControl, createResource } from 'frappe-ui'
import { showError } from '@/utils/toast'
import { downloadFile } from '@/utils/download'

function firstOfMonth() {
  const d = new Date()
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10)
}

function lastOfMonth() {
  const d = new Date()
  return new Date(d.getFullYear(), d.getMonth() + 1, 0).toISOString().slice(0, 10)
}

const filters = reactive({
  from_date: firstOfMonth(),
  to_date: lastOfMonth(),
})

const payroll = createResource({
  url: 'neer_jal.api.employees.run_payroll',
})

function run() {
  if (!filters.from_date || !filters.to_date) {
    showError('Please choose both a from and to date')
    return
  }
  payroll.submit(
    { ...filters },
    {
      onError(error) {
        showError(error, 'Could not run payroll')
      },
    },
  )
}

const grandTotal = computed(() => (payroll.data || []).reduce((sum, row) => sum + Number(row.total_pay || 0), 0))

const payslipLoading = ref(null)

async function downloadPayslip(row) {
  payslipLoading.value = row.employee
  const params = new URLSearchParams({
    employee: row.employee,
    from_date: filters.from_date,
    to_date: filters.to_date,
  })
  const url = `/api/method/neer_jal.api.employees.download_payslip_pdf?${params.toString()}`
  const filename = `payslip-${row.employee}-${filters.from_date}-to-${filters.to_date}.pdf`
  try {
    await downloadFile(url, filename)
  } catch {
    // downloadFile already surfaced a toast
  } finally {
    payslipLoading.value = null
  }
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
