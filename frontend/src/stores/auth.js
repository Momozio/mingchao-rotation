import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!token.value)

  const setTokens = (accessToken, refresh) => {
    token.value = accessToken
    refreshToken.value = refresh
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refresh)
  }

  const clearTokens = () => {
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  const login = async (username, password) => {
    const data = await authAPI.login(username, password)
    setTokens(data.access, data.refresh)
    user.value = data.user
    return data
  }

  const register = async (username, password, passwordConfirm) => {
    const data = await authAPI.register(username, password, passwordConfirm)
    return data
  }

  const logout = () => {
    clearTokens()
    user.value = null
  }

  const fetchUser = async () => {
    if (!token.value) {
      user.value = null
      return null
    }
    try {
      user.value = await authAPI.getCurrentUser()
      return user.value
    } catch (error) {
      user.value = null
      return null
    }
  }

  const checkAuth = async () => {
    if (!token.value) {
      return false
    }
    try {
      user.value = await authAPI.getCurrentUser()
      return true
    } catch (error) {
      if (error.message === 'Token expired') {
        try {
          const data = await authAPI.refreshToken(refreshToken.value)
          setTokens(data.access, data.refresh)
          user.value = await authAPI.getCurrentUser()
          return true
        } catch (refreshError) {
          logout()
          return false
        }
      }
      logout()
      return false
    }
  }

  return {
    user,
    token,
    refreshToken,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    checkAuth,
    setTokens,
    clearTokens
  }
})
