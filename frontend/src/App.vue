<template>
  <div class="app">
    <router-view />
    <!-- 底部导航栏 -->
    <nav class="bottom-nav" v-if="showBottomNav">
      <router-link to="/" class="nav-item">
        <div class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 9L12 2L21 9V20C21 20.5523 20.5523 21 20 21H4C3.44772 21 3 20.5523 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 22V12H15V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span>首页</span>
      </router-link>
      <router-link to="/publish" class="nav-item">
        <div class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="8" x2="12" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span>发布</span>
      </router-link>
      <div class="nav-item" :class="{ 'router-link-active': $route.name === 'chat' || $route.name === 'no-activity' }" @click="goToChat">
        <div class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span>聊天</span>
      </div>
      <router-link to="/profile" class="nav-item">
        <div class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span>我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      showBottomNav: true
    }
  },
  watch: {
    $route(to) {
      // 在登录页面、成功页面、退出页面和完成页面隐藏底部导航栏
      this.showBottomNav = !['login', 'success', 'quit', 'complete'].includes(to.name)
    }
  },
  methods: {
    goToChat() {
      // 直接跳转到聊天页面，由ChatWrapper处理显示逻辑
      this.$router.push('/chat')
    }
  }
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Helvetica Neue', 'Arial', 'sans-serif';
  background-color: #ffffff;
  color: #333333;
  overflow-x: hidden;
}

.app {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
}

/* 底部导航栏 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  background-color: #ffffff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  padding: 10px 0;
  z-index: 1000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #666666;
  transition: color 0.3s;
}

.nav-item.router-link-active {
  color: #007aff;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

.nav-item span {
  font-size: 12px;
}
</style>