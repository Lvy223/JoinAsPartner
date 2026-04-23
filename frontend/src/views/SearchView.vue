<template>
  <div class="search-page">
    <!-- 搜索头部 -->
    <header class="search-header">
      <button class="back-btn" @click="goBack">←</button>
      <div class="search-input-wrapper">
        <input
          type="text"
          v-model="keyword"
          placeholder="搜索活动、地点、标签..."
          @keyup.enter="handleSearch"
          ref="searchInput"
        >
        <button v-if="keyword" class="clear-btn" @click="clearKeyword">✕</button>
      </div>
      <button class="search-btn" @click="handleSearch">搜索</button>
    </header>

    <!-- 搜索内容 -->
    <main class="search-content">
      <!-- 搜索历史 -->
      <div v-if="!hasSearched && searchHistory.length > 0" class="search-history">
        <div class="section-header">
          <h3>搜索历史</h3>
          <button class="clear-history" @click="clearHistory">清空</button>
        </div>
        <div class="history-tags">
          <button
            v-for="(item, index) in searchHistory"
            :key="index"
            class="history-tag"
            @click="searchFromHistory(item)"
          >{{ item }}</button>
        </div>
      </div>

      <!-- 热门搜索 -->
      <div v-if="!hasSearched" class="hot-search">
        <div class="section-header">
          <h3>热门搜索</h3>
        </div>
        <div class="hot-tags">
          <button
            v-for="(item, index) in hotSearches"
            :key="index"
            class="hot-tag"
            :class="{ 'top': index < 3 }"
            @click="searchFromHistory(item)"
          >
            <span class="rank">{{ index + 1 }}</span>
            <span class="text">{{ item }}</span>
          </button>
        </div>
      </div>

      <!-- 搜索结果 -->
      <div v-if="hasSearched" class="search-results">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading">
          <div class="loading-spinner"></div>
          <span>搜索中...</span>
        </div>

        <!-- 无结果 -->
        <div v-else-if="results.length === 0" class="no-result">
          <div class="no-result-icon">🔍</div>
          <h3>未找到相关活动</h3>
          <p>换个关键词试试吧</p>
        </div>

        <!-- 结果列表 -->
        <div v-else>
          <div class="result-count">找到 {{ totalCount }} 个相关活动</div>
          <div
            v-for="activity in results"
            :key="activity.id"
            class="result-card"
            @click="goToActivityDetail(activity.id)"
          >
            <div class="activity-type">
              <span class="type-tag">
                {{ getActivityIcon(activity.category) }} {{ getActivityTypeName(activity.category) }}
              </span>
            </div>
            <h3 class="activity-title" v-html="highlightKeyword(activity.title)"></h3>
            <p class="activity-description">{{ activity.description }}</p>
            <div class="activity-info">
              <div class="info-item">
                <span class="info-icon location"></span>
                <span v-html="highlightKeyword(activity.location_name || '未知地点')"></span>
              </div>
              <div class="info-item">
                <span class="info-icon users"></span>
                {{ activity.current_participants || 0 }}/{{ activity.max_participants || '不限' }}人
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { activitiesAPI } from '@/api'

export default {
  name: 'SearchView',
  data() {
    return {
      keyword: '',
      hasSearched: false,
      isLoading: false,
      results: [],
      totalCount: 0,
      searchHistory: [],
      hotSearches: [
        '考研',
        '篮球',
        '图书馆',
        '自习',
        '跑步',
        '志愿服务',
        '周末活动',
        '学习小组'
      ]
    }
  },
  mounted() {
    this.loadSearchHistory()
    this.$refs.searchInput.focus()
  },
  methods: {
    loadSearchHistory() {
      const history = localStorage.getItem('searchHistory')
      if (history) {
        this.searchHistory = JSON.parse(history)
      }
    },
    saveSearchHistory(keyword) {
      const history = this.searchHistory.filter(item => item !== keyword)
      history.unshift(keyword)
      this.searchHistory = history.slice(0, 10)
      localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
    },
    clearHistory() {
      this.searchHistory = []
      localStorage.removeItem('searchHistory')
    },
    clearKeyword() {
      this.keyword = ''
      this.hasSearched = false
      this.results = []
      this.$refs.searchInput.focus()
    },
    async handleSearch() {
      if (!this.keyword.trim()) {
        return
      }

      this.hasSearched = true
      this.isLoading = true
      this.saveSearchHistory(this.keyword)

      try {
        const response = await activitiesAPI.search(this.keyword)
        // 后端返回格式: { code: 200, data: { activities: [...], total, ... } }
        const data = response.data || response
        this.results = data.activities || []
        this.totalCount = data.total || this.results.length
      } catch (error) {
        console.error('搜索失败:', error)
        this.results = []
        this.totalCount = 0
      } finally {
        this.isLoading = false
      }
    },
    searchFromHistory(keyword) {
      this.keyword = keyword
      this.handleSearch()
    },
    highlightKeyword(text) {
      if (!this.keyword || !text) return text
      const regex = new RegExp(`(${this.keyword})`, 'gi')
      return text.replace(regex, '<span class="highlight">$1</span>')
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
    goToActivityDetail(id) {
      this.$router.push(`/activity/${id}`)
    },
    goBack() {
      this.$router.back()
    }
  }
}
</script>

<style scoped>
/* 原有样式保持不变 */
.search-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.search-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #333333;
  cursor: pointer;
  padding: 4px;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
}

.search-input-wrapper input {
  width: 100%;
  padding: 10px 36px 10px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  background-color: #f5f5f5;
}

.search-input-wrapper input:focus {
  border-color: #007aff;
  background-color: #ffffff;
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 16px;
  color: #999999;
  cursor: pointer;
}

.search-btn {
  background-color: #007aff;
  color: #ffffff;
  border: none;
  padding: 10px 16px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-btn:hover {
  background-color: #0056b3;
}

.search-content {
  padding: 16px;
}

.search-history,
.hot-search {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333333;
}

.clear-history {
  background: none;
  border: none;
  font-size: 14px;
  color: #999999;
  cursor: pointer;
}

.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-tag {
  padding: 6px 12px;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 14px;
  color: #666666;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-tag:hover {
  background-color: #e8f4f8;
  border-color: #007aff;
  color: #007aff;
}

.hot-tags {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hot-tag {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #ffffff;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.hot-tag:hover {
  background-color: #f5f5f5;
}

.hot-tag .rank {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #999999;
}

.hot-tag.top .rank {
  background-color: #ff3b30;
  color: #ffffff;
}

.hot-tag .text {
  font-size: 14px;
  color: #333333;
}

.search-results {
  background-color: #ffffff;
  border-radius: 12px;
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
  to {
    transform: rotate(360deg);
  }
}

.no-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 0;
}

.no-result-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.no-result h3 {
  font-size: 18px;
  color: #333333;
  margin-bottom: 8px;
}

.no-result p {
  font-size: 14px;
  color: #666666;
}

.result-count {
  font-size: 14px;
  color: #666666;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.result-card {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.result-card:last-child {
  border-bottom: none;
}

.result-card:hover {
  background-color: #f9f9f9;
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

.activity-title :deep(.highlight) {
  color: #ff3b30;
  font-weight: 600;
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
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666666;
}

.info-item :deep(.highlight) {
  color: #ff3b30;
  font-weight: 600;
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
</style>
