<template>
  <div class="mx-auto max-w-5xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Customers</h1>
        <p class="text-sm text-gray-500">Master list of customers</p>
      </div>
      <Button v-if="isManager" theme="blue" variant="solid" class="w-full sm:w-auto" @click="showNewDialog = true">
        + New Customer
      </Button>
    </div>

    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
      <FormControl
        class="sm:w-64"
        type="text"
        placeholder="Search by ID or name..."
        v-model="search"
        @update:modelValue="onFilterChange"
      />
      <FormControl
        type="checkbox"
        label="Only show pending dues / cans"
        v-model="onlyPending"
        @update:modelValue="onFilterChange"
      />
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[640px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">ID</th>
            <th class="px-4 py-3 font-medium">Name</th>
            <th class="px-4 py-3 font-medium">Phone</th>
            <th class="px-4 py-3 font-medium">City / Area</th>
            <th class="px-4 py-3 font-medium">Cans Pending</th>
            <th class="px-4 py-3 font-medium">Amount Due</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in pagedCustomers"
            :key="row.name"
            class="cursor-pointer border-b last:border-0 hover:bg-gray-50"
            @click="$router.push(`/customers/${row.name}`)"
          >
            <td class="px-4 py-3 text-gray-600">{{ row.customer_code }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">
              {{ row.customer_name }}
              <Badge v-if="row.disabled" variant="subtle" theme="red" class="ml-2">Disabled</Badge>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ row.phone || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.city || '-' }}</td>
            <td class="px-4 py-3">
              <Badge :theme="row.cans_pending > 0 ? 'orange' : 'gray'" variant="subtle">
                {{ row.cans_pending || 0 }}
              </Badge>
            </td>
            <td class="px-4 py-3">
              <Badge :theme="row.amount_due > 0 ? 'red' : 'gray'" variant="subtle">
                {{ formatCurrency(row.amount_due) }}
              </Badge>
            </td>
          </tr>
          <tr v-if="!customerSearch.loading && !pagedCustomers.length">
            <td colspan="6" class="px-4 py-10 text-center text-gray-400">
              No customers found
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="customerSearch.loading" class="mt-4 text-center text-sm text-gray-400">
      Loading...
    </div>

    <div class="mt-4 flex justify-center gap-2" v-if="hasPreviousPage || hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!hasPreviousPage" @click="previousPage">
        Previous
      </Button>
      <Button theme="blue" variant="outline" :disabled="!hasNextPage" @click="nextPage">
        Next
      </Button>
    </div>

    <CustomerFormDialog v-if="isManager" v-model="showNewDialog" :customers="customers" @created="onCreated" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Button, FormControl, Badge, createResource, createListResource } from 'frappe-ui'
import CustomerFormDialog from '@/components/CustomerFormDialog.vue'
import { isManager } from '@/utils/session'

const search = ref('')
const onlyPending = ref(false)
const showNewDialog = ref(false)

const pageLength = 10
const page = ref(1)

// used only so CustomerFormDialog can call .insert.submit() to create a customer;
// the actual list shown on this page is driven by customerSearch below, since we
// need to match "code or name" and "due or pending" as two independent OR-groups,
// which the plain list-filter API can't express in a single call
const customers = createListResource({
  doctype: 'Customer',
  fields: ['name'],
  pageLength: 1,
  auto: false,
})

const customerSearch = createResource({
  url: 'neer_jal.api.customers.search_customers',
  auto: true,
  params: { search: '', only_pending: 0, start: 0, page_length: pageLength },
  initialData: [],
})

const pagedCustomers = computed(() => (customerSearch.data || []).slice(0, pageLength))
const hasPreviousPage = computed(() => page.value > 1)
const hasNextPage = computed(() => (customerSearch.data || []).length > pageLength)

function reload() {
  customerSearch.update({
    params: {
      search: search.value,
      only_pending: onlyPending.value ? 1 : 0,
      start: (page.value - 1) * pageLength,
      page_length: pageLength,
    },
  })
  customerSearch.reload()
}

let searchTimeout
function onFilterChange() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    reload()
  }, 300)
}

function onCreated() {
  page.value = 1
  reload()
}

function nextPage() {
  if (!hasNextPage.value) return
  page.value += 1
  reload()
}

function previousPage() {
  if (!hasPreviousPage.value) return
  page.value -= 1
  reload()
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
