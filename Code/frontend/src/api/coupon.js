import request from './request'

// ============ 优惠券 ============
// 创建优惠券
export function createCoupon(data) {
  return request({ url: '/coupons', method: 'post', data })
}
// 获取优惠券列表
export function listCoupons(params) {
  return request({ url: '/coupons', method: 'get', params })
}
// 获取优惠券详情
export function getCoupon(id) {
  return request({ url: `/coupons/${id}`, method: 'get' })
}
// 更新优惠券
export function updateCoupon(id, data) {
  return request({ url: `/coupons/${id}`, method: 'put', data })
}
// 删除优惠券
export function deleteCoupon(id) {
  return request({ url: `/coupons/${id}`, method: 'delete' })
}

// ============ 用户优惠券 ============
// 创建用户优惠券
export function createUserCoupon(data) {
  return request({ url: '/coupons/user-coupons', method: 'post', data })
}
// 获取用户优惠券列表
export function listUserCoupons(params) {
  return request({ url: '/coupons/user-coupons', method: 'get', params })
}
// 获取用户优惠券详情
export function getUserCoupon(id) {
  return request({ url: `/coupons/user-coupons/${id}`, method: 'get' })
}
// 更新用户优惠券
export function updateUserCoupon(id, data) {
  return request({ url: `/coupons/user-coupons/${id}`, method: 'put', data })
}
// 删除用户优惠券
export function deleteUserCoupon(id) {
  return request({ url: `/coupons/user-coupons/${id}`, method: 'delete' })
}

// ============ 优惠券使用日志 ============
// 创建使用日志
export function createUseLog(data) {
  return request({ url: '/coupons/use-logs', method: 'post', data })
}
// 获取使用日志
export function listUseLogs(params) {
  return request({ url: '/coupons/use-logs', method: 'get', params })
}
// 获取使用日志详情
export function getUseLog(id) {
  return request({ url: `/coupons/use-logs/${id}`, method: 'get' })
}
// 更新使用日志
export function updateUseLog(id, data) {
  return request({ url: `/coupons/use-logs/${id}`, method: 'put', data })
}
// 删除使用日志
export function deleteUseLog(id) {
  return request({ url: `/coupons/use-logs/${id}`, method: 'delete' })
}

// ============ 营销活动 ============
// 创建活动
export function createActivity(data) {
  return request({ url: '/coupons/activities', method: 'post', data })
}
// 获取活动列表
export function listActivities(params) {
  return request({ url: '/coupons/activities', method: 'get', params })
}
// 获取活动详情
export function getActivity(id) {
  return request({ url: `/coupons/activities/${id}`, method: 'get' })
}
// 更新活动
export function updateActivity(id, data) {
  return request({ url: `/coupons/activities/${id}`, method: 'put', data })
}
// 删除活动
export function deleteActivity(id) {
  return request({ url: `/coupons/activities/${id}`, method: 'delete' })
}

// ============ 活动商品关联 ============
// 关联商品
export function addActivityGoods(activityId, productId) {
  return request({ url: `/coupons/activities/${activityId}/goods`, method: 'post', params: { product_id: productId } })
}
// 获取活动商品
export function listActivityGoods(activityId, params) {
  return request({ url: `/coupons/activities/${activityId}/goods`, method: 'get', params })
}
// 移除活动商品
export function removeActivityGoods(activityId, productId) {
  return request({ url: `/coupons/activities/${activityId}/goods`, method: 'delete', params: { product_id: productId } })
}

// ============ 活动订单关联 ============
// 关联订单
export function addActivityOrders(activityId, orderId) {
  return request({ url: `/coupons/activities/${activityId}/orders`, method: 'post', params: { orders_id: orderId } })
}
// 获取活动订单
export function listActivityOrders(activityId, params) {
  return request({ url: `/coupons/activities/${activityId}/orders`, method: 'get', params })
}
// 移除活动订单
export function removeActivityOrders(activityId, orderId) {
  return request({ url: `/coupons/activities/${activityId}/orders`, method: 'delete', params: { orders_id: orderId } })
}
