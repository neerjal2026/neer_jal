<template>
  <Dialog v-model="show" :options="{ title: vehicle ? 'Edit Vehicle' : 'New Vehicle', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4">
        <FormControl
          label="Vehicle Number"
          required
          :disabled="!!vehicle"
          v-model="form.vehicle_number"
          :description="vehicle ? 'Vehicle number cannot be changed after creation' : ''"
        />
        <FormControl label="Model" v-model="form.model" />
        <FormControl type="number" label="Mileage (km/l)" v-model="form.mileage" />
      </div>
      <ErrorMessage class="mt-3 block" :message="vehicles.insert.error || vehicles.setValue.error" />
    </template>
    <template #actions>
      <Button
        theme="blue" variant="solid"
        class="w-full"
        :loading="vehicles.insert.loading || vehicles.setValue.loading"
        @click="submit"
      >
        Save
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
  vehicles: { type: Object, required: true },
  vehicle: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'created', 'updated'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function emptyForm() {
  if (props.vehicle) {
    return {
      vehicle_number: props.vehicle.vehicle_number,
      model: props.vehicle.model,
      mileage: props.vehicle.mileage,
    }
  }
  return { vehicle_number: '', model: '', mileage: 0 }
}

let form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

function submit() {
  if (!form.vehicle_number) {
    showError('Vehicle number is required')
    return
  }

  if (props.vehicle) {
    props.vehicles.setValue.submit(
      { name: props.vehicle.name, model: form.model, mileage: form.mileage },
      {
        onSuccess(doc) {
          showSuccess('Vehicle updated')
          show.value = false
          emit('updated', doc)
        },
        onError(error) {
          showError(error, 'Could not update vehicle')
        },
      },
    )
    return
  }

  props.vehicles.insert.submit(
    { ...form },
    {
      onSuccess(doc) {
        showSuccess('Vehicle added')
        show.value = false
        emit('created', doc)
      },
      onError(error) {
        showError(error, 'Could not add vehicle')
      },
    },
  )
}
</script>
