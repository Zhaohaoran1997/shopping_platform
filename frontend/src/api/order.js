import request from '@/utils/request'

// 获取订单列表
export function getOrderList(params) {
  return request({
    url: '/orders/orders/',
    method: 'get',
    params
  })
}

// 获取订单详情
export function getOrderDetail(id) {
  return request({
    url: `/orders/orders/${id}/`,
    method: 'get'
  })
}

// 创建订单
export function createOrder(data) {
  return request({
    url: '/orders/orders/',
    method: 'post',
    data
  })
}

// 取消订单
export function cancelOrder(id) {
  return request({
    url: `/orders/orders/${id}/cancel/`,
    method: 'post'
  })
}

// 支付订单
export function payOrder(id, data) {
  return request({
    url: `/orders/orders/${id}/pay/`,
    method: 'post',
    data
  })
}

// 获取支付状态
export function getPaymentStatus(id) {
  return request({
    url: `/orders/orders/${id}/payment_status/`,
    method: 'get'
  })
}

// 确认收货
export function confirmReceive(id) {
  return request({
    url: `/orders/orders/${id}/confirm_receive/`,
    method: 'post'
  })
} 