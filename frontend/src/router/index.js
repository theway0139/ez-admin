import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('../views/Logs.vue')
  },
  {
    path: '/robots',
    name: 'RobotManagement',
    component: () => import('../views/RobotManagement.vue')
  },
  {
    path: '/tasks',
    name: 'TaskScheduling',
    component: () => import('../views/TaskScheduling.vue')
  },
  {
    path: '/video-playback',
    name: 'VideoPlayback',
    component: () => import('../views/VideoPlayback.vue')
  },
  {
    path: '/real-time-monitoring',
    name: 'RealTimeMonitoring',
    component: () => import('../views/RealTimeMonitoring.vue')
  },
  {
    path: '/event-management',
    name: 'EventManagement',
    component: () => import('../views/EventManagement.vue')
  },
  {
    path: '/performance-monitoring',
    name: 'PerformanceMonitoring',
    component: () => import('../views/PerformanceMonitoring.vue')
  },
  {
    path: '/data-analysis',
    name: 'DataAnalysis',
    component: () => import('../views/DataAnalysis.vue')
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router