import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { UserInfo, LoginForm } from '@/types'
import * as authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<UserInfo | null>(null)
  const accessToken = ref<string>('')
  const refreshTokenValue = ref<string>('')
  const loading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // Actions
  async function login(form: LoginForm) {
    loading.value = true
    try {
      const res = await authApi.login(form)
      accessToken.value = res.access_token
      refreshTokenValue.value = res.refresh_token
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('refresh_token', res.refresh_token)
      
      // 获取用户信息
      await fetchUserInfo()
      return true
    } catch (error) {
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUserInfo() {
    try {
      const res = await authApi.getMe()
      user.value = res
      return res
    } catch (error) {
      user.value = null
      throw error
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearAuth()
    }
  }

  function clearAuth() {
    user.value = null
    accessToken.value = ''
    refreshTokenValue.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  function initializeAuth() {
    const token = localStorage.getItem('access_token')
    const refresh = localStorage.getItem('refresh_token')
    if (token) {
      accessToken.value = token
      refreshTokenValue.value = refresh || ''
      fetchUserInfo().catch(() => clearAuth())
    }
  }

  async function refreshAccessToken() {
    const refresh = refreshTokenValue.value || localStorage.getItem('refresh_token')
    if (!refresh) {
      clearAuth()
      throw new Error('No refresh token')
    }
    try {
      const res = await authApi.refreshToken(refresh)
      accessToken.value = res.access_token
      refreshTokenValue.value = res.refresh_token
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('refresh_token', res.refresh_token)
      return res.access_token
    } catch (error) {
      clearAuth()
      throw error
    }
  }

  return {
    user,
    accessToken,
    refreshTokenValue,
    loading,
    isAuthenticated,
    isAdmin,
    login,
    fetchUserInfo,
    logout,
    clearAuth,
    initializeAuth,
    refreshAccessToken
  }
})
