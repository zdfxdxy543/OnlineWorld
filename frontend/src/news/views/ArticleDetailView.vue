<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getArticle } from '../api/newsApi'

const route = useRoute()
const article = ref(null)
const loading = ref(true)
const errorText = ref('')

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

async function loadArticle() {
  loading.value = true
  errorText.value = ''
  try {
    article.value = await getArticle(route.params.articleId)
  } catch (error) {
    article.value = null
    errorText.value = 'Unable to load article from server.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(loadArticle)
</script>

<template>
  <div class="news-article-detail">
    <div v-if="loading" class="news-loading">
      <p>Loading article...</p>
      <p class="news-loading__small">Please wait while we fetch the content.</p>
    </div>

    <div v-else-if="errorText" class="news-error">
      <h2>Article Not Found</h2>
      <p>{{ errorText }}</p>
      <p class="news-error__small">The article may have been removed or the link is incorrect.</p>
      <RouterLink to="/news" class="news-link">← Back to News Home</RouterLink>
    </div>

    <article v-else-if="article" class="news-article-content">
      <header class="news-article-header">
        <div class="news-article-header__meta">
          <span class="news-article-header__category">
            {{ getCategoryDisplayName(article.category) }}
          </span>
          <span v-if="article.is_pinned" class="news-article-header__badge">PINNED</span>
        </div>
        <h1 class="news-article-header__title">{{ article.title }}</h1>
        <div class="news-article-header__info">
          <span class="news-article-header__author">By {{ article.author_id }}</span>
          <span class="news-article-header__separator">|</span>
          <span class="news-article-header__date">{{ formatDate(article.published_at) }}</span>
          <span class="news-article-header__separator">|</span>
          <span class="news-article-header__views">{{ article.views }} views</span>
        </div>
      </header>

      <div class="news-article-body">
        <div class="news-article-body__content" v-html="article.content"></div>
      </div>

      <footer class="news-article-footer">
        <div class="news-article-footer__actions">
          <RouterLink to="/news" class="news-article-footer__link">← Back to News</RouterLink>
          <button type="button" class="news-article-footer__button">Print Article</button>
          <button type="button" class="news-article-footer__button">Share</button>
        </div>

        <div v-if="article.related_thread_ids && article.related_thread_ids.length > 0" class="news-article-footer__related">
          <h3 class="news-article-footer__related-title">Related Forum Discussions</h3>
          <ul class="news-article-footer__related-list">
            <li v-for="threadId in article.related_thread_ids" :key="threadId">
              <RouterLink :to="`/forum/thread/${threadId}`">
                View discussion in forum →
              </RouterLink>
            </li>
          </ul>
        </div>

        <div v-if="article.related_share_ids && article.related_share_ids.length > 0" class="news-article-footer__related">
          <h3 class="news-article-footer__related-title">Related Documents</h3>
          <ul class="news-article-footer__related-list">
            <li v-for="shareId in article.related_share_ids" :key="shareId">
              <RouterLink :to="`/netdisk?share=${shareId}`">
                View document in archive →
              </RouterLink>
            </li>
          </ul>
        </div>
      </footer>
    </article>
  </div>
</template>

<style scoped>
.news-article-detail {
  min-height: 500px;
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

.news-link {
  display: inline-block;
  margin-top: 1rem;
  color: #000080;
  text-decoration: underline;
}

.news-article-content {
  background: #ffffff;
  border: 1px solid #808080;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.news-article-header {
  border-bottom: 3px solid #ffd700;
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
}

.news-article-header__meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.news-article-header__category {
  background: #000080;
  color: #ffffff;
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.news-article-header__badge {
  background: #ff0000;
  color: #ffffff;
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
}

.news-article-header__title {
  font-size: 2rem;
  font-weight: bold;
  color: #000000;
  margin: 0 0 1rem 0;
  line-height: 1.3;
  font-family: 'Georgia', serif;
}

.news-article-header__info {
  font-size: 0.85rem;
  color: #808080;
  font-family: 'Arial', sans-serif;
}

.news-article-header__author {
  color: #000080;
  font-weight: bold;
}

.news-article-header__separator {
  margin: 0 0.5rem;
}

.news-article-body {
  margin-bottom: 2rem;
}

.news-article-body__content {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #000000;
  font-family: 'Times New Roman', Times, serif;
}

.news-article-body__content :deep(p) {
  margin-bottom: 1rem;
}

.news-article-body__content :deep(h2) {
  font-size: 1.4rem;
  color: #000080;
  margin: 1.5rem 0 0.75rem 0;
  font-family: 'Georgia', serif;
  border-bottom: 1px solid #808080;
  padding-bottom: 0.25rem;
}

.news-article-body__content :deep(h3) {
  font-size: 1.2rem;
  color: #000080;
  margin: 1.25rem 0 0.5rem 0;
  font-family: 'Georgia', serif;
}

.news-article-body__content :deep(ul),
.news-article-body__content :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.news-article-body__content :deep(li) {
  margin-bottom: 0.5rem;
}

.news-article-body__content :deep(blockquote) {
  border-left: 4px solid #ffd700;
  padding-left: 1rem;
  margin: 1.5rem 0;
  font-style: italic;
  color: #808080;
  background: #f5f5dc;
  padding: 1rem;
}

.news-article-body__content :deep(strong) {
  color: #000080;
  font-weight: bold;
}

.news-article-footer {
  border-top: 2px solid #808080;
  padding-top: 1.5rem;
}

.news-article-footer__actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.news-article-footer__link {
  display: inline-block;
  background: #000080;
  color: #ffffff;
  padding: 0.6rem 1.2rem;
  text-decoration: none;
  font-weight: bold;
  font-size: 0.85rem;
  border: 1px solid #000080;
}

.news-article-footer__link:hover {
  background: #ffd700;
  color: #000080;
  border-color: #ffd700;
}

.news-article-footer__button {
  background: #ffffff;
  color: #000000;
  padding: 0.6rem 1.2rem;
  font-weight: bold;
  font-size: 0.85rem;
  border: 1px solid #808080;
  cursor: pointer;
  font-family: 'Arial', sans-serif;
}

.news-article-footer__button:hover {
  background: #f0f0f0;
  border-color: #000000;
}

.news-article-footer__related {
  background: #f5f5dc;
  border: 1px solid #808080;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
}

.news-article-footer__related-title {
  font-size: 1rem;
  font-weight: bold;
  color: #000080;
  margin: 0 0 0.75rem 0;
  text-transform: uppercase;
  font-family: 'Arial', sans-serif;
}

.news-article-footer__related-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.news-article-footer__related-list li {
  margin-bottom: 0.5rem;
}

.news-article-footer__related-list a {
  color: #000080;
  text-decoration: none;
  font-size: 0.9rem;
}

.news-article-footer__related-list a:hover {
  text-decoration: underline;
  color: #ff0000;
}

@media (max-width: 768px) {
  .news-article-content {
    padding: 1.5rem;
  }

  .news-article-header__title {
    font-size: 1.5rem;
  }

  .news-article-body__content {
    font-size: 1rem;
  }

  .news-article-footer__actions {
    flex-direction: column;
  }

  .news-article-footer__link,
  .news-article-footer__button {
    width: 100%;
    text-align: center;
  }
}
</style>
