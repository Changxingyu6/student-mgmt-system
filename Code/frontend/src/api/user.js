import request from './request'

export function getUsers(page = 1, limit = 10) {
  return request({
    url: '/users',
    method: 'get',
    params: { page, limit }
  })
}

export function getLockedUsers() {
  return request({
    url: '/users/locked',
    method: 'get'
  })
}

export function unlockUser(userId) {
  return request({
    url: `/users/${userId}/unlock`,
    method: 'post'
  })
}