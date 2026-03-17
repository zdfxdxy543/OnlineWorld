<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="academic-shell">
    <header class="academic-header">
      <div class="academic-header__top">
        <div class="academic-logo">
          <span class="academic-logo__icon">CN</span>
          <span class="academic-logo__text">Academic Library</span>
        </div>
        <div class="academic-header__nav">
          <RouterLink to="/academic" class="academic-header__link">Home</RouterLink>
          <RouterLink to="/academic/search" class="academic-header__link">Search</RouterLink>
          <RouterLink to="/academic/categories" class="academic-header__link">Journals</RouterLink>
          <RouterLink to="/academic/author" class="academic-header__link">Authors</RouterLink>
        </div>
      </div>
      <div class="academic-header__search-bar">
        <select class="academic-search-select">
          <option value="title">Title</option>
          <option value="author">Author</option>
          <option value="keyword">Keyword</option>
          <option value="abstract">Abstract</option>
        </select>
        <input type="text" class="academic-search-input" placeholder="Enter search terms..." />
        <RouterLink to="/academic/search" class="academic-search-btn">Search</RouterLink>
      </div>
    </header>

    <div class="academic-body">
      <aside class="academic-sidebar">
        <div class="academic-sidebar__section">
          <h3 class="academic-sidebar__title">Categories</h3>
          <ul class="academic-sidebar__list">
            <li><RouterLink to="/academic/search?category=computer">Computer Science (45)</RouterLink></li>
            <li><RouterLink to="/academic/search?category=medicine">Medicine (32)</RouterLink></li>
            <li><RouterLink to="/academic/search?category=economics">Economics (28)</RouterLink></li>
            <li><RouterLink to="/academic/search?category=education">Education (21)</RouterLink></li>
            <li><RouterLink to="/academic/search?category=engineering">Engineering (38)</RouterLink></li>
            <li><RouterLink to="/academic/search?category=law">Law (15)</RouterLink></li>
          </ul>
        </div>
        <div class="academic-sidebar__section">
          <h3 class="academic-sidebar__title">Quick Links</h3>
          <ul class="academic-sidebar__list">
            <li><RouterLink to="/academic/search?type=hot">Hot Papers</RouterLink></li>
            <li><RouterLink to="/academic/search?type=new">New Arrivals</RouterLink></li>
            <li><RouterLink to="/academic/search?type=free">Free Full Text</RouterLink></li>
          </ul>
        </div>
        <div class="academic-sidebar__section">
          <h3 class="academic-sidebar__title">Help</h3>
          <ul class="academic-sidebar__list">
            <li><a href="#">Search Help</a></li>
            <li><a href="#">Browser Settings</a></li>
            <li><a href="#">FAQ</a></li>
          </ul>
        </div>
        <div class="academic-sidebar__section academic-sidebar__section--date">
          <div class="academic-sidebar__date">{{ new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) }}</div>
          <div class="academic-sidebar__time">{{ new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) }}</div>
        </div>
      </aside>

      <main class="academic-main">
        <RouterView />
      </main>
    </div>

    <footer class="academic-footer">
      <div class="academic-footer__content">
        <p>&copy; 1998-2001 Academic Library. All Rights Reserved.</p>
        <p>Hotline: 010-62791812 | Email: service@academiclib.cn</p>
        <p class="academic-footer__info">
          This system is for demonstration purposes only.<br>
          ICP Registration:京ICP备00000001号
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.academic-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  font-family: Arial, Helvetica, sans-serif;
}

.academic-header {
  background: linear-gradient(to bottom, #2b6cb0 0%, #1a4971 100%);
  padding-bottom: 8px;
}

.academic-header__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 10px;
  border-bottom: 1px solid #1e3a5f;
}

.academic-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.academic-logo__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #c53030;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  font-family: Arial, sans-serif;
  border-radius: 3px;
}

.academic-logo__text {
  color: #fff;
  font-size: 22px;
  font-weight: bold;
  letter-spacing: 2px;
}

.academic-header__nav {
  display: flex;
  gap: 20px;
}

.academic-header__link {
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 2px;
}

.academic-header__link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.academic-header__search-bar {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  gap: 0;
}

.academic-search-select {
  width: 90px;
  height: 30px;
  border: 1px solid #4a90c2;
  border-right: none;
  padding: 0 8px;
  font-size: 13px;
  background: #fff;
  color: #333;
}

.academic-search-input {
  flex: 1;
  height: 30px;
  border: 1px solid #4a90c2;
  padding: 0 10px;
  font-size: 13px;
  max-width: 400px;
}

.academic-search-btn {
  height: 30px;
  padding: 0 20px;
  background: #c53030;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: bold;
  display: flex;
  align-items: center;
  border: none;
  cursor: pointer;
}

.academic-search-btn:hover {
  background: #9b2c2c;
}

.academic-body {
  display: flex;
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px;
  gap: 15px;
  width: 100%;
}

.academic-sidebar {
  width: 180px;
  flex-shrink: 0;
}

.academic-sidebar__section {
  background: #fff;
  border: 1px solid #ccc;
  margin-bottom: 10px;
}

.academic-sidebar__title {
  background: linear-gradient(to bottom, #e8f0f8 0%, #d4e4f0 100%);
  margin: 0;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: bold;
  color: #1a4971;
  border-bottom: 1px solid #a8c8e0;
}

.academic-sidebar__list {
  list-style: none;
  margin: 0;
  padding: 6px 0;
}

.academic-sidebar__list li {
  padding: 4px 12px;
}

.academic-sidebar__list a {
  color: #333;
  text-decoration: none;
  font-size: 12px;
}

.academic-sidebar__list a:hover {
  color: #c53030;
  text-decoration: underline;
}

.academic-sidebar__section--date {
  text-align: center;
  padding: 10px;
}

.academic-sidebar__date {
  font-size: 14px;
  color: #1a4971;
  font-weight: bold;
}

.academic-sidebar__time {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.academic-main {
  flex: 1;
  background: #fff;
  border: 1px solid #ccc;
  min-height: 500px;
}

.academic-footer {
  background: #1a4971;
  color: #fff;
  padding: 20px;
  text-align: center;
  font-size: 12px;
}

.academic-footer__content p {
  margin: 4px 0;
}

.academic-footer__info {
  margin-top: 10px !important;
  color: #a8c8e0;
  font-size: 11px;
}
</style>
