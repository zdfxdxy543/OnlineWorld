const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }
  return response.json()
}

export function getNewsStats() {
  return request('/news/stats')
}

export function getCategories() {
  return request('/news/categories').then((data) => data.categories || [])
}

export function getArticles(category = null, limit = 20) {
  const params = new URLSearchParams()
  if (category) params.append('category', category)
  if (limit) params.append('limit', limit)
  const queryString = params.toString()
  return request(`/news/articles${queryString ? '?' + queryString : ''}`).then((data) => data.articles || [])
}

export function getArticle(articleId) {
  return request(`/news/articles/${articleId}`)
}

export function getHotArticles(limit = 5) {
  return request(`/news/hot-articles?limit=${limit}`).then((data) => data.articles || [])
}
