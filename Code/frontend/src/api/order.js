import request from './request'

// 从购物车创建订单
export function createOrderFromCart(data) {
  return request({ url: '/orders/create-from-cart', method: 'post', data })
}

// 获取用户订单列表（支持筛选）
export function getUserOrders(userId, filters = {}) {
  const params = {}
  if (filters.order_id) params.order_id = filters.order_id
  if (filters.order_status) params.order_status = filters.order_status
  if (filters.pay_status) params.pay_status = filters.pay_status
  if (filters.logistics_status) params.logistics_status = filters.logistics_status
  if (filters.start_time) params.start_time = filters.start_time
  if (filters.end_time) params.end_time = filters.end_time
  return request({ url: `/orders/user/${userId}`, method: 'get', params })
}

// 获取订单明细
export function getOrderItems(orderId) {
  return request({ url: `/orders/items/${orderId}`, method: 'get' })
}
