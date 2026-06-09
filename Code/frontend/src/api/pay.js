import request from './request'

// 查询支付记录
export function getPay(payId) {
  return request({ url: `/pay_api/pay/${payId}`, method: 'get' })
}
// 查询用户的所有支付记录
export function getUserPays(userId) {
  return request({ url: `/pay_api/pay/user/${userId}`, method: 'get' })
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
