import BASE_URL from '@/api/config'
import { io } from 'socket.io-client'

let socket = null

/**
 * 初始化 Socket.IO 连接
 * @param {string} token - JWT token（从 localStorage 获取）
 * @returns {object} socket 实例
 */
export const initSocket = (token) => {
  if (!token) {
    console.error('无法初始化 Socket：缺少 token')
    return null
  }

  if (socket && socket.connected) {
    console.log('Socket 已连接，无需重复初始化')
    return socket
  }

  // 关闭已有连接（如果有）
  if (socket) {
    socket.disconnect()
  }

  // 创建新连接，token 通过查询参数传递（后端从 environ 解析）
  const SOCKET_URL = process.env.NODE_ENV === 'production'
    ? 'https://api.yourcompany.com'
    : 'http://localhost:8000'

  socket = io(SOCKET_URL, {
    query: { token },
    transports: ['websocket', 'polling'], // 优先使用 WebSocket
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
  })

  // 连接事件监听
  socket.on('connect', () => {
    console.log('WebSocket 连接成功，sid:', socket.id)
  })

  socket.on('connect_error', (err) => {
    console.error('WebSocket 连接失败:', err.message)
    // 检查是否是认证失败（token 无效或过期）
    // 后端可能返回 "Missing token" 或 "Invalid token"
    if (err.message === 'Invalid token' || err.message === 'Missing token') {
      // 清除本地存储的认证信息
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      // 提示用户重新登录
      alert('登录已过期，请重新登录')
      // 跳转到登录页（如果当前不在登录页）
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
  })

  socket.on('disconnect', (reason) => {
    console.log('WebSocket 断开:', reason)
  })

  return socket
}

/**
 * 获取当前 socket 实例（若未初始化则返回 null）
 */
export const getSocket = () => socket

/**
 * 断开连接
 */
export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

/**
 * 加入活动房间
 * @param {string|number} activityId
 */
export const joinActivityRoom = (activityId) => {
  if (socket && socket.connected) {
    socket.emit('client_join_activity', { activity_id: String(activityId) })
  } else {
    console.warn('Socket 未连接，无法加入房间')
  }
}

/**
 * 离开活动房间
 * @param {string|number} activityId
 */
export const leaveActivityRoom = (activityId) => {
  if (socket && socket.connected) {
    socket.emit('client_leave_activity', { activity_id: String(activityId) })
  }
}

/**
 * 发送聊天消息
 * @param {string|number} activityId
 * @param {string} content
 */
export const sendChatMessage = (activityId, content) => {
  if (socket && socket.connected) {
    socket.emit('client_send_message', {
      activity_id: String(activityId),
      content: content
    })
  } else {
    console.error('Socket 未连接，消息发送失败')
    throw new Error('WebSocket 未连接')
  }
}

export default {
  initSocket,
  getSocket,
  disconnectSocket,
  joinActivityRoom,
  leaveActivityRoom,
  sendChatMessage
}