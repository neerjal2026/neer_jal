<template>
  <div class="mx-auto max-w-2xl p-4 sm:p-6" v-if="settings.doc">
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Settings</h1>
      <p class="text-sm text-gray-500">App-wide settings for Neer Jal</p>
    </div>

    <div class="rounded-lg border bg-white p-5">
      <h2 class="mb-1 text-sm font-semibold uppercase text-gray-500">SMS Notifications</h2>
      <p class="mb-4 text-xs text-gray-400">
        When enabled, the customer and their sales manager receive an SMS after each delivery.
        Each customer can also be individually opted out from their customer page. An SMS gateway
        must still be configured for messages to actually send.
      </p>
      <div class="boxed-fields">
        <FormControl
          type="checkbox"
          label="Enable delivery SMS notifications"
          v-model="settings.doc.enable_sms_notifications"
          @change="save"
        />
      </div>
      <ErrorMessage class="mt-3 block" :message="settings.save.error" />
    </div>
  </div>
  <div v-else class="p-6 text-gray-400">Loading...</div>
</template>

<script setup>
import { FormControl, ErrorMessage, createDocumentResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const settings = createDocumentResource({
  doctype: 'Sales Settings',
  name: 'Sales Settings',
})

function save() {
  // The checkbox's change event can fire the handler twice in quick succession
  // (e.g. a double tap on mobile). Without this guard, the second submit races
  // the first and fails with a TimestampMismatchError since the first request
  // has already advanced `modified` in the DB by the time the second lands.
  if (settings.save.loading) return
  settings.save.submit(null, {
    onSuccess() {
      showSuccess('Settings saved')
    },
    onError(error) {
      if (error?.exc_type === 'TimestampMismatchError') {
        settings.reload()
        showError('Settings changed elsewhere, reloaded the latest version. Please try again.')
        return
      }
      showError(error, 'Could not save settings')
    },
  })
}
</script>
