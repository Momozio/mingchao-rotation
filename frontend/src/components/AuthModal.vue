<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'login-success'])

const authStore = useAuthStore()

const isRegister = ref(false)
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const close = () => {
  emit('update:modelValue', false)
  error.value = ''
  username.value = ''
  password.value = ''
  confirmPassword.value = ''
}

const submit = async () => {
  error.value = ''
  
  if (!username.value || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }
  
  if (isRegister.value) {
    if (password.value !== confirmPassword.value) {
      error.value = '两次密码不一致'
      return
    }
    if (password.value.length < 6) {
      error.value = '密码长度至少 6 位'
      return
    }
  }
  
  loading.value = true
  
  try {
    if (isRegister.value) {
      await authStore.register(username.value, password.value, confirmPassword.value)
    } else {
      await authStore.login(username.value, password.value)
    }
    emit('login-success')
    close()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="auth-overlay" @click.self="close">
      <div class="auth-card">
        <div class="auth-header">
          <img src="/assets/logo.png" alt="logo" class="auth-logo" />
          <h2>{{ isRegister ? '注册账号' : '登录' }}</h2>
        </div>
        
        <form @submit.prevent="submit" class="auth-form">
          <div class="form-group">
            <label>用户名</label>
            <input 
              v-model="username" 
              type="text" 
              placeholder="请输入用户名"
              autocomplete="username"
            />
          </div>
          
          <div class="form-group">
            <label>密码</label>
            <input 
              v-model="password" 
              type="password" 
              placeholder="请输入密码"
              autocomplete="current-password"
            />
          </div>
          
          <div v-if="isRegister" class="form-group">
            <label>确认密码</label>
            <input 
              v-model="confirmPassword" 
              type="password" 
              placeholder="请再次输入密码"
              autocomplete="new-password"
            />
          </div>
          
          <div v-if="error" class="error-msg">{{ error }}</div>
          
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '处理中...' : (isRegister ? '注册' : '登录') }}
          </button>
        </form>
        
        <div class="auth-footer">
          <span>{{ isRegister ? '已有账号？' : '还没有账号？' }}</span>
          <a href="#" @click.prevent="isRegister = !isRegister; error = ''">
            {{ isRegister ? '立即登录' : '立即注册' }}
          </a>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.auth-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.auth-card {
  background: var(--bg-secondary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 380px;
  border: 1px solid var(--border-color);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  margin-bottom: 16px;
}

.auth-header h2 {
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.form-group input {
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 15px;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(255, 45, 85, 0.15);
}

.error-msg {
  color: #ff3b30;
  font-size: 13px;
  text-align: center;
  padding: 12px;
  background: rgba(255, 59, 48, 0.1);
  border-radius: 8px;
}

.submit-btn {
  padding: 16px;
  border-radius: 12px;
  border: none;
  background: var(--accent-color);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: scale(1.02);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-footer {
  margin-top: 24px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
}

.auth-footer a {
  color: var(--accent-color);
  text-decoration: none;
  margin-left: 4px;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
