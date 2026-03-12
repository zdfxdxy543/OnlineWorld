<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { getFileContent, getFileDownloadUrl } from '../api/netdiskApi'

const route = useRoute()
const form = ref({
  fileId: String(route.query.share || '').trim(),
  accessCode: '',
})

const loading = ref(false)
const openedFile = ref(null)
const error = ref('')

async function handleOpenFile() {
  error.value = ''
  openedFile.value = null

  const fileId = form.value.fileId.trim()
  const accessCode = form.value.accessCode.trim()

  if (!fileId || !accessCode) {
    error.value = '请输入文件ID和访问密码。'
    return
  }

  loading.value = true
  try {
    openedFile.value = await getFileContent(fileId, accessCode)
  } catch (err) {
    error.value = err?.message || '文件获取失败，请检查文件ID和密码。'
  } finally {
    loading.value = false
  }
}

function handleDownload() {
  if (!openedFile.value) {
    return
  }
  const fileId = form.value.fileId.trim()
  const accessCode = form.value.accessCode.trim()
  window.open(getFileDownloadUrl(fileId, accessCode), '_blank')
}

function formatSize(bytes) {
  if (!Number.isFinite(bytes)) {
    return '-'
  }
  if (bytes < 1024) {
    return `${bytes} B`
  }
  return `${(bytes / 1024).toFixed(1)} KB`
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}
</script>

<template>
  <div class="nd-access-page">
    <section class="nd-panel nd-panel--form">
      <h1 class="nd-title">文件获取</h1>
      <p class="nd-subtitle">输入分享文件 ID（share_id）与访问密码后可查看并下载文件。</p>

      <p v-if="error" class="nd-error">{{ error }}</p>

      <form class="nd-form" @submit.prevent="handleOpenFile">
        <label class="nd-label" for="resource-id">文件 ID（share_id）</label>
        <input
          id="resource-id"
          v-model="form.fileId"
          class="nd-input"
          type="text"
          placeholder="例如: sh-00009"
          autocomplete="off"
          required
        />

        <label class="nd-label" for="access-code">访问密码</label>
        <input
          id="access-code"
          v-model="form.accessCode"
          class="nd-input"
          type="text"
          placeholder="例如: A1B2C3"
          autocomplete="off"
          required
        />

        <button class="nd-btn nd-btn--primary" type="submit" :disabled="loading">
          {{ loading ? '正在获取...' : '打开文件' }}
        </button>
      </form>
    </section>

    <section class="nd-panel nd-panel--viewer">
      <template v-if="!openedFile">
        <div class="nd-empty">请先输入正确的文件 ID 与访问密码。</div>
      </template>

      <template v-else>
        <header class="nd-file-header">
          <div class="nd-file-meta">
            <h2 class="nd-file-title">{{ openedFile.title }}</h2>
            <p class="nd-file-sub">
              {{ openedFile.file_name }} · {{ formatSize(openedFile.size_bytes) }} · {{ formatDate(openedFile.created_at) }}
            </p>
          </div>
          <button class="nd-btn nd-btn--download" @click="handleDownload">下载到本地</button>
        </header>

        <pre class="nd-content">{{ openedFile.content }}</pre>
      </template>
    </section>
  </div>
</template>

<style scoped>
*,
*::before,
*::after {
  box-sizing: border-box;
}

.nd-access-page {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 1rem;
  align-items: start;
}

.nd-panel {
  border: 2px solid #a5d6a7;
  border-radius: 6px;
  background: #f1f8e9;
}

.nd-panel--form {
  padding: 1rem;
}

.nd-title {
  margin: 0;
  color: #1b5e20;
  font-size: 1.2rem;
  font-weight: 700;
}

.nd-subtitle {
  margin: 0.5rem 0 1rem;
  color: #33691e;
  font-size: 0.88rem;
}

.nd-error {
  margin: 0 0 0.8rem;
  border: 1px solid #e57373;
  border-radius: 4px;
  background: #ffebee;
  color: #b71c1c;
  padding: 0.5rem 0.6rem;
  font-size: 0.84rem;
}

.nd-form {
  display: grid;
  gap: 0.55rem;
}

.nd-label {
  color: #2e7d32;
  font-size: 0.82rem;
  font-weight: 700;
}

.nd-input {
  width: 100%;
  border: 1px solid #66bb6a;
  border-radius: 4px;
  padding: 0.48rem 0.55rem;
  background: #ffffff;
  color: #1b3a1f;
  font-size: 0.9rem;
}

.nd-btn {
  border: 1px solid #2e7d32;
  border-radius: 4px;
  padding: 0.48rem 0.75rem;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
}

.nd-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.nd-btn--primary {
  margin-top: 0.35rem;
  background: #2e7d32;
  color: #e8f5e9;
}

.nd-btn--primary:hover:not(:disabled) {
  background: #1b5e20;
}

.nd-panel--viewer {
  min-height: 420px;
  background: #f9fbe7;
  overflow: hidden;
}

.nd-empty {
  color: #689f38;
  padding: 2.2rem 1.4rem;
  font-size: 0.92rem;
}

.nd-file-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.8rem;
  padding: 0.8rem 1rem;
  border-bottom: 2px solid #c5e1a5;
  background: #dcedc8;
}

.nd-file-title {
  margin: 0;
  color: #1b5e20;
  font-size: 1rem;
}

.nd-file-sub {
  margin: 0.25rem 0 0;
  color: #558b2f;
  font-size: 0.78rem;
}

.nd-btn--download {
  background: #2e7d32;
  color: #e8f5e9;
  flex-shrink: 0;
}

.nd-btn--download:hover {
  background: #1b5e20;
}

.nd-content {
  margin: 0;
  padding: 0.95rem 1rem;
  white-space: pre-wrap;
  word-break: break-word;
  color: #1b3a1f;
  font-size: 0.85rem;
  line-height: 1.62;
  max-height: 620px;
  overflow-y: auto;
}

@media (max-width: 900px) {
  .nd-access-page {
    grid-template-columns: 1fr;
  }
}
</style>
