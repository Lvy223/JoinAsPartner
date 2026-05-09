<template>
  <div class="publish-page">
    <header class="header">
      <button @click="goBack" class="back-button">
        <i class="back-icon"></i>
      </button>
      <h1>发布活动</h1>
    </header>

    <main class="main-content">
      <form id="publish-form" class="form" @submit.prevent="publishActivity">
        <!-- 活动标题 -->
        <div class="form-group">
          <label class="form-label">活动标题 <span class="required">*</span></label>
          <input
            v-model="formData.title"
            type="text"
            placeholder="例如：周末篮球友谊赛"
            class="form-input"
            required
          >
        </div>

        <!-- 活动描述 -->
        <div class="form-group">
          <label class="form-label">活动描述 <span class="required">*</span></label>
          <textarea
            v-model="formData.description"
            placeholder="详细描述活动内容、要求、注意事项等"
            class="form-textarea"
            rows="4"
            required
          ></textarea>
        </div>

        <!-- 活动分类 -->
        <div class="form-group">
          <label class="form-label">活动分类 <span class="required">*</span></label>
          <select v-model="formData.category" class="form-input" required>
            <option value="">请选择分类</option>
            <option value="study">📚 学习</option>
            <option value="sports">🏀 运动</option>
            <option value="volunteer">🤝 志愿</option>
            <option value="meal">🍚 约饭</option>
            <option value="hobby">🎨 兴趣</option>
            <option value="other">其他</option>
          </select>
        </div>

        <!-- 活动标签 -->
        <div class="form-group">
          <label class="form-label">活动标签（可多个，用逗号分隔）</label>
          <input
            v-model="tagsInput"
            type="text"
            placeholder="例如：篮球,交友,周末"
            class="form-input"
          >
          <div class="form-hint">标签有助于推荐给感兴趣的人</div>
        </div>

        <!-- 时间设置 -->
        <div class="form-row">
          <div class="form-group half">
            <label class="form-label">开始时间 <span class="required">*</span></label>
            <input
              v-model="formData.start_time"
              type="datetime-local"
              class="form-input"
              required
            >
          </div>
          <div class="form-group half">
            <label class="form-label">结束时间 <span class="required">*</span></label>
            <input
              v-model="formData.end_time"
              type="datetime-local"
              class="form-input"
              required
            >
          </div>
        </div>

        <!-- 报名截止时间（可选） -->
        <div class="form-group">
          <label class="form-label">报名截止时间（可选）</label>
          <input
            v-model="formData.deadline"
            type="datetime-local"
            class="form-input"
          >
        </div>

        <!-- 地点信息 -->
        <div class="form-group">
          <label class="form-label">地点名称 <span class="required">*</span></label>
          <input
            v-model="formData.location_name"
            type="text"
            placeholder="例如：学校体育馆"
            class="form-input"
            required
          >
        </div>

        <div class="form-group">
          <label class="form-label">详细地址</label>
          <input
            v-model="formData.address_detail"
            type="text"
            placeholder="具体位置，如：3号场地"
            class="form-input"
          >
        </div>

        <!-- 位置坐标（可选） -->
        <div class="form-row">
          <div class="form-group half">
            <label class="form-label">经度</label>
            <input
              v-model.number="formData.longitude"
              type="number"
              step="any"
              placeholder="例如：116.397128"
              class="form-input"
            >
          </div>
          <div class="form-group half">
            <label class="form-label">纬度</label>
            <input
              v-model.number="formData.latitude"
              type="number"
              step="any"
              placeholder="例如：39.916527"
              class="form-input"
            >
          </div>
        </div>
        <div class="form-group">
          <button type="button" class="location-btn" @click="getCurrentLocation">
            📍 获取当前位置
          </button>
        </div>

        <!-- 人数限制 -->
        <div class="form-group">
          <label class="form-label">最大参与人数（0表示不限）</label>
          <input
            v-model.number="formData.max_participants"
            type="number"
            min="0"
            step="1"
            class="form-input"
          >
        </div>

        <!-- 发布按钮 -->
        <button
          type="submit"
          class="publish-button"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '发布中...' : '发布活动' }}
        </button>
      </form>
    </main>
  </div>
</template>

<script>
import { activitiesAPI } from '@/api'

export default {
  name: 'PublishView',
  data() {
    return {
      formData: {
        title: '',
        description: '',
        category: '',
        start_time: '',
        end_time: '',
        deadline: '',
        location_name: '',
        address_detail: '',
        longitude: null,
        latitude: null,
        max_participants: 0
      },
      tagsInput: '',
      isSubmitting: false
    }
  },
  methods: {
    goBack() {
      this.$router.back()
    },
    getCurrentLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            this.formData.longitude = position.coords.longitude
            this.formData.latitude = position.coords.latitude
          },
          (error) => {
            console.error('获取位置失败', error)
            alert('无法获取当前位置')
          }
        )
      } else {
        alert('浏览器不支持地理定位')
      }
    },
    async publishActivity() {
      if (this.isSubmitting) return

      // 简单校验
      if (!this.formData.title.trim() || !this.formData.description.trim() || !this.formData.category) {
        alert('请填写标题、描述和分类')
        return
      }

      this.isSubmitting = true

      try {
        // 组装标签数据
        const tags = this.tagsInput.split(',').map(t => t.trim()).filter(Boolean)

        const payload = {
          ...this.formData,
          tags: JSON.stringify(tags)
        }

        const response = await activitiesAPI.create(payload)

        if (response.code === 200) {
          alert('发布成功！')

          // 发送事件通知聊天页面刷新活动列表（如果 eventBus 存在）
          if (this.$eventBus) {
            this.$eventBus.$emit('activity-updated')
          }

          this.$router.push('/')
        } else {
          alert(response.message || '发布失败，请重试')
        }
      } catch (error) {
        console.error('发布活动失败:', error)
        alert('发布失败，请检查网络连接')
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

<style scoped>
.publish-page {
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
  margin-right: 16px;
}

.back-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"></path></svg>');
  background-size: contain;
  background-repeat: no-repeat;
}

.header h1 {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #333333;
}

.main-content {
  flex: 1;
  padding-top: 80px;
  padding-bottom: 80px;
  padding-left: 24px;
  padding-right: 24px;
  overflow-y: auto;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group.half {
  flex: 1;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333333;
}

.required {
  color: #ff3b30;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  color: #333333;
  outline: none;
  transition: border-color 0.3s ease;
  font-family: inherit;
}

.form-input:focus, .form-textarea:focus {
  border-color: #007aff;
}

.form-textarea {
  resize: vertical;
}

.form-hint {
  font-size: 12px;
  color: #999999;
}

.location-btn {
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
  color: #007aff;
  cursor: pointer;
  transition: all 0.3s;
}

.location-btn:hover {
  background-color: #e8f4f8;
  border-color: #007aff;
}

.publish-button {
  width: 100%;
  padding: 14px;
  background-color: #48bb78;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 12px;
}

.publish-button:hover:not(:disabled) {
  background-color: #38a169;
}

.publish-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}
</style>