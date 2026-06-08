import request from './request'

// 获取地址列表
export function getAddresses() {
  return request({
    url: '/addresses',
    method: 'get'
  })
}

// 获取默认地址
export function getDefaultAddress() {
  return request({
    url: '/addresses/default',
    method: 'get'
  })
}

// 创建地址
export function createAddress(data) {
  return request({
    url: '/addresses',
    method: 'post',
    data
  })
}

// 更新地址
export function updateAddress(addressId, data) {
  return request({
    url: `/addresses/${addressId}`,
    method: 'put',
    data
  })
}

// 删除地址
export function deleteAddress(addressId) {
  return request({
    url: `/addresses/${addressId}`,
    method: 'delete'
  })
}

// 设置默认地址
export function setDefaultAddress(addressId) {
  return request({
    url: `/addresses/${addressId}/default`,
    method: 'post'
  })
}