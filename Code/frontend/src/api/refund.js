import request from './request'

// 查询退款记录
export function getRefund(refundId) {
  return request({ url: `/refund_api/refund/${refundId}`, method: 'get' })
}
// 提交退款申请
export function createRefund(data) {
  return request({ url: '/refund_api/refund', method: 'post', data })
}
// 更新退款状态
export function updateRefund(data) {
  return request({ url: '/refund_api/refund', method: 'put', data })
}
// 删除退款记录
export function deleteRefund(refundId) {
  return request({ url: `/refund_api/refund/${refundId}`, method: 'delete' })
}
