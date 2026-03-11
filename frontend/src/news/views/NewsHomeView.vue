<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getArticles, getCategories, getHotArticles } from '../api/newsApi'

const route = useRoute()
const articles = ref([])
const hotArticles = ref([])
const categories = ref([])
const loading = ref(true)
const errorText = ref('')
const currentCategory = ref('')

function getCategoryDisplayName(category) {
  const names = {
    official: 'Official Announcements',
    breaking: 'Breaking News',
    community: 'Community News',
    investigation: 'Investigation Updates',
  }
  return names[category] || category
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function loadArticles() {
  loading.value = true
  errorText.value = ''
  try {
    const category = route.query.category || null
    currentCategory.value = category || 'all'
    articles.value = await getArticles(category)
  } catch (error) {
    articles.value = []
    errorText.value = 'Unable to load articles from server.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function loadInitialData() {
  loading.value = true
  errorText.value = ''
  try {
    categories.value = await getCategories()
    hotArticles.value = await getHotArticles(5)
    await loadArticles()
  } catch (error) {
    errorText.value = 'Unable to load news data.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(loadInitialData)
watch(() => route.query.category, loadArticles)
</script>

<template>
  <div class="news-home">
    <div v-if="loading" class="news-loading">
      <p>Loading news articles...</p>
      <p class="news-loading__small">Please wait while we fetch the latest updates.</p>
    </div>

    <div v-else-if="errorText" class="news-error">
      <h2>Unable to Load News</h2>
      <p>{{ errorText }}</p>
      <p class="news-error__small">Please try again later or contact the administrator.</p>
    </div>

    <div v-else class="news-content">
      <div class="news-section">
        <h2 class="news-section__title">
          {{ currentCategory === 'all' ? 'Latest News' : getCategoryDisplayName(currentCategory) }}
        </h2>

        <div v-if="articles.length === 0" class="news-empty">
          <p>No articles found in this category.</p>
          <RouterLink to="/news" class="news-link">View all articles</RouterLink>
        </div>

        <div v-else class="news-articles">
          <article
            v-for="article in articles"
            :key="article.article_id"
            class="news-article"
            :class="{ 'news-article--pinned': article.is_pinned }"
          >
            <div v-if="article.is_pinned" class="news-article__badge">PINNED</div>
            <h3 class="news-article__title">
              <RouterLink :to="`/news/article/${article.article_id}`">
                {{ article.title }}
              </RouterLink>
            </h3>
            <div class="news-article__meta">
              <span class="news-article__category">{{ getCategoryDisplayName(article.category) }}</span>
              <span class="news-article__separator">|</span>
              <span class="news-article__author">{{ article.author_id }}</span>
              <span class="news-article__separator">|</span>
              <span class="news-article__date">{{ formatDate(article.published_at) }}</span>
            </div>
            <p class="news-article__excerpt">{{ article.excerpt }}</p>
            <RouterLink :to="`/news/article/${article.article_id}`" class="news-article__readmore">
              Read more →
            </RouterLink>
          </article>
        </div>
      </div>

      <aside class="news-sidebar-content">
        <div class="news-sidebar-box">
          <h3 class="news-sidebar-box__title">Categories</h3>
          <ul class="news-sidebar-box__list">
            <li :class="{ active: currentCategory === 'all' }">
              <RouterLink to="/news">All News</RouterLink>
            </li>
            <li v-for="cat in categories" :key="cat.slug" :class="{ active: currentCategory === cat.slug }">
              <RouterLink :to="`/news?category=${cat.slug}`">{{ cat.name }}</RouterLink>
            </li>
          </ul>
        </div>

        <div v-if="hotArticles.length > 0" class="news-sidebar-box">
          <h3 class="news-sidebar-box__title">Hot Articles</h3>
          <ul class="news-sidebar-box__list news-sidebar-box__list--hot">
            <li v-for="article in hotArticles" :key="article.article_id">
              <RouterLink :to="`/news/article/${article.article_id}`">
                {{ article.title }}
              </RouterLink>
              <span class="news-sidebar-box__views">{{ article.views }} views</span>
            </li>
          </ul>
        </div>

        <div class="news-sidebar-box news-sidebar-box--ad">
          <h3 class="news-sidebar-box__title">Advertisement</h3>
          <div class="news-ad">
            <p class="news-ad__text">Visit our community forum for lively discussions!</p>
            <RouterLink to="/forum" class="news-ad__link">Go to Forum →</RouterLink>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.news-home {
  min-height: 400px;
}

.news-loading,
.news-error {
  text-align: center;
  padding: 3rem 1rem;
  color: #000000;
}

.news-loading h2,
.news-error h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #000080;
}

.news-loading__small,
.news-error__small {
  font-size: 0.9rem;
  color: #808080;
  font-style: italic;
}

.news-content {
  display: flex;
  gap: 2rem;
}

.news-section {
  flex: 1;
}

.news-section__title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #000080;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid #ffd700;
  font-family: 'Georgia', serif;
}

.news-empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #808080;
}

.news-link {
  color: #000080;
  text-decoration: underline;
}

.news-articles {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.news-article {
  background: #ffffff;
  border: 1px solid #808080;
  padding: 1.25rem;
  position: relative;
  transition: box-shadow 0.2s;
}

.news-article:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.news-article--pinned {
  border: 2px solid #ffd700;
  background: #fffff0;
}

.news-article__badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #ff0000;
  color: #ffffff;
  padding: 0.25rem 0.5rem;
  font-size: 0.7rem;
  font-weight: bold;
  text-transform: uppercase;
}

.news-article__title {
  font-size: 1.3rem;
  margin: 0 0 0.75rem 0;
  font-family: 'Georgia', serif;
}

.news-article__title a {
  color: #000080;
  text-decoration: none;
}

.news-article__title a:hover {
  color: #ff0000;
  text-decoration: underline;
}

.news-article__meta {
  font-size: 0.8rem;
  color: #808080;
  margin-bottom: 0.75rem;
  font-family: 'Arial', sans-serif;
}

.news-article__category {
  color: #000080;
  font-weight: bold;
  text-transform: uppercase;
}

.news-article__separator {
  margin: 0 0.5rem;
}

.news-article__excerpt {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #000000;
  margin-bottom: 0.75rem;
}

.news-article__readmore {
  color: #000080;
  font-weight: bold;
  text-decoration: none;
  font-size: 0.9rem;
}

.news-article__readmore:hover {
  text-decoration: underline;
  color: #ff0000;
}

.news-sidebar-content {
  width: 280px;
  flex-shrink: 0;
}

.news-sidebar-box {
  background: #f0f0f0;
  border: 1px solid #808080;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.news-sidebar-box__title {
  font-size: 1rem;
  font-weight: bold;
  color: #000080;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ffd700;
  text-transform: uppercase;
  font-family: 'Arial', sans-serif;
}

.news-sidebar-box__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.news-sidebar-box__list li {
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px dotted #808080;
}

.news-sidebar-box__list li:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.news-sidebar-box__list li.active a {
  color: #ff0000;
  font-weight: bold;
}

.news-sidebar-box__list a {
  color: #000080;
  text-decoration: none;
  font-size: 0.85rem;
}

.news-sidebar-box__list a:hover {
  text-decoration: underline;
}

.news-sidebar-box__list--hot li {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-sidebar-box__views {
  font-size: 0.75rem;
  color: #808080;
  font-style: italic;
}

.news-sidebar-box--ad {
  background: #fffff0;
  border: 2px dashed #ffd700;
}

.news-ad {
  text-align: center;
}

.news-ad__text {
  font-size: 0.85rem;
  color: #000000;
  margin-bottom: 0.75rem;
  font-style: italic;
}

.news-ad__link {
  display: inline-block;
  background: #000080;
  color: #ffffff;
  padding: 0.5rem 1rem;
  text-decoration: none;
  font-weight: bold;
  font-size: 0.85rem;
}

.news-ad__link:hover {
  background: #ffd700;
  color: #000080;
}

@media (max-width: 900px) {
  .news-content {
    flex-direction: column;
  }

  .news-sidebar-content {
    width: 100%;
  }
}
</style>
