import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Forecast from '@/views/Forecast.vue'
import Orders from '@/views/Orders.vue'
import Bills from '@/views/Bills.vue'
import Business from '@/views/Business.vue'
import Customers from '@/views/Customers.vue'
import Users from '@/views/Users.vue'
import Logs from '@/views/Logs.vue'

const routes = [
  { path: '/', name: 'Login', component: Login },
  { path: '/forecast', name: 'Forecast', component: Forecast, meta: { requiresAuth: true } },
  { path: '/orders', name: 'Orders', component: Orders, meta: { requiresAuth: true } },
  { path: '/bills', name: 'Bills', component: Bills, meta: { requiresAuth: true } },
  { path: '/business', name: 'Business', component: Business, meta: { requiresAuth: true } },
  { path: '/customers', name: 'Customers', component: Customers, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/users', name: 'Users', component: Users, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/logs', name: 'Logs', component: Logs, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/inventory', name: 'Inventory', component: () => import('@/views/Inventory.vue'), meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫（如果有的话）
router.beforeEach((to, from, next) => {
  // ... 你的守卫逻辑
  next()
})

export default router