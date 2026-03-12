<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getProducts, getCategories } from '../api/p2pstoreApi'

const route = useRoute()
const products = ref([])
const categories = ref([])
const loading = ref(true)
const errorText = ref('')
const currentCategory = ref('')

function getCategoryDisplayName(category) {
  const names = {
    electronics: 'Electronics',
    clothing: 'Clothing & Accessories',
    books: 'Books & Media',
    other: 'Other Items',
  }
  return names[category] || category
}

function formatPrice(price) {
  if (typeof price === 'number') {
    return `$${price.toFixed(2)}`
  }
  return '$0.00'
}

function getProductImage(product) {
  // 2000年风格的图片占位符
  return `https://via.placeholder.com/120x100?text=${encodeURIComponent(product.name)}`
}

async function loadProducts() {
  loading.value = true
  errorText.value = ''
  try {
    const category = route.query.category || null
    currentCategory.value = category || 'all'
    products.value = await getProducts(category)
  } catch (error) {
    products.value = []
    errorText.value = 'Unable to load products from server.'
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
    await loadProducts()
  } catch (error) {
    errorText.value = 'Unable to load marketplace data.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(loadInitialData)
watch(() => route.query.category, loadProducts)
</script>

<template>
  <div class="p2pstore-home">
    <div v-if="loading" class="p2pstore-loading">
      <p>Loading products...</p>
      <p class="p2pstore-loading__small">Please wait while we fetch the latest listings.</p>
    </div>

    <div v-else-if="errorText" class="p2pstore-error">
      <h2>Unable to Load Marketplace</h2>
      <p>{{ errorText }}</p>
      <p class="p2pstore-error__small">Please try again later or contact the administrator.</p>
    </div>

    <div v-else class="p2pstore-content">
      <div class="p2pstore-section">
        <h2 class="p2pstore-section__title">
          {{ currentCategory === 'all' ? 'All Listings' : getCategoryDisplayName(currentCategory) }}
        </h2>

        <div v-if="products.length === 0" class="p2pstore-empty">
          <p>No products found in this category.</p>
          <RouterLink to="/p2pstore" class="p2pstore-link">View all listings</RouterLink>
        </div>

        <table v-else class="p2pstore-products-table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Description</th>
              <th>Price</th>
              <th>Seller</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in products" :key="product.product_id" class="p2pstore-product-row">
              <td class="p2pstore-product-image">
                <img :src="getProductImage(product)" :alt="product.name" width="120" height="100">
              </td>
              <td class="p2pstore-product-info">
                <h3 class="p2pstore-product-name">
                  <RouterLink :to="`/p2pstore/product/${product.product_id}`">
                    {{ product.name }}
                  </RouterLink>
                </h3>
                <p class="p2pstore-product-description">{{ product.description }}</p>
              </td>
              <td class="p2pstore-product-price">{{ formatPrice(product.price) }}</td>
              <td class="p2pstore-product-seller">{{ product.seller_id }}</td>
              <td class="p2pstore-product-action">
                <RouterLink :to="`/p2pstore/product/${product.product_id}`" class="p2pstore-button">
                  View Details
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <aside class="p2pstore-sidebar-content">
        <div class="p2pstore-sidebar-box">
          <h3 class="p2pstore-sidebar-box__title">Categories</h3>
          <ul class="p2pstore-sidebar-box__list">
            <li :class="{ active: currentCategory === 'all' }">
              <RouterLink to="/p2pstore">All Categories</RouterLink>
            </li>
            <li v-for="cat in categories" :key="cat.slug" :class="{ active: currentCategory === cat.slug }">
              <RouterLink :to="`/p2pstore?category=${cat.slug}`">{{ cat.name }}</RouterLink>
            </li>
          </ul>
        </div>

        <div class="p2pstore-sidebar-box">
          <h3 class="p2pstore-sidebar-box__title">Marketplace Stats</h3>
          <div class="p2pstore-stats">
            <p>Total Listings: {{ products.length }}</p>
            <p>Active Sellers: 42</p>
            <p>Today's Sales: 12</p>
          </div>
        </div>

        <div class="p2pstore-sidebar-box p2pstore-sidebar-box--ad">
          <h3 class="p2pstore-sidebar-box__title">Featured Seller</h3>
          <div class="p2pstore-featured-seller">
            <p class="p2pstore-featured-seller__name">GreenLeaf Electronics</p>
            <p class="p2pstore-featured-seller__rating">⭐⭐⭐⭐⭐ (45 reviews)</p>
            <p class="p2pstore-featured-seller__info">Specializing in vintage electronics</p>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.p2pstore-home {
  min-height: 400px;
}

.p2pstore-loading,
.p2pstore-error {
  text-align: center;
  padding: 3rem 1rem;
  color: #000000;
}

.p2pstore-loading h2,
.p2pstore-error h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #006400;
}

.p2pstore-loading__small,
.p2pstore-error__small {
  font-size: 0.9rem;
  color: #666666;
  font-style: italic;
}

.p2pstore-content {
  display: flex;
  gap: 2rem;
}

.p2pstore-section {
  flex: 1;
}

.p2pstore-section__title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #006400;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid #ffd700;
}

.p2pstore-empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #666666;
}

.p2pstore-link {
  color: #006400;
  text-decoration: underline;
}

.p2pstore-products-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #cccccc;
  background: #ffffff;
}

.p2pstore-products-table th {
  background: #006400;
  color: #ffffff;
  padding: 0.75rem;
  text-align: left;
  font-weight: bold;
  border: 1px solid #cccccc;
}

.p2pstore-products-table td {
  padding: 1rem;
  border: 1px solid #cccccc;
  vertical-align: top;
}

.p2pstore-product-row:hover {
  background: #f5f5f5;
}

.p2pstore-product-image img {
  border: 1px solid #cccccc;
  background: #f0f0f0;
}

.p2pstore-product-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.p2pstore-product-name a {
  color: #006400;
  text-decoration: none;
}

.p2pstore-product-name a:hover {
  color: #ff4500;
  text-decoration: underline;
}

.p2pstore-product-description {
  margin: 0;
  font-size: 0.9rem;
  color: #666666;
}

.p2pstore-product-price {
  font-weight: bold;
  color: #ff4500;
  font-size: 1.1rem;
}

.p2pstore-product-seller {
  font-size: 0.9rem;
  color: #333333;
}

.p2pstore-button {
  display: inline-block;
  background: #006400;
  color: #ffffff;
  padding: 0.5rem 1rem;
  text-decoration: none;
  font-weight: bold;
  font-size: 0.85rem;
  border: 1px solid #004d00;
  transition: background 0.2s;
}

.p2pstore-button:hover {
  background: #ffd700;
  color: #006400;
}

.p2pstore-sidebar-content {
  width: 280px;
  flex-shrink: 0;
}

.p2pstore-sidebar-box {
  background: #f0f0f0;
  border: 1px solid #cccccc;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.p2pstore-sidebar-box__title {
  font-size: 1rem;
  font-weight: bold;
  color: #006400;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ffd700;
  text-transform: uppercase;
}

.p2pstore-sidebar-box__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.p2pstore-sidebar-box__list li {
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px dotted #cccccc;
}

.p2pstore-sidebar-box__list li:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.p2pstore-sidebar-box__list li.active a {
  color: #ff4500;
  font-weight: bold;
}

.p2pstore-sidebar-box__list a {
  color: #006400;
  text-decoration: none;
  font-size: 0.85rem;
}

.p2pstore-sidebar-box__list a:hover {
  text-decoration: underline;
}

.p2pstore-stats {
  font-size: 0.85rem;
  color: #333333;
  padding: 0.5rem;
  background: #ffffff;
  border: 1px solid #cccccc;
}

.p2pstore-stats p {
  margin: 0.25rem 0;
}

.p2pstore-sidebar-box--ad {
  background: #f0fff0;
  border: 2px dashed #32cd32;
}

.p2pstore-featured-seller {
  text-align: center;
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #32cd32;
}

.p2pstore-featured-seller__name {
  font-weight: bold;
  color: #006400;
  margin: 0 0 0.25rem 0;
}

.p2pstore-featured-seller__rating {
  color: #ffd700;
  margin: 0 0 0.25rem 0;
}

.p2pstore-featured-seller__info {
  font-size: 0.85rem;
  color: #666666;
  margin: 0;
}

@media (max-width: 900px) {
  .p2pstore-content {
    flex-direction: column;
  }

  .p2pstore-sidebar-content {
    width: 100%;
  }

  .p2pstore-products-table {
    font-size: 0.9rem;
  }

  .p2pstore-products-table th,
  .p2pstore-products-table td {
    padding: 0.5rem;
  }

  .p2pstore-product-image img {
    width: 80px;
    height: 60px;
  }
}
</style>