import request from './request'

/**
 * 从购物车创建订单
 */
export function createOrderFromCart(userId) {
  return request({
    url: '/orders/create-from-cart',
    method: 'post',
    headers: {
      'user-id': userId
    }
  })
}