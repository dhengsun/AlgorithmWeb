import axios from 'axios'
import router from '@/router'  // 引入路由实例
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://ip', // 改为你的实际ip
  timeout: 5000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const accessToken = localStorage.getItem('access_token')
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)// 响应拦截器
request.interceptors.response.use(
  response => {
    return response
  },
  async error => {
    if (error.response) {
      const { status } = error.response

      if (status === 401) {
        // token 过期或无效
        const refreshToken = localStorage.getItem('refresh_token')

        if (refreshToken) {
          try {
            // 尝试使用 refresh token 获取新的 access token
            const response = await axios.post('/auth/token/refresh/', {
              refresh: refreshToken
            })

            // 更新 localStorage 中的 token
            localStorage.setItem('access_token', response.data.access)

            // 重试原来的请求
            error.config.headers['Authorization'] = `Bearer ${response.data.access}`
            return request(error.config)
          } catch (refreshError) {
            // refresh token 也过期了，清除所有 token 并跳转到登录页
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user_info')
            router.push('/login')
            ElMessage.error('登录已过期，请重新登录')
          }
        } else {
          router.push('/login')
          ElMessage.error('请先登录')
        }
      } else if (status === 403) {
        ElMessage.error('没有权限进行此操作')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (status === 500) {
        ElMessage.error('服务器错误，请稍后重试')
      } else {
        ElMessage.error(error.response.data.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查你的网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default request
