<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 关闭按钮 -->
      <button class="close-btn" @click="goBack">✕</button>

      <!-- Logo和标题 -->
      <div class="login-header">
        <div class="logo">🤝</div>
        <h1>搭个伙</h1>
        <p>校园组队平台</p>
      </div>

      <!-- 登录/注册切换 -->
      <div class="tab-switcher">
        <button
          class="tab-btn"
          :class="{ 'active': activeTab === 'login' }"
          @click="switchTab('login')"
        >登录</button>
        <button
          class="tab-btn"
          :class="{ 'active': activeTab === 'register' }"
          @click="switchTab('register')"
        >注册</button>
      </div>

      <!-- 登录表单 -->
      <form v-if="activeTab === 'login'" class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名/手机号</label>
          <input
            type="text"
            v-model="loginForm.username"
            placeholder="请输入用户名或手机号"
            required
          >
        </div>
        <div class="form-group">
          <label>密码</label>
          <div class="password-input">
            <input
              :type="showLoginPassword ? 'text' : 'password'"
              v-model="loginForm.password"
              placeholder="请输入密码"
              required
            >
            <button
              type="button"
              class="toggle-password"
              @click="showLoginPassword = !showLoginPassword"
            >
              {{ showLoginPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>
        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="loginForm.remember">
            <span>记住我</span>
          </label>
          <a href="#" class="forgot-password">忘记密码？</a>
        </div>
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          <span v-if="isSubmitting">登录中...</span>
          <span v-else>登录</span>
        </button>
      </form>

      <!-- 注册表单（简化版，匹配后端字段） -->
      <form v-else class="register-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名</label>
          <input
            type="text"
            v-model="registerForm.username"
            placeholder="请设置用户名"
            required
          >
        </div>
        <div class="form-group">
          <label>手机号</label>
          <input
            type="tel"
            v-model="registerForm.phone"
            placeholder="请输入手机号"
          >
        </div>
        <div class="form-group">
          <label>昵称</label>
          <input
            type="text"
            v-model="registerForm.nickname"
            placeholder="请输入昵称"
            required
          >
        </div>
        <div class="form-group">
          <label>密码</label>
          <div class="password-input">
            <input
              :type="showRegisterPassword ? 'text' : 'password'"
              v-model="registerForm.password"
              placeholder="请输入密码（6-20位）"
              required
            >
            <button
              type="button"
              class="toggle-password"
              @click="showRegisterPassword = !showRegisterPassword"
            >
              {{ showRegisterPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          <span v-if="isSubmitting">注册中...</span>
          <span v-else>注册</span>
        </button>
      </form>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="error-message">
        <span>{{ errorMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { userAPI } from '@/api'

export default {
  name: 'LoginView',
  data() {
    return {
      activeTab: 'login',
      loginForm: {
        username: '',
        password: '',
        remember: false
      },
      registerForm: {
        username: '',
        phone: '',
        nickname: '',
        password: ''
      },
      showLoginPassword: false,
      showRegisterPassword: false,
      isSubmitting: false,
      errorMessage: ''
    }
  },
  methods: {
    goBack() {
      this.$router.back()
    },
    switchTab(tab) {
      this.activeTab = tab
      this.errorMessage = ''
    },

    async handleLogin() {
      if (this.isSubmitting) return
      this.isSubmitting = true
      this.errorMessage = ''

      try {
        const response = await userAPI.login({
          username: this.loginForm.username,
          password: this.loginForm.password
        })
        console.log('登录接口返回:', response) // 调试用

        const data = response.data || response
        const token = data.token
        const user = data.user

        console.log('即将保存的token:', token)
        console.log('即将保存的user:', user)

        if (response.code === 200 && token) {
          localStorage.setItem('token', token)
          localStorage.setItem('userInfo', JSON.stringify(user || {}))
          console.log('✅ token 已保存到本地:', token)
          this.$router.push('/')
        } else {
          this.errorMessage = response.message || '登录失败'
        }
      } catch (error) {
        console.error('登录失败:', error)
        this.errorMessage = '登录失败，请检查用户名和密码'
      } finally {
        this.isSubmitting = false
      }
    },

    async handleRegister() {
      if (this.isSubmitting) return

      if (!this.registerForm.username.trim()) {
        this.errorMessage = '请输入用户名'
        return
      }
      if (!this.registerForm.nickname.trim()) {
        this.errorMessage = '请输入昵称'
        return
      }
      if (!this.registerForm.password || this.registerForm.password.length < 6) {
        this.errorMessage = '密码长度至少6位'
        return
      }

      this.isSubmitting = true
      this.errorMessage = ''

      try {
        const response = await userAPI.register({
          username: this.registerForm.username,
          password: this.registerForm.password,
          nickname: this.registerForm.nickname,
          phone: this.registerForm.phone || undefined
        })

        if (response.code === 200) {
          alert('注册成功！请登录')
          this.loginForm.username = this.registerForm.username
          this.switchTab('login')
        } else {
          this.errorMessage = response.message || '注册失败'
        }
      } catch (error) {
        console.error('注册失败:', error)
        this.errorMessage = error.response?.data?.message || '注册失败，请重试'
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，与之前相同 */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
  overflow-y: auto;
}

.login-container {
  width: 100%;
  max-width: 400px;
  background-color: #ffffff;
  border-radius: 16px;
  padding: 32px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  color: #999999;
  cursor: pointer;
  padding: 8px;
  line-height: 1;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #333333;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 48px;
  margin-bottom: 12px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: bold;
  color: #333333;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #666666;
}

.tab-switcher {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  padding: 12px;
  background-color: #f5f5f5;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #666666;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background-color: #007aff;
  color: #ffffff;
}

.login-form,
.register-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  border-color: #007aff;
}

.password-input {
  position: relative;
}

.password-input input {
  padding-right: 50px;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  font-size: 14px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.remember-me input {
  width: auto;
}

.forgot-password {
  color: #007aff;
  text-decoration: none;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background-color: #007aff;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0056b3;
  transform: translateY(-2px);
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background-color: #fff3f3;
  border: 1px solid #ffe0e0;
  border-radius: 8px;
  color: #ff3b30;
  font-size: 14px;
  text-align: center;
}
</style>