import request from './request'

// 获取用户列表（管理员）
export function getUsers(page = 1, limit = 10) {
  return request({
    url: '/users',
    method: 'get',
    params: { page, limit }
  })
}

// 获取用户详情（管理员）
export function getUserDetail(userId) {
  return request({
    url: `/users/${userId}`,
    method: 'get'
  })
}

// 创建用户（管理员）
export function createUser(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

// 更新用户（管理员）
export function updateUser(userId, data) {
  return request({
    url: `/users/${userId}`,
    method: 'put',
    data
  })
}

// 删除用户（管理员）
export function deleteUser(userId) {
  return request({
    url: `/users/${userId}`,
    method: 'delete'
  })
}

// 获取锁定用户列表（管理员）
export function getLockedUsers() {
  return request({
    url: '/users/locked',
    method: 'get'
  })
}

// 解锁用户（管理员）
export function unlockUser(userId) {
  return request({
    url: `/users/${userId}/unlock`,
    method: 'post'
  })
}

// 充值余额（管理员）
export function rechargeBalance(userId, data) {
  return request({
    url: `/users/${userId}/recharge`,
    method: 'post',
    data
  })
}

// 修改用户角色（管理员）
export function updateUserRole(userId, data) {
  return request({
    url: `/users/${userId}/role`,
    method: 'post',
    data
  })
}