import request from '@/utils/request'

// 获取商品列表
export function getProductList(params) {
  return request({
    url: '/products/',
    method: 'get',
    params
  })
}

// 获取商品详情
export function getProductDetail(id) {
  return request({
    url: `/products/${id}/`,
    method: 'get'
  })
}

// 获取商品分类列表
export function getCategoryList() {
  return request({
    url: '/categories/',
    method: 'get'
  })
}

// 获取商品评论列表
export function getProductReviews(productId, params) {
  return request({
    url: `/products/${productId}/reviews/`,
    method: 'get',
    params
  })
}

// 创建商品评论
export function createProductReview(productId, data) {
  return request({
    url: `/products/${productId}/reviews/`,
    method: 'post',
    data
  })
} 