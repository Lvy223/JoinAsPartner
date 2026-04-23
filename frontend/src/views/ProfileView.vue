<template>
  <div class="profile-page">
    <header class="header">
      <h1>我的</h1>
    </header>

    <main class="main-content">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading">
        <span>加载中...</span>
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="error">
        <span>{{ error }}</span>
        <button @click="loadUserInfo">重试</button>
      </div>

      <!-- 个人信息 -->
      <div v-else>
        <div class="user-info">
          <div class="avatar">
            <img v-if="userInfo.avatar" :src="userInfo.avatar" :alt="userInfo.nickname" class="avatar-img">
            <i v-else class="avatar-icon"></i>
          </div>
          <div class="user-details">
            <h2>{{ userInfo.nickname || userInfo.username || '用户' }}</h2>
            <p class="bio">{{ userInfo.bio || '暂无简介' }}</p>
          </div>
        </div>

        <!-- 我的活动 -->
        <div class="section">
          <h3 class="section-title">我的活动</h3>
          <div class="activity-stats">
            <div class="stat-card">
              <p class="stat-number">{{ userInfo.stats?.participated_count || 0 }}</p>
              <p class="stat-label">已参与</p>
            </div>
            <div class="stat-card">
              <p class="stat-number">{{ userInfo.stats?.created_count || 0 }}</p>
              <p class="stat-label">已发布</p>
            </div>
            <div class="stat-card">
              <p class="stat-number">{{ userInfo.credit_score || 100 }}</p>
              <p class="stat-label">信用分</p>
            </div>
          </div>
        </div>

        <!-- 兴趣标签（从 userInfo.interests 读取） -->
        <div class="section">
          <h3 class="section-title">兴趣标签</h3>
          <div class="interest-tags">
            <span
              v-for="(interest, index) in (userInfo.interests || [])"
              :key="index"
              class="interest-tag"
            >{{ interest }}</span>
            <span class="add-tag" @click="goToSettings">+ 编辑</span>
          </div>
        </div>

        <!-- 加入时间 -->
        <div class="section">
          <h3 class="section-title">账号信息</h3>
          <div class="account-info">
            <p>加入时间：{{ formatDate(userInfo.created_at) }}</p>
            <p>用户名：{{ userInfo.username }}</p>
          </div>
        </div>

        <!-- 设置选项 -->
        <div class="section">
          <h3 class="section-title">设置</h3>
          <div class="settings">
            <button class="setting-item" @click="goToSettings">
              <span>个人设置</span>
              <i class="chevron-icon"></i>
            </button>
            <button class="setting-item" @click="goToManage">
              <span>活动管理</span>
              <i class="chevron-icon"></i>
            </button>
            <button class="setting-item login-btn" @click="goToLogin">
              <span>登录</span>
              <i class="chevron-icon"></i>
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { userAPI } from '@/api'

export default {
  name: 'ProfileView',
  data() {
    return {
      userInfo: {
        stats: {}      // 统计数据占位
      },
      isLoading: false,
      error: null
    }
  },
  mounted() {
    this.loadUserInfo()
  },
  methods: {
    async loadUserInfo() {
      this.isLoading = true
      this.error = null

      try {
        const response = await userAPI.getProfile()
        // 后端返回格式: { code: 200, data: { user: {...}, stats: {...} } }
        if (response.code === 200 && response.data) {
          this.userInfo = {
            ...response.data.user,
            stats: response.data.stats || {}
          }
        } else {
          this.error = response.message || '加载失败'
        }
      } catch (err) {
        console.error('加载用户信息失败:', err)
        this.error = '加载用户信息失败，请重试'
      } finally {
        this.isLoading = false
      }
    },
    formatDate(dateString) {
      if (!dateString) return '未知'
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    goToSettings() {
      this.$router.push('/settings')
    },
    goToManage() {
      this.$router.push('/manage')
    },
    goToLogin() {
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
/* 保持原有样式，与之前相同，仅微调 */
.profile-page {
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

.header h1 {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
}

.main-content {
  flex: 1;
  padding-top: 80px;
  padding-bottom: 80px;
  overflow-y: auto;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 24px;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #e8f4f8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.avatar-icon {
  display: inline-block;
  width: 32px;
  height: 32px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  color: #48bb78;
}

.user-details h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 4px;
}

.bio {
  font-size: 14px;
  color: #666666;
}

.section {
  padding: 16px 24px;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 16px;
}

.activity-stats {
  display: flex;
  gap: 16px;
}

.stat-card {
  flex: 1;
  background-color: #e8f4f8;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stat-number {
  font-size: 20px;
  font-weight: 600;
  color: #48bb78;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666666;
}

.interest-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.interest-tag {
  padding: 4px 12px;
  border-radius: 16px;
  background-color: #e8f4f8;
  color: #333333;
  font-size: 14px;
}

.add-tag {
  padding: 4px 12px;
  border-radius: 16px;
  background-color: #f0f0f0;
  color: #007aff;
  font-size: 14px;
  cursor: pointer;
}

.add-tag:hover {
  background-color: #e0e0e0;
}

.account-info {
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.account-info p {
  font-size: 14px;
  color: #333333;
  margin: 0 0 4px 0;
}

.settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.setting-item {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  color: #333333;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.setting-item:hover {
  background-color: #f0f0f0;
}

.setting-item.login-btn {
  background-color: #007aff;
  color: #ffffff;
}

.setting-item.login-btn:hover {
  background-color: #0056b3;
}

.chevron-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  color: #999999;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  color: #666666;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: #ff3b30;
}

.error button {
  margin-top: 12px;
  padding: 8px 16px;
  background: #007aff;
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
}

.avatar-img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}
</style>