<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPaperById, getDownloadUrl } from '../api/academicApi'

const route = useRoute()
const router = useRouter()
const paper = ref(null)
const loading = ref(true)
const error = ref('')
const downloading = ref(false)

onMounted(async () => {
  const paperId = route.params.paperId
  try {
    paper.value = await getPaperById(paperId)
  } catch (err) {
    error.value = 'Paper not found'
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function handleDownload() {
  if (!paper.value) return
  downloading.value = true
  const url = getDownloadUrl(paper.value.paper_id)
  setTimeout(() => {
    alert(`Downloading: ${paper.value.file_name}\nFile size: ${formatSize(paper.value.file_size)}`)
    downloading.value = false
  }, 500)
}

function handleReadOnline() {
  if (!paper.value) return
  alert(`Opening online reader: ${paper.value.title}`)
}
</script>

<template>
  <div class="academic-detail">
    <div v-if="loading" class="academic-detail__loading">
      Loading paper information...
    </div>
    
    <div v-else-if="error" class="academic-detail__error">
      <h2>{{ error }}</h2>
      <p>The paper you are looking for does not exist or has been removed.</p>
      <RouterLink to="/academic/search" class="academic-detail__back-link">Back to Search</RouterLink>
    </div>
    
    <div v-else class="academic-detail__content">
      <div class="academic-detail__breadcrumb">
        <RouterLink to="/academic">Home</RouterLink>
        <span class="academic-detail__separator">&gt;</span>
        <RouterLink to="/academic/search">Search</RouterLink>
        <span class="academic-detail__separator">&gt;</span>
        <span>Paper Details</span>
      </div>
      
      <div class="academic-detail__header">
        <h1 class="academic-detail__title">{{ paper.title }}</h1>
        <div class="academic-detail__actions">
          <button class="academic-detail__btn academic-detail__btn--read" @click="handleReadOnline">
            Read Online
          </button>
          <button class="academic-detail__btn academic-detail__btn--download" @click="handleDownload" :disabled="downloading">
            {{ downloading ? 'Downloading...' : 'Download Full Text' }}
          </button>
        </div>
      </div>
      
      <div class="academic-detail__info">
        <div class="academic-detail__row">
          <span class="academic-detail__label">Author(s):</span>
          <span class="academic-detail__value">{{ paper.authors.join(', ') }}</span>
        </div>
        <div class="academic-detail__row">
          <span class="academic-detail__label">Institution:</span>
          <span class="academic-detail__value">{{ paper.institution }}</span>
        </div>
        <div class="academic-detail__row">
          <span class="academic-detail__label">Journal:</span>
          <span class="academic-detail__value">{{ paper.journal }}</span>
        </div>
        <div class="academic-detail__row">
          <span class="academic-detail__label">Published:</span>
          <span class="academic-detail__value">{{ formatDate(paper.publish_date) }}</span>
        </div>
        <div class="academic-detail__row">
          <span class="academic-detail__label">Keywords:</span>
          <span class="academic-detail__value">
            <span v-for="(kw, idx) in paper.keywords" :key="kw" class="academic-detail__keyword">
              {{ kw }}<span v-if="idx < paper.keywords.length - 1">, </span>
            </span>
          </span>
        </div>
        <div class="academic-detail__row">
          <span class="academic-detail__label">Pages:</span>
          <span class="academic-detail__value">{{ paper.pages }} pages</span>
        </div>
        <div class="academic-detail__row">
          <span class="academic-detail__label">File Size:</span>
          <span class="academic-detail__value">{{ formatSize(paper.file_size) }}</span>
        </div>
        <div class="academic-detail__row">
          <span class="academic-detail__label">Downloads:</span>
          <span class="academic-detail__value academic-detail__value--highlight">{{ paper.downloads }} times</span>
        </div>
      </div>
      
      <div class="academic-detail__section">
        <h2 class="academic-detail__section-title">Abstract</h2>
        <p class="academic-detail__abstract">{{ paper.abstract }}</p>
      </div>
      
      <div class="academic-detail__section">
        <h2 class="academic-detail__section-title">Full Text Preview</h2>
        <div class="academic-detail__preview">
          <div class="academic-detail__preview-placeholder">
            <div class="academic-detail__preview-icon">PDF</div>
            <p>This paper is in PDF format, {{ paper.pages }} pages total</p>
            <p class="academic-detail__preview-hint">Click "Read Online" or "Download Full Text" to view the complete content</p>
          </div>
        </div>
      </div>
      
      <div class="academic-detail__nav">
        <RouterLink to="/academic/search" class="academic-detail__back-link">Back to Search Results</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.academic-detail {
  padding: 15px;
}

.academic-detail__loading,
.academic-detail__error {
  text-align: center;
  padding: 60px;
  color: #666;
  font-size: 14px;
}

.academic-detail__error h2 {
  color: #c53030;
  margin-bottom: 10px;
}

.academic-detail__breadcrumb {
  padding: 10px 15px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  margin-bottom: 20px;
  font-size: 12px;
}

.academic-detail__breadcrumb a {
  color: #1a4971;
  text-decoration: none;
}

.academic-detail__breadcrumb a:hover {
  text-decoration: underline;
}

.academic-detail__separator {
  margin: 0 8px;
  color: #999;
}

.academic-detail__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #a8c8e0;
}

.academic-detail__title {
  margin: 0;
  color: #1a4971;
  font-size: 20px;
  line-height: 1.4;
  flex: 1;
  padding-right: 20px;
}

.academic-detail__actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.academic-detail__btn {
  padding: 8px 20px;
  font-size: 13px;
  border: none;
  cursor: pointer;
  text-decoration: none;
}

.academic-detail__btn--read {
  background: #2b6cb0;
  color: #fff;
}

.academic-detail__btn--read:hover {
  background: #1a4971;
}

.academic-detail__btn--download {
  background: #c53030;
  color: #fff;
}

.academic-detail__btn--download:hover {
  background: #9b2c2c;
}

.academic-detail__btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.academic-detail__info {
  background: #f8fafc;
  border: 1px solid #e0e0e0;
  padding: 15px 20px;
  margin-bottom: 20px;
}

.academic-detail__row {
  display: flex;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px dashed #e8e8e8;
}

.academic-detail__row:last-child {
  border-bottom: none;
}

.academic-detail__label {
  color: #666;
  width: 100px;
  flex-shrink: 0;
}

.academic-detail__value {
  color: #333;
  flex: 1;
}

.academic-detail__value--highlight {
  color: #c53030;
  font-weight: bold;
}

.academic-detail__keyword {
  color: #2b6cb0;
}

.academic-detail__section {
  margin-bottom: 25px;
}

.academic-detail__section-title {
  margin: 0 0 12px;
  padding: 8px 12px;
  background: #e8f4f8;
  border-left: 4px solid #2b6cb0;
  color: #1a4971;
  font-size: 15px;
}

.academic-detail__abstract {
  margin: 0;
  font-size: 13px;
  line-height: 1.8;
  color: #333;
  text-align: justify;
}

.academic-detail__preview {
  border: 1px solid #e0e0e0;
  min-height: 200px;
}

.academic-detail__preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fafafa;
  color: #666;
}

.academic-detail__preview-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 70px;
  background: #c53030;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
}

.academic-detail__preview-hint {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.academic-detail__nav {
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.academic-detail__back-link {
  color: #2b6cb0;
  text-decoration: none;
  font-size: 13px;
}

.academic-detail__back-link:hover {
  text-decoration: underline;
}
</style>
