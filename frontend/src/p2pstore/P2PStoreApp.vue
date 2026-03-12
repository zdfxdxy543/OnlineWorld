<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="p2pstore-shell">
    <header class="p2pstore-header">
      <div class="p2pstore-header__top">
        <div class="p2pstore-logo">
          <span class="p2pstore-logo__icon">🛒</span>
          <span class="p2pstore-logo__text">GreenLeaf P2P Marketplace</span>
        </div>
        <div class="p2pstore-slogan">Buy & Sell Directly with Community Members</div>
      </div>
      <nav class="p2pstore-nav">
        <RouterLink to="/p2pstore" class="p2pstore-nav__link">Home</RouterLink>
        <RouterLink to="/p2pstore?category=electronics" class="p2pstore-nav__link">Electronics</RouterLink>
        <RouterLink to="/p2pstore?category=clothing" class="p2pstore-nav__link">Clothing</RouterLink>
        <RouterLink to="/p2pstore?category=books" class="p2pstore-nav__link">Books</RouterLink>
        <RouterLink to="/p2pstore?category=other" class="p2pstore-nav__link">Other</RouterLink>
        <RouterLink to="/forum" class="p2pstore-nav__link p2pstore-nav__link--alt">→ Forum</RouterLink>
      </nav>
    </header>

    <div class="p2pstore-body">
      <aside class="p2pstore-sidebar">
        <div class="p2pstore-sidebar__section">
          <h3 class="p2pstore-sidebar__title">Quick Links</h3>
          <ul class="p2pstore-sidebar__list">
            <li><RouterLink to="/forum">Community Forum</RouterLink></li>
            <li><RouterLink to="/news">Latest News</RouterLink></li>
            <li><RouterLink to="/netdisk">File Archive</RouterLink></li>
          </ul>
        </div>
        <div class="p2pstore-sidebar__section">
          <h3 class="p2pstore-sidebar__title">Site Info</h3>
          <div class="p2pstore-sidebar__info">
            <p>Members: 1,245</p>
            <p>Listings: 3,789</p>
            <p>Transactions: 8,921</p>
          </div>
        </div>
        <div class="p2pstore-sidebar__section">
          <h3 class="p2pstore-sidebar__title">Security Tips</h3>
          <ul class="p2pstore-sidebar__list">
            <li>Always meet in public places</li>
            <li>Inspect items before payment</li>
            <li>Use secure payment methods</li>
            <li>Trust your instincts</li>
          </ul>
        </div>
      </aside>

      <main class="p2pstore-main">
        <RouterView />
      </main>
    </div>

    <footer class="p2pstore-footer">
      <div class="p2pstore-footer__content">
        <p>© 2000-2001 GreenLeaf P2P Marketplace. All rights reserved.</p>
        <p>Connecting community members since 2000.</p>
        <p class="p2pstore-footer__disclaimer">
          This is a fictional P2P marketplace for demonstration purposes only.
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

.p2pstore-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f0f0;
  color: #000000;
  font-family: 'Arial', sans-serif;
}

.p2pstore-header {
  background: linear-gradient(to bottom, #006400, #228b22);
  color: #ffffff;
  border-bottom: 3px solid #ffd700;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.p2pstore-header__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.p2pstore-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.p2pstore-logo__icon {
  font-size: 2rem;
  text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
}

.p2pstore-logo__text {
  font-size: 1.5rem;
  font-weight: bold;
  letter-spacing: 0.05em;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.p2pstore-slogan {
  font-size: 0.9rem;
  font-style: italic;
  color: #98fb98;
}

.p2pstore-nav {
  display: flex;
  background: #006400;
  border-top: 1px solid #32cd32;
  flex-wrap: wrap;
}

.p2pstore-nav__link {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  color: #ffffff;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-right: 1px solid #32cd32;
  transition: background 0.2s;
}

.p2pstore-nav__link:hover,
.p2pstore-nav__link.router-link-active {
  background: #ffd700;
  color: #006400;
}

.p2pstore-nav__link--alt {
  margin-left: auto;
  background: #228b22;
}

.p2pstore-nav__link--alt:hover {
  background: #ffd700;
}

.p2pstore-body {
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

.p2pstore-sidebar {
  width: 200px;
  background: #f5f5f5;
  border-right: 1px solid #cccccc;
  padding: 1rem;
  flex-shrink: 0;
}

.p2pstore-sidebar__section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px dashed #cccccc;
}

.p2pstore-sidebar__section:last-child {
  border-bottom: none;
}

.p2pstore-sidebar__title {
  font-size: 1rem;
  font-weight: bold;
  color: #006400;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  border-bottom: 2px solid #ffd700;
  padding-bottom: 0.25rem;
}

.p2pstore-sidebar__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.p2pstore-sidebar__list li {
  margin-bottom: 0.5rem;
}

.p2pstore-sidebar__list a {
  color: #006400;
  text-decoration: none;
  font-size: 0.85rem;
}

.p2pstore-sidebar__list a:hover {
  text-decoration: underline;
  color: #ff4500;
}

.p2pstore-sidebar__info {
  font-size: 0.85rem;
  color: #333333;
  padding: 0.5rem;
  background: #ffffff;
  border: 1px solid #cccccc;
}

.p2pstore-sidebar__info p {
  margin: 0.25rem 0;
}

.p2pstore-main {
  flex: 1;
  padding: 1.5rem;
  background: #ffffff;
}

.p2pstore-footer {
  background: #006400;
  color: #ffffff;
  padding: 1rem;
  text-align: center;
  border-top: 3px solid #ffd700;
}

.p2pstore-footer__content {
  max-width: 1200px;
  margin: 0 auto;
}

.p2pstore-footer p {
  margin: 0.25rem 0;
  font-size: 0.8rem;
}

.p2pstore-footer__disclaimer {
  font-style: italic;
  color: #98fb98;
  margin-top: 0.75rem;
}

@media (max-width: 768px) {
  .p2pstore-body {
    flex-direction: column;
  }

  .p2pstore-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #cccccc;
  }

  .p2pstore-header__top {
    flex-direction: column;
    text-align: center;
  }

  .p2pstore-nav {
    flex-direction: column;
  }

  .p2pstore-nav__link {
    border-right: none;
    border-bottom: 1px solid #32cd32;
  }

  .p2pstore-nav__link--alt {
    margin-left: 0;
  }
}
</style>