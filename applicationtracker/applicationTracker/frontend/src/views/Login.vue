<template>
  <div class="login-container">
    <!-- Custom Toast Notification -->
    <div v-if="toastMessage" :class="['toast-notification', toastType]">
      {{ toastMessage }}
      <button @click="closeToast" class="toast-close">&times;</button>
    </div>

    <div class="login-card card">
      <h2 class="login-title">Sign In</h2>
      <p class="login-subtitle">Enter your credentials to access the Application Tracker</p>
      
      <form @submit.prevent="handleLogin" class="login-form" novalidate>
        <div class="form-group">
          <label>Email *</label>
          <input 
            type="email" 
            v-model="email" 
            placeholder="admin@example.com" 
            autofocus
            :class="{'input-error': validationErrors.email}"
          />
          <span class="error-msg" v-if="validationErrors.email">{{ validationErrors.email }}</span>
        </div>
        
        <div class="form-group">
          <label>Password *</label>
          <input 
            type="password" 
            v-model="password" 
            placeholder="••••••••" 
            :class="{'input-error': validationErrors.password}"
          />
          <span class="error-msg" v-if="validationErrors.password">{{ validationErrors.password }}</span>
        </div>
        
        <button type="submit" class="btn-primary login-btn" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <div class="auth-link">
        <router-link to="/register">Don't have an account? Sign up</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)

const validationErrors = ref({
  email: '',
  password: ''
})

const toastMessage = ref('')
const toastType = ref('error')
let toastTimeout = null

const showToast = (message, type = 'error') => {
  toastMessage.value = message
  toastType.value = type
  if (toastTimeout) clearTimeout(toastTimeout)
  toastTimeout = setTimeout(() => { closeToast() }, 5000)
}

const closeToast = () => {
  toastMessage.value = ''
}

const handleLogin = async () => {
  validationErrors.value = { email: '', password: '' }
  let hasErrors = false

  if (!email.value || !email.value.trim()) {
    validationErrors.value.email = "BITTE FÜLLE DIESES FELD AUS."
    hasErrors = true
  }
  if (!password.value || !password.value.trim()) {
    validationErrors.value.password = "BITTE FÜLLE DIESES FELD AUS."
    hasErrors = true
  }

  if (hasErrors) return

  loading.value = true

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })

    const data = await res.json()

    if (res.ok) {
      localStorage.setItem('authToken', data.token)
      router.push('/')
    } else {
      showToast(data.error || 'Login failed. Please check your credentials.', 'error')
    }
  } catch (error) {
    showToast('Failed to connect to the server.', 'error')
    console.error("Login error:", error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: var(--bg-color);
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
  background-color: var(--card-bg);
  border: 3px solid var(--text-main);
  border-radius: 12px;
  box-shadow: 8px 8px 0px var(--primary-color);
  box-sizing: border-box;
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
    box-shadow: 5px 5px 0px var(--primary-color);
  }
}

.login-title {
  text-align: center;
  color: var(--primary-color);
  border-bottom: none;
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-shadow: 2px 2px 0px var(--secondary-color);
}

.login-subtitle {
  text-align: center;
  color: var(--text-main);
  font-weight: 600;
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.login-form label {
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.85rem;
}

.login-form input {
  padding: 0.8rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-main);
  border: 3px solid var(--text-main);
  border-radius: 8px;
  background-color: #fff;
  transition: all 0.2s ease-in-out;
  outline: none;
}

.login-form input::placeholder {
  color: #a0aec0;
  font-weight: 500;
}

.login-form input:focus {
  border-color: var(--primary-color);
  box-shadow: 4px 4px 0px var(--secondary-color);
  transform: translate(-2px, -2px);
}

.login-form input.input-error {
  border-color: #ef4444; /* red */
  background-color: #fef2f2;
}

.login-form input.input-error:focus {
  box-shadow: 4px 4px 0px #ef4444;
}

.error-msg {
  display: block;
  color: #ef4444;
  font-size: 0.8rem;
  font-weight: 800;
  margin-top: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

/* Toast Notification Styles */
.toast-notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1100;
  padding: 1rem 3rem 1rem 1.5rem;
  border-radius: 8px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 3px solid var(--text-main);
  box-shadow: 6px 6px 0px var(--text-main);
  animation: slide-down 0.3s ease-out forwards;
  max-width: 90%;
  text-align: center;
}

.toast-notification.error {
  background-color: #fee2e2;
  color: #b91c1c;
}

.toast-notification.success {
  background-color: #dcfce3;
  color: #166534;
}

.toast-close {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  font-size: 1.5rem;
  font-weight: bold;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
}

.toast-close:hover {
  opacity: 1;
}

@keyframes slide-down {
  0% { top: -100px; opacity: 0; }
  100% { top: 20px; opacity: 1; }
}

.login-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background-color: var(--primary-color);
  color: #fff;
  border: 3px solid var(--text-main);
  border-radius: 8px;
  margin-top: 1rem;
  box-shadow: 4px 4px 0px var(--text-main);
  cursor: pointer;
  transition: all 0.1s ease-in-out;
}

.login-btn:hover:not(:disabled) {
  transform: translate(-3px, -3px);
  box-shadow: 7px 7px 0px var(--text-main);
  background-color: var(--primary-hover);
}

.login-btn:active:not(:disabled) {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px var(--text-main);
}

.login-btn:disabled {
  opacity: 0.7;
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
}

.auth-link {
  text-align: center;
  margin-top: 1.5rem;
}

.auth-link a {
  color: var(--text-main);
  font-weight: 700;
  text-decoration: underline;
  transition: color 0.1s;
}

.auth-link a:hover {
  color: var(--primary-color);
}
</style>