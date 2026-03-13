<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="social-shell">
    <header class="social-header">
      <div class="social-header__top">
        <div class="social-logo">
          <span class="social-logo__icon">💬</span>
          <span class="social-logo__text">GreenLeaf Social</span>
        </div>
        <div class="social-slogan">Share Your Life & Discover Stories</div>
      </div>
      <nav class="social-nav">
        <RouterLink to="/social" class="social-nav__link">Home</RouterLink>
        <RouterLink to="/social?tag=daily" class="social-nav__link">Daily Life</RouterLink>
        <RouterLink to="/social?tag=food" class="social-nav__link">Food</RouterLink>
        <RouterLink to="/social?tag=travel" class="social-nav__link">Travel</RouterLink>
        <RouterLink to="/social?tag=mystery" class="social-nav__link">Mystery</RouterLink>
        <RouterLink to="/forum" class="social-nav__link social-nav__link--alt">→ Forum</RouterLink>
      </nav>
    </header>

    <div class="social-body">
      <aside class="social-sidebar">
        <div class="social-sidebar__section">
          <h3 class="social-sidebar__title">Quick Links</h3>
          <ul class="social-sidebar__list">
            <li><RouterLink to="/forum">Community Forum</RouterLink></li>
            <li><RouterLink to="/news">Latest News</RouterLink></li>
            <li><RouterLink to="/p2pstore">Marketplace</RouterLink></li>
          </ul>
        </div>
        <div class="social-sidebar__section">
          <h3 class="social-sidebar__title">Community Stats</h3>
          <div class="social-sidebar__info">
            <p>Members: 2,456</p>
            <p>Posts: 12,789</p>
            <p>Replies: 45,678</p>
          </div>
        </div>
        <div class="social-sidebar__section">
          <h3 class="social-sidebar__title">Popular Tags</h3>
          <ul class="social-sidebar__list">
            <li><RouterLink to="/social?tag=daily">#daily</RouterLink></li>
            <li><RouterLink to="/social?tag=food">#food</RouterLink></li>
            <li><RouterLink to="/social?tag=travel">#travel</RouterLink></li>
            <li><RouterLink to="/social?tag=mystery">#mystery</RouterLink></li>
          </ul>
        </div>
      </aside>

      <main class="social-main">
        <RouterView />
      </main>
    </div>

    <footer class="social-footer">
      <div class="social-footer__content">
        <p>© 2000-2001 GreenLeaf Social. All rights reserved.</p>
        <p>Connecting friends and neighbors since 2000.</p>
        <p class="social-footer__disclaimer">
          This is a fictional social network for demonstration purposes only.
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

.social-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fffaf0;
  color: #000000;
  font-family: 'Arial', sans-serif;
}

.social-header {
  background: linear-gradient(to bottom, #ff6b6b, #ee5a5a);
  color: #ffffff;
  border-bottom: 3px solid #ffd700;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.social-header__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.social-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.social-logo__icon {
  font-size: 2rem;
  text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
}

.social-logo__text {
  font-size: 1.5rem;
  font-weight: bold;
  letter-spacing: 0.05em;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.social-slogan {
  font-size: 0.9rem;
  font-style: italic;
  color: #ffe4e1;
}

.social-nav {
  display: flex;
  background: #ff6b6b;
  border-top: 1px solid #ff8787;
  flex-wrap: wrap;
}

.social-nav__link {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  color: #ffffff;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-right: 1px solid #ff8787;
  transition: background 0.2s;
}

.social-nav__link:hover,
.social-nav__link.router-link-active {
  background: #ffd700;
  color: #ff6b6b;
}

.social-nav__link--alt {
  margin-left: auto;
  background: #ee5a5a;
}

.social-nav__link--alt:hover {
  background: #ffd700;
}

.social-body {
  display: flex;
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  background: #ffffff;
  border: 1px solid #cccccc;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.social-sidebar {
  width: 200px;
  background: #fff8dc;
  border-right: 1px solid #cccccc;
  padding: 1rem;
  flex-shrink: 0;
}

.social-sidebar__section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px dashed #cccccc;
}

.social-sidebar__section:last-child {
  border-bottom: none;
}

.social-sidebar__title {
  font-size: 1rem;
  font-weight: bold;
  color: #ff6b6b;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  border-bottom: 2px solid #ffd700;
  padding-bottom: 0.25rem;
}

.social-sidebar__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.social-sidebar__list li {
  margin-bottom: 0.5rem;
}

.social-sidebar__list a {
  color: #ff6b6b;
  text-decoration: none;
  font-size: 0.85rem;
}

.social-sidebar__list a:hover {
  text-decoration: underline;
  color: #ff4500;
}

.social-sidebar__info {
  font-size: 0.85rem;
  color: #333333;
  padding: 0.5rem;
  background: #ffffff;
  border: 1px solid #cccccc;
}

.social-sidebar__info p {
  margin: 0.25rem 0;
}

.social-main {
  flex: 1;
  padding: 1.5rem;
  background: #ffffff;
}

.social-footer {
  background: #ff6b6b;
  color: #ffffff;
  padding: 1rem;
  text-align: center;
  border-top: 3px solid #ffd700;
}

.social-footer__content {
  max-width: 1200px;
  margin: 0 auto;
}

.social-footer p {
  margin: 0.25rem 0;
  font-size: 0.8rem;
}

.social-footer__disclaimer {
  font-style: italic;
  color: #ffe4e1;
  margin-top: 0.75rem;
}

@media (max-width: 768px) {
  .social-body {
    flex-direction: column;
  }

  .social-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #cccccc;
  }

  .social-header__top {
    flex-direction: column;
    text-align: center;
  }

  .social-nav {
    flex-direction: column;
  }

  .social-nav__link {
    border-right: none;
    border-bottom: 1px solid #ff8787;
  }

  .social-nav__link--alt {
    margin-left: 0;
  }
}
</style>
