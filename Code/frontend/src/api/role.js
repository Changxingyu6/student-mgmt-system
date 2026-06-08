import request from './request'

// 获取角色列表（管理员）
export function getRoles() {
  return request({
    url: '/roles',
    method: 'get'
  })
}

// 获取角色详情（管理员）
export function getRoleDetail(roleId) {
  return request({
    url: `/roles/${roleId}`,
    method: 'get'
  })
}

// 创建角色（管理员）
export function createRole(data) {
  return request({
    url: '/roles',
    method: 'post',
    data
  })
}

// 更新角色（管理员）
export function updateRole(roleId, data) {
  return request({
    url: `/roles/${roleId}`,
    method: 'put',
    data
  })
}

// 删除角色（管理员）
export function deleteRole(roleId) {
  return request({
    url: `/roles/${roleId}`,
    method: 'delete'
  })
}