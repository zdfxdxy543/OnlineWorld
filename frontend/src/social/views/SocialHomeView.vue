<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getPosts, createPost, createReply } from '../api/socialApi'

const route = useRoute()
const posts = ref([])
const loading = ref(true)
const errorText = ref('')
const currentTag = ref('')
const nextCursor = ref(null)
const loadingMore = ref(false)

const newPostContent = ref('')
const showNewPostForm = ref(false)
const replyContents = ref({})
const showReplyForms = ref({})

function getTagDisplayName(tag) {
  const names = {
    daily: 'Daily Life',
    food: 'Food & Dining',
    travel: 'Travel & Adventure',
    mystery: 'Mystery & Clues',
  }
  return names[tag] || tag
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getAvatar(userId) {
  return `https://via.placeholder.com/40x40?text=${encodeURIComponent(userId.charAt(0).toUpperCase())}`
}

async function loadPosts(cursor = null) {
  if (cursor) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  errorText.value = ''
  try {
    const tag = route.query.tag || null
    currentTag.value = tag || 'all'
    const result = await getPosts(10, cursor, tag)
    if (cursor) {
      posts.value = [...posts.value, ...result.posts]
    } else {
      posts.value = result.posts
    }
    nextCursor.value = result.nextCursor
  } catch (error) {
    posts.value = []
    errorText.value = 'Unable to load posts from server.'
    console.error(error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function handleCreatePost() {
  if (!newPostContent.value.trim()) return
  
  try {
    const tags = currentTag.value !== 'all' ? [currentTag.value] : []
    const newPost = await createPost(newPostContent.value, tags)
    if (newPost) {
      posts.value.unshift(newPost)
      newPostContent.value = ''
      showNewPostForm.value = false
    }
  } catch (error) {
    errorText.value = 'Failed to create post.'
    console.error(error)
  }
}

async function handleReply(postId) {
  const content = replyContents.value[postId]
  if (!content || !content.trim()) return
  
  try {
    const newReply = await createReply(postId, content)
    if (newReply) {
      const post = posts.value.find(p => p.id === postId)
      if (post) {
        if (!post.replies) {
          post.replies = []
        }
        post.replies.push(newReply)
      }
      replyContents.value[postId] = ''
      showReplyForms.value[postId] = false
    }
  } catch (error) {
    errorText.value = 'Failed to post reply.'
    console.error(error)
  }
}

function toggleReplyForm(postId) {
  showReplyForms.value[postId] = !showReplyForms.value[postId]
}

function toggleNewPostForm() {
  showNewPostForm.value = !showNewPostForm.value
}

async function loadMorePosts() {
  if (nextCursor.value && !loadingMore.value) {
    await loadPosts(nextCursor.value)
  }
}

onMounted(() => loadPosts())
watch(() => route.query.tag, () => loadPosts())
</script>

<template>
  <div class="social-home">
    <div v-if="loading" class="social-loading">
      <p>Loading posts...</p>
      <p class="social-loading__small">Please wait while we fetch the latest updates.</p>
    </div>

    <div v-else-if="errorText" class="social-error">
      <h2>Unable to Load Posts</h2>
      <p>{{ errorText }}</p>
      <p class="social-error__small">Please try again later or contact administrator.</p>
    </div>

    <div v-else class="social-content">
      <div class="social-section">
        <h2 class="social-section__title">
          {{ currentTag === 'all' ? 'All Posts' : getTagDisplayName(currentTag) }}
        </h2>

        <div class="social-new-post">
          <button v-if="!showNewPostForm" @click="toggleNewPostForm" class="social-button social-button--primary">
            + Create New Post
          </button>
          
          <div v-else class="social-new-post-form">
            <h3 class="social-new-post-form__title">Create a New Post</h3>
            <textarea
              v-model="newPostContent"
              class="social-textarea"
              placeholder="What's on your mind? (Keep it short - 1-2 sentences)"
              rows="3"
            ></textarea>
            <div class="social-new-post-form__actions">
              <button @click="handleCreatePost" class="social-button social-button--primary">
                Post
              </button>
              <button @click="toggleNewPostForm" class="social-button social-button--secondary">
                Cancel
              </button>
            </div>
          </div>
        </div>

        <div v-if="posts.length === 0" class="social-empty">
          <p>No posts found.</p>
          <RouterLink to="/social" class="social-link">View all posts</RouterLink>
        </div>

        <div v-else class="social-posts">
          <div v-for="post in posts" :key="post.id" class="social-post">
            <div class="social-post__header">
              <div class="social-post__author">
                <img :src="getAvatar(post.author_id)" :alt="post.author_id" class="social-avatar">
                <div class="social-post__author-info">
                  <span class="social-post__author-name">{{ post.author_id }}</span>
                  <span class="social-post__date">{{ formatDate(post.created_at) }}</span>
                </div>
              </div>
              <div class="social-post__likes">
                ❤️ {{ post.likes }}
              </div>
            </div>

            <div class="social-post__content">
              {{ post.content }}
            </div>

            <div v-if="post.tags && post.tags.length > 0" class="social-post__tags">
              <span v-for="tag in post.tags" :key="tag" class="social-tag">
                #{{ tag }}
              </span>
            </div>

            <div v-if="post.replies && post.replies.length > 0" class="social-post__replies">
              <div v-for="reply in post.replies" :key="reply.id" class="social-reply">
                <div class="social-reply__header">
                  <img :src="getAvatar(reply.author_id)" :alt="reply.author_id" class="social-avatar social-avatar--small">
                  <div class="social-reply__author-info">
                    <span class="social-reply__author-name">{{ reply.author_id }}</span>
                    <span class="social-reply__date">{{ formatDate(reply.created_at) }}</span>
                  </div>
                </div>
                <div class="social-reply__content">
                  {{ reply.content }}
                </div>
              </div>
            </div>

            <div class="social-post__actions">
              <button @click="toggleReplyForm(post.id)" class="social-button social-button--small">
                {{ showReplyForms[post.id] ? 'Cancel Reply' : 'Reply' }}
              </button>
            </div>

            <div v-if="showReplyForms[post.id]" class="social-reply-form">
              <textarea
                v-model="replyContents[post.id]"
                class="social-textarea social-textarea--small"
                :placeholder="`Reply to ${post.author_id}...`"
                rows="2"
              ></textarea>
              <div class="social-reply-form__actions">
                <button @click="handleReply(post.id)" class="social-button social-button--primary social-button--small">
                  Reply
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="nextCursor" class="social-load-more">
          <button 
            @click="loadMorePosts" 
            :disabled="loadingMore"
            class="social-button social-button--load-more"
          >
            {{ loadingMore ? 'Loading...' : 'Load More Posts' }}
          </button>
        </div>
      </div>

      <aside class="social-sidebar-content">
        <div class="social-sidebar-box">
          <h3 class="social-sidebar-box__title">Tags</h3>
          <ul class="social-sidebar-box__list">
            <li :class="{ active: currentTag === 'all' }">
              <RouterLink to="/social">All Posts</RouterLink>
            </li>
            <li :class="{ active: currentTag === 'daily' }">
              <RouterLink to="/social?tag=daily">#daily</RouterLink>
            </li>
            <li :class="{ active: currentTag === 'food' }">
              <RouterLink to="/social?tag=food">#food</RouterLink>
            </li>
            <li :class="{ active: currentTag === 'travel' }">
              <RouterLink to="/social?tag=travel">#travel</RouterLink>
            </li>
            <li :class="{ active: currentTag === 'mystery' }">
              <RouterLink to="/social?tag=mystery">#mystery</RouterLink>
            </li>
          </ul>
        </div>

        <div class="social-sidebar-box">
          <h3 class="social-sidebar-box__title">Community Stats</h3>
          <div class="social-stats">
            <p>Total Posts: {{ posts.length }}</p>
            <p>Active Members: 156</p>
            <p>Today's Activity: 42</p>
          </div>
        </div>

        <div class="social-sidebar-box social-sidebar-box--ad">
          <h3 class="social-sidebar-box__title">Featured Member</h3>
          <div class="social-featured-member">
            <img :src="getAvatar('aria')" alt="aria" class="social-featured-member__avatar">
            <p class="social-featured-member__name">Aria_Threadweaver</p>
            <p class="social-featured-member__rating">⭐⭐⭐⭐⭐ (89 posts)</p>
            <p class="social-featured-member__info">Sharing stories and clues</p>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.social-home {
  min-height: 400px;
}

.social-loading,
.social-error {
  text-align: center;
  padding: 3rem 1rem;
  color: #000000;
}

.social-loading h2,
.social-error h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #ff6b6b;
}

.social-loading__small,
.social-error__small {
  font-size: 0.9rem;
  color: #666666;
  font-style: italic;
}

.social-content {
  display: flex;
  gap: 2rem;
}

.social-section {
  flex: 1;
}

.social-section__title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #ff6b6b;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid #ffd700;
}

.social-new-post {
  margin-bottom: 2rem;
}

.social-new-post-form {
  background: #fff8dc;
  border: 2px solid #ffd700;
  padding: 1.5rem;
  border-radius: 5px;
}

.social-new-post-form__title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #ff6b6b;
  margin-bottom: 1rem;
}

.social-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cccccc;
  border-radius: 3px;
  font-family: 'Arial', sans-serif;
  font-size: 0.9rem;
  resize: vertical;
  margin-bottom: 1rem;
}

.social-textarea--small {
  font-size: 0.85rem;
  padding: 0.5rem;
}

.social-new-post-form__actions {
  display: flex;
  gap: 0.5rem;
}

.social-button {
  display: inline-block;
  background: #ff6b6b;
  color: #ffffff;
  padding: 0.5rem 1rem;
  border: 1px solid #ee5a5a;
  border-radius: 3px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.social-button:hover {
  background: #ffd700;
  color: #ff6b6b;
}

.social-button--primary {
  background: #ff6b6b;
}

.social-button--secondary {
  background: #cccccc;
  color: #333333;
  border-color: #999999;
}

.social-button--secondary:hover {
  background: #ffd700;
  color: #333333;
}

.social-button--small {
  padding: 0.3rem 0.75rem;
  font-size: 0.8rem;
}

.social-button--load-more {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
}

.social-button:disabled {
  background: #cccccc;
  color: #666666;
  cursor: not-allowed;
}

.social-empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #666666;
}

.social-link {
  color: #ff6b6b;
  text-decoration: underline;
}

.social-posts {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.social-post {
  background: #ffffff;
  border: 1px solid #cccccc;
  border-radius: 5px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.social-post__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.social-post__author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.social-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #ffd700;
}

.social-avatar--small {
  width: 32px;
  height: 32px;
}

.social-post__author-info {
  display: flex;
  flex-direction: column;
}

.social-post__author-name {
  font-weight: bold;
  color: #ff6b6b;
  font-size: 0.95rem;
}

.social-post__date {
  font-size: 0.8rem;
  color: #999999;
}

.social-post__likes {
  font-size: 0.9rem;
  color: #ff6b6b;
}

.social-post__content {
  font-size: 0.95rem;
  color: #333333;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.social-post__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.social-tag {
  background: #fff8dc;
  color: #ff6b6b;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: bold;
}

.social-post__replies {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #cccccc;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.social-reply {
  background: #fffaf0;
  border: 1px solid #ffd700;
  border-radius: 3px;
  padding: 0.75rem;
}

.social-reply__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.social-reply__author-info {
  display: flex;
  flex-direction: column;
}

.social-reply__author-name {
  font-weight: bold;
  color: #ff6b6b;
  font-size: 0.85rem;
}

.social-reply__date {
  font-size: 0.75rem;
  color: #999999;
}

.social-reply__content {
  font-size: 0.9rem;
  color: #333333;
  line-height: 1.4;
}

.social-post__actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.social-reply-form {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #cccccc;
}

.social-reply-form__actions {
  display: flex;
  gap: 0.5rem;
}

.social-load-more {
  margin-top: 2rem;
  text-align: center;
}

.social-sidebar-content {
  width: 280px;
  flex-shrink: 0;
}

.social-sidebar-box {
  background: #fff8dc;
  border: 1px solid #cccccc;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 5px;
}

.social-sidebar-box__title {
  font-size: 1rem;
  font-weight: bold;
  color: #ff6b6b;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ffd700;
  text-transform: uppercase;
}

.social-sidebar-box__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.social-sidebar-box__list li {
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px dotted #cccccc;
}

.social-sidebar-box__list li:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.social-sidebar-box__list li.active a {
  color: #ff4500;
  font-weight: bold;
}

.social-sidebar-box__list a {
  color: #ff6b6b;
  text-decoration: none;
  font-size: 0.85rem;
}

.social-sidebar-box__list a:hover {
  text-decoration: underline;
}

.social-stats {
  font-size: 0.85rem;
  color: #333333;
  padding: 0.5rem;
  background: #ffffff;
  border: 1px solid #cccccc;
  border-radius: 3px;
}

.social-stats p {
  margin: 0.25rem 0;
}

.social-sidebar-box--ad {
  background: #fff0f5;
  border: 2px dashed #ff6b6b;
}

.social-featured-member {
  text-align: center;
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #ff6b6b;
  border-radius: 3px;
}

.social-featured-member__avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 3px solid #ffd700;
  margin-bottom: 0.5rem;
}

.social-featured-member__name {
  font-weight: bold;
  color: #ff6b6b;
  margin: 0 0 0.25rem 0;
}

.social-featured-member__rating {
  color: #ffd700;
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
}

.social-featured-member__info {
  font-size: 0.85rem;
  color: #666666;
  margin: 0;
}

@media (max-width: 900px) {
  .social-content {
    flex-direction: column;
  }

  .social-sidebar-content {
    width: 100%;
  }

  .social-post {
    padding: 0.75rem;
  }

  .social-avatar {
    width: 32px;
    height: 32px;
  }

  .social-avatar--small {
    width: 28px;
    height: 28px;
  }
}
</style>
