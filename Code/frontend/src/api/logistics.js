import request from './request'

// 查询物流
export function getLogistics(logisticsId) {
  return request({ url: `/logistics_api/logistics/${logisticsId}`, method: 'get' })
}
// 通过订单ID查询物流
export function getLogisticsByOrder(orderId) {
  return request({ url: `/logistics_api/logistics/order/${orderId}`, method: 'get' })
}
// 创建物流
export function createLogistics(data) {
  return request({ url: '/logistics_api/logistics', method: 'post', data })
}
// 更新物流
export function updateLogistics(data) {
  return request({ url: '/logistics_api/logistics', method: 'put', data })
}
// 查询用户的所有物流记录
export function getUserLogistics(userId) {
  return request({ url: `/logistics_api/logistics/user/${userId}`, method: 'get' })
}
// 确认收货
export function confirmReceipt(logisticsId) {
  return request({ url: `/logistics_api/logistics/${logisticsId}/confirm`, method: 'put' })
}
