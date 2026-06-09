import request from './request'

// 获取登录日志
export function getLoginLogs(params = {}) {
  return request({
    url: '/logs/login',
    method: 'get',
    params
  })
}
