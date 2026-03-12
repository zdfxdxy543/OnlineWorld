<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { buildPageSrcDoc, getMainPage } from '../api/mainpageApi'

const route = useRoute()

const state = ref('idle')
const errorMessage = ref('')
const page = ref(null)

const slug = computed(() => String(route.params.slug || '').trim())
const srcdoc = computed(() => buildPageSrcDoc(page.value))

async function loadPage() {
  if (!slug.value) {
    state.value = 'error'
    errorMessage.value = 'Missing page slug.'
    return
  }

  state.value = 'loading'
  errorMessage.value = ''

  try {
    page.value = await getMainPage(slug.value)
    state.value = 'success'
    document.title = page.value?.title || slug.value
  } catch (error) {
    page.value = null
    state.value = 'error'
    errorMessage.value =
      error instanceof Error && error.message === 'PAGE_NOT_FOUND'
        ? 'This generated page does not exist.'
        : 'Failed to load the generated page.'
  }
}

onMounted(loadPage)
watch(slug, loadPage)
</script>

<template>
  <section v-if="state === 'loading'" class="main-page-status">
    <div class="main-page-card">
      <p class="eyebrow">Loading</p>
      <h1>Fetching generated page</h1>
      <p>The frontend is retrieving the published HTML for this slug.</p>
    </div>
  </section>

  <section v-else-if="state === 'error'" class="main-page-status">
    <div class="main-page-card error">
      <p class="eyebrow">Unavailable</p>
      <h1>{{ errorMessage }}</h1>
      <p>Check whether the backend has published this slug and the API is reachable.</p>
    </div>
  </section>

  <iframe
    v-else
    class="main-page-frame"
    :srcdoc="srcdoc"
    :title="page?.title || slug"
    sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
  />
</template>

<style scoped>
.main-page-status {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top, rgba(214, 185, 120, 0.28), transparent 35%),
    linear-gradient(180deg, #f5efe5 0%, #ebe2d4 100%);
}

.main-page-card {
  width: min(680px, 100%);
  padding: 32px;
  border-radius: 24px;
  background: rgba(255, 252, 247, 0.9);
  box-shadow: 0 18px 50px rgba(62, 43, 19, 0.12);
  color: #2a241d;
}

.main-page-card.error {
  border: 1px solid rgba(160, 70, 70, 0.22);
}

.eyebrow {
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 12px;
  color: #8c6f4a;
}

h1 {
  margin: 0 0 12px;
  font-size: clamp(28px, 4vw, 42px);
}

p {
  margin: 0;
  line-height: 1.6;
}

.main-page-frame {
  display: block;
  width: 100%;
  min-height: 100vh;
  border: 0;
  background: #fff;
}
</style>
