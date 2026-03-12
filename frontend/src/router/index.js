import { createRouter, createWebHistory } from 'vue-router'
import ForumHomeView from '../forum/views/ForumHomeView.vue'
import ForumApp from '../forum/ForumApp.vue'
import NetdiskApp from '../netdisk/NetdiskApp.vue'
import NetdiskView from '../forum/views/NetdiskView.vue'
import NewsApp from '../news/NewsApp.vue'
import NewsHomeView from '../news/views/NewsHomeView.vue'
import P2PStoreApp from '../p2pstore/P2PStoreApp.vue'
import P2PStoreHomeView from '../p2pstore/views/P2PStoreHomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/forum',
    },
    {
      path: '/forum',
      component: ForumApp,
      children: [
        {
          path: '',
          name: 'forum-home',
          component: ForumHomeView,
        },
        {
          path: 'board/:slug',
          name: 'forum-board',
          component: () => import('../forum/views/BoardView.vue'),
        },
        {
          path: 'thread/:threadId',
          name: 'forum-thread-detail',
          component: () => import('../forum/views/ThreadDetailView.vue'),
        },
        {
          path: 'user/:userId',
          name: 'forum-user-profile',
          component: () => import('../forum/views/UserProfileView.vue'),
        },
      ],
    },
    {
      path: '/netdisk',
      component: NetdiskApp,
      children: [
        {
          path: '',
          name: 'netdisk-home',
          component: NetdiskView,
        },
      ],
    },
    {
      path: '/news',
      component: NewsApp,
      children: [
        {
          path: '',
          name: 'news-home',
          component: NewsHomeView,
        },
        {
          path: 'article/:articleId',
          name: 'news-article-detail',
          component: () => import('../news/views/ArticleDetailView.vue'),
        },
      ],
    },
    {
      path: '/p2pstore',
      component: P2PStoreApp,
      children: [
        {
          path: '',
          name: 'p2pstore-home',
          component: P2PStoreHomeView,
        },
        {
          path: 'product/:productId',
          name: 'p2pstore-product-detail',
          component: () => import('../p2pstore/views/P2PStoreProductView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../forum/views/NotFoundView.vue'),
    },
  ],
})

export default router
