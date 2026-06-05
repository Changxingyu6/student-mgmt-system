import request from './request'

export function login(username, password) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  return request({
    url: '/auth/login',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function getUserInfo() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}

export function updateUserInfo(username, password) {
  const params = {}
  if (username) params.username = username
  if (password) params.password = password
  return request({
    url: '/auth/me',
    method: 'put',
    params
  })
}