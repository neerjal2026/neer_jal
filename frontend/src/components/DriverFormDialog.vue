<template>
  <Dialog v-model="show" :options="{ title: driver ? 'Edit Driver' : 'New Driver', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4">
        <FormControl label="Driver Name" required v-model="form.driver_name" />
        <FormControl
          label="Phone"
          v-model="form.phone"
          maxlength="10"
          description="10-digit phone number"
        />
        <FormControl label="License Number" v-model="form.license_number" />
      </div>
      <ErrorMessage class="mt-3 block" :message="drivers.insert.error || drivers.setValue.error" />
    </template>
    <template #actions>
      <Button
        theme="blue" variant="solid"
        class="w-full"
        :loading="drivers.insert.loading || drivers.setValue.loading"
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
import { checkPhoneNumber } from '@/utils/phone'

const props = defineProps({
  modelValue: Boolean,
  drivers: { type: Object, required: true },
  driver: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'created', 'updated'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function emptyForm() {
  if (props.driver) {
    return {
      driver_name: props.driver.driver_name,
      phone: props.driver.phone,
      license_number: props.driver.license_number,
    }
  }
  return { driver_name: '', phone: '', license_number: '' }
}

let form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

function submit() {
  if (!form.driver_name) {
    showError('Driver name is required')
    return
  }
  const phoneError = checkPhoneNumber(form.phone)
  if (phoneError) {
    showError(phoneError)
    return
  }

  if (props.driver) {
    props.drivers.setValue.submit(
      { name: props.driver.name, ...form },
      {
        onSuccess(doc) {
          showSuccess('Driver updated')
          show.value = false
          emit('updated', doc)
        },
        onError(error) {
          showError(error, 'Could not update driver')
        },
      },
    )
    return
  }

  props.drivers.insert.submit(
    { ...form },
    {
      onSuccess(doc) {
        showSuccess('Driver added')
        show.value = false
        emit('created', doc)
      },
      onError(error) {
        showError(error, 'Could not add driver')
      },
    },
  )
}
</script>
