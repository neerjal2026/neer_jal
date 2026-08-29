<template>
  <Dialog v-model="show" :options="{ title: 'Reset Password', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4">
        <FormControl label="Employee Login" :model-value="userLabel" disabled />
        <FormControl
          type="password"
          label="New Password"
          required
          v-model="password"
          description="Avoid common or easily guessed passwords. Share this with the employee."
        />
      </div>
      <ErrorMessage class="mt-3 block" :message="reset.error" />
    </template>
    <template #actions>
      <Button theme="blue" variant="solid" class="w-full" :loading="reset.loading" @click="submit">
        Reset Password
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'
import { checkPasswordStrength } from '@/utils/password'

const props = defineProps({
  modelValue: Boolean,
  user: { type: String, default: '' },
  userLabel: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const password = ref('')

watch(show, (value) => {
  if (value) password.value = ''
})

const reset = createResource({
  url: 'neer_jal.api.users.reset_sales_user_password',
})

function submit() {
  if (!password.value) {
    showError('Enter a new password')
    return
  }
  const passwordError = checkPasswordStrength(password.value, {
    inputs: [props.userLabel, props.user],
  })
  if (passwordError) {
    showError(passwordError)
    return
  }
  reset.submit(
    { user: props.user, new_password: password.value },
    {
      onSuccess() {
        showSuccess('Password reset')
        show.value = false
      },
      onError(error) {
        showError(error, 'Could not reset password')
      },
    },
  )
}
</script>
