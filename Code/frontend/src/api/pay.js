import request from './request'

// 查询支付记录
export function getPay(payId) {
  return request({ url: `/pay_api/pay/${payId}`, method: 'get' })
}
// 查询用户的所有支付记录（支持筛选）
export function getUserPays(userId, filters = {}) {
  const params = {}
  if (filters.order_no) params.order_no = filters.order_no
  if (filters.pay_status) params.pay_status = filters.pay_status
  if (filters.pay_method) params.pay_method = filters.pay_method
  if (filters.start_time) params.start_time = filters.start_time
  if (filters.end_time) params.end_time = filters.end_time
  return request({ url: `/pay_api/pay/user/${userId}`, method: 'get', params })
}

// 创建支付记录
export function createPay(data) {
  return request({ url: '/pay_api/pay', method: 'post', data })
}
// 处理支付
export function processPay(data) {
  return request({ url: '/pay_api/pay/process', method: 'post', data })
}
// 更新支付记录
export function updatePay(data) {
  return request({ url: '/pay_api/pay', method: 'put', data })
}
// 删除支付记录
export function deletePay(payId) {
  return request({ url: `/pay_api/pay/${payId}`, method: 'delete' })
}
