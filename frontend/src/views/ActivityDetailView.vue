<template>
  <div class="activity-detail">
    <header class="header">
      <button @click="goBack" class="back-button">
        <i class="back-icon"></i>
      </button>
    </header>

    <main class="main-content">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading">
        <div class="loading-spinner"></div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon"></div>
        <p>{{ error }}</p>
        <button class="retry-button" @click="loadActivityDetail">重试</button>
      </div>

      <!-- 活动详情 -->
      <div v-else-if="activity" class="detail-content">
        <div class="activity-type">
          <span class="type-tag">
            {{ getActivityIcon(activity.category) }} {{ getActivityTypeName(activity.category) }}
          </span>
        </div>
        <h2 class="activity-title">{{ activity.title }}</h2>
        <p class="activity-description" v-html="activity.description ? activity.description.replace(/\n/g, '<br>') : ''"></p>

        <div class="activity-info">
          <div class="info-item">
            <span class="info-icon location"></span>
            <span>{{ activity.location_name || '未知地点' }}</span>
          </div>
          <div class="info-item">
            <span class="info-icon calendar"></span>
            <span>{{ formatDateTime(activity.start_time) }}</span>
          </div>
          <div class="info-item">
            <span class="info-icon users"></span>
            <span>当前{{ activity.current_participants || 0 }}人 / 目标{{ activity.max_participants || '不限' }}人</span>
          </div>
        </div>

        <div class="members-section" v-if="members.length > 0">
          <h3 class="section-title">已加入成员</h3>
          <div class="members-list">
            <div
              v-for="member in members"
              :key="member.id"
              class="member-item"
            >
              <div class="member-avatar">
                <i class="avatar-icon"></i>
              </div>
              <p class="member-name">{{ member.nickname || '用户' + member.id }}</p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div class="bottom-bar" v-if="!isLoading && !error">
      <button
        class="join-button"
        @click="joinActivity"
        :disabled="isJoining"
      >
        {{ isJoining ? '加入中...' : '一键加入' }}
      </button>
    </div>
  </div>
</template>

<script>
import { activitiesAPI } from '@/api'

export default {
  name: 'ActivityDetailView',
  data() {
    return {
      activity: null,
      members: [],        // 成员列表（后端可能需要单独接口，这里暂时用 activity.members 占位）
      isLoading: true,
      isJoining: false,
      error: null
    }
  },
  mounted() {
    this.loadActivityDetail()
  },
  methods: {
    goBack() {
      this.$router.push('/')
    },
    async loadActivityDetail() {
      this.isLoading = true
      this.error = null

      try {
        const id = this.$route.params.id
        const response = await activitiesAPI.getDetail(id)
        // 后端返回格式: { code: 200, data: {...} }
        if (response.code === 200) {
          this.activity = response.data
          // 如果后端返回的 activity 中包含 members 数组，则直接使用
          this.members = this.activity.members || []
          // 如果后端没有返回成员列表，可以另外调用接口获取（可选）
        } else {
          this.error = response.message || '加载失败'
        }
      } catch (err) {
        console.error('加载活动详情失败:', err)
        this.error = '加载失败，请重试'
      } finally {
        this.isLoading = false
      }
    },
    getActivityIcon(category) {
      const icons = {
        study: '📚',
        sports: '🏀',
        volunteer: '🤝',
        meal: '🍚',
        hobby: '🎨'
      }
      return icons[category] || '📋'
    },
    getActivityTypeName(category) {
      const names = {
        study: '学习',
        sports: '运动',
        volunteer: '志愿',
        meal: '约饭',
        hobby: '兴趣'
      }
      return names[category] || '其他'
    },
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '时间待定'
      const date = new Date(dateTimeStr)
      return date.toLocaleString()
    },
    async joinActivity() {
      if (this.isJoining) return

      this.isJoining = true

      const timeout = setTimeout(() => {
        this.isJoining = false
        alert('请求超时，请重试')
      }, 10000)

      try {
        // 调用真实 API 加入活动
        const response = await activitiesAPI.join(this.activity.id)
        clearTimeout(timeout)
        if (response.code === 200) {
          // 加入成功后，跳转到成功页面（不再操作 localStorage）
          this.$router.push({
            path: '/success',
            query: { type: 'join' }
          })
        } else {
          alert(response.message || '加入失败，请重试')
        }
      } catch (error) {
        clearTimeout(timeout)
        console.error('加入活动失败:', error)
        alert('加入失败，请重试')
      } finally {
        this.isJoining = false
      }
    }
  }
}
</script>

<style scoped>
/* 保持原有样式不变，省略以节省篇幅，实际使用时保留原有 ActivityDetailView.vue 的样式 */
.activity-detail {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background-color: #ffffff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  border-bottom: 1px solid #e0e0e0;
}

.back-button {
  background: none;
  border: none;
  font-size: 18px;
  color: #333333;
  cursor: pointer;
}

.back-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"></path></svg>');
  background-size: contain;
  background-repeat: no-repeat;
}

.main-content {
  flex: 1;
  padding-top: 80px;
  padding-bottom: 80px;
  padding-left: 24px;
  padding-right: 24px;
  overflow-y: auto;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 48px 0;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(72, 187, 120, 0.3);
  border-radius: 50%;
  border-top-color: #48bb78;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 0;
  color: #666666;
}

.error-icon {
  width: 48px;
  height: 48px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  margin-bottom: 16px;
}

.retry-button {
  margin-top: 16px;
  padding: 8px 16px;
  border-radius: 8px;
  background-color: #48bb78;
  color: #ffffff;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background-color: #38a169;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-type {
  margin-bottom: 8px;
}

.type-tag {
  padding: 4px 8px;
  border-radius: 12px;
  background-color: #e8f4f8;
  color: #333333;
  font-size: 12px;
  font-weight: 500;
}

.activity-title {
  font-size: 20px;
  font-weight: 600;
  color: #333333;
}

.activity-description {
  font-size: 14px;
  color: #666666;
  line-height: 1.5;
}

.activity-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333333;
}

.info-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
  color: #48bb78;
}

.info-icon.location {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>');
}

.info-icon.calendar {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>');
}

.info-icon.users {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>');
}

.members-section {
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 12px;
}

.members-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.member-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.member-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #e8f4f8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.avatar-icon {
  display: inline-block;
  width: 24px;
  height: 24px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  color: #48bb78;
}

.member-name {
  font-size: 12px;
  color: #666666;
}

.bottom-bar {
  position: fixed;
  bottom: 60px;
  left: 0;
  right: 0;
  background-color: #ffffff;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
  z-index: 9;
}

.join-button {
  width: 100%;
  padding: 12px;
  background-color: #48bb78;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.join-button:hover:not(:disabled) {
  background-color: #38a169;
}

.join-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}
</style>