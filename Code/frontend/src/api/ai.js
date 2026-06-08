import request from './request'

// AI对话
export function chat(messages) {
  return request({
    url: '/ai/chat',
    method: 'post',
    data: { messages }
  })
}