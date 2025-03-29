import request from '@/utils/request'

// 获取可用优惠券列表
export function getAvailableCoupons() {
  return request({
    url: '/coupons/user-coupons/',
    method: 'get',
    params: {
      status: 0  // 0: 未使用
    }
  })
}

// 获取所有优惠券列表
export function getCouponList() {
  return request({
    url: '/coupons/user-coupons/',
    method: 'get'
  })
}

// 使用优惠券
export function useCoupon(couponId) {
  return request({
    url: `/coupons/user-coupons/${couponId}/use/`,
    method: 'post'
  })
} 