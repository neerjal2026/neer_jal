<template>
  <div class="mx-auto max-w-3xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Drivers</h1>
        <p class="text-sm text-gray-500">Drivers who accompany delivery trips</p>
      </div>
      <Button v-if="isManager" theme="blue" variant="solid" class="w-full sm:w-auto" @click="openNew">
        + New Driver
      </Button>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[480px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Driver Name</th>
            <th class="px-4 py-3 font-medium">Phone</th>
            <th class="px-4 py-3 font-medium">License Number</th>
            <th v-if="isManager" class="px-4 py-3 font-medium">Disabled</th>
            <th v-if="isManager" class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in drivers.data" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.driver_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.phone || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.license_number || '-' }}</td>
            <td v-if="isManager" class="px-4 py-3">
              <input
                type="checkbox"
                :checked="!!row.disabled"
                @change="toggleDisabled(row)"
              />
            </td>
            <td v-if="isManager" class="px-4 py-3">
              <Button theme="blue" variant="outline" @click="openEdit(row)">Edit</Button>
            </td>
          </tr>
          <tr v-if="!drivers.list.loading && !drivers.data?.length">
            <td :colspan="isManager ? 5 : 3" class="px-4 py-10 text-center text-gray-400">
              No drivers added yet
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-4 flex justify-center gap-2" v-if="drivers.hasPreviousPage || drivers.hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!drivers.hasPreviousPage" @click="drivers.previous()">
        Previous
      </Button>
      <Button theme="blue" variant="outline" :disabled="!drivers.hasNextPage" @click="drivers.next()">
        Next
      </Button>
    </div>

    <DriverFormDialog
      v-if="isManager"
      v-model="showDialog"
      :drivers="drivers"
      :driver="editingDriver"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, createListResource } from 'frappe-ui'
import DriverFormDialog from '@/components/DriverFormDialog.vue'
import { isManager } from '@/utils/session'
import { showSuccess, showError } from '@/utils/toast'

const showDialog = ref(false)
const editingDriver = ref(null)

const drivers = createListResource({
  doctype: 'Driver',
  fields: ['name', 'driver_name', 'phone', 'license_number', 'disabled'],
  orderBy: 'driver_name asc',
  pageLength: 10,
  auto: true,
})

function openNew() {
  editingDriver.value = null
  showDialog.value = true
}

function openEdit(row) {
  editingDriver.value = row
  showDialog.value = true
}

function toggleDisabled(row) {
  drivers.setValue.submit(
    { name: row.name, disabled: row.disabled ? 0 : 1 },
    {
      onSuccess() {
        showSuccess('Driver updated')
      },
      onError(error) {
        showError(error, 'Could not update driver')
      },
    },
  )
}
</script>
