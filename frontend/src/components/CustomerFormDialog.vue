<template>
  <Dialog v-model="show" :options="{ title: 'New Customer', size: 'lg' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormControl
          class="sm:col-span-2"
          label="Customer Name"
          required
          v-model="form.customer_name"
        />
        <FormControl
          label="Phone"
          required
          v-model="form.phone"
          maxlength="10"
          description="10-digit phone number"
        />
        <FormControl label="City / Area" v-model="form.city" />
        <FormControl
          class="sm:col-span-2"
          type="textarea"
          label="Address"
          v-model="form.address_line"
        />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Water Can Settings
        </div>
        <FormControl
          type="number"
          label="Cans Required (per delivery)"
          v-model="form.cans_required"
        />
        <FormControl type="number" label="Rate per Can" v-model="form.rate_per_can" />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Notes
        </div>
        <FormControl class="sm:col-span-2" type="textarea" label="Notes" v-model="form.notes" />
        <FormControl
          class="sm:col-span-2"
          type="checkbox"
          label="Send SMS notifications for deliveries"
          v-model="form.sms_enabled"
        />
      </div>
      <ErrorMessage class="mt-3 block" :message="customers.insert.error" />
    </template>
    <template #actions>
      <Button
        theme="blue" variant="solid"
        class="w-full"
        :loading="customers.insert.loading"
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
  customers: { type: Object, required: true },
})
const emit = defineEmits(['update:modelValue', 'created'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function emptyForm() {
  return {
    customer_name: '',
    phone: '',
    address_line: '',
    city: '',
    cans_required: 0,
    rate_per_can: 0,
    notes: '',
    sms_enabled: 1,
  }
}

let form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

function submit() {
  if (!form.customer_name) {
    showError('Customer name is required')
    return
  }
  if (!form.phone) {
    showError('Phone number is required')
    return
  }
  const phoneError = checkPhoneNumber(form.phone)
  if (phoneError) {
    showError(phoneError)
    return
  }
  props.customers.insert.submit(
    { ...form },
    {
      onSuccess(doc) {
        showSuccess('Customer created')
        show.value = false
        emit('created', doc)
      },
      onError(error) {
        showError(error, 'Could not create customer')
      },
    },
  )
}
</script>
