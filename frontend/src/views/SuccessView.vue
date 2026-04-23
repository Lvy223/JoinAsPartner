<template>
  <div class="success-view">
    <div class="success-container">
      <div class="success-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" fill="#4CD964"/>
          <path d="M7 12L10 15L17 8" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1>{{ title }}</h1>
      <p>{{ message }}</p>
      <div class="button-group">
        <button class="primary-button" @click="goToHome">返回首页</button>
        <button v-if="showChatButton" class="secondary-button" @click="goToChat">进入聊天</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SuccessView',
  data() {
    return {
      title: '操作成功',
      message: '您的操作已成功完成',
      showChatButton: false
    }
  },
  mounted() {
    // 从路由参数中获取信息
    const { type } = this.$route.query
    if (type === 'join') {
      this.title = '加入队伍成功'
      this.message = '您已成功加入该队伍，现在可以与队友聊天交流'
      this.showChatButton = true
    } else if (type === 'publish') {
      this.title = '发布任务成功'
      this.message = '您的任务已成功发布，期待更多同学的加入'
    }
  },
  methods: {
    goToHome() {
      this.$router.push('/')
    },
    goToChat() {
      this.$router.push('/chat')
    }
  }
}
</script>

<style scoped>
.success-view {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #ffffff;
}

.success-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.success-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
}

.success-icon svg {
  width: 100%;
  height: 100%;
}

.success-container h1 {
  font-size: 24px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 12px;
}

.success-container p {
  font-size: 16px;
  color: #666666;
  margin-bottom: 32px;
  line-height: 1.5;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 240px;
}

.primary-button {
  padding: 12px 24px;
  background-color: #007aff;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.primary-button:hover {
  background-color: #0066cc;
}

.secondary-button {
  padding: 12px 24px;
  background-color: #f5f5f5;
  color: #333333;
  border: 1px solid #dddddd;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.secondary-button:hover {
  background-color: #eeeeee;
  border-color: #cccccc;
}
</style>