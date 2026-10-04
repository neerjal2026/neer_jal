<template>
  <Dialog v-model="show" :options="{ title: 'Close Trip', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4">
        <FormControl label="Vehicle" :model-value="trip?.vehicle" disabled />
        <FormControl label="Starting KM" :model-value="trip?.start_km" disabled />
        <FormControl label="Trip Route" :model-value="routeLabel(trip?.trip_route)" disabled />
        <FormControl label="Driver Credit on Completion" :model-value="trip?.route_price || 0" disabled />
        <FormControl type="number" label="Ending KM (Odometer)" required v-model="endKm" />
      </div>
      <p v-if="distance !== null" class="mt-3 text-sm text-gray-500">
        Distance travelled: <span class="font-medium text-gray-900">{{ distance }} km</span>
      </p>
      <ErrorMessage class="mt-3 block" :message="closeTrip.error" />
    </template>
    <template #actions>
      <Button theme="blue" variant="solid" class="w-full" :loading="closeTrip.loading" @click="submit">
        Close Trip
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createListResource, createResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
  trip: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'closed'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const endKm = ref(0)
const routes = createListResource({ doctype: 'Trip Route', fields: ['name', 'route_name'], pageLength: 200, auto: true })

function routeLabel(route) {
  return routes.data?.find((item) => item.name === route)?.route_name || route || '-'
}

watch(show, (value) => {
  if (value) {
    endKm.value = props.trip?.start_km || 0
  }
})

const distance = computed(() => {
  if (!props.trip) return null
  const value = Number(endKm.value) - Number(props.trip.start_km)
  return Number.isFinite(value) ? value : null
})

const closeTrip = createResource({
  url: 'frappe.client.set_value',
})

function submit() {
  if (Number(endKm.value) < Number(props.trip?.start_km)) {
    showError('Ending KM cannot be less than Starting KM')
    return
  }
  closeTrip.submit(
    {
      doctype: 'Trip',
      name: props.trip.name,
      fieldname: { end_km: endKm.value },
    },
    {
      onSuccess() {
        showSuccess('Trip closed')
        show.value = false
        emit('closed')
      },
      onError(error) {
        showError(error, 'Could not close trip')
      },
    },
  )
}
</script>
