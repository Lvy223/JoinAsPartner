// src/api/index.js
import axios from 'axios'
import BASE_URL from './config'

// 创建axios实例
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000, // 请求超时时间10秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 在请求发送前处理
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('发送请求:', config.method.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 在接收到响应后处理
api.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url)
    return response.data // 直接返回数据部分
  },
  (error) => {
    console.error('响应错误:', error.message)

    if (error.response) {
      // 服务器返回了错误状态码
      const status = error.response.status
      const message = error.response.data?.message || '请求失败'

      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          window.location.href = '/login'
          break
        case 403:
          alert('没有权限执行此操作')
          break
        case 404:
          alert('请求的资源不存在')
          break
        case 500:
          alert('服务器错误，请稍后重试')
          break
        default:
          alert(message)
      }
    } else if (error.request) {
      // 请求发送但没有收到响应（后端未启动或网络断开）
      console.error('网络错误，请检查后端服务是否运行')
      alert('网络错误，请检查网络连接或后端服务状态')
    } else {
      // 请求配置出错
      alert('请求配置错误')
    }

    return Promise.reject(error)
  }
)

// ==================== 活动相关API ====================
export const activitiesAPI = {
  // 获取活动列表（信息流）
  getList: (params = {}) => api.get('/activities/feed', { params }),

  // 获取活动详情
  getDetail: (id) => api.get(`/activities/${id}`),

  // 创建活动
  create: (data) => api.post('/activities', data),

  // 取消活动（创建者）
  cancel: (id) => api.post(`/activities/${id}/cancel`),

  // 退出活动（参与者）
  quit: (id, data = {}) => api.post(`/activities/${id}/quit`, data),

  // 完成活动并提交反馈
  complete: (id, data) => api.post(`/activities/${id}/complete`, data),

  // 加入活动
  join: (id) => api.post(`/activities/${id}/join`),

  // 获取我加入的活动（需后端提供）
  getMyActivities: () => api.get('/auth/user/activities'),

  // 搜索活动（需后端提供，暂时使用前端过滤）
  search: (keyword) => api.get('/activities/search', { params: { keyword } })
}

// ==================== 用户相关API ====================
export const userAPI = {
  // 用户登录（参数格式：{ username, password }）
  login: (credentials) => api.post('/auth/login', {
    username: credentials.username,
    password: credentials.password
  }),

  // 用户注册（参数格式：{ username, password, nickname, phone }）
  register: (data) => api.post('/auth/register', data),

  // 获取用户信息
  getProfile: () => api.get('/auth/profile'),

  // 更新用户信息（需要后端支持 PUT /user/profile）
  updateProfile: (data) => api.put('/auth/profile', data),

  // 更新兴趣标签
  updateInterests: (data) => api.put('/auth/update-interests', data),

  // 上传头像
  uploadAvatar: (formData) => api.post('/user/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),

  // 修改密码
  changePassword: (data) => api.put('/user/password', data),

  // 获取用户统计数据
  getStats: () => api.get('/auth/stats'),

  // 获取用户发布的活动
  getCreatedActivities: () => api.get('/auth/user/created-activities')
}

// ==================== 文件上传API ====================
export const uploadAPI = {
  // 上传图片
  uploadImage: (formData) => api.post('/upload/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),

  // 上传文件
  uploadFile: (formData) => api.post('/upload/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// ==================== 通知相关API ====================
export const notificationAPI = {
  // 获取通知列表
  getList: (params = {}) => api.get('/notifications', { params }),

  // 标记通知为已读
  markAsRead: (id) => api.put(`/notifications/${id}/read`),

  // 标记所有通知为已读
  markAllAsRead: () => api.put('/notifications/read-all'),

  // 获取未读通知数量
  getUnreadCount: () => api.get('/notifications/unread-count')
}

// 导出默认实例
export default api