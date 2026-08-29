<template>
  <div class="mx-auto max-w-3xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Vehicles</h1>
        <p class="text-sm text-gray-500">Vehicles used for delivery trips</p>
      </div>
      <Button v-if="isManager" theme="blue" variant="solid" class="w-full sm:w-auto" @click="openNew">
        + New Vehicle
      </Button>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[480px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Vehicle Number</th>
            <th class="px-4 py-3 font-medium">Model</th>
            <th class="px-4 py-3 font-medium">Mileage</th>
            <th v-if="isManager" class="px-4 py-3 font-medium">Disabled</th>
            <th v-if="isManager" class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in vehicles.data" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.vehicle_number }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.model || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.mileage || '-' }}</td>
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
          <tr v-if="!vehicles.list.loading && !vehicles.data?.length">
            <td :colspan="isManager ? 5 : 3" class="px-4 py-10 text-center text-gray-400">
              No vehicles added yet
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-4 flex justify-center gap-2" v-if="vehicles.hasPreviousPage || vehicles.hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!vehicles.hasPreviousPage" @click="vehicles.previous()">
        Previous
      </Button>
      <Button theme="blue" variant="outline" :disabled="!vehicles.hasNextPage" @click="vehicles.next()">
        Next
      </Button>
    </div>

    <VehicleFormDialog
      v-if="isManager"
      v-model="showDialog"
      :vehicles="vehicles"
      :vehicle="editingVehicle"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, createListResource } from 'frappe-ui'
import VehicleFormDialog from '@/components/VehicleFormDialog.vue'
import { isManager } from '@/utils/session'
import { showSuccess, showError } from '@/utils/toast'

const showDialog = ref(false)
const editingVehicle = ref(null)

const vehicles = createListResource({
  doctype: 'Vehicle',
  fields: ['name', 'vehicle_number', 'model', 'mileage', 'disabled'],
  orderBy: 'vehicle_number asc',
  pageLength: 10,
  auto: true,
})

function openNew() {
  editingVehicle.value = null
  showDialog.value = true
}

function openEdit(row) {
  editingVehicle.value = row
  showDialog.value = true
}

function toggleDisabled(row) {
  vehicles.setValue.submit(
    { name: row.name, disabled: row.disabled ? 0 : 1 },
    {
      onSuccess() {
        showSuccess('Vehicle updated')
      },
      onError(error) {
        showError(error, 'Could not update vehicle')
      },
    },
  )
}
</script>
