<template>
  <div class="mx-auto max-w-6xl p-4 sm:p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Reports</h1>
      <p class="text-sm text-gray-500">Filter deliveries by date, customer or sales person</p>
    </div>

    <div class="boxed-fields mb-6 grid grid-cols-1 gap-4 rounded-lg border bg-white p-5 sm:grid-cols-2 lg:grid-cols-4">
      <FormControl type="date" label="From Date" v-model="filters.from_date" />
      <FormControl type="date" label="To Date" v-model="filters.to_date" />
      <FormControl
        type="select"
        label="Customer"
        :options="customerOptions"
        v-model="filters.customer"
      />
      <FormControl
        type="select"
        label="Sales Person"
        :options="salesPersonOptions"
        v-model="filters.sales_person"
      />
      <div class="flex items-end gap-2 sm:col-span-2 lg:col-span-4">
        <Button theme="blue" variant="solid" :loading="report.loading" @click="search">
          Search
        </Button>
        <Button theme="blue" variant="outline" :loading="downloading" @click="downloadPdf">
          Export PDF
        </Button>
      </div>
    </div>

    <div v-if="report.data" class="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Deliveries</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ report.data.entries.length }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Total Cans Given</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ report.data.totals.cans_given }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Total Amount</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ formatCurrency(report.data.totals.amount) }}</p>
      </div>
    </div>

    <div v-if="report.data" class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div v-for="mode in report.data.payment_modes" :key="mode" class="rounded-lg border bg-white p-4">
        <div class="flex items-center gap-2">
          <Badge :theme="paymentTheme(mode)" variant="subtle">{{ mode }}</Badge>
        </div>
        <p class="mt-1 text-xl font-semibold text-gray-900">
          {{ formatCurrency(report.data.totals.by_payment_mode[mode]) }}
        </p>
      </div>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[920px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Date</th>
            <th class="px-4 py-3 font-medium">Customer</th>
            <th class="px-4 py-3 font-medium">Sales Person</th>
            <th class="px-4 py-3 font-medium">Given</th>
            <th class="px-4 py-3 font-medium">Refill</th>
            <th
              v-for="mode in report.data?.payment_modes || []"
              :key="mode"
              class="px-4 py-3 font-medium text-right"
            >
              {{ mode }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in pagedEntries" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 text-gray-600">{{ row.sales_date }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.customer_name || row.customer }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.sales_person_name || row.sales_person }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.cans_given }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.cans_returned }}</td>
            <td
              v-for="mode in report.data.payment_modes"
              :key="mode"
              class="px-4 py-3 text-right text-gray-600"
            >
              {{ row.payment_mode === mode ? formatCurrency(row.amount) : '-' }}
            </td>
          </tr>
          <tr v-if="report.data && !report.data.entries.length">
            <td :colspan="5 + (report.data.payment_modes?.length || 0)" class="px-4 py-10 text-center text-gray-400">
              No deliveries found for these filters
            </td>
          </tr>
          <tr v-if="!report.data">
            <td colspan="5" class="px-4 py-10 text-center text-gray-400">
              Choose a date range and click Search
            </td>
          </tr>
        </tbody>
        <tfoot v-if="report.data && report.data.entries.length">
          <tr class="border-t bg-gray-50 font-semibold text-gray-900">
            <td class="px-4 py-3" colspan="3">Total ({{ report.data.entries.length }} deliveries)</td>
            <td class="px-4 py-3 text-right">{{ report.data.totals.cans_given }}</td>
            <td class="px-4 py-3 text-right">{{ report.data.totals.cans_returned }}</td>
            <td v-for="mode in report.data.payment_modes" :key="mode" class="px-4 py-3 text-right">
              {{ formatCurrency(report.data.totals.by_payment_mode[mode]) }}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="mt-4 flex justify-center gap-2" v-if="hasPreviousPage || hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!hasPreviousPage" @click="page--">
        Previous
      </Button>
      <Button theme="blue" variant="outline" :disabled="!hasNextPage" @click="page++">
        Next
      </Button>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Button, FormControl, Badge, createResource, createListResource } from 'frappe-ui'
import { showError } from '@/utils/toast'
import { downloadFile } from '@/utils/download'

function today() {
  return new Date().toISOString().slice(0, 10)
}

function daysAgo(n) {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d.toISOString().slice(0, 10)
}

const filters = reactive({
  from_date: daysAgo(30),
  to_date: today(),
  customer: '',
  sales_person: '',
})

const pageLength = 10
const page = ref(1)

const customers = createListResource({
  doctype: 'Customer',
  fields: ['name', 'customer_code', 'customer_name'],
  orderBy: 'customer_name asc',
  pageLength: 200,
  auto: true,
})

const salesPersons = createResource({
  url: 'neer_jal.api.users.list_sales_users',
  auto: true,
  params: { start: 0, page_length: 200 },
  initialData: [],
})

const customerOptions = computed(() => [
  { label: 'All Customers', value: '' },
  ...(customers.data || []).map((c) => ({ label: `${c.customer_code ? c.customer_code + ' - ' : ''}${c.customer_name}`, value: c.name })),
])

const salesPersonOptions = computed(() => [
  { label: 'All Sales Persons', value: '' },
  ...(salesPersons.data || []).map((u) => ({ label: u.full_name, value: u.name })),
])

const report = createResource({
  url: 'neer_jal.api.reports.get_delivery_report',
})

function search() {
  if (!filters.from_date || !filters.to_date) {
    showError('Please choose both a from and to date')
    return
  }
  page.value = 1
  report.submit(
    { ...filters },
    {
      onError(error) {
        showError(error, 'Could not load report')
      },
    },
  )
}

const pagedEntries = computed(() => {
  if (!report.data) return []
  const start = (page.value - 1) * pageLength
  return report.data.entries.slice(start, start + pageLength)
})

const hasPreviousPage = computed(() => page.value > 1)
const hasNextPage = computed(() => {
  if (!report.data) return false
  return page.value * pageLength < report.data.entries.length
})

const downloading = ref(false)

async function downloadPdf() {
  if (!filters.from_date || !filters.to_date) {
    showError('Please choose both a from and to date')
    return
  }
  downloading.value = true
  const params = new URLSearchParams({
    from_date: filters.from_date,
    to_date: filters.to_date,
  })
  if (filters.customer) params.set('customer', filters.customer)
  if (filters.sales_person) params.set('sales_person', filters.sales_person)

  const url = `/api/method/neer_jal.api.reports.download_delivery_report_pdf?${params.toString()}`
  const filename = `delivery-report-${filters.from_date}-to-${filters.to_date}.pdf`
  try {
    await downloadFile(url, filename)
  } catch {
    // downloadFile already surfaced a toast
  } finally {
    downloading.value = false
  }
}

function paymentTheme(mode) {
  return { Cash: 'green', UPI: 'blue', Pending: 'red', LCR: 'orange', Free: 'gray' }[mode] || 'gray'
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
