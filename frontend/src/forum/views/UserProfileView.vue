<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getUserProfile } from '../api/forumApi'

const route = useRoute()
const user = ref(null)
const recentThreads = ref([])
const loading = ref(true)
const errorText = ref('')

async function loadUser() {
  loading.value = true
  errorText.value = ''
  try {
    const payload = await getUserProfile(route.params.userId)
    user.value = payload.user
    recentThreads.value = payload.recent_threads
  } catch (error) {
    user.value = null
    recentThreads.value = []
    errorText.value = 'Unable to load user profile from API.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(loadUser)
watch(() => route.params.userId, loadUser)
</script>

<template>
  <section v-if="loading" class="panel">
    <h2 class="panel-title">Loading user profile...</h2>
  </section>

  <section v-else-if="user" class="forum-layout">
    <article class="panel">
      <h2 class="panel-title">User Control Panel</h2>
      <div class="profile-grid">
        <div>
          <p><strong>Username:</strong> {{ user.name }}</p>
          <p><strong>Title:</strong> {{ user.title }}</p>
          <p><strong>Status:</strong> {{ user.status }}</p>
          <p><strong>Join Date:</strong> {{ user.join_date }}</p>
        </div>
        <div>
          <p><strong>Posts:</strong> {{ user.posts }}</p>
          <p><strong>Reputation:</strong> {{ user.reputation }}</p>
          <p><strong>Signature:</strong> {{ user.signature }}</p>
        </div>
      </div>
      <p class="muted">{{ user.bio }}</p>
    </article>

    <aside class="panel">
      <h2 class="panel-title">Recent Threads</h2>
      <ul class="compact-list">
        <li v-for="thread in recentThreads" :key="thread.id">
          <RouterLink :to="`/thread/${thread.id}`">{{ thread.title }}</RouterLink>
          <p class="muted">{{ thread.replies }} replies / {{ thread.views }} views</p>
        </li>
      </ul>
    </aside>
  </section>

  <section v-else class="panel">
    <h2 class="panel-title">User not found</h2>
    <p class="muted">{{ errorText || 'This account may have been retired from the simulation.' }}</p>
    <RouterLink to="/">Return to forum home</RouterLink>
  </section>
</template>
