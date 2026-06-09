import request from './request'

// 查询退货物流
export function getReturnLogistics(returnLogisticsId) {
  return request({ url: `/return_logistics_api/return_logistics/${returnLogisticsId}`, method: 'get' })
}
// 通过售后单ID查询退货物流
export function getReturnLogisticsByAfterSales(afterSalesId) {
  return request({ url: `/return_logistics_api/return_logistics/after_sales/${afterSalesId}`, method: 'get' })
}
// 创建退货物流
export function createReturnLogistics(data) {
  return request({ url: '/return_logistics_api/return_logistics', method: 'post', data })
}
// 更新退货物流
export function updateReturnLogistics(data) {
  return request({ url: '/return_logistics_api/return_logistics', method: 'put', data })
}
// 删除退货物流
export function deleteReturnLogistics(returnLogisticsId) {
  return request({ url: `/return_logistics_api/return_logistics/${returnLogisticsId}`, method: 'delete' })
}
