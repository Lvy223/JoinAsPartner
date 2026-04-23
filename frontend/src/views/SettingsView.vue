<template>
  <div class="settings-page">
    <!-- 头部 -->
    <header class="settings-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>设置</h1>
      <div style="width: 40px;"></div>
    </header>

    <!-- 设置内容 -->
    <main class="settings-content">
      <!-- 个人信息 -->
      <div class="settings-section">
        <h3 class="section-title">个人信息</h3>
        <div class="settings-group">
          <div class="setting-item" @click="editAvatar">
            <span class="item-label">头像</span>
            <div class="item-value">
              <img v-if="userInfo.avatar" :src="userInfo.avatar" class="avatar-preview" />
              <div v-else class="avatar-placeholder">👤</div>
              <span class="arrow">›</span>
            </div>
          </div>
          <div class="setting-item" @click="editField('nickname', '昵称', userInfo.nickname)">
            <span class="item-label">昵称</span>
            <div class="item-value">
              <span>{{ userInfo.nickname || '未设置' }}</span>
              <span class="arrow">›</span>
            </div>
          </div>
          <div class="setting-item" @click="editField('bio', '个人简介', userInfo.bio)">
            <span class="item-label">个人简介</span>
            <div class="item-value">
              <span>{{ userInfo.bio || '未设置' }}</span>
              <span class="arrow">›</span>
            </div>
          </div>
          <div class="setting-item">
            <span class="item-label">性别</span>
            <div class="item-value">
              <select v-model="userInfo.gender" @change="updateUserInfo">
                <option value="">未设置</option>
                <option value="male">男</option>
                <option value="female">女</option>
                <option value="other">其他</option>
              </select>
              <span class="arrow">›</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 兴趣标签（新增可编辑区域） -->
      <div class="settings-section">
        <h3 class="section-title">兴趣标签</h3>
        <div class="settings-group">
          <div class="interest-tags-container">
            <div class="tags-list">
              <span
                v-for="(tag, index) in interestTags"
                :key="index"
                class="interest-tag"
              >
                {{ tag }}
                <button class="remove-tag" @click="removeTag(index)">×</button>
              </span>
              <div class="add-tag-input" v-if="showAddTagInput">
                <input
                  type="text"
                  v-model="newTag"
                  @keyup.enter="addTag"
                  @blur="cancelAddTag"
                  placeholder="输入新标签"
                  ref="tagInput"
                />
              </div>
              <button v-else class="add-tag-btn" @click="showAddTagInput = true">
                + 添加标签
              </button>
            </div>
            <button class="save-interests-btn" @click="saveInterests" :disabled="isSavingInterests">
              {{ isSavingInterests ? '保存中...' : '保存兴趣标签' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 账号安全 -->
      <div class="settings-section">
        <h3 class="section-title">账号安全</h3>
        <div class="settings-group">
          <div class="setting-item" @click="changePassword">
            <span class="item-label">修改密码</span>
            <div class="item-value">
              <span class="arrow">›</span>
            </div>
          </div>
          <div class="setting-item">
            <span class="item-label">绑定手机</span>
            <div class="item-value">
              <span>{{ userInfo.phone || '未绑定' }}</span>
              <span class="arrow">›</span>
            </div>
          </div>
          <div class="setting-item">
            <span class="item-label">绑定邮箱</span>
            <div class="item-value">
              <span>{{ userInfo.email || '未绑定' }}</span>
              <span class="arrow">›</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 隐私设置 -->
      <div class="settings-section">
        <h3 class="section-title">隐私设置</h3>
        <div class="settings-group">
          <div class="setting-item">
            <span class="item-label">公开个人信息</span>
            <div class="item-value">
              <label class="switch">
                <input type="checkbox" v-model="privacySettings.showProfile" @change="updatePrivacy" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="setting-item">
            <span class="item-label">公开活动记录</span>
            <div class="item-value">
              <label class="switch">
                <input type="checkbox" v-model="privacySettings.showActivities" @change="updatePrivacy" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="setting-item">
            <span class="item-label">允许陌生人私信</span>
            <div class="item-value">
              <label class="switch">
                <input type="checkbox" v-model="privacySettings.allowMessage" @change="updatePrivacy" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- 通知设置 -->
      <div class="settings-section">
        <h3 class="section-title">通知设置</h3>
        <div class="settings-group">
          <div class="setting-item">
            <span class="item-label">活动提醒</span>
            <div class="item-value">
              <label class="switch">
                <input type="checkbox" v-model="notificationSettings.activityReminder" @change="updateNotification" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="setting-item">
            <span class="item-label">消息通知</span>
            <div class="item-value">
              <label class="switch">
                <input type="checkbox" v-model="notificationSettings.messageNotification" @change="updateNotification" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="setting-item">
            <span class="item-label">系统通知</span>
            <div class="item-value">
              <label class="switch">
                <input type="checkbox" v-model="notificationSettings.systemNotification" @change="updateNotification" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- 其他 -->
      <div class="settings-section">
        <h3 class="section-title">其他</h3>
        <div class="settings-group">
          <div class="setting-item" @click="clearCache">
            <span class="item-label">清除缓存</span>
            <div class="item-value">
              <span>{{ cacheSize }}</span>
              <span class="arrow">›</span>
            </div>
          </div>
          <div class="setting-item" @click="showAbout">
            <span class="item-label">关于我们</span>
            <div class="item-value">
              <span class="arrow">›</span>
            </div>
          </div>
          <div class="setting-item" @click="showFeedback">
            <span class="item-label">意见反馈</span>
            <div class="item-value">
              <span class="arrow">›</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 退出登录 -->
      <button class="logout-btn" @click="handleLogout">退出登录</button>

      <!-- 版本信息 -->
      <div class="version-info">
        <p>版本号：v1.0.0</p>
      </div>
    </main>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <h3>{{ editTitle }}</h3>
        <input
          type="text"
          v-model="editValue"
          :placeholder="`请输入${editTitle}`"
          ref="editInput"
        />
        <div class="modal-buttons">
          <button class="cancel-btn" @click="closeEditModal">取消</button>
          <button class="confirm-btn" @click="saveEdit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { userAPI } from '@/api'

export default {
  name: 'SettingsView',
  data() {
    return {
      userInfo: {
        avatar: '',
        nickname: '',
        bio: '',
        gender: '',
        phone: '',
        email: '',
        interests: []       // 兴趣标签数组
      },
      interestTags: [],     // 本地编辑的兴趣标签副本
      showAddTagInput: false,
      newTag: '',
      isSavingInterests: false,
      privacySettings: {
        showProfile: true,
        showActivities: true,
        allowMessage: true
      },
      notificationSettings: {
        activityReminder: true,
        messageNotification: true,
        systemNotification: true
      },
      cacheSize: '0KB',
      showEditModal: false,
      editField: '',
      editTitle: '',
      editValue: ''
    }
  },
  mounted() {
    this.loadUserInfo()
    this.calculateCacheSize()
  },
  methods: {
    async loadUserInfo() {
      try {
        const response = await userAPI.getProfile()
        const data = response.data || response
        if (data.user) {
          this.userInfo = { ...this.userInfo, ...data.user }
          // 初始化兴趣标签副本
          this.interestTags = [...(this.userInfo.interests || [])]
        }
      } catch (error) {
        console.error('加载用户信息失败:', error)
      }
    },
    // 兴趣标签编辑方法
    addTag() {
      const tag = this.newTag.trim()
      if (tag && !this.interestTags.includes(tag)) {
        this.interestTags.push(tag)
      }
      this.newTag = ''
      this.showAddTagInput = false
    },
    removeTag(index) {
      this.interestTags.splice(index, 1)
    },
    cancelAddTag() {
      this.showAddTagInput = false
      this.newTag = ''
    },
    async saveInterests() {
      if (this.isSavingInterests) return
      this.isSavingInterests = true
      try {
        await userAPI.updateInterests({ interests: this.interestTags })
        // 更新本地 userInfo 中的 interests
        this.userInfo.interests = [...this.interestTags]
        alert('兴趣标签保存成功')
      } catch (error) {
        console.error('保存兴趣标签失败:', error)
        alert('保存失败，请重试')
      } finally {
        this.isSavingInterests = false
      }
    },
    editAvatar() {
      alert('头像上传功能开发中...')
    },
    editField(field, title, value) {
      this.editField = field
      this.editTitle = title
      this.editValue = value || ''
      this.showEditModal = true
      this.$nextTick(() => {
        this.$refs.editInput.focus()
      })
    },
    closeEditModal() {
      this.showEditModal = false
      this.editField = ''
      this.editTitle = ''
      this.editValue = ''
    },
    async saveEdit() {
      if (!this.editValue.trim()) {
        alert('内容不能为空')
        return
      }

      this.userInfo[this.editField] = this.editValue
      await this.updateUserInfo()
      this.closeEditModal()
    },
    async updateUserInfo() {
      try {
        // 注意：后端目前只有更新兴趣标签的接口，对于昵称、简介等可能需要额外接口
        // 此处仅演示更新昵称和简介，如果后端无对应接口，可暂时注释或扩展
        // 若需要更新昵称和简介，需后端新增 /api/user/profile (PUT) 接口
        // 这里只更新兴趣标签已单独处理，其他字段的更新需要后端支持
        if (this.editField === 'nickname' || this.editField === 'bio') {
          // 可调用后端通用更新接口（如果存在）
          console.log('更新字段', this.editField, this.editValue)
          // 临时提示
          alert('昵称和简介更新功能开发中，请联系管理员')
        } else {
          await userAPI.updateProfile(this.userInfo)
          alert('保存成功')
        }
      } catch (error) {
        console.error('更新用户信息失败:', error)
        alert('保存失败，请重试')
      }
    },
    updatePrivacy() {
      localStorage.setItem('privacySettings', JSON.stringify(this.privacySettings))
    },
    updateNotification() {
      localStorage.setItem('notificationSettings', JSON.stringify(this.notificationSettings))
    },
    changePassword() {
      alert('修改密码功能开发中...')
    },
    clearCache() {
      if (confirm('确定要清除缓存吗？')) {
        localStorage.clear()
        this.cacheSize = '0KB'
        alert('缓存已清除')
      }
    },
    calculateCacheSize() {
      let total = 0
      for (let key in localStorage) {
        if (localStorage.hasOwnProperty(key)) {
          total += localStorage.getItem(key).length * 2
        }
      }
      if (total < 1024) {
        this.cacheSize = total + 'B'
      } else if (total < 1024 * 1024) {
        this.cacheSize = (total / 1024).toFixed(2) + 'KB'
      } else {
        this.cacheSize = (total / 1024 / 1024).toFixed(2) + 'MB'
      }
    },
    showAbout() {
      alert('搭个伙 v1.0.0\n校园组队平台\n让组队更简单')
    },
    showFeedback() {
      alert('意见反馈功能开发中...')
    },
    handleLogout() {
      if (confirm('确定要退出登录吗？')) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        this.$router.push('/login')
      }
    },
    goBack() {
      this.$router.back()
    }
  }
}
</script>

<style scoped>
/* 原有样式保持不变，添加兴趣标签相关样式 */
.settings-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}
.settings-header h1 {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
}
.back-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #333333;
  cursor: pointer;
}
.settings-content {
  padding: 16px;
  padding-bottom: 32px;
}
.settings-section {
  margin-bottom: 24px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #666666;
  margin-bottom: 12px;
  padding-left: 4px;
}
.settings-group {
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
}
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.setting-item:last-child {
  border-bottom: none;
}
.setting-item:hover {
  background-color: #f9f9f9;
}
.item-label {
  font-size: 16px;
  color: #333333;
}
.item-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666666;
}
.arrow {
  font-size: 18px;
  color: #cccccc;
}
.avatar-preview {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}
.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
select {
  border: none;
  background: none;
  font-size: 14px;
  color: #666666;
  outline: none;
  text-align: right;
  direction: rtl;
}
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 28px;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 28px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: #007aff;
}
input:checked + .slider:before {
  transform: translateX(20px);
}
/* 兴趣标签区域样式 */
.interest-tags-container {
  padding: 16px;
}
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  align-items: center;
}
.interest-tag {
  display: inline-flex;
  align-items: center;
  background-color: #e8f4f8;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  color: #333;
}
.remove-tag {
  background: none;
  border: none;
  font-size: 16px;
  margin-left: 6px;
  cursor: pointer;
  color: #999;
}
.remove-tag:hover {
  color: #ff3b30;
}
.add-tag-input {
  display: inline-flex;
}
.add-tag-input input {
  padding: 6px 12px;
  border: 1px solid #007aff;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
}
.add-tag-btn {
  background-color: #f0f0f0;
  border: none;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  color: #007aff;
}
.add-tag-btn:hover {
  background-color: #e0e0e0;
}
.save-interests-btn {
  background-color: #007aff;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  width: 100%;
  transition: background 0.3s;
}
.save-interests-btn:hover:not(:disabled) {
  background-color: #0056b3;
}
.save-interests-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
.logout-btn {
  width: 100%;
  padding: 14px;
  background-color: #ffffff;
  color: #ff3b30;
  border: 1px solid #ff3b30;
  border-radius: 12px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 16px;
}
.logout-btn:hover {
  background-color: #ff3b30;
  color: #ffffff;
}
.version-info {
  text-align: center;
  padding: 16px 0;
  font-size: 12px;
  color: #999999;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.modal-content {
  width: 80%;
  max-width: 320px;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
}
.modal-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 16px;
  text-align: center;
}
.modal-content input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  margin-bottom: 16px;
}
.modal-content input:focus {
  border-color: #007aff;
}
.modal-buttons {
  display: flex;
  gap: 12px;
}
.cancel-btn,
.confirm-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.cancel-btn {
  background-color: #f5f5f5;
  color: #666666;
}
.confirm-btn {
  background-color: #007aff;
  color: #ffffff;
}
.cancel-btn:hover {
  background-color: #e0e0e0;
}
.confirm-btn:hover {
  background-color: #0056b3;
}
</style>