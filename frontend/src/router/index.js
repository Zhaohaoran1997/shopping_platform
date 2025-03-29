import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/products',
        name: 'Products',
        component: () => import('@/views/Products.vue'),
        meta: { title: '商品列表' }
      },
      {
        path: '/products/:id',
        name: 'ProductDetail',
        component: () => import('@/views/ProductDetail.vue'),
        meta: { title: '商品详情' }
      },
      {
        path: '/cart',
        name: 'Cart',
        component: () => import('@/views/Cart.vue'),
        meta: { title: '购物车' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/auth/Profile.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (requiresGuest && authStore.isAuthenticated) {
    next('/')
  } else {
    // 设置页面标题
    document.title = to.meta.title ? `${to.meta.title} - 购物平台` : '购物平台'
    next()
  }
})

export default router 