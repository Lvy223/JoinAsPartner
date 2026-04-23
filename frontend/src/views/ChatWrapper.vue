<template>
  <div>
    <ChatView v-if="hasActivities" />
    <NoActivityView v-else />
  </div>
</template>

<script>
import { userAPI } from '@/api'
export default {
  data() {
    return { myActivities: [] }
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
        const res = await userAPI.getMyActivities()
        if (res.code === 200) this.myActivities = res.data
      } catch(e) { console.error(e) }
    }
  }
}
</script>