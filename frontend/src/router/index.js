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
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router