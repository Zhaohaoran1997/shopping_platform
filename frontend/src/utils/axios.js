import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// 创建 axios 实例
const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 10000
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // token 过期或无效，清除认证信息并跳转到登录页
          const authStore = useAuthStore()
          authStore.clearAuth()
          window.location.href = '/login'
          break
        case 403:
          // 权限不足
          break
        case 404:
          // 资源不存在
          break
        case 500:
          // 服务器错误
          break
        default:
          break
      }
    }
    return Promise.reject(error)
  }
)

export default instance 