import request from './request'

// ============ 用户统计 ============
// 当周新增用户数（最近7天）
export function getWeeklyNewUsers() {
  return request({ url: '/data-analysis/users/weekly', method: 'get' })
}

// 当月新增用户数（最近30天）
export function getMonthlyNewUsers() {
  return request({ url: '/data-analysis/users/monthly', method: 'get' })
}

// 用户综合统计
export function getUserStatistics() {
  return request({ url: '/data-analysis/users/statistics', method: 'get' })
}

// 用户等级统计
export function getUserLevelStatistics() {
  return request({ url: '/data-analysis/users/level-statistics', method: 'get' })
}

// ============ 商品统计 ============
// 销量前N商品
export function getTopSellingGoods(limit = 20) {
  return request({ url: '/data-analysis/goods/top-selling', method: 'get', params: { limit } })
}

// 商品分类统计
export function getCategoryStatistics() {
  return request({ url: '/data-analysis/goods/category-statistics', method: 'get' })
}

// 库存预警商品
export function getLowStockGoods() {
  return request({ url: '/data-analysis/goods/low-stock', method: 'get' })
}

// ============ 订单统计 ============
// 订单统计（按日/周/月）
export function getOrderStatistics(period = 'day') {
  return request({ url: '/data-analysis/orders/statistics', method: 'get', params: { period } })
}

// 支付方式统计
export function getPaymentStatistics() {
  return request({ url: '/data-analysis/orders/payment-statistics', method: 'get' })
}

// 超时未付款订单
export function getOverdueUnpaidOrders(timeoutHours = 24) {
  return request({ url: '/data-analysis/orders/overdue-unpaid', method: 'get', params: { timeout_hours: timeoutHours } })
}

// 长时间未发货订单
export function getLongTimeUnshippedOrders(timeoutHours = 48) {
  return request({ url: '/data-analysis/orders/long-time-unshipped', method: 'get', params: { timeout_hours: timeoutHours } })
}

// ============ 营销统计 ============
// 优惠券统计
export function getCouponStatistics() {
  return request({ url: '/data-analysis/marketing/coupon-statistics', method: 'get' })
}

// 营销活动统计
export function getActivityStatistics() {
  return request({ url: '/data-analysis/marketing/activity-statistics', method: 'get' })
}
