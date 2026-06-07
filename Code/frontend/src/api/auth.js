import request from './request'

export function login(username, password) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  return request({
    url: '/users/login',
    method: 'post',
    data: formData
  })
}

export function getUserInfo() {
  return request({
    url: '/users/me',
    method: 'get'
  })
}

export function updateUserInfo(username, password) {
  const params = {}
  if (username) params.username = username
  if (password) params.password = password
  return request({
    url: '/users/me',
    method: 'put',
    params
  })
}