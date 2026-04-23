<template>
  <div class="activity-complete">
    <div class="complete-container">
      <div class="complete-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" fill="#4CD964"/>
          <path d="M7 12L10 15L17 8" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <h1 class="complete-title">活动已完成</h1>
      <p class="complete-description">恭喜你成功完成了本次活动，期待你在未来的活动中继续表现出色！</p>

      <div class="activity-info" v-if="currentActivity">
        <h3 class="info-title">{{ currentActivity.title }}</h3>
        <div class="info-details">
          <div class="info-item">
            <span class="info-label">活动分类：</span>
            <span class="info-value">{{ getCategoryName(currentActivity.category) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">参与人数：</span>
            <span class="info-value">{{ currentActivity.current_participants || 0 }}人</span>
          </div>
          <div class="info-item">
            <span class="info-label">活动时间：</span>
            <span class="info-value">{{ formatTime(currentActivity.start_time) }}</span>
          </div>
        </div>
      </div>

      <div class="feedback-section">
        <h3 class="feedback-title">活动评分</h3>
        <div class="rating-stars">
          <span
            v-for="star in 5"
            :key="star"
            class="star"
            :class="{ 'active': rating >= star }"
            @click="rating = star"
          >★</span>
        </div>
        <textarea
          v-model="feedback"
          class="feedback-textarea"
          placeholder="留下你的活动反馈（可选）"
          rows="3"
        ></textarea>
      </div>

      <div class="button-group">
        <button class="primary-button" @click="submitFeedback" :disabled="isSubmitting">
          {{ isSubmitting ? '提交中...' : '提交反馈' }}
        </button>
        <button class="secondary-button" @click="goToHome">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script>
import { activitiesAPI, userAPI } from '@/api'

export default {
  name: 'ActivityCompleteView',
  data() {
    return {
      currentActivity: null,
      rating: 5,
      feedback: '',
      isSubmitting: false
    }
  },
  async mounted() {
    await this.loadCurrentActivity()
  },
  methods: {
    async loadCurrentActivity() {
      const activityId = localStorage.getItem('currentActivityId')
      if (!activityId) {
        this.currentActivity = null
        return
      }
      try {
        // 调用活动详情接口获取活动信息
        const response = await activitiesAPI.getDetail(activityId)
        if (response.code === 200) {
          this.currentActivity = response.data
        } else {
          console.error('获取活动详情失败:', response.message)
          this.currentActivity = null
        }
      } catch (error) {
        console.error('加载活动详情失败:', error)
        this.currentActivity = null
      }
    },
    getCategoryName(category) {
      const names = {
        study: '学习',
        sports: '运动',
        volunteer: '志愿',
        meal: '约饭',
        hobby: '兴趣'
      }
      return names[category] || '其他'
    },
    formatTime(timeStr) {
      if (!timeStr) return '时间待定'
      const date = new Date(timeStr)
      return date.toLocaleString()
    },
    async submitFeedback() {
      if (this.isSubmitting) return

      this.isSubmitting = true

      try {
        const activityId = localStorage.getItem('currentActivityId')
        if (!activityId) {
          alert('未找到当前活动，请返回重试')
          this.$router.back()
          return
        }
        // 提交评价（调用 /api/review 接口）
        // 注意：被评价人 user_id 需要用户选择，这里简化：评价活动本身？后端 review 接口需要 reviewed_user_id。
        // 为了演示，我们假设评价对象是活动创建者（或当前用户自己评价活动），但规范应是对参与者评价。
        // 此处我们调用一个活动完成接口，而非评价接口。假设后端提供 /api/activities/<id>/complete
        // 如果使用评价接口，需要额外选择被评价人。这里我们调用一个自定义完成接口。
        // 实际应根据产品设计调整。这里暂时使用评价接口的占位，需要后端补充活动完成接口。
        // 示例：调用活动完成接口
        const response = await activitiesAPI.complete(activityId, {
          rating: this.rating,
          comment: this.feedback
        })
        if (response.code === 200) {
          // 清除当前活动ID
          localStorage.removeItem('currentActivityId')
          // 跳转到成功页面
          this.$router.push({
            path: '/success',
            query: { type: 'complete' }
          })
        } else {
          alert(response.message || '提交失败，请重试')
        }
      } catch (error) {
        console.error('提交反馈失败:', error)
        alert('提交失败，请重试')
      } finally {
        this.isSubmitting = false
      }
    },
    goToHome() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.activity-complete {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.complete-container {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 40px 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.complete-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.complete-icon svg {
  width: 100%;
  height: 100%;
}

.complete-title {
  font-size: 24px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 12px;
}

.complete-description {
  font-size: 16px;
  color: #666666;
  margin-bottom: 32px;
  line-height: 1.5;
}

.activity-info {
  background-color: #f9f9f9;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 32px;
  text-align: left;
}

.info-title {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 12px;
}

.info-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  font-size: 14px;
}

.info-label {
  color: #666666;
  margin-right: 8px;
  min-width: 80px;
}

.info-value {
  color: #333333;
  font-weight: 500;
}

.feedback-section {
  margin-bottom: 32px;
  text-align: left;
}

.feedback-title {
  font-size: 16px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 12px;
}

.rating-stars {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.star {
  font-size: 24px;
  color: #e0e0e0;
  cursor: pointer;
  transition: color 0.3s;
}

.star:hover, .star.active {
  color: #FFD700;
}

.feedback-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

.feedback-textarea:focus {
  outline: none;
  border-color: #007aff;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.primary-button {
  padding: 12px;
  background-color: #007aff;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.primary-button:hover:not(:disabled) {
  background-color: #0066cc;
}

.primary-button:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

.secondary-button {
  padding: 12px;
  background-color: #f5f5f5;
  color: #333333;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.secondary-button:hover {
  background-color: #e0e0e0;
}
</style>