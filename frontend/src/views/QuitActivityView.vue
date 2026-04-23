<template>
  <div class="quit-activity">
    <div class="quit-container">
      <div class="quit-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="#FF3B30"/>
          <path d="M15 9L9 15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M9 9L15 15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <h1 class="quit-title">确定要退出队伍吗？</h1>
      <p class="quit-description">退出后将无法继续参与该活动的聊天和相关事宜</p>

      <div class="button-group">
        <button class="cancel-button" @click="cancelQuit">取消</button>
        <button class="confirm-button" @click="confirmQuit" :disabled="isQuitting">
          {{ isQuitting ? '退出中...' : '确定退出' }}
        </button>
      </div>

      <div class="reason-section">
        <h3 class="reason-title">请选择退出原因（可选）</h3>
        <div class="reason-options">
          <div
            v-for="(reason, index) in reasonOptions"
            :key="index"
            class="reason-option"
            :class="{ 'selected': selectedReason === reason.value }"
            @click="selectedReason = reason.value"
          >
            <div class="reason-radio"></div>
            <span class="reason-text">{{ reason.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { activitiesAPI } from '@/api'

export default {
  name: 'QuitActivityView',
  data() {
    return {
      isQuitting: false,
      selectedReason: '',
      reasonOptions: [
        { label: '时间冲突', value: 'time_conflict' },
        { label: '找到了其他活动', value: 'other_activity' },
        { label: '活动不符合预期', value: 'not_expected' },
        { label: '个人原因', value: 'personal_reason' },
        { label: '其他', value: 'other' }
      ]
    }
  },
  methods: {
    cancelQuit() {
      this.$router.back()
    },
    async confirmQuit() {
      if (this.isQuitting) return

      this.isQuitting = true

      try {
        const activityId = localStorage.getItem('currentActivityId')
        if (!activityId) {
          alert('未找到当前活动，请返回重试')
          this.$router.back()
          return
        }
        // 调用后端退出活动接口（需要后端实现 POST /api/activities/<id>/quit）
        // 注意：activitiesAPI.quit 需要先在 index.js 中定义
        const response = await activitiesAPI.quit(activityId, { reason: this.selectedReason })
        if (response.code === 200) {
          // 退出成功后，清除本地存储的当前活动ID
          localStorage.removeItem('currentActivityId')
          // 跳转到成功页面
          this.$router.push({
            path: '/success',
            query: { type: 'quit' }
          })
        } else {
          alert(response.message || '退出失败，请重试')
        }
      } catch (error) {
        console.error('退出活动失败:', error)
        alert('退出失败，请重试')
      } finally {
        this.isQuitting = false
      }
    }
  }
}
</script>

<style scoped>
.quit-activity {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.quit-container {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 40px 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.quit-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.quit-icon svg {
  width: 100%;
  height: 100%;
}

.quit-title {
  font-size: 24px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 12px;
}

.quit-description {
  font-size: 16px;
  color: #666666;
  margin-bottom: 32px;
  line-height: 1.5;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
}

.cancel-button {
  flex: 1;
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

.cancel-button:hover {
  background-color: #e0e0e0;
}

.confirm-button {
  flex: 1;
  padding: 12px;
  background-color: #FF3B30;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.confirm-button:hover:not(:disabled) {
  background-color: #FF2D22;
}

.confirm-button:disabled {
  background-color: #FF9999;
  cursor: not-allowed;
}

.reason-section {
  text-align: left;
}

.reason-title {
  font-size: 16px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 16px;
}

.reason-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reason-option {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.reason-option:hover {
  background-color: #f9f9f9;
}

.reason-option.selected {
  border-color: #007aff;
  background-color: #f0f8ff;
}

.reason-radio {
  width: 20px;
  height: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 50%;
  margin-right: 12px;
  position: relative;
}

.reason-option.selected .reason-radio {
  border-color: #007aff;
  background-color: #007aff;
}

.reason-option.selected .reason-radio::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background-color: #ffffff;
  border-radius: 50%;
}

.reason-text {
  font-size: 14px;
  color: #333333;
}
</style>