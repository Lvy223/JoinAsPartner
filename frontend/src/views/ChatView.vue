<template>
  <div class="chat-page">
    <!-- 顶部导航 -->
    <div class="chat-header">
      <button class="back-btn" @click="goBack">←</button>
      <div class="header-center" @click="toggleActivityMenu">
        <h3>{{ currentActivity ? currentActivity.title : '队伍聊天' }}</h3>
        <span v-if="myActivities.length > 1" class="dropdown-arrow">▼</span>
      </div>
      <button class="menu-btn" @click="toggleMenu">
        <i class="menu-icon"></i>
      </button>

      <!-- 活动切换菜单 -->
      <div v-if="showActivityMenu" class="activity-switch-overlay" @click="showActivityMenu = false">
        <div class="activity-switch-popup" @click.stop>
          <div
            v-for="act in myActivities"
            :key="act.id"
            class="activity-option"
            :class="{ active: currentActivity?.id === act.id }"
            @click="switchActivity(act)"
          >
            {{ act.title }}
            <span v-if="currentActivity?.id === act.id">✓</span>
          </div>
        </div>
      </div>
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
          :class="{ own: Number(msg.user_id) === Number(currentUserId) }"
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
import { userAPI, activitiesAPI } from '@/api'
import socketService from '@/utils/socket'

export default {
  name: 'ChatView',
  data() {
    return {
      currentActivity: null,
      myActivities: [],
      currentUserId: null,
      messages: [],
      newMessage: '',
      pendingMessage: '',
      isSending: false,
      isLoading: false,
      error: null,
      showMenu: false,
      showActivityMenu: false,
      offlineMessages: [],
      isSocketConnected: false,
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
    this.$eventBus?.$on('activity-updated', this.handleActivityUpdated)
  },
  beforeUnmount() {
    const socket = socketService.getSocket()
    if (socket) {
      Object.values(this.socketEventHandlers).forEach(handler => {
        if (handler) socket.off(handler)
      })
    }
    if (this.currentActivity) {
      socketService.leaveActivityRoom(this.currentActivity.id)
    }
    this.$eventBus?.$off('activity-updated', this.handleActivityUpdated)
  },
  methods: {
    handleActivityUpdated() {
      console.log('检测到活动更新，正在刷新聊天列表...')
      this.loadMyActivities()
    },
    async loadCurrentUser() {
      try {
        const res = await userAPI.getProfile()
        if (res.code === 200 && res.data && res.data.user) {
          this.currentUserId = res.data.user.id
        }
      } catch (err) {
        console.error('获取用户信息失败:', err)
      }
    },
    async loadMyActivities() {
      this.isLoading = true
      this.error = null
      try {
        if (!this.currentUserId) {
          await this.loadCurrentUser()
        }
        if (!this.currentUserId) {
          this.error = '无法获取用户身份'
          return
        }

        const listRes = await activitiesAPI.getList({ page: 1, per_page: 100 })
        const allActivities = listRes?.data?.activities || listRes?.activities || []

        const relatedActs = allActivities.filter(act => {
          if (act.creator_id === this.currentUserId) return true
          if (act.participants && Array.isArray(act.participants)) {
            return act.participants.some(p => p.user_id === this.currentUserId)
          }
          if (act.role === 1 || act.role === 3) return true
          return false
        })

        this.myActivities = relatedActs.map(item => ({
          id: item.id,
          title: item.title,
          creator_id: item.creator_id,
          role: item.role || (item.creator_id === this.currentUserId ? 3 : 1)
        }))
      } catch (err) {
        console.error('加载活动列表失败:', err)
        this.error = '加载活动列表失败'
      } finally {
        this.isLoading = false
        this.determineCurrentActivity()
      }
    },
    determineCurrentActivity() {
      const routeId = this.$route.query.activityId
      let activityId = routeId || localStorage.getItem('currentActivityId')

      if (activityId && this.myActivities.length) {
        this.currentActivity = this.myActivities.find(a => String(a.id) === String(activityId))
      }

      if (!this.currentActivity && this.myActivities.length) {
        this.currentActivity = this.myActivities[0]
      }

      if (this.currentActivity) {
        localStorage.setItem('currentActivityId', this.currentActivity.id)
        const socket = socketService.getSocket()
        if (socket?.connected) {
          socketService.joinActivityRoom(this.currentActivity.id)
        }
      } else {
        this.error = '您还没有参与任何活动，请先加入或创建一个活动'
      }
    },
    toggleActivityMenu() {
      if (this.myActivities.length > 1) {
        this.showActivityMenu = !this.showActivityMenu
      }
    },
    switchActivity(activity) {
      if (this.currentActivity?.id !== activity.id) {
        // 离开旧房间
        if (this.currentActivity) {
          socketService.leaveActivityRoom(this.currentActivity.id)
        }
        // 切换活动
        this.currentActivity = activity
        this.messages = []
        localStorage.setItem('currentActivityId', activity.id)
        // 加入新房间
        const socket = socketService.getSocket()
        if (socket?.connected) {
          socketService.joinActivityRoom(activity.id)
        }
      }
      this.showActivityMenu = false
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

      this.socketEventHandlers.connect = () => {
        this.isSocketConnected = true
        if (this.currentActivity?.id) {
          socketService.joinActivityRoom(this.currentActivity.id)
        }
      }
      socket.on('connect', this.socketEventHandlers.connect)

      this.socketEventHandlers.newMessage = (payload) => {
        if (String(payload.activity_id) === String(this.currentActivity?.id)) {
          this.messages.push(payload)
          this.scrollToBottom()
        }
      }
      socket.on('server_new_message', this.socketEventHandlers.newMessage)

      this.socketEventHandlers.joined = (data) => {
        console.log('已加入房间:', data)
      }
      socket.on('server_joined', this.socketEventHandlers.joined)

      this.socketEventHandlers.offlineMessage = (msg) => {
        if (String(msg.activity_id) === String(this.currentActivity?.id)) {
          this.messages.push(msg)
          this.scrollToBottom()
        } else {
          this.offlineMessages.push(msg)
        }
      }
      socket.on('server_offline_message', this.socketEventHandlers.offlineMessage)

      this.socketEventHandlers.error = (err) => {
        console.error('服务器错误:', err)
        if (err.reason === 'Not a member of this activity') {
          alert('您不是该活动成员，无法发送消息')
        }
      }
      socket.on('server_error', this.socketEventHandlers.error)

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
  position: relative;
}
.header-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  gap: 4px;
}
.header-center h3 {
  font-size: 18px;
  font-weight: 600;
}
.dropdown-arrow {
  font-size: 12px;
  color: #999;
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

/* 活动切换弹出 */
.activity-switch-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.3);
  z-index: 200;
  display: flex;
  justify-content: center;
  padding-top: 60px;
}
.activity-switch-popup {
  background: white;
  border-radius: 12px;
  width: 80%;
  max-width: 300px;
  max-height: 300px;
  overflow-y: auto;
  align-self: flex-start;
}
.activity-option {
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.activity-option:hover { background: #f5f5f5; }
.activity-option.active { color: #007aff; font-weight: 600; }

/* 菜单 */
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

/* 聊天消息 */
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
  flex-shrink: 0;
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

/* 输入区 */
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