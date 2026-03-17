<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getPapers, getCategories } from '../api/academicApi'

const route = useRoute()
const papers = ref([])
const categories = ref([])
const loading = ref(true)
const searchForm = ref({
  keyword: '',
  field: 'title',
  category: '',
  yearStart: '',
  yearEnd: '',
})

onMounted(async () => {
  categories.value = await getCategories()
  await handleSearch()
})

watch(() => route.query, async () => {
  if (route.query.q) {
    searchForm.value.keyword = route.query.q
  }
  if (route.query.category) {
    searchForm.value.category = route.query.category
  }
  await handleSearch()
}, { immediate: true })

async function handleSearch() {
  loading.value = true
  const allPapers = await getPapers()
  
  let filtered = [...allPapers]
  
  if (searchForm.value.keyword) {
    const kw = searchForm.value.keyword.toLowerCase()
    filtered = filtered.filter(p => {
      if (searchForm.value.field === 'title') {
        return p.title.toLowerCase().includes(kw)
      } else if (searchForm.value.field === 'author') {
        return p.authors.some(a => a.toLowerCase().includes(kw))
      } else if (searchForm.value.field === 'keyword') {
        return p.keywords.some(k => k.toLowerCase().includes(kw))
      } else if (searchForm.value.field === 'abstract') {
        return p.abstract.toLowerCase().includes(kw)
      }
      return true
    })
  }
  
  papers.value = filtered
  loading.value = false
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function resetSearch() {
  searchForm.value = {
    keyword: '',
    field: 'title',
    category: '',
    yearStart: '',
    yearEnd: '',
  }
  handleSearch()
}
</script>

<template>
  <div class="academic-search">
    <div class="academic-search__box">
      <h2 class="academic-search__title">Search Papers</h2>
      <div class="academic-search__form">
        <div class="academic-search__row">
          <label class="academic-search__label">Keywords:</label>
          <input 
            v-model="searchForm.keyword" 
            type="text" 
            class="academic-search__input"
            placeholder="Enter search terms..."
            @keyup.enter="handleSearch"
          />
          <select v-model="searchForm.field" class="academic-search__select">
            <option value="title">Title</option>
            <option value="author">Author</option>
            <option value="keyword">Keyword</option>
            <option value="abstract">Abstract</option>
          </select>
        </div>
        <div class="academic-search__row">
          <label class="academic-search__label">Category:</label>
          <select v-model="searchForm.category" class="academic-search__select">
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <label class="academic-search__label academic-search__label--date">Year:</label>
          <input 
            v-model="searchForm.yearStart" 
            type="text" 
            class="academic-search__input academic-search__input--year"
            placeholder="From"
          />
          <span class="academic-search__separator">to</span>
          <input 
            v-model="searchForm.yearEnd" 
            type="text" 
            class="academic-search__input academic-search__input--year"
            placeholder="To"
          />
        </div>
        <div class="academic-search__buttons">
          <button class="academic-search__btn academic-search__btn--primary" @click="handleSearch">Search</button>
          <button class="academic-search__btn" @click="resetSearch">Reset</button>
        </div>
      </div>
    </div>

    <div class="academic-search__results">
      <div class="academic-search__results-header">
        <span class="academic-search__count">Found {{ papers.length }} results</span>
      </div>
      
      <div v-if="loading" class="academic-search__loading">
        Searching, please wait...
      </div>
      
      <div v-else-if="papers.length === 0" class="academic-search__empty">
        No matching papers found. Please try different search terms.
      </div>
      
      <div v-else class="academic-paper-list">
        <div v-for="(paper, index) in papers" :key="paper.paper_id" class="academic-paper-card">
          <div class="academic-paper-card__index">{{ index + 1 }}</div>
          <div class="academic-paper-card__body">
            <h3 class="academic-paper-card__title">
              <RouterLink :to="`/academic/paper/${paper.paper_id}`">{{ paper.title }}</RouterLink>
            </h3>
            <div class="academic-paper-card__meta">
              <span class="academic-paper-card__label">Author(s):</span>
              <span>{{ paper.authors.join(', ') }}</span>
            </div>
            <div class="academic-paper-card__meta">
              <span class="academic-paper-card__label">Institution:</span>
              <span>{{ paper.institution }}</span>
            </div>
            <div class="academic-paper-card__meta">
              <span class="academic-paper-card__label">Journal:</span>
              <span>{{ paper.journal }}</span>
              <span class="academic-paper-card__separator">|</span>
              <span>{{ formatDate(paper.publish_date) }}</span>
            </div>
            <div class="academic-paper-card__meta">
              <span class="academic-paper-card__label">Keywords:</span>
              <span>{{ paper.keywords.join(', ') }}</span>
            </div>
            <p class="academic-paper-card__abstract">{{ paper.abstract }}</p>
            <div class="academic-paper-card__footer">
              <RouterLink :to="`/academic/paper/${paper.paper_id}`" class="academic-paper-card__link">View Details</RouterLink>
              <span class="academic-paper-card__stats">{{ paper.downloads }} downloads</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.academic-search {
  padding: 15px;
}

.academic-search__box {
  background: #f0f7fc;
  border: 1px solid #a8c8e0;
  padding: 20px;
  margin-bottom: 20px;
}

.academic-search__title {
  margin: 0 0 15px;
  color: #1a4971;
  font-size: 16px;
  border-bottom: 1px solid #a8c8e0;
  padding-bottom: 8px;
}

.academic-search__row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.academic-search__label {
  color: #333;
  font-size: 13px;
  white-space: nowrap;
}

.academic-search__label--date {
  margin-left: 20px;
}

.academic-search__input {
  flex: 1;
  height: 28px;
  border: 1px solid #a8c8e0;
  padding: 0 10px;
  font-size: 13px;
  max-width: 300px;
}

.academic-search__input--year {
  width: 80px;
  max-width: 80px;
}

.academic-search__select {
  height: 28px;
  border: 1px solid #a8c8e0;
  padding: 0 8px;
  font-size: 13px;
  background: #fff;
  min-width: 120px;
}

.academic-search__separator {
  color: #666;
  font-size: 13px;
}

.academic-search__buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.academic-search__btn {
  padding: 6px 25px;
  font-size: 13px;
  border: 1px solid #2b6cb0;
  background: #fff;
  color: #2b6cb0;
  cursor: pointer;
}

.academic-search__btn:hover {
  background: #e8f4f8;
}

.academic-search__btn--primary {
  background: #2b6cb0;
  color: #fff;
}

.academic-search__btn--primary:hover {
  background: #1a4971;
}

.academic-search__results {
  min-height: 300px;
}

.academic-search__results-header {
  padding: 10px 15px;
  background: #e8f4f8;
  border: 1px solid #a8c8e0;
  margin-bottom: 15px;
}

.academic-search__count {
  color: #1a4971;
  font-size: 13px;
  font-weight: bold;
}

.academic-search__loading,
.academic-search__empty {
  text-align: center;
  padding: 60px;
  color: #666;
  font-size: 14px;
}

.academic-paper-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.academic-paper-card {
  display: flex;
  gap: 15px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  background: #fff;
}

.academic-paper-card:hover {
  border-color: #a8c8e0;
  background: #fafafa;
}

.academic-paper-card__index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #2b6cb0;
  color: #fff;
  font-size: 13px;
  font-weight: bold;
  flex-shrink: 0;
}

.academic-paper-card__body {
  flex: 1;
}

.academic-paper-card__title {
  margin: 0 0 10px;
  font-size: 15px;
}

.academic-paper-card__title a {
  color: #1a4971;
  text-decoration: none;
}

.academic-paper-card__title a:hover {
  color: #c53030;
  text-decoration: underline;
}

.academic-paper-card__meta {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.academic-paper-card__label {
  color: #333;
}

.academic-paper-card__separator {
  margin: 0 8px;
  color: #ccc;
}

.academic-paper-card__abstract {
  margin: 10px 0;
  font-size: 12px;
  color: #555;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.academic-paper-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.academic-paper-card__link {
  color: #2b6cb0;
  text-decoration: none;
  font-size: 12px;
}

.academic-paper-card__link:hover {
  text-decoration: underline;
}

.academic-paper-card__stats {
  font-size: 11px;
  color: #888;
}
</style>
