<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getThread } from '../api/forumApi'

const route = useRoute()
const thread = ref(null)
const loading = ref(true)
const errorText = ref('')

const boardNameBySlug = {
  'town-square': 'Town Square',
  bazaar: 'Bazaar',
  whispers: 'Whispers',
  'station-terminal': 'Station Terminal',
}

const userNameById = {
  aria: 'Aria_Threadweaver',
  milo: 'Milo_Bazaar',
  eve: 'Eve_Observer',
}

const IMAGE_MARKDOWN_PATTERN = /!\[[^\]]*\]\(([^)]+)\)/g
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
const apiOrigin = (() => {
  try {
    return new URL(apiBaseUrl).origin
  } catch {
    return 'http://127.0.0.1:8000'
  }
})()

function normalizeAssetUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('/')) return `${apiOrigin}${url}`
  return `${apiOrigin}/${url}`
}

function extractPostImageUrls(content) {
  const rawContent = String(content || '')
  const matches = [...rawContent.matchAll(IMAGE_MARKDOWN_PATTERN)]
  return matches
    .map((match) => normalizeAssetUrl((match[1] || '').trim()))
    .filter(Boolean)
}

function plainPostText(content) {
  return String(content || '').replace(IMAGE_MARKDOWN_PATTERN, '').trim()
}

async function loadThread() {
  loading.value = true
  errorText.value = ''
  try {
    thread.value = await getThread(route.params.threadId)
  } catch (error) {
    thread.value = null
    errorText.value = 'Unable to load thread from API.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(loadThread)
watch(() => route.params.threadId, loadThread)
</script>

<template>
  <section v-if="loading" class="panel">
    <h2 class="panel-title">Loading thread...</h2>
  </section>

  <section v-else-if="thread" class="thread-layout">
    <article class="panel thread-main">
      <header class="thread-header">
        <p class="muted">
          <RouterLink to="/forum">Forum Home</RouterLink>
          / <RouterLink :to="`/forum/board/${thread.board_slug}`">{{ boardNameBySlug[thread.board_slug] || thread.board_slug }}</RouterLink>
        </p>
        <h2 class="panel-title">{{ thread.title }}</h2>
      </header>

      <article v-for="post in thread.posts" :key="post.id" class="post-card">
        <aside class="post-author">
          <RouterLink :to="`/forum/user/${post.author_id}`" class="user-link">
            {{ userNameById[post.author_id] || post.author_id }}
          </RouterLink>
          <p class="muted">Forum Member</p>
          <p class="muted">Status: Active</p>
        </aside>
        <div class="post-content">
          <div class="post-meta">
            <span>#{{ post.id }}</span>
            <span>{{ post.created_at }}</span>
          </div>
          <p style="white-space: pre-line;">{{ plainPostText(post.content) }}</p>
          <img
            v-for="(imageUrl, index) in extractPostImageUrls(post.content)"
            :key="`${post.id}-img-${index}`"
            :src="imageUrl"
            :alt="`Generated image ${index + 1}`"
            style="display:block;margin-top:10px;max-width:100%;border:1px solid #b9b9b9;"
            loading="lazy"
          >
          <p class="signature">Message archived by OnlineWorld BBS.</p>
        </div>
      </article>
    </article>

    <aside class="panel thread-tools">
      <h3 class="panel-title">Thread Tools</h3>
      <div class="tool-buttons">
        <button type="button">Reply</button>
        <button type="button">Watch Thread</button>
        <button type="button">Print View</button>
        <button type="button">Report Thread</button>
      </div>
      <p class="muted">Replies: {{ thread.replies }}</p>
      <p class="muted">Views: {{ thread.views }}</p>
      <p class="muted">Last reply: {{ thread.last_reply_at }}</p>
    </aside>
  </section>

  <section v-else class="panel">
    <h2 class="panel-title">Thread not found</h2>
    <p class="muted">{{ errorText || 'The thread was archived or removed by moderators.' }}</p>
    <RouterLink to="/forum">Return to forum home</RouterLink>
  </section>
</template>
