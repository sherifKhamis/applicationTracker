import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { requiresGuest: true } // Only non-logged-in users can see this
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { requiresGuest: true } // Only non-logged-in users can see this
    },
    {
      path: '/',
      name: 'Dashboard',
      component: Dashboard,
      meta: { requiresAuth: true } // Only authenticated users can see this
    }
  ]
})

// Navigation Guard for Authenication
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('authToken')

  if (to.meta.requiresAuth && !isAuthenticated) {
    // If the route needs auth and the user isn't logged in, redirect to login
    next('/login')
  } else if (to.meta.requiresGuest && isAuthenticated) {
    // If the user tries to go to login while already logged in, redirect to dashboard
    next('/')
  } else {
    next()
  }
})

export default router