import request from './request'

export function updateUserInfo(data) {
  const formData = new FormData()
  formData.append('old_password', data.old_password)
  formData.append('new_password', data.new_password)
  return request({
    url: '/auth/me',
    method: 'put',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getUserInfo() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}