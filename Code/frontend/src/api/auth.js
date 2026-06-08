import request from './request'

// 用户登录
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

// 用户注册
export function register(data) {
  return request({
    url: '/users/register',
    method: 'post',
    data
  })
}

// 获取当前用户信息
export function getUserInfo() {
  return request({
    url: '/users/me',
    method: 'get'
  })
}

// 修改密码
export function updatePassword(data) {
  return request({
    url: '/users/me',
    method: 'put',
    data
  })
}

// 更新个人信息
export function updateProfile(data) {
  return request({
    url: '/users/me/profile',
    method: 'put',
    data
  })
}

// 更新用户信息（别名）
export function updateUserInfo(data) {
  return request({
    url: '/users/me',
    method: 'put',
    data
  })
}