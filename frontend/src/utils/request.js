import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000
})

// 请求拦截器
request.interceptors.request.use(
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
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          const authStore = useAuthStore()
          authStore.clearAuth()
          window.location.href = '/login'
          break
        default:
          ElMessage.error(error.response.data.message || '请求失败')
      }
    }
    return Promise.reject(error)
  }
)

export default request 