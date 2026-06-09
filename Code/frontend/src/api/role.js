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
