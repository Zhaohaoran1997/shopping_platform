import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'

// 获取地址列表
export function getAddressList() {
  const authStore = useAuthStore()
  return request({
    url: `/users/${authStore.user.id}/addresses/`,
    method: 'get'
  })
}

// 创建新地址
export function createAddress(data) {
  const authStore = useAuthStore()
  return request({
    url: `/users/${authStore.user.id}/addresses/`,
    method: 'post',
    data
  })
}

// 更新地址
export function updateAddress(id, data) {
  const authStore = useAuthStore()
  return request({
    url: `/users/${authStore.user.id}/addresses/${id}/`,
    method: 'put',
    data
  })
}

// 删除地址
export function deleteAddress(id) {
  const authStore = useAuthStore()
  return request({
    url: `/users/${authStore.user.id}/addresses/${id}/`,
    method: 'delete'
  })
}

// 设置默认地址
export function setDefaultAddress(id) {
  const authStore = useAuthStore()
  return request({
    url: `/users/${authStore.user.id}/addresses/${id}/set_default/`,
    method: 'post'
  })
} 