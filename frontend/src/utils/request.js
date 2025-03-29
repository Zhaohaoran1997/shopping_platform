import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

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
          // 清除认证信息
          authStore.clearAuth()
          // 显示提示信息
          ElMessage.error('登录已过期，请重新登录')
          // 保存当前路由
          const currentRoute = router.currentRoute.value
          // 跳转到登录页面，并记录来源页面
          router.push({
            path: '/login',
            query: { redirect: currentRoute.fullPath }
          })
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

export default request 