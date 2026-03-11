<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { getBoards, getHotThreads } from '../api/forumApi'

const forumBoards = ref([])
const hotThreads = ref([])
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

onMounted(async () => {
  try {
    const [boards, threads] = await Promise.all([getBoards(), getHotThreads(5)])
    forumBoards.value = boards
    hotThreads.value = threads
  } catch (error) {
    errorText.value = 'Unable to load forum data from API.'
    console.error(error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section v-if="loading" class="panel">
    <h2 class="panel-title">Forum Index</h2>
    <p class="muted">Loading latest forum data...</p>
  </section>

  <section v-else-if="errorText" class="panel">
    <h2 class="panel-title">Forum Index</h2>
    <p class="muted">{{ errorText }}</p>
  </section>

  <section v-else class="forum-layout">
    <article class="panel">
      <h2 class="panel-title">Forum Index</h2>
      <table class="forum-table">
        <thead>
          <tr>
            <th>Board</th>
            <th>Threads</th>
            <th>Posts</th>
            <th>Latest Activity</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="board in forumBoards" :key="board.slug">
            <td>
              <RouterLink :to="`/board/${board.slug}`" class="board-name">{{ board.name }}</RouterLink>
              <p class="muted">{{ board.description }}</p>
              <p class="muted">Moderator: {{ board.moderator }}</p>
            </td>
            <td>{{ board.threads }}</td>
            <td>{{ board.posts }}</td>
            <td>
              <template v-if="board.latest_thread">
                <RouterLink :to="`/thread/${board.latest_thread.id}`">
                  {{ board.latest_thread.title }}
                </RouterLink>
                <p class="muted">
                  by {{ userNameById(board.latest_thread.last_reply_by_id) }}
                  at {{ board.latest_thread.last_reply_at }}
                </p>
              </template>
              <template v-else>
                <p class="muted">No activity yet</p>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </article>

    <aside class="right-stack">
      <article class="panel">
        <h2 class="panel-title">Hot Threads</h2>
        <ul class="compact-list">
          <li v-for="thread in hotThreads" :key="thread.id">
            <RouterLink :to="`/thread/${thread.id}`">{{ thread.title }}</RouterLink>
            <p class="muted">{{ thread.views }} views / {{ thread.replies }} replies</p>
          </li>
        </ul>
      </article>

      <article class="panel">
        <h2 class="panel-title">Forum Bulletin</h2>
        <ul class="compact-list">
          <li>Daily backup starts at 02:00 server time.</li>
          <li>All bazaar listings now require checksum metadata.</li>
          <li>Whispers board accepts encrypted attachments this week.</li>
          <li>Use report tags to flag timeline contradictions.</li>
        </ul>
      </article>
    </aside>
  </section>
</template>
