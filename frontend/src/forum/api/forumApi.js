const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }
  return response.json()
}

export function getForumStats() {
  return request('/forum/stats')
}

export function getBoards() {
  return request('/forum/boards')
}

export function getHotThreads(limit = 5) {
  return request(`/forum/hot-threads?limit=${limit}`)
}

export function getBoardThreads(boardSlug) {
  return request(`/forum/boards/${boardSlug}/threads`)
}

export function getThread(threadId) {
  return request(`/forum/threads/${threadId}`)
}

export function getUserProfile(userId) {
  return request(`/forum/users/${userId}`)
}
