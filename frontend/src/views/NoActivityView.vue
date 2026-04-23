<template>
  <div class="no-activity-view">
    <div class="no-activity-container">
      <div class="no-activity-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="#999999" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="9" y1="10" x2="15" y2="10" stroke="#999999" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1>暂无活动</h1>
      <p>您还没有加入任何活动<br>快去首页寻找感兴趣的活动吧！</p>
      <button class="back-home-button" @click="goToHome">返回首页</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NoActivityView',
  methods: {
    goToHome() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.no-activity-view {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f8f9fa;
}

.no-activity-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.no-activity-icon {
  width: 120px;
  height: 120px;
  margin-bottom: 24px;
  opacity: 0.6;
}

.no-activity-icon svg {
  width: 100%;
  height: 100%;
}

.no-activity-container h1 {
  font-size: 20px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 12px;
}

.no-activity-container p {
  font-size: 14px;
  color: #666666;
  margin-bottom: 32px;
  line-height: 1.6;
}

.back-home-button {
  padding: 12px 32px;
  background-color: #007aff;
  color: #ffffff;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.back-home-button:hover {
  background-color: #0066cc;
}
</style>
