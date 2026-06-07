import { defineStore } from 'pinia'
import { login as loginApi, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),

  actions: {
    async login(username, password) {
      try {
        const res = await loginApi(username, password)
        this.token = res.data.access_token
        localStorage.setItem('token', this.token)
        return res
      } catch (error) {
        // 重新抛出错误，让组件处理
        throw error
      }
    },

    async getUserInfo() {
      const res = await getUserInfo()
      this.userInfo = res.data
      return res
    },

    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
    }
  }
})