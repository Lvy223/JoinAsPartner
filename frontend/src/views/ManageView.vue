<template>
  <div class="manage-page">
    <header class="manage-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>活动管理</h1>
      <div style="width: 40px;"></div>
    </header>

    <div class="tab-switcher">
      <button
        class="tab-btn"
        :class="{ 'active': activeTab === 'published' }"
        @click="switchTab('published')"
      >我发布的</button>
      <button
        class="tab-btn"
        :class="{ 'active': activeTab === 'joined' }"
        @click="switchTab('joined')"
      >我参与的</button>
    </div>

    <main class="manage-content">
      <div v-if="isLoading" class="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <div v-else-if="activities.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>暂无活动</h3>
        <p v-if="activeTab === 'published'">你还没有发布过活动</p>
        <p v-else>你还没有参与过活动</p>
        <button v-if="activeTab === 'published'" class="action-btn" @click="goToPublish">
          发布活动
        </button>
      </div>

      <div v-else class="activity-list">
        <div
          v-for="activity in activities"
          :key="activity.id"
          class="activity-card"
        >
          <div class="card-header">
            <span class="type-tag">
              {{ getActivityIcon(activity.category) }} {{ getActivityTypeName(activity.category) }}
            </span>
            <span class="status-tag" :class="getStatusClass(activity.status)">
              {{ getStatusText(activity.status) }}
            </span>
          </div>

          <h3 class="activity-title" @click="goToActivityDetail(activity.id)">
            {{ activity.title }}
          </h3>

          <div class="activity-info">
            <div class="info-item">
              <span class="info-icon location"></span>
              {{ activity.location_name || '未知地点' }}
            </div>
            <div class="info-item">
              <span class="info-icon users"></span>
              {{ activity.current_participants }}/{{ activity.max_participants || '不限' }}人
            </div>
            <div class="info-item">
              <span class="info-icon time"></span>
              {{ formatTime(activity.start_time) }}
            </div>
          </div>

          <div class="card-actions">
            <button
              v-if="activeTab === 'published'"
              class="action-btn edit"
              @click="editActivity(activity.id)"
            >编辑</button>
            <button
              v-if="activeTab === 'published'"
              class="action-btn manage"
              @click="manageMembers(activity.id)"
            >管理成员</button>
            <button
              v-if="activeTab === 'joined'"
              class="action-btn chat"
              @click="goToChat(activity.id)"
            >进入群聊</button>
            <button
              class="action-btn danger"
              @click="handleAction(activity)"
            >
              {{ activeTab === 'published' ? '解散活动' : '退出活动' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { activitiesAPI, userAPI } from '@/api'

export default {
  name: 'ManageView',
  data() {
    return {
      activeTab: 'published',
      activities: [],
      isLoading: false
    }
  },
  mounted() {
    this.loadActivities()
  },
  methods: {
    async loadActivities() {
      this.isLoading = true
      try {
        if (this.activeTab === 'published') {
          // 调用后端接口获取用户发布的活动
          const response = await userAPI.getCreatedActivities()
          if (response.code === 200) {
            this.activities = response.data || []
          } else {
            this.activities = []
          }
        } else {
          // 调用后端接口获取用户参与的活动
          const response = await userAPI.getMyActivities()
          if (response.code === 200) {
            this.activities = response.data || []
          } else {
            this.activities = []
          }
        }
      } catch (error) {
        console.error('加载活动失败:', error)
        this.activities = []
      } finally {
        this.isLoading = false
      }
    },
    switchTab(tab) {
      this.activeTab = tab
      this.loadActivities()
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
    getStatusClass(status) {
      const map = {
        0: 'preparing',
        1: 'active',
        2: 'active',
        3: 'ended',
        4: 'cancelled'
      }
      return map[status] || 'active'
    },
    getStatusText(status) {
      const texts = {
        0: '筹备中',
        1: '报名中',
        2: '进行中',
        3: '已结束',
        4: '已取消'
      }
      return texts[status] || '进行中'
    },
    formatTime(timeStr) {
      if (!timeStr) return '时间待定'
      const date = new Date(timeStr)
      return date.toLocaleString()
    },
    goToActivityDetail(id) {
      this.$router.push(`/activity/${id}`)
    },
    editActivity(id) {
      alert('编辑活动功能开发中...')
    },
    manageMembers(id) {
      alert('成员管理功能开发中...')
    },
    goToChat(activityId) {
      // 设置当前活动ID，然后跳转到聊天页面
      localStorage.setItem('currentActivityId', activityId)
      this.$router.push('/chat')
    },
    async handleAction(activity) {
      if (this.activeTab === 'published') {
        if (confirm('确定要解散这个活动吗？解散后无法恢复。')) {
          await this.disbandActivity(activity.id)
        }
      } else {
        if (confirm('确定要退出这个活动吗？退出后将无法参与聊天。')) {
          await this.quitActivity(activity.id)
        }
      }
    },
    async disbandActivity(id) {
      try {
        // 调用后端取消活动接口（仅创建者可用）
        const response = await activitiesAPI.cancel(id)
        if (response.code === 200) {
          alert('活动已解散')
          this.loadActivities()
        } else {
          alert(response.message || '解散失败')
        }
      } catch (error) {
        console.error('解散活动失败:', error)
        alert('解散失败，请重试')
      }
    },
    async quitActivity(id) {
      try {
        // 调用后端退出活动接口（需要后端补充 POST /api/activities/<id>/quit）
        // 暂时使用加入接口的反向，但需要后端支持。这里假设已有 quit 接口。
        const response = await activitiesAPI.quit(id)
        if (response.code === 200) {
          alert('已退出活动')
          this.loadActivities()
        } else {
          alert(response.message || '退出失败')
        }
      } catch (error) {
        console.error('退出活动失败:', error)
        alert('退出失败，请重试')
      }
    },
    goToPublish() {
      this.$router.push('/publish')
    },
    goBack() {
      this.$router.back()
    }
  }
}
</script>

<style scoped>
/* 保持原有样式不变 */
.manage-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.manage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.manage-header h1 {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
}
.back-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #333333;
  cursor: pointer;
}
.tab-switcher {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
}
.tab-btn {
  flex: 1;
  padding: 10px;
  background-color: #f5f5f5;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  color: #666666;
  cursor: pointer;
  transition: all 0.3s ease;
}
.tab-btn.active {
  background-color: #007aff;
  color: #ffffff;
}
.manage-content {
  padding: 16px;
}
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 0;
  gap: 12px;
}
.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 122, 255, 0.3);
  border-radius: 50%;
  border-top-color: #007aff;
  animation: spin 1s ease-in-out infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
}
.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}
.empty-state h3 {
  font-size: 18px;
  color: #333333;
  margin-bottom: 8px;
}
.empty-state p {
  font-size: 14px;
  color: #666666;
  margin-bottom: 24px;
}
.action-btn {
  padding: 12px 32px;
  background-color: #007aff;
  color: #ffffff;
  border: none;
  border-radius: 24px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.action-btn:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.activity-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.type-tag {
  display: inline-block;
  padding: 4px 8px;
  background-color: #e8f4f8;
  color: #333333;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.status-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.status-tag.preparing {
  background-color: #fff3e0;
  color: #ff9800;
}
.status-tag.active {
  background-color: #e8f5e9;
  color: #4caf50;
}
.status-tag.ended {
  background-color: #f5f5f5;
  color: #999999;
}
.status-tag.cancelled {
  background-color: #ffebee;
  color: #f44336;
}
.activity-title {
  font-size: 16px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 12px;
  cursor: pointer;
}
.activity-title:hover {
  color: #007aff;
}
.activity-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666666;
}
.info-icon {
  display: inline-block;
  width: 14px;
  height: 14px;
  background-size: contain;
  background-repeat: no-repeat;
}
.info-icon.location {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>');
}
.info-icon.users {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>');
}
.info-icon.time {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>');
}
.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.card-actions .action-btn {
  flex: 1;
  min-width: 80px;
  padding: 8px 12px;
  font-size: 12px;
}
.card-actions .action-btn.edit {
  background-color: #e3f2fd;
  color: #1976d2;
}
.card-actions .action-btn.manage {
  background-color: #f3e5f5;
  color: #7b1fa2;
}
.card-actions .action-btn.chat {
  background-color: #e8f5e9;
  color: #388e3c;
}
.card-actions .action-btn.danger {
  background-color: #ffebee;
  color: #d32f2f;
}
.card-actions .action-btn:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}
</style>