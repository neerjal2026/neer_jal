import { createRouter, createWebHistory } from 'vue-router'
import { session } from './utils/session'

const routes = [
  {
    path: '/',
    redirect: '/trips',
  },
  {
    path: '/vehicles',
    name: 'VehicleList',
    component: () => import('@/pages/VehicleList.vue'),
  },
  {
    path: '/employees',
    name: 'EmployeeList',
    component: () => import('@/pages/EmployeeList.vue'),
  },
  {
    path: '/time-clock',
    name: 'TimeClockList',
    component: () => import('@/pages/TimeClockList.vue'),
  },
  {
    path: '/time-clock/:employee',
    name: 'EmployeeTimeLogs',
    component: () => import('@/pages/EmployeeTimeLogs.vue'),
    props: true,
  },
  {
    path: '/payroll',
    name: 'PayrollReport',
    component: () => import('@/pages/PayrollReport.vue'),
  },
  {
    path: '/salary-advances',
    name: 'SalaryAdvanceList',
    component: () => import('@/pages/SalaryAdvanceList.vue'),
  },
  {
    path: '/trips',
    name: 'TripList',
    component: () => import('@/pages/TripList.vue'),
  },
  {
    path: '/trips/:tripId',
    name: 'TripDetail',
    component: () => import('@/pages/TripDetail.vue'),
    props: true,
  },
  {
    path: '/trip-routes',
    name: 'TripRouteList',
    component: () => import('@/pages/TripRouteList.vue'),
  },
  {
    path: '/reports',
    name: 'ReportsList',
    component: () => import('@/pages/ReportsList.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/neer_jal'),
  routes,
})

// Office Staff users only have the HR tabs, so land them on Time Clock.
router.beforeEach(async (to, from) => {
  if (to.path === '/trips' && from.path === '/') {
    if (session.loading) await session.promise
    if (session.data?.is_hr_manager && !session.data?.is_manager && !(session.data?.roles || []).includes('Sales User')) {
      return '/time-clock'
    }
  }
})

export default router
