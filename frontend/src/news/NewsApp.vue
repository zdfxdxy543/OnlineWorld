<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="news-shell">
    <header class="news-header">
      <div class="news-header__top">
        <div class="news-logo">
          <span class="news-logo__icon">★</span>
          <span class="news-logo__text">GreenLeaf Daily News</span>
        </div>
        <div class="news-slogan">Your Trusted Source for Local Information</div>
      </div>
      <nav class="news-nav">
        <RouterLink to="/news" class="news-nav__link">Home</RouterLink>
        <RouterLink to="/news?category=official" class="news-nav__link">Official</RouterLink>
        <RouterLink to="/news?category=breaking" class="news-nav__link">Breaking</RouterLink>
        <RouterLink to="/news?category=community" class="news-nav__link">Community</RouterLink>
        <RouterLink to="/news?category=investigation" class="news-nav__link">Investigation</RouterLink>
        <RouterLink to="/forum" class="news-nav__link news-nav__link--alt">→ Forum</RouterLink>
      </nav>
    </header>

    <div class="news-body">
      <aside class="news-sidebar">
        <div class="news-sidebar__section">
          <h3 class="news-sidebar__title">Quick Links</h3>
          <ul class="news-sidebar__list">
            <li><RouterLink to="/forum">Visit Forum</RouterLink></li>
            <li><RouterLink to="/netdisk">File Archive</RouterLink></li>
          </ul>
        </div>
        <div class="news-sidebar__section">
          <h3 class="news-sidebar__title">Today's Date</h3>
          <div class="news-sidebar__date">{{ new Date().toLocaleDateString() }}</div>
        </div>
      </aside>

      <main class="news-main">
        <RouterView />
      </main>
    </div>

    <footer class="news-footer">
      <div class="news-footer__content">
        <p>© 2000-2001 GreenLeaf Daily News. All rights reserved.</p>
        <p>Published by GreenLeaf Media Group. Contact: editor@greenleaf.local</p>
        <p class="news-footer__disclaimer">
          This is a fictional news site for demonstration purposes only.
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
*,
*::before,
*::after {
  box-sizing: border-box;
}

.news-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5dc;
  color: #000000;
  font-family: 'Times New Roman', Times, serif;
}

.news-header {
  background: linear-gradient(to bottom, #000080, #0000cd);
  color: #ffffff;
  border-bottom: 4px solid #ffd700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.news-header__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.news-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.news-logo__icon {
  font-size: 2.5rem;
  color: #ffd700;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
}

.news-logo__text {
  font-size: 1.8rem;
  font-weight: bold;
  font-family: 'Georgia', serif;
  letter-spacing: 0.05em;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.news-slogan {
  font-size: 0.9rem;
  font-style: italic;
  color: #add8e6;
  font-family: 'Georgia', serif;
}

.news-nav {
  display: flex;
  background: #000080;
  border-top: 2px solid #4169e1;
  flex-wrap: wrap;
}

.news-nav__link {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  color: #ffffff;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-right: 1px solid #4169e1;
  transition: background 0.2s;
  font-family: 'Arial', sans-serif;
}

.news-nav__link:hover,
.news-nav__link.router-link-active {
  background: #ffd700;
  color: #000080;
}

.news-nav__link--alt {
  margin-left: auto;
  background: #4169e1;
}

.news-nav__link--alt:hover {
  background: #ffd700;
}

.news-body {
  display: flex;
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.news-sidebar {
  width: 200px;
  background: #e8e8e8;
  border-right: 2px solid #808080;
  padding: 1rem;
  flex-shrink: 0;
}

.news-sidebar__section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px dashed #808080;
}

.news-sidebar__section:last-child {
  border-bottom: none;
}

.news-sidebar__title {
  font-size: 1rem;
  font-weight: bold;
  color: #000080;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  font-family: 'Arial', sans-serif;
  border-bottom: 2px solid #ffd700;
  padding-bottom: 0.25rem;
}

.news-sidebar__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.news-sidebar__list li {
  margin-bottom: 0.5rem;
}

.news-sidebar__list a {
  color: #000080;
  text-decoration: none;
  font-size: 0.85rem;
}

.news-sidebar__list a:hover {
  text-decoration: underline;
  color: #ff0000;
}

.news-sidebar__date {
  font-size: 0.85rem;
  color: #000000;
  font-weight: bold;
  padding: 0.5rem;
  background: #ffffff;
  border: 1px solid #808080;
  text-align: center;
}

.news-main {
  flex: 1;
  padding: 1.5rem;
  background: #ffffff;
  border-left: 2px solid #808080;
}

.news-footer {
  background: #000080;
  color: #ffffff;
  padding: 1rem;
  text-align: center;
  border-top: 4px solid #ffd700;
}

.news-footer__content {
  max-width: 1200px;
  margin: 0 auto;
}

.news-footer p {
  margin: 0.25rem 0;
  font-size: 0.8rem;
}

.news-footer__disclaimer {
  font-style: italic;
  color: #add8e6;
  margin-top: 0.75rem;
}

@media (max-width: 768px) {
  .news-body {
    flex-direction: column;
  }

  .news-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 2px solid #808080;
  }

  .news-header__top {
    flex-direction: column;
    text-align: center;
  }

  .news-nav {
    flex-direction: column;
  }

  .news-nav__link {
    border-right: none;
    border-bottom: 1px solid #4169e1;
  }

  .news-nav__link--alt {
    margin-left: 0;
  }
}
</style>
