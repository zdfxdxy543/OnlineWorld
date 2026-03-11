<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { getForumStats } from './api/forumApi'

const forumStats = ref({
  online_users: 0,
  total_threads: 0,
  total_posts: 0,
})

onMounted(async () => {
  try {
    forumStats.value = await getForumStats()
  } catch (error) {
    console.error('Failed to load forum stats:', error)
  }
})
</script>

<template>
  <div class="site-shell">
    <header class="site-header panel">
      <div class="header-top">
        <h1>OnlineWorld BBS 2001</h1>
        <p>Connected worlds, persistent stories, endless rumors.</p>
      </div>
      <div class="header-meta">
        <span>Users online: {{ forumStats.online_users }}</span>
        <span>Total threads: {{ forumStats.total_threads }}</span>
        <span>Total posts: {{ forumStats.total_posts }}</span>
      </div>
      <nav class="top-nav">
        <RouterLink to="/forum">Forum Home</RouterLink>
        <RouterLink to="/forum/board/town-square">Town Square</RouterLink>
        <RouterLink to="/forum/board/bazaar">Bazaar</RouterLink>
        <RouterLink to="/forum/board/whispers">Whispers</RouterLink>
        <RouterLink to="/forum/user/aria">My Profile</RouterLink>
        <RouterLink to="/news">Switch to GreenLeaf News</RouterLink>
        <RouterLink to="/netdisk">Switch to BlueBox Netdisk</RouterLink>
      </nav>
      <div class="search-row">
        <label for="forum-search">Quick Search:</label>
        <input id="forum-search" type="text" placeholder="Search threads, users, clues..." />
        <button type="button">Search</button>
      </div>
    </header>

    <main>
      <RouterView />
    </main>

    <footer class="site-footer panel">
      <p>OnlineWorld BBS is best viewed at 1024x768 with modern nostalgia enabled.</p>
      <p>Powered by Vue 3, styled like the golden age of message boards.</p>
    </footer>
  </div>
</template>
