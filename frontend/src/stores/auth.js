import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/utils/axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isAuthenticated = ref(!!token.value)

  const setAuth = (newToken, userData) => {
    token.value = newToken
    user.value = userData
    isAuthenticated.value = true
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const clearAuth = () => {
    token.value = ''
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const login = async (credentials) => {
    try {
      const response = await axios.post('/users/login/', credentials)
      const { token: newToken, user: userData } = response.data
      setAuth(newToken, userData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || '登录失败')
    }
  }

  const register = async (userData) => {
    try {
      const registerData = {
        ...userData,
        password2: userData.confirmPassword
      }
      delete registerData.confirmPassword
      
      const response = await axios.post('/users/', registerData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || '注册失败')
    }
  }

  const logout = async () => {
    try {
      await axios.post('/users/logout/')
      clearAuth()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearAuth()
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put('/users/profile/', profileData)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || '更新个人信息失败')
    }
  }

  const changePassword = async (passwordData) => {
    try {
      const changePasswordData = {
        old_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
        new_password2: passwordData.confirmPassword
      }
      await axios.post('/users/change_password/', changePasswordData)
    } catch (error) {
      throw new Error(error.response?.data?.error || '修改密码失败')
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile,
    changePassword
  }
}) 