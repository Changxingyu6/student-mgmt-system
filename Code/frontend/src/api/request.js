import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 直接从 localStorage 获取 token，避免在非 Vue 上下文使用 Pinia
    const token = localStorage.getItem('token')
    console.log('Request URL:', config.url)
    console.log('Token from localStorage:', token ? '存在' : '不存在')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('Authorization header set:', config.headers.Authorization)
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      // 检查是否是登录接口（通过 URL 判断）
      if (error.config?.url?.includes('/users/login')) {
        // 登录接口的 401 错误，抛出错误让组件处理显示
        return Promise.reject(error)
      }
      // 其他 401 错误（如 token 过期）
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      window.location.href = '/login'
    } else {
      ElMessage.error(error.response?.data?.detail || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request