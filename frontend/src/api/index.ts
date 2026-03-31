import axios, { type AxiosInstance, type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

/**
 * 获取 API 基础 URL
 * 在 Electron 环境中动态获取后端端口
 * 在浏览器环境中使用相对路径（通过 Vite proxy）
 */
async function getBaseURL(): Promise<string> {
  // 检查是否在 Electron 环境中
  if (window.isElectron && window.electronAPI) {
    try {
      const port = await window.electronAPI.getBackendPort()
      return `http://127.0.0.1:${port}/api/v1`
    } catch (error) {
      console.error('Failed to get backend port:', error)
      return '/api/v1'
    }
  }
  return '/api/v1'
}

/**
 * 创建 axios 实例
 */
async function createAPI(): Promise<AxiosInstance> {
  const baseURL = await getBaseURL()
  
  const api: AxiosInstance = axios.create({
    baseURL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // 请求拦截器
  api.interceptors.request.use(
    (config) => {
      const authStore = useAuthStore()
      if (authStore.accessToken) {
        config.headers.Authorization = `Bearer ${authStore.accessToken}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器
  api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const authStore = useAuthStore()
      const originalRequest = error.config

      if (!originalRequest) {
        return Promise.reject(error)
      }

      // 处理 401 错误，尝试刷新 token
      if (error.response?.status === 401 && !originalRequest.headers._retry) {
        originalRequest.headers._retry = true
        
        try {
          const newToken = await authStore.refreshAccessToken()
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return api(originalRequest)
        } catch (refreshError) {
          ElMessage.error('登录已过期，请重新登录')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }

      // 处理其他错误
      const message = (error.response?.data as { detail?: string })?.detail || error.message || '请求失败'
      ElMessage.error(message)
      return Promise.reject(error)
    }
  )

  return api
}

// 创建 API 实例
let apiInstance: AxiosInstance | null = null

/**
 * 获取 API 实例（单例模式）
 */
export async function getAPI(): Promise<AxiosInstance> {
  if (!apiInstance) {
    apiInstance = await createAPI()
  }
  return apiInstance
}

// 为了兼容现有代码，导出一个默认的 API 实例
// 注意：在 Electron 环境中，这个实例的 baseURL 可能不正确
// 建议在新的代码中使用 getAPI() 函数
const defaultAPI: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
defaultAPI.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
defaultAPI.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const authStore = useAuthStore()
    const originalRequest = error.config

    if (!originalRequest) {
      return Promise.reject(error)
    }

    // 处理 401 错误，尝试刷新 token
    if (error.response?.status === 401 && !originalRequest.headers._retry) {
      originalRequest.headers._retry = true
      
      try {
        const newToken = await authStore.refreshAccessToken()
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return defaultAPI(originalRequest)
      } catch (refreshError) {
        ElMessage.error('登录已过期，请重新登录')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // 处理其他错误
    const message = (error.response?.data as { detail?: string })?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default defaultAPI
