<template>
  <div class="home-page">
    <!-- 顶部导航 -->
    <header class="header">
      <h1>搭个伙</h1>
      <div class="header-actions">
        <button class="search-btn" @click="goToSearch">
          <i class="search-icon"></i>
        </button>
        <button class="refresh-btn" @click="refreshActivities">
          <i class="refresh-icon"></i>
        </button>
        <button id="filter-btn" @click="toggleFilterPanel">
          <i class="filter-icon"></i>
        </button>
      </div>
    </header>

    <!-- 筛选面板（默认隐藏） -->
    <div id="filter-panel" class="filter-panel" :class="{ 'hidden': !showFilterPanel }">
      <div class="filter-buttons">
        <button
          v-for="type in filterTypes"
          :key="type.value"
          class="filter-button"
          :class="activeFilter === type.value ? 'active' : ''"
          @click="selectFilter(type.value)"
        >{{ type.label }}</button>
      </div>
    </div>

    <!-- 活动信息流 -->
    <main class="main-content" ref="mainContent"
          @scroll="handleScroll">
      <div class="activity-feed">
        <!-- 骨架屏 -->
        <div v-if="isLoading && currentPage === 1" class="skeleton-list">
          <div v-for="i in 3" :key="i" class="skeleton-card">
            <div class="skeleton-tag"></div>
            <div class="skeleton-title"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text short"></div>
            <div class="skeleton-footer">
              <div class="skeleton-info"></div>
              <div class="skeleton-time"></div>
            </div>
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <h3>加载失败</h3>
          <p>{{ error }}</p>
          <button class="retry-button" @click="loadActivities(true)">
            <span>重新加载</span>
          </button>
        </div>

        <!-- 空状态 -->
        <div v-else-if="activities.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>暂无活动</h3>
          <p>还没有人发布活动，快来发布第一个吧！</p>
          <button class="publish-button" @click="goToPublish">
            发布活动
          </button>
        </div>

        <!-- 活动卡片 -->
        <div v-else>
          <div
            v-for="activity in activities"
            :key="activity.id"
            class="activity-card"
            @click="goToActivityDetail(activity.id)"
          >
            <div class="activity-type">
              <span class="type-tag">
                {{ getActivityIcon(activity.category) }} {{ getActivityTypeName(activity.category) }}
              </span>
            </div>
            <h3 class="activity-title">{{ activity.title }}</h3>
            <p class="activity-description">{{ activity.description }}</p>
            <div class="activity-info">
              <div class="info-item">
                <span class="info-icon location"></span>
                {{ activity.location_name || '未知地点' }}
              </div>
              <div class="info-item">
                <span class="info-icon users"></span>
                {{ activity.current_participants || 0 }}/{{ activity.max_participants || '不限' }}人
              </div>
              <div v-if="activity.creator?.credit_score >= 90" class="info-item high-credit">
                <span class="info-icon check"></span> 高信用
              </div>
            </div>
            <div class="activity-time">{{ formatTime(activity.created_at) }}</div>

            <!-- ✅ 修复：区分发布者和参与者 -->
            <div class="card-actions">
              <!-- 自己发布的活动：显示"我发布的" -->
              <button
                v-if="activity.creator_id === currentUserId"
                class="action-btn published"
                disabled
              >
                我发布的
              </button>

              <!-- 别人的活动：显示"一键加入" -->
              <button
                v-else-if="activity.status === 1"
                class="action-btn join"
                @click.stop="joinActivity(activity.id)"
              >
                一键加入
              </button>
            </div>
          </div>

          <!-- 加载更多指示器 -->
          <div v-if="isLoading && currentPage > 1" class="loading-more">
            <div class="loading-spinner small"></div>
            <span>加载更多...</span>
          </div>

          <!-- 没有更多数据 -->
          <div v-if="!hasMoreData && activities.length > 0" class="no-more">
            <div class="no-more-line"></div>
            <span>已经到底了</span>
            <div class="no-more-line"></div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { activitiesAPI, userAPI } from '@/api'

export default {
  name: 'HomeView',
  data() {
    return {
      activities: [],
      currentPage: 1,
      pageSize: 10,
      isLoading: false,
      hasMoreData: true,
      error: null,
      showFilterPanel: false,
      activeFilter: '',
      filterTypes: [
        { label: '全部', value: '' },
        { label: '学习', value: 'study' },
        { label: '运动', value: 'sports' },
        { label: '志愿', value: 'volunteer' },
        { label: '约饭', value: 'meal' },
        { label: '兴趣', value: 'hobby' }
      ],
      currentUserId: null  // ✅ 新增：当前用户ID
    }
  },
  async mounted() {
    await this.loadCurrentUser()  // ✅ 新增：加载当前用户信息
    this.loadActivities()
  },
  methods: {
    // ✅ 新增：获取当前用户信息
    async loadCurrentUser() {
      try {
        const response = await userAPI.getProfile()
        if (response.code === 200 && response.data && response.data.user) {
          this.currentUserId = response.data.user.id
        }
      } catch (err) {
        console.error('获取用户信息失败:', err)
      }
    },
    async loadActivities(isRefresh = false) {
      if (isRefresh) {
        this.currentPage = 1
        this.hasMoreData = true
        this.activities = []
        this.error = null
      }

      if (this.isLoading || !this.hasMoreData) return

      this.isLoading = true

      try {
        const params = {
          page: this.currentPage,
          per_page: this.pageSize,
          category: this.activeFilter || undefined
        }

        const response = await activitiesAPI.getList(params)
        const data = response.data || response
        const activities = data.activities || []
        const total = data.total || 0

        if (activities.length > 0) {
          this.activities = [...this.activities, ...activities]
          this.currentPage++

          if (this.activities.length >= total) {
            this.hasMoreData = false
          }
        } else {
          this.hasMoreData = false
        }
      } catch (err) {
        console.error('加载活动列表失败:', err)
        this.error = '加载失败，请重试'
      } finally {
        this.isLoading = false
      }
    },
    async joinActivity(activityId) {
      try {
        const response = await activitiesAPI.join(activityId)
        if (response.code === 200) {
          alert('加入成功！')
          this.loadActivities(true)  // 刷新列表
        } else {
          alert(response.message || '加入失败')
        }
      } catch (err) {
        console.error('加入活动失败:', err)
        alert('加入失败，请重试')
      }
    },
    refreshActivities() {
      this.loadActivities(true)
    },
    handleScroll() {
      const element = this.$refs.mainContent
      if (!element) return

      const scrollTop = element.scrollTop
      const scrollHeight = element.scrollHeight
      const clientHeight = element.clientHeight

      if (scrollTop + clientHeight >= scrollHeight - 100) {
        if (!this.isLoading && this.hasMoreData) {
          this.loadActivities()
        }
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
    formatTime(timeString) {
      if (!timeString) return ''
      const now = new Date()
      const time = new Date(timeString)
      const diffMs = now - time
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

      if (diffHours < 1) {
        return '刚刚'
      } else if (diffHours < 24) {
        return `${diffHours}小时前`
      } else if (diffDays < 7) {
        return `${diffDays}天前`
      } else {
        return time.toLocaleDateString('zh-CN')
      }
    },
    toggleFilterPanel() {
      this.showFilterPanel = !this.showFilterPanel
    },
    selectFilter(type) {
      this.activeFilter = type
      this.showFilterPanel = false
      this.loadActivities(true)
    },
    goToActivityDetail(id) {
      this.$router.push(`/activity/${id}`)
    },
    goToPublish() {
      this.$router.push('/publish')
    },
    goToProfile() {
      this.$router.push('/profile')
    },
    goToSearch() {
      this.$router.push('/search')
    }
  }
}
</script>

<style scoped>
/* 保持原有样式不变 */
.home-page {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
  overflow: hidden;
}

.header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background-color: #ffffff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.header h1 {
  font-size: 20px;
  font-weight: bold;
  color: #333333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
}

.search-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  color: #666666;
}

.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
}

.refresh-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6"></path><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  color: #666666;
  transition: transform 0.3s ease;
}

.refresh-btn:hover .refresh-icon {
  transform: rotate(180deg);
}

#filter-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #666666;
  cursor: pointer;
}

.filter-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>');
  background-size: contain;
  background-repeat: no-repeat;
}

.filter-panel {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  background-color: #ffffff;
  padding: 16px 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 9;
  transition: transform 0.3s ease;
}

.filter-panel.hidden {
  transform: translateY(-100%);
  pointer-events: none;
}

.filter-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-button {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background-color: #ffffff;
  color: #666666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-button:hover {
  background-color: #f5f5f5;
}

.filter-button.active {
  background-color: #007aff;
  color: #ffffff;
  border-color: #007aff;
}

.main-content {
  flex: 1;
  margin-top: 64px;
  padding-bottom: 80px;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.activity-feed {
  padding: 16px;
}

/* 骨架屏样式 */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.skeleton-tag {
  width: 60px;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}

.skeleton-title {
  width: 80%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}

.skeleton-text {
  width: 100%;
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
}

.skeleton-info {
  width: 120px;
  height: 12px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-time {
  width: 60px;
  height: 12px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 错误状态样式 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-state h3 {
  font-size: 18px;
  color: #333333;
  margin-bottom: 8px;
}

.error-state p {
  font-size: 14px;
  color: #666666;
  margin-bottom: 24px;
}

.retry-button {
  padding: 12px 32px;
  background-color: #007aff;
  color: #ffffff;
  border: none;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-button:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}

/* 空状态样式 */
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

.publish-button {
  padding: 12px 32px;
  background-color: #007aff;
  color: #ffffff;
  border: none;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.publish-button:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}

/* 活动卡片样式 */
.activity-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}

.activity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.activity-card:active {
  transform: scale(0.98);
}

.activity-type {
  margin-bottom: 8px;
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

.activity-title {
  font-size: 16px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.activity-description {
  font-size: 14px;
  color: #666666;
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.activity-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666666;
}

.info-item.high-credit {
  color: #007aff;
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

.info-icon.check {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>');
}

.activity-time {
  font-size: 12px;
  color: #999999;
  text-align: right;
}

/* 卡片操作按钮样式 */
.card-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.published {
  background-color: #e8f5e9;
  color: #388e3c;
  cursor: default;
}

.action-btn.join {
  background-color: #007aff;
  color: #ffffff;
}

.action-btn.join:hover {
  background-color: #0056b3;
}

/* 加载更多样式 */
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 0;
  color: #666666;
  font-size: 14px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 122, 255, 0.3);
  border-radius: 50%;
  border-top-color: #007aff;
  animation: spin 1s ease-in-out infinite;
}

.loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 没有更多数据样式 */
.no-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 0;
  color: #999999;
  font-size: 14px;
}

.no-more-line {
  flex: 1;
  height: 1px;
  background-color: #e0e0e0;
}
</style>