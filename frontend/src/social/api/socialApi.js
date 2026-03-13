const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
const DEFAULT_AUTHOR_ID = import.meta.env.VITE_SOCIAL_AUTHOR_ID || 'aria'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }
  return response.json()
}

export function getPosts(limit = 20, cursor = null, tag = null) {
  const params = new URLSearchParams()
  if (limit) params.append('limit', limit)
  if (cursor) params.append('cursor', cursor)
  if (tag) params.append('tag', tag)
  const queryString = params.toString()
  return request(`/social/posts${queryString ? '?' + queryString : ''}`).then((data) => ({
    posts: data.posts || [],
    nextCursor: data.next_cursor || null,
  }))
}

export function getPost(postId) {
  return request(`/social/posts/${postId}`)
}

export function createPost(content, tags = []) {
  return request('/social/posts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content, tags, author_id: DEFAULT_AUTHOR_ID }),
  }).then((data) => data || null)
}

export function createReply(postId, content) {
  return request('/social/replies', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ post_id: postId, content, author_id: DEFAULT_AUTHOR_ID }),
  }).then((data) => data || null)
}
