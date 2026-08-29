<template>
  <Dialog v-model="show" :options="{ title: 'Settle Due Amount', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormControl class="sm:col-span-2" label="Customer" :model-value="customerLabel" disabled />
        <FormControl
          class="sm:col-span-2"
          label="Amount to Settle"
          :model-value="formatCurrency(currentDue)"
          disabled
        />
        <FormControl
          type="select"
          label="Paid Via"
          required
          :options="['Cash', 'UPI']"
          v-model="form.payment_mode"
        />
        <FormControl type="date" label="Date" v-model="form.payment_date" />
        <FormControl class="sm:col-span-2" type="textarea" label="Notes" v-model="form.notes" />
      </div>
      <p class="mt-3 text-xs text-gray-400">
        This marks every pending delivery for this customer as paid via the selected mode.
      </p>
      <ErrorMessage class="mt-3 block" :message="settle.error" />
    </template>
    <template #actions>
      <Button theme="blue" variant="solid" class="w-full" :loading="settle.loading" @click="submit">
        Settle Due
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
  customer: { type: String, required: true },
  customerLabel: { type: String, default: '' },
  currentDue: { type: [Number, String], default: 0 },
})
const emit = defineEmits(['update:modelValue', 'settled'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function today() {
  return new Date().toISOString().slice(0, 10)
}

function emptyForm() {
  return {
    payment_mode: 'Cash',
    payment_date: today(),
    notes: '',
  }
}

let form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

const settle = createResource({
  url: 'neer_jal.api.settlement.settle_customer_dues',
})

function submit() {
  settle.submit(
    {
      customer: props.customer,
      payment_mode: form.payment_mode,
      payment_date: form.payment_date,
      notes: form.notes,
    },
    {
      onSuccess() {
        showSuccess('Due settled')
        show.value = false
        emit('settled')
      },
      onError(error) {
        showError(error, 'Could not settle due')
      },
    },
  )
}
</script>
