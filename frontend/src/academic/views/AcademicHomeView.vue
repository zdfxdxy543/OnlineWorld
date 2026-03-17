<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getHotPapers, getPapers } from '../api/academicApi'

const hotPapers = ref([])
const latestPapers = ref([])
const loading = ref(true)

onMounted(async () => {
  loading.value = true
  hotPapers.value = await getHotPapers(5)
  latestPapers.value = await getPapers()
  loading.value = false
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
</script>

<template>
  <div class="academic-home">
    <div class="academic-welcome">
      <h2 class="academic-welcome__title">Welcome to Academic Library</h2>
      <p class="academic-welcome__desc">
        Access academic journals, theses, conference papers and more from 1990-2001. 
        Comprehensive academic research resources at your fingertips.
      </p>
    </div>

    <div class="academic-section">
      <h3 class="academic-section__title">
        <span class="academic-section__icon">H</span>
        Hot Papers
      </h3>
      <div class="academic-paper-list">
        <div v-for="paper in hotPapers" :key="paper.paper_id" class="academic-paper-item">
          <div class="academic-paper-item__rank">{{ hotPapers.indexOf(paper) + 1 }}</div>
          <div class="academic-paper-item__content">
            <h4 class="academic-paper-item__title">
              <RouterLink :to="`/academic/paper/${paper.paper_id}`">{{ paper.title }}</RouterLink>
            </h4>
            <div class="academic-paper-item__meta">
              <span class="academic-paper-item__author">{{ paper.authors.join(', ') }}</span>
              <span class="academic-paper-item__separator">|</span>
              <span class="academic-paper-item__journal">{{ paper.journal }}</span>
            </div>
            <div class="academic-paper-item__stats">
              <span>Downloads: {{ paper.downloads }}</span>
              <span class="academic-paper-item__separator">|</span>
              <span>{{ paper.pages }} pages</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="academic-section">
      <h3 class="academic-section__title">
        <span class="academic-section__icon">N</span>
        New Arrivals
      </h3>
      <table class="academic-table">
        <thead>
          <tr>
            <th class="academic-table__col-title">Title</th>
            <th class="academic-table__col-author">Author(s)</th>
            <th class="academic-table__col-journal">Journal</th>
            <th class="academic-table__col-date">Date</th>
            <th class="academic-table__col-downloads">Downloads</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="paper in latestPapers" :key="paper.paper_id">
            <td class="academic-table__col-title">
              <RouterLink :to="`/academic/paper/${paper.paper_id}`">{{ paper.title }}</RouterLink>
            </td>
            <td class="academic-table__col-author">{{ paper.authors.join(', ') }}</td>
            <td class="academic-table__col-journal">{{ paper.journal }}</td>
            <td class="academic-table__col-date">{{ formatDate(paper.publish_date) }}</td>
            <td class="academic-table__col-downloads">{{ paper.downloads }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="academic-section academic-section--stats">
      <h3 class="academic-section__title">Database Statistics</h3>
      <div class="academic-stats">
        <div class="academic-stats__item">
          <div class="academic-stats__value">128,456</div>
          <div class="academic-stats__label">Total Papers</div>
        </div>
        <div class="academic-stats__item">
          <div class="academic-stats__value">3,892</div>
          <div class="academic-stats__label">Journals</div>
        </div>
        <div class="academic-stats__item">
          <div class="academic-stats__value">89,234</div>
          <div class="academic-stats__label">Theses</div>
        </div>
        <div class="academic-stats__item">
          <div class="academic-stats__value">15,678</div>
          <div class="academic-stats__label">Conference Papers</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.academic-home {
  padding: 15px;
}

.academic-welcome {
  background: linear-gradient(to bottom, #f0f7fc 0%, #e8f4f8 100%);
  border: 1px solid #a8c8e0;
  padding: 20px;
  margin-bottom: 20px;
}

.academic-welcome__title {
  margin: 0 0 10px;
  color: #1a4971;
  font-size: 18px;
  font-weight: bold;
}

.academic-welcome__desc {
  margin: 0;
  color: #333;
  font-size: 13px;
  line-height: 1.6;
}

.academic-section {
  margin-bottom: 25px;
}

.academic-section__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px;
  padding: 8px 12px;
  background: #e8f4f8;
  border-left: 4px solid #2b6cb0;
  color: #1a4971;
  font-size: 15px;
}

.academic-section__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #c53030;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
}

.academic-paper-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.academic-paper-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px;
  background: #fafafa;
  border: 1px solid #e0e0e0;
}

.academic-paper-item__rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #2b6cb0;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.academic-paper-item__content {
  flex: 1;
}

.academic-paper-item__title {
  margin: 0 0 6px;
  font-size: 14px;
}

.academic-paper-item__title a {
  color: #1a4971;
  text-decoration: none;
}

.academic-paper-item__title a:hover {
  color: #c53030;
  text-decoration: underline;
}

.academic-paper-item__meta {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.academic-paper-item__separator {
  margin: 0 6px;
  color: #ccc;
}

.academic-paper-item__stats {
  font-size: 11px;
  color: #888;
}

.academic-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.academic-table th {
  background: #e8f4f8;
  color: #1a4971;
  font-weight: bold;
  padding: 8px;
  text-align: left;
  border-bottom: 2px solid #a8c8e0;
}

.academic-table td {
  padding: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.academic-table__col-title {
  width: 45%;
}

.academic-table__col-title a {
  color: #1a4971;
  text-decoration: none;
}

.academic-table__col-title a:hover {
  color: #c53030;
  text-decoration: underline;
}

.academic-table__col-author {
  width: 20%;
}

.academic-table__col-journal {
  width: 20%;
}

.academic-table__col-date {
  width: 10%;
}

.academic-table__col-downloads {
  width: 5%;
  text-align: center;
}

.academic-table tr:hover {
  background: #f5f9fc;
}

.academic-section--stats {
  background: #f0f7fc;
  padding: 15px;
  border: 1px solid #a8c8e0;
}

.academic-stats {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.academic-stats__item {
  padding: 10px;
}

.academic-stats__value {
  font-size: 24px;
  font-weight: bold;
  color: #c53030;
}

.academic-stats__label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
</style>
