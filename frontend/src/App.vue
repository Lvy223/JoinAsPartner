<template>
  <div class="app">
    <router-view />
    <!-- 底部导航栏，已提高层级 -->
    <nav class="bottom-nav" v-if="showBottomNav">
      <router-link to="/" class="nav-item">
        <div class="nav-icon">🏠</div>
        <span>首页</span>
      </router-link>

      <router-link to="/publish" class="nav-item">
        <div class="nav-icon">➕</div>
        <span>发布</span>
      </router-link>

      <div class="nav-item" @click="goToChat">
        <div class="nav-icon">💬</div>
        <span>聊天</span>
      </div>

      <!-- 我的按钮，增强点击能力和层级 -->
      <div class="nav-item" @click="forceGoToProfile">
        <div class="nav-icon">👤</div>
        <span>我的</span>
      </div>
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
      this.$router.push('/chat')
    },
    forceGoToProfile() {
      const token = localStorage.getItem('token')
      if (!token) {
        // 没登录，直接进登录页
        this.$router.push('/login')
      } else {
        this.$router.push('/profile')
      }
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
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC';
}

.app {
  height: 100vh;
}

/* 底部导航栏 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
  background: #fff;
  border-top: 1px solid #eee;
  z-index: 2000; /* 提高层级，确保不被页面内容遮挡 */
}

.nav-item {
  text-align: center;
  font-size: 12px;
  color: #666;
}

.nav-icon {
  font-size: 20px;
}
</style>