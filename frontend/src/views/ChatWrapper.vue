<template>
  <div>
    <ChatView v-if="hasActivities" />
    <NoActivityView v-else />
  </div>
</template>

<script>
import { activitiesAPI, userAPI } from '@/api'
import ChatView from './ChatView.vue'
import NoActivityView from './NoActivityView.vue'

export default {
  components: {
    ChatView,
    NoActivityView
  },
  data() {
    return {
      myActivities: []
    }
  },
  computed: {
    hasActivities() {
      return this.myActivities.length > 0
    }
  },
  async mounted() {
    await this.loadActivities()
  },
  methods: {
    async loadActivities() {
      try {
        // 1. 获取当前登录用户ID
        const profileRes = await userAPI.getProfile()
        const userId = profileRes?.data?.user?.id
        if (!userId) {
          this.myActivities = []
          return
        }

        // 2. 拉取首页活动列表（与首页看到的数据一模一样）
        const listRes = await activitiesAPI.getList({ page: 1, per_page: 100 })
        const allActivities = listRes?.data?.activities || listRes?.activities || []

        // 3. 筛选出“我创建的”或“我参与的”
        this.myActivities = allActivities.filter(act => {
          // 创建者
          if (act.creator_id === userId) return true
          // 已参与者（根据后端返回的 participants 数组）
          if (act.participants && Array.isArray(act.participants)) {
            return act.participants.some(p => p.user_id === userId)
          }
          // 也可根据已知的 role 字段（如果后端在列表中返回了）
          if (act.role === 1 || act.role === 3) return true
          return false
        })
      } catch (e) {
        console.error('加载活动列表失败:', e)
        this.myActivities = []
      }
    }
  }
}
</script>