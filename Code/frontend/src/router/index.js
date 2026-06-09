import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/Roles.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/Logs.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'addresses',
        name: 'Addresses',
        component: () => import('@/views/Addresses.vue')
      },
      {
        path: 'cart',
        name: 'Cart',
        component: () => import('@/views/Cart.vue')
      },
      {
        path: 'ai',
        name: 'AIChat',
        component: () => import('@/views/AIChat.vue')
      },
      {
        path: 'goods',
        name: 'Goods',
        component: () => import('@/views/Goods.vue')
      },
      {
        path: 'coupons',
        name: 'Coupons',
        component: () => import('@/views/Coupons.vue')
      },
      {
        path: 'payments',
        name: 'Payments',
        component: () => import('@/views/Payments.vue')
      },
      {
        path: 'logistics',
        name: 'Logistics',
        component: () => import('@/views/Logistics.vue')
      },
      {
        path: 'refunds',
        name: 'Refunds',
        component: () => import('@/views/Refunds.vue')
      },
      {
        path: 'return-logistics',
        name: 'ReturnLogistics',
        component: () => import('@/views/ReturnLogistics.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const token = userStore.token

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else if (to.meta.requiresAdmin) {
    // 检查是否是管理员
    let userInfo = userStore.userInfo
    // 如果用户信息为空，尝试获取
    if (!userInfo && token) {
      try {
        await userStore.getUserInfo()
        userInfo = userStore.userInfo
      } catch (error) {
        console.error('获取用户信息失败:', error)
        next('/login')
        return
      }
    }
    if (userInfo && userInfo.role === 'admin') {
      next()
    } else {
      next('/')
    }
  } else {
    next()
  }
})

export default router