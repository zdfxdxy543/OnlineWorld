<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getBoardThreads } from '../api/forumApi'

const route = useRoute()
const board = ref(null)
const threads = ref([])
const loading = ref(true)
const errorText = ref('')

function userNameById(userId) {
  const aliases = {
    aria: 'Aria_Threadweaver',
    milo: 'Milo_Bazaar',
    eve: 'Eve_Observer',
  }
  return aliases[userId] || userId
}

async function loadBoard() {
  loading.value = true
  errorText.value = ''
  try {
    const payload = await getBoardThreads(route.params.slug)
    board.value = payload.board
    threads.value = payload.threads
  } catch (error) {
    board.value = null
    threads.value = []
    errorText.value = 'Unable to load board from API.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(loadBoard)
watch(() => route.params.slug, loadBoard)
</script>

<template>
  <section v-if="loading" class="panel">
    <h2 class="panel-title">Loading board...</h2>
  </section>

  <section v-else-if="board" class="panel">
    <header class="board-header">
      <h2 class="panel-title">{{ board.name }}</h2>
      <p class="muted">{{ board.description }}</p>
      <div class="board-actions">
        <button type="button">New Thread</button>
        <button type="button">Mark All Read</button>
        <button type="button">Subscribe Board</button>
      </div>
    </header>

    <table class="forum-table">
      <thead>
        <tr>
          <th>Topic</th>
          <th>Author</th>
          <th>Replies</th>
          <th>Views</th>
          <th>Last Reply</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="thread in threads" :key="thread.id">
          <td>
            <span v-if="thread.pinned" class="tag">Pinned</span>
            <RouterLink :to="`/forum/thread/${thread.id}`">{{ thread.title }}</RouterLink>
            <p class="muted">Tags: {{ thread.tags.join(', ') }}</p>
          </td>
          <td>
            <RouterLink :to="`/forum/user/${thread.author_id}`">{{ userNameById(thread.author_id) }}</RouterLink>
          </td>
          <td>{{ thread.replies }}</td>
          <td>{{ thread.views }}</td>
          <td>
            <RouterLink :to="`/forum/user/${thread.last_reply_by_id}`">
              {{ userNameById(thread.last_reply_by_id) }}
            </RouterLink>
            <p class="muted">{{ thread.last_reply_at }}</p>
          </td>
        </tr>
      </tbody>
    </table>
  </section>

  <section v-else class="panel">
    <h2 class="panel-title">Board not found</h2>
    <p class="muted">{{ errorText || 'The board may have moved to a different server node.' }}</p>
    <RouterLink to="/forum">Return to forum home</RouterLink>
  </section>
</template>
