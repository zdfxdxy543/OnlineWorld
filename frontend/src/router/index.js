import { createRouter, createWebHistory } from 'vue-router'
import ForumHomeView from '../forum/views/ForumHomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'forum-home',
      component: ForumHomeView,
    },
    {
      path: '/board/:slug',
      name: 'board',
      component: () => import('../forum/views/BoardView.vue'),
    },
    {
      path: '/thread/:threadId',
      name: 'thread-detail',
      component: () => import('../forum/views/ThreadDetailView.vue'),
    },
    {
      path: '/user/:userId',
      name: 'user-profile',
      component: () => import('../forum/views/UserProfileView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../forum/views/NotFoundView.vue'),
    },
  ],
})

export default router
