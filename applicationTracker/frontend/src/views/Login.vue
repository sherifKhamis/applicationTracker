<template>
  <div class="login-container">
    <div class="login-card card">
      <h2 class="login-title">Sign In</h2>
      <p class="login-subtitle">Enter your credentials to access the Application Tracker</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>Email</label>
          <input 
            type="email" 
            v-model="email" 
            placeholder="admin@example.com" 
            required 
            autofocus 
          />
        </div>
        
        <div class="form-group">
          <label>Password</label>
          <input 
            type="password" 
            v-model="password" 
            placeholder="••••••••" 
            required 
          />
        </div>

        <div v-if="errorMessage" class="error-alert">
          {{ errorMessage }}
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
const errorMessage = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })

    const data = await res.json()

    if (res.ok) {
      // Basic client-side session management
      localStorage.setItem('authToken', data.token)
      router.push('/')
    } else {
      errorMessage.value = data.error || 'Login failed. Please check your credentials.'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the server.'
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

.error-alert {
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: bold;
  text-align: center;
  border: 2px solid #b91c1c;
  box-shadow: 3px 3px 0px #b91c1c;
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