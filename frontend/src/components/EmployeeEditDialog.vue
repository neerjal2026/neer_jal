<template>
  <Dialog v-model="show" :options="{ title: 'Edit Employee', size: 'lg' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormControl label="Employee ID" disabled :model-value="employee?.employee_code" />
        <FormControl label="Employee Name" disabled :model-value="employee?.employee_name" />
        <FormControl type="date" label="Date of Birth" v-model="form.dob" />
        <FormControl type="select" label="Gender" :options="genderOptions" v-model="form.gender" />
        <FormControl
          label="Phone"
          v-model="form.phone"
          maxlength="10"
          description="10-digit phone number (optional)"
        />
        <FormControl label="Email" v-model="form.email" />
        <FormControl type="number" label="Hourly Wage" v-model="form.hourly_wage" />
        <FormControl label="Designation" v-model="form.designation" />
        <FormControl
          type="select"
          label="Employment Type"
          :options="employmentTypeOptions"
          v-model="form.employment_type"
        />
        <FormControl type="select" label="Status" :options="statusOptions" v-model="form.status" />
        <FormControl label="Joining Date" disabled :model-value="employee?.joining_date" />
        <FormControl type="date" label="Relieving Date" v-model="form.relieving_date" />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Address & ID
        </div>
        <FormControl type="textarea" label="Current Address" v-model="form.current_address" />
        <FormControl type="textarea" label="Permanent Address" v-model="form.permanent_address" />
        <FormControl
          label="Pincode"
          v-model="form.pincode"
          maxlength="6"
          description="6-digit postal PIN code (optional)"
        />
        <FormControl label="State" v-model="form.state" />
        <FormControl
          label="ID Number"
          v-model="form.id_number"
          description="e.g. Aadhaar number (optional)"
        />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Emergency & Education
        </div>
        <FormControl label="Emergency Contact" v-model="form.emergency_contact" />
        <FormControl label="Education" v-model="form.education" />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Bank Details
        </div>
        <FormControl label="Bank" v-model="form.bank_name" />
        <FormControl label="Account No" v-model="form.account_no" />
        <FormControl label="IFSC Code" v-model="form.ifsc_code" />
        <FormControl label="Others" v-model="form.other_bank_details" />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Notes
        </div>
        <FormControl class="sm:col-span-2" type="textarea" label="Notes" v-model="form.notes" />
        <FormControl class="sm:col-span-2" type="checkbox" label="Disabled" v-model="form.disabled" />
      </div>
      <ErrorMessage class="mt-3 block" :message="update.error" />
    </template>
    <template #actions>
      <Button theme="blue" variant="solid" class="w-full" :loading="update.loading" @click="submit">
        Save
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'
import { checkPhoneNumber } from '@/utils/phone'

const props = defineProps({
  modelValue: Boolean,
  employee: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'updated'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const genderOptions = [
  { label: '', value: '' },
  { label: 'Male', value: 'Male' },
  { label: 'Female', value: 'Female' },
  { label: 'Other', value: 'Other' },
]

const employmentTypeOptions = [
  { label: '', value: '' },
  { label: 'Full-time', value: 'Full-time' },
  { label: 'Part-time', value: 'Part-time' },
  { label: 'Contract', value: 'Contract' },
  { label: 'Daily Wage', value: 'Daily Wage' },
]

const statusOptions = [
  { label: 'Active', value: 'Active' },
  { label: 'On Leave', value: 'On Leave' },
  { label: 'Resigned', value: 'Resigned' },
  { label: 'Terminated', value: 'Terminated' },
]

const FIELDS = [
  'phone',
  'hourly_wage',
  'notes',
  'disabled',
  'relieving_date',
  'dob',
  'gender',
  'email',
  'employment_type',
  'status',
  'designation',
  'current_address',
  'permanent_address',
  'pincode',
  'state',
  'id_number',
  'emergency_contact',
  'education',
  'bank_name',
  'account_no',
  'ifsc_code',
  'other_bank_details',
]

function emptyForm() {
  return Object.fromEntries(FIELDS.map((f) => [f, f === 'hourly_wage' ? 0 : f === 'disabled' ? 0 : '']))
}

let form = reactive(emptyForm())

watch(
  () => props.employee,
  (employee) => {
    if (!employee) return
    for (const field of FIELDS) {
      form[field] = employee[field] || (field === 'hourly_wage' ? 0 : field === 'disabled' ? 0 : '')
    }
  },
  { immediate: true },
)

const update = createResource({
  url: 'neer_jal.api.employees.update_employee',
})

function submit() {
  if (form.phone) {
    const phoneError = checkPhoneNumber(form.phone)
    if (phoneError) {
      showError(phoneError)
      return
    }
  }
  if (form.pincode && !/^\d{6}$/.test(form.pincode)) {
    showError('Pincode must be exactly 6 digits')
    return
  }
  if (form.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) {
    showError('Enter a valid email address')
    return
  }
  update.submit(
    { name: props.employee.name, ...form },
    {
      onSuccess() {
        showSuccess('Employee updated')
        show.value = false
        emit('updated')
      },
      onError(error) {
        showError(error, 'Could not update employee')
      },
    },
  )
}
</script>
