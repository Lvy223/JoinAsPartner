import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PublishView from '../views/PublishView.vue'
import ProfileView from '../views/ProfileView.vue'
import ActivityDetailView from '../views/ActivityDetailView.vue'
import ChatWrapper from '../views/ChatWrapper.vue'
import SuccessView from '../views/SuccessView.vue'
import NoActivityView from '../views/NoActivityView.vue'
import LoginView from '../views/LoginView.vue'
import SearchView from '../views/SearchView.vue'
import SettingsView from '../views/SettingsView.vue'
import ManageView from '../views/ManageView.vue'
import QuitActivityView from '../views/QuitActivityView.vue'
import ActivityCompleteView from '../views/ActivityCompleteView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/publish',
    name: 'publish',
    component: PublishView
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView
  },
  {
    path: '/activity/:id',
    name: 'activityDetail',
    component: ActivityDetailView
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatWrapper
  },
  {
    path: '/no-activity',
    name: 'no-activity',
    component: NoActivityView
  },
  {
    path: '/success',
    name: 'success',
    component: SuccessView
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView
  },
  {
    path: '/manage',
    name: 'manage',
    component: ManageView
  },
  {
    path: '/quit',
    name: 'quit',
    component: QuitActivityView
  },
  {
    path: '/complete',
    name: 'complete',
    component: ActivityCompleteView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router