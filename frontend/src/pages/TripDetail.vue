<template>
  <div v-if="trip.doc" class="mx-auto max-w-5xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <router-link to="/trips" class="text-sm text-gray-500 hover:underline">&larr; Trips</router-link>
        <h1 class="mt-1 text-2xl font-semibold text-gray-900">{{ trip.doc.name }}</h1>
        <p class="text-sm text-gray-500">Started {{ trip.doc.start_time }}</p>
      </div>
      <div class="flex gap-2">
        <Button theme="blue" variant="outline" :loading="downloading" @click="downloadPdf">Export PDF</Button>
        <Button v-if="trip.doc.status === 'Active'" theme="blue" variant="solid" @click="showClose = true">Close Trip</Button>
      </div>
    </div>

    <div class="rounded-lg border bg-white p-5">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase text-gray-500">Trip Details</h2>
        <Badge :theme="trip.doc.status === 'Active' ? 'orange' : 'green'" variant="subtle">{{ trip.doc.status }}</Badge>
      </div>
      <div class="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
        <div><span class="text-gray-500">Driver:</span> <span class="text-gray-900">{{ trip.doc.driver }}</span></div>
        <div><span class="text-gray-500">Vehicle:</span> <span class="text-gray-900">{{ trip.doc.vehicle }}</span></div>
        <div><span class="text-gray-500">Trip Route:</span> <span class="text-gray-900">{{ routeLabel(trip.doc.trip_route) }}</span></div>
        <div><span class="text-gray-500">Route Price:</span> <span class="text-gray-900">{{ formatCurrency(trip.doc.route_price) }}</span></div>
        <div><span class="text-gray-500">Driver Credit:</span> <span class="text-gray-900">{{ formatCurrency(trip.doc.driver_credit) }}</span></div>
        <div><span class="text-gray-500">Starting KM:</span> <span class="text-gray-900">{{ trip.doc.start_km }}</span></div>
        <div><span class="text-gray-500">Ending KM:</span> <span class="text-gray-900">{{ trip.doc.end_km ?? '-' }}</span></div>
        <div><span class="text-gray-500">Distance:</span> <span class="text-gray-900">{{ trip.doc.distance_km ?? '-' }} km</span></div>
        <div><span class="text-gray-500">Start Time:</span> <span class="text-gray-900">{{ trip.doc.start_time }}</span></div>
        <div><span class="text-gray-500">End Time:</span> <span class="text-gray-900">{{ trip.doc.end_time || '-' }}</span></div>
        <div v-if="trip.doc.notes" class="sm:col-span-2"><span class="text-gray-500">Notes:</span> <span class="text-gray-900">{{ trip.doc.notes }}</span></div>
      </div>
    </div>

    <TripCloseDialog v-model="showClose" :trip="trip.doc" @closed="trip.reload()" />
  </div>
  <div v-else class="p-6 text-gray-400">Loading...</div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, Badge, createDocumentResource, createListResource } from 'frappe-ui'
import TripCloseDialog from '@/components/TripCloseDialog.vue'
import { downloadFile } from '@/utils/download'
import { showError } from '@/utils/toast'

const props = defineProps({ tripId: { type: String, required: true } })
const showClose = ref(false)
const downloading = ref(false)
const trip = createDocumentResource({ doctype: 'Trip', name: props.tripId })
const routes = createListResource({ doctype: 'Trip Route', fields: ['name', 'route_name'], pageLength: 200, auto: true })

function routeLabel(route) {
  return routes.data?.find((item) => item.name === route)?.route_name || route || '-'
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function downloadPdf() {
  downloading.value = true
  try {
    await downloadFile(`/api/method/neer_jal.api.reports.download_trip_report_pdf?trip=${props.tripId}`, `trip-report-${props.tripId}.pdf`)
  } catch (error) {
    showError(error, 'Could not download trip report')
  } finally {
    downloading.value = false
  }
}
</script>
