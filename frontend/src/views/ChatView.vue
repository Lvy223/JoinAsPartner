<template>
  <div class="chat-page">
    <!-- 顶部导航 -->
    <div class="chat-header">
      <button class="back-btn" @click="goBack">←</button>
      <h3>{{ currentActivity ? currentActivity.title : '队伍聊天' }}</h3>
      <button class="menu-btn" @click="toggleMenu">
        <i class="menu-icon"></i>
      </button>
    </div>

    <!-- 菜单弹出层 -->
    <div v-if="showMenu" class="menu-overlay" @click="toggleMenu">
      <div class="menu-popup" @click.stop>
        <button class="menu-item complete-item" @click="goToComplete">
          <span>活动完成</span>
        </button>
        <button class="menu-item quit-item" @click="goToQuit">
          <span>退出队伍</span>
        </button>
        <button class="menu-item cancel-item" @click="toggleMenu">
          <span>取消</span>
        </button>
      </div>
    </div>

    <!-- 聊天内容 -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="isLoading" class="loading">
        <span>加载中...</span>
      </div>
      <div v-else-if="error" class="error">
        <span>{{ error }}</span>
        <button @click="refreshChat">重试</button>
      </div>
      <div v-else>
        <div class="message system">
          <div class="system-message">
            <span>聊天记录</span>
          </div>
        </div>
        <div
          v-for="msg in messages"
          :key="msg.id || msg.timestamp"
          class="message"
          :class="{ own: msg.user_id === currentUserId }"
        >
          <div class="message-avatar">{{ getUserInitial(msg.user_id) }}</div>
          <div class="message-content">
            <div class="message-bubble">
              <p>{{ msg.content }}</p>
            </div>
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>
        <div v-if="isSending" class="message own">
          <div class="message-avatar">我</div>
          <div class="message-content">
            <div class="message-bubble sending">
              <p>{{ pendingMessage }}</p>
            </div>
            <div class="message-time">发送中...</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息输入框 -->
    <div class="chat-input">
      <input
        type="text"
        v-model="newMessage"
        placeholder="输入消息..."
        @keyup.enter="sendMessage"
        :disabled="isSending"
      />
      <button
        class="send-btn"
        @click="sendMessage"
        :disabled="isSending || !newMessage.trim()"
      >
        发送
      </button>
    </div>
  </div>
</template>

<script>
import { userAPI } from '@/api'
import socketService from '@/utils/socket'

export default {
  name: 'ChatView',
  data() {
    return {
      currentActivity: null,     // 当前聊天活动对象
      myActivities: [],          // 用户参与的所有活动列表（从后端获取）
      currentUserId: null,       // 当前登录用户ID
      messages: [],              // 消息数组
      newMessage: '',
      pendingMessage: '',
      isSending: false,
      isLoading: false,
      error: null,
      showMenu: false,
      offlineMessages: [],
      isSocketConnected: false,
      // 保存监听器函数引用，用于清理
      socketEventHandlers: {
        connect: null,
        newMessage: null,
        joined: null,
        offlineMessage: null,
        error: null,
        kick: null
      }
    }
  },
  async mounted() {
    await this.loadCurrentUser()
    await this.loadMyActivities()
    this.initWebSocket()
    this.setupSocketListeners()
  },
  beforeUnmount() {
    // 清理 WebSocket 监听器
    const socket = socketService.getSocket()
    if (socket) {
      if (this.socketEventHandlers.connect) {
        socket.off('connect', this.socketEventHandlers.connect)
      }
      if (this.socketEventHandlers.newMessage) {
        socket.off('server_new_message', this.socketEventHandlers.newMessage)
      }
      if (this.socketEventHandlers.joined) {
        socket.off('server_joined', this.socketEventHandlers.joined)
      }
      if (this.socketEventHandlers.offlineMessage) {
        socket.off('server_offline_message', this.socketEventHandlers.offlineMessage)
      }
      if (this.socketEventHandlers.error) {
        socket.off('server_error', this.socketEventHandlers.error)
      }
      if (this.socketEventHandlers.kick) {
        socket.off('server_kick', this.socketEventHandlers.kick)
      }
    }
    // 离开活动房间
    if (this.currentActivity) {
      socketService.leaveActivityRoom(this.currentActivity.id)
    }
  },
  watch: {
    '$route': {
      handler() {
        this.refreshChat()
      },
      immediate: false
    }
  },
  methods: {
    async loadCurrentUser() {
      try {
        const res = await userAPI.getProfile()
        if (res.code === 200 && res.data && res.data.user) {
          this.currentUserId = res.data.user.id
        } else {
          const userInfo = localStorage.getItem('userInfo')
          if (userInfo) {
            this.currentUserId = JSON.parse(userInfo).id
          }
        }
      } catch (err) {
        console.error('获取用户信息失败:', err)
      }
    },
    async loadMyActivities() {
      this.isLoading = true
      this.error = null
      try {
        const response = await userAPI.getMyActivities()
        if (response.code === 200 && Array.isArray(response.data)) {
          this.myActivities = response.data.map(item => {
            const act = item
            return {
              id: act.id,
              title: act.title,
              description: act.description,
              location: act.location_name || '未知地点',
              time: act.start_time ? new Date(act.start_time).toLocaleString() : '时间待定',
              currentMembers: act.current_participants || 0,
              targetMembers: act.max_participants || 0,
              creator_id: act.creator_id,
              creator_nickname: act.creator_nickname,
              status: act.status,
              role: item.role,
              joined_at: item.joined_at
            }
          })
        } else {
          this.myActivities = []
          console.warn('获取活动列表失败:', response.message)
        }
      } catch (err) {
        console.error('加载活动列表失败:', err)
        this.error = '加载活动列表失败，请重试'
        this.myActivities = []
      } finally {
        this.isLoading = false
        this.determineCurrentActivity()
      }
    },
    determineCurrentActivity() {
      const routeId = this.$route.query.activityId
      const storedId = localStorage.getItem('currentActivityId')
      const activityId = routeId || storedId
      if (activityId && this.myActivities.length) {
        this.currentActivity = this.myActivities.find(a => String(a.id) === String(activityId))
      }
      if (!this.currentActivity && this.myActivities.length) {
        this.currentActivity = this.myActivities[0]
      }
      if (this.currentActivity) {
        localStorage.setItem('currentActivityId', this.currentActivity.id)
        // 如果 WebSocket 已连接，立即加入房间；否则等待 connect 事件触发
        const socket = socketService.getSocket()
        if (socket && socket.connected) {
          socketService.joinActivityRoom(this.currentActivity.id)
        }
      }
    },
    initWebSocket() {
      const token = localStorage.getItem('token')
      if (!token) {
        this.error = '未登录，无法连接聊天'
        return
      }
      socketService.initSocket(token)
    },
    setupSocketListeners() {
      const socket = socketService.getSocket()
      if (!socket) return

      // 连接成功时加入房间
      this.socketEventHandlers.connect = () => {
        console.log('WebSocket connected, joining room if activity exists')
        this.isSocketConnected = true
        if (this.currentActivity?.id) {
          socketService.joinActivityRoom(this.currentActivity.id)
        }
      }
      socket.on('connect', this.socketEventHandlers.connect)

      // 新消息
      this.socketEventHandlers.newMessage = (payload) => {
        if (String(payload.activity_id) === String(this.currentActivity?.id)) {
          this.messages.push(payload)
          this.scrollToBottom()
        } else {
          console.log('收到其他活动消息:', payload)
        }
      }
      socket.on('server_new_message', this.socketEventHandlers.newMessage)

      // 加入房间确认
      this.socketEventHandlers.joined = (data) => {
        console.log('已加入房间:', data)
      }
      socket.on('server_joined', this.socketEventHandlers.joined)

      // 离线消息
      this.socketEventHandlers.offlineMessage = (msg) => {
        if (String(msg.activity_id) === String(this.currentActivity?.id)) {
          this.messages.push(msg)
          this.scrollToBottom()
        } else {
          this.offlineMessages.push(msg)
        }
      }
      socket.on('server_offline_message', this.socketEventHandlers.offlineMessage)

      // 错误
      this.socketEventHandlers.error = (err) => {
        console.error('服务器错误:', err)
        if (err.reason === 'Not a member of this activity') {
          alert('您不是该活动成员，无法发送消息')
        }
      }
      socket.on('server_error', this.socketEventHandlers.error)

      // 被踢下线
      this.socketEventHandlers.kick = (data) => {
        alert(data.reason || '您在其他设备登录，将被强制下线')
        localStorage.removeItem('token')
        this.$router.push('/login')
      }
      socket.on('server_kick', this.socketEventHandlers.kick)
    },
    async refreshChat() {
      this.determineCurrentActivity()
      if (this.currentActivity) {
        // 如果已连接，立即加入；否则 connect 事件会处理
        const socket = socketService.getSocket()
        if (socket?.connected) {
          socketService.joinActivityRoom(this.currentActivity.id)
        }
        this.messages = []
        await this.loadHistoryMessages()
      }
      this.scrollToBottom()
    },
    async loadHistoryMessages() {
      // 加载离线消息（示例，可根据实际需求扩展）
      this.isLoading = false
      const offlineForThis = this.offlineMessages.filter(
        m => String(m.activity_id) === String(this.currentActivity?.id)
      )
      this.messages = [...offlineForThis]
      this.offlineMessages = this.offlineMessages.filter(
        m => String(m.activity_id) !== String(this.currentActivity?.id)
      )
    },
    sendMessage() {
      if (!this.newMessage.trim() || this.isSending) return
      if (!this.currentActivity) {
        alert('请先选择活动')
        return
      }

      const content = this.newMessage.trim()
      this.pendingMessage = content
      this.isSending = true

      try {
        socketService.sendChatMessage(this.currentActivity.id, content)
        this.newMessage = ''
      } catch (err) {
        console.error('发送失败:', err)
        alert('发送失败，请检查网络')
      } finally {
        this.isSending = false
        this.pendingMessage = ''
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp * 1000)
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    },
    getUserInitial(userId) {
      return userId ? String(userId).slice(-2) : '??'
    },
    goBack() {
      this.$router.push('/')
    },
    toggleMenu() {
      this.showMenu = !this.showMenu
    },
    goToQuit() {
      this.showMenu = false
      this.$router.push('/quit')
    },
    goToComplete() {
      this.showMenu = false
      this.$router.push('/complete')
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，与原有 ChatView.vue 相同 */
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
  position: relative;
}
.chat-header {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
}
.chat-header h3 {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
}
.back-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  margin-right: 16px;
}
.menu-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  margin-left: 16px;
}
.menu-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>');
  background-size: contain;
  background-repeat: no-repeat;
}
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}
.menu-popup {
  background-color: #ffffff;
  border-radius: 16px;
  width: 90%;
  max-width: 300px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}
.menu-item {
  width: 100%;
  padding: 16px;
  border: none;
  background: none;
  font-size: 16px;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s;
  border-bottom: 1px solid #f0f0f0;
}
.menu-item:hover {
  background-color: #f9f9f9;
}
.complete-item {
  color: #4CD964;
}
.quit-item {
  color: #FF3B30;
}
.cancel-item {
  border-bottom: none;
  background-color: #f5f5f5;
  color: #333333;
}
.cancel-item:hover {
  background-color: #e0e0e0;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 120px;
}
.message {
  display: flex;
  margin-bottom: 16px;
}
.message.own {
  flex-direction: row-reverse;
}
.message.system {
  justify-content: center;
}
.system-message {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  color: #666666;
  text-align: center;
  display: inline-block;
}
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin: 0 10px;
}
.message-content {
  max-width: 70%;
}
.message-bubble {
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.4;
}
.message:not(.own) .message-bubble {
  background: #ffffff;
  border-bottom-left-radius: 4px;
}
.message.own .message-bubble {
  background: #007aff;
  color: #ffffff;
  border-bottom-right-radius: 4px;
}
.message-time {
  font-size: 11px;
  color: #999999;
  margin-top: 4px;
  text-align: right;
}
.chat-input {
  display: flex;
  padding: 12px 16px;
  background: #ffffff;
  border-top: 1px solid #e0e0e0;
  position: fixed;
  bottom: 60px;
  left: 0;
  right: 0;
  z-index: 100;
}
.chat-input input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  margin-right: 10px;
}
.send-btn {
  padding: 10px 20px;
  background: #007aff;
  color: #ffffff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}
.send-btn:hover {
  background: #0066cc;
}
.send-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
}
.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}
.error button {
  margin-top: 10px;
  padding: 6px 12px;
  background: #007aff;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
}
</style>