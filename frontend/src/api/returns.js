import request from '@/utils/request'

// 获取退换货列表
export function getReturnList(params) {
  return request({
    url: '/returns/requests/',
    method: 'get',
    params
  })
}

// 获取退换货详情
export function getReturnDetail(id) {
  return request({
    url: `/returns/requests/${id}/`,
    method: 'get'
  })
}

// 创建退换货申请
export function createReturnRequest(data) {
  return request({
    url: '/returns/requests/',
    method: 'post',
    data
  })
}

// 上传退换货图片
export function uploadReturnImage(data) {
  return request({
    url: '/returns/upload/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取可退换货的订单列表
export function getReturnableOrders(params) {
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

// 搜索订单
export function searchOrders(params) {
  return request({
    url: '/orders/orders/',
    method: 'get',
    params
  })
}

// 获取订单商品列表
export function getOrderProducts(orderId) {
  return request({
    url: `/orders/orders/${orderId}/products/`,
    method: 'get'
  })
}

// 提交物流信息
export function submitShippingInfo(id, data) {
  return request({
    url: `/returns/requests/${id}/shipping/`,
    method: 'post',
    data
  })
} 