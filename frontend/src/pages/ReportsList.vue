<template>
  <div class="mx-auto max-w-6xl p-4 sm:p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Trip Sheet</h1>
      <p class="text-sm text-gray-500">Driver trips and route-credit totals</p>
    </div>

    <div class="boxed-fields mb-6 grid grid-cols-1 gap-4 rounded-lg border bg-white p-5 sm:grid-cols-2 lg:grid-cols-4">
      <FormControl type="date" label="From Date" v-model="filters.from_date" />
      <FormControl type="date" label="To Date" v-model="filters.to_date" />
      <FormControl type="select" label="Driver" :options="driverOptions" v-model="filters.driver" />
      <div class="flex items-end gap-2">
        <Button theme="blue" variant="solid" :loading="sheet.loading" @click="search">Search</Button>
        <Button theme="blue" variant="outline" :loading="downloading" @click="downloadPdf">PDF</Button>
      </div>
    </div>

    <div v-if="sheet.data" class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Trips</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ sheet.data.totals.trip_count }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Completed</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ sheet.data.totals.completed_count }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Total Route Price</p>
        <p class="mt-1 text-xl font-semibold text-gray-900">{{ formatCurrency(sheet.data.totals.route_price) }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Driver Credit Earned</p>
        <p class="mt-1 text-xl font-semibold text-gray-900">{{ formatCurrency(sheet.data.totals.driver_credit) }}</p>
      </div>
    </div>

    <div v-if="sheet.data" class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[1040px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Started</th>
            <th class="px-4 py-3 font-medium">Driver</th>
            <th class="px-4 py-3 font-medium">Vehicle</th>
            <th class="px-4 py-3 font-medium">Route</th>
            <th class="px-4 py-3 font-medium">Start KM</th>
            <th class="px-4 py-3 font-medium">End KM</th>
            <th class="px-4 py-3 font-medium">Distance</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium">Route Price</th>
            <th class="px-4 py-3 font-medium">Driver Credit</th>
            <th class="px-4 py-3 font-medium">Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trip in sheet.data.trips" :key="trip.name" class="cursor-pointer border-b last:border-0 hover:bg-gray-50" @click="$router.push(`/trips/${trip.name}`)">
            <td class="px-4 py-3 text-gray-600">{{ trip.start_time }}</td>
            <td class="px-4 py-3 text-gray-600">{{ trip.driver_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ trip.vehicle }}</td>
            <td class="px-4 py-3 text-gray-600">{{ trip.route_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ trip.start_km }}</td>
            <td class="px-4 py-3 text-gray-600">{{ trip.end_km ?? '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ trip.distance_km ?? '-' }}</td>
            <td class="px-4 py-3"><Badge :theme="trip.status === 'Active' ? 'orange' : 'green'" variant="subtle">{{ trip.status }}</Badge></td>
            <td class="px-4 py-3 text-gray-600">{{ formatCurrency(trip.route_price) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ formatCurrency(trip.driver_credit) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ trip.notes || '-' }}</td>
          </tr>
          <tr v-if="!sheet.data.trips.length"><td colspan="11" class="px-4 py-10 text-center text-gray-400">No trips found for these filters</td></tr>
        </tbody>
        <tfoot v-if="sheet.data.trips.length" class="border-t bg-gray-50 font-semibold text-gray-900">
          <tr>
            <td class="px-4 py-3" colspan="8">Totals</td>
            <td class="px-4 py-3">{{ formatCurrency(sheet.data.totals.route_price) }}</td>
            <td class="px-4 py-3">{{ formatCurrency(sheet.data.totals.driver_credit) }}</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>
    <div v-else class="rounded-lg border bg-white px-4 py-10 text-center text-gray-400">Choose a date range and search</div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Badge, Button, FormControl, createResource } from 'frappe-ui'
import { showError } from '@/utils/toast'
import { downloadFile } from '@/utils/download'

function today() {
  return new Date().toISOString().slice(0, 10)
}

function daysAgo(days) {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString().slice(0, 10)
}

const filters = reactive({ from_date: daysAgo(30), to_date: today(), driver: '' })
const drivers = createResource({
  url: 'neer_jal.api.users.list_drivers',
  auto: true,
  params: { start: 0, page_length: 200 },
  initialData: [],
})
const driverOptions = computed(() => [
  { label: 'All Drivers', value: '' },
  ...(drivers.data || []).map((user) => ({ label: user.full_name, value: user.name })),
])
const sheet = createResource({ url: 'neer_jal.api.reports.get_trip_sheet' })
const downloading = ref(false)

function search() {
  if (!filters.from_date || !filters.to_date) {
    showError('Please choose both a from and to date')
    return
  }
  sheet.submit({ ...filters }, { onError: (error) => showError(error, 'Could not load trip sheet') })
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function downloadPdf() {
  if (!filters.from_date || !filters.to_date) {
    showError('Please choose both a from and to date')
    return
  }
  downloading.value = true
  const params = new URLSearchParams({ from_date: filters.from_date, to_date: filters.to_date })
  if (filters.driver) params.set('driver', filters.driver)
  try {
    await downloadFile(
      `/api/method/neer_jal.api.reports.download_trip_sheet_pdf?${params.toString()}`,
      `driver-trip-sheet-${filters.from_date}-to-${filters.to_date}.pdf`,
    )
  } catch {
    // downloadFile already surfaced a toast
  } finally {
    downloading.value = false
  }
}
</script>
