import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import Layout from '@/views/Layout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: { public: true }
    },
    {
      path: '/',
      component: Layout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: '控制台' }
        },
        {
          path: 'params',
          name: 'Params',
          component: () => import('@/views/ParamsView.vue'),
          meta: { title: '参数管理' }
        },
        {
          path: 'users',
          name: 'Users',
          component: () => import('@/views/UsersView.vue'),
          meta: { title: '用户管理', adminOnly: true }
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { title: '个人设置' }
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (!to.meta.public && !authStore.isAuthenticated) {
    next('/login')
    return
  }

  if (to.meta.adminOnly && authStore.user?.role !== 'admin') {
    next('/dashboard')
    return
  }

  if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }

  next()
})

export default router
