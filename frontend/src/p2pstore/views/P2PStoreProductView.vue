<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { getProduct, createOrder } from '../api/p2pstoreApi'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const loading = ref(true)
const errorText = ref('')
const orderSuccess = ref(false)
const quantity = ref(1)

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
  return `https://via.placeholder.com/300x250?text=${encodeURIComponent(product.name)}`
}

async function loadProduct() {
  loading.value = true
  errorText.value = ''
  orderSuccess.value = false
  try {
    const productId = route.params.productId
    product.value = await getProduct(productId)
    if (!product.value) {
      errorText.value = 'Product not found.'
    }
  } catch (error) {
    errorText.value = 'Unable to load product details.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function handlePurchase() {
  if (!product.value) return
  
  try {
    await createOrder(product.value.product_id, quantity.value)
    orderSuccess.value = true
    // 3秒后重置成功状态
    setTimeout(() => {
      orderSuccess.value = false
    }, 3000)
  } catch (error) {
    errorText.value = 'Failed to create order. Please try again.'
    console.error(error)
  }
}

onMounted(loadProduct)
</script>

<template>
  <div class="p2pstore-product">
    <div v-if="loading" class="p2pstore-loading">
      <p>Loading product details...</p>
      <p class="p2pstore-loading__small">Please wait while we fetch the information.</p>
    </div>

    <div v-else-if="errorText" class="p2pstore-error">
      <h2>Error</h2>
      <p>{{ errorText }}</p>
      <p class="p2pstore-error__small">
        <RouterLink to="/p2pstore" class="p2pstore-link">Back to Marketplace</RouterLink>
      </p>
    </div>

    <div v-else-if="!product" class="p2pstore-error">
      <h2>Product Not Found</h2>
      <p>The product you are looking for does not exist.</p>
      <p class="p2pstore-error__small">
        <RouterLink to="/p2pstore" class="p2pstore-link">Back to Marketplace</RouterLink>
      </p>
    </div>

    <div v-else class="p2pstore-product-content">
      <div class="p2pstore-product-header">
        <h1 class="p2pstore-product-title">{{ product.name }}</h1>
        <div class="p2pstore-product-meta">
          <span class="p2pstore-product-category">{{ getCategoryDisplayName(product.category) }}</span>
          <span class="p2pstore-product-separator">|</span>
          <span class="p2pstore-product-seller">Seller: {{ product.seller_id }}</span>
        </div>
      </div>

      <div class="p2pstore-product-main">
        <div class="p2pstore-product-image-container">
          <img :src="getProductImage(product)" :alt="product.name" width="300" height="250">
        </div>

        <div class="p2pstore-product-info">
          <div class="p2pstore-product-price-section">
            <div class="p2pstore-product-price">{{ formatPrice(product.price) }}</div>
            <div class="p2pstore-product-stock">
              <span v-if="product.stock > 0" class="p2pstore-product-stock-available">
                In Stock: {{ product.stock }} items
              </span>
              <span v-else class="p2pstore-product-stock-unavailable">
                Out of Stock
              </span>
            </div>
          </div>

          <div class="p2pstore-product-quantity">
            <label for="quantity">Quantity:</label>
            <input 
              type="number" 
              id="quantity" 
              v-model.number="quantity" 
              min="1" 
              :max="product.stock || 10"
              class="p2pstore-input"
            >
          </div>

          <div class="p2pstore-product-actions">
            <button 
              class="p2pstore-button p2pstore-button--primary" 
              @click="handlePurchase"
              :disabled="product.stock <= 0"
            >
              Buy Now
            </button>
            <button class="p2pstore-button">
              Add to Wishlist
            </button>
          </div>

          <div v-if="orderSuccess" class="p2pstore-success-message">
            <p>Order created successfully! Thank you for your purchase.</p>
          </div>
        </div>
      </div>

      <div class="p2pstore-product-description">
        <h2 class="p2pstore-section-title">Product Description</h2>
        <div class="p2pstore-description-content">
          <p>{{ product.description }}</p>
        </div>
      </div>

      <div class="p2pstore-product-seller-info">
        <h2 class="p2pstore-section-title">Seller Information</h2>
        <div class="p2pstore-seller-details">
          <p><strong>Seller:</strong> {{ product.seller_id }}</p>
          <p><strong>Member Since:</strong> January 2000</p>
          <p><strong>Rating:</strong> ⭐⭐⭐⭐⭐ (45 reviews)</p>
          <p><strong>Response Rate:</strong> 98%</p>
        </div>
      </div>

      <div class="p2pstore-related-products">
        <h2 class="p2pstore-section-title">Related Products</h2>
        <div class="p2pstore-related-products-list">
          <div class="p2pstore-related-product" v-for="i in 3" :key="i">
            <img src="https://via.placeholder.com/120x100?text=Related+Item" alt="Related Product" width="120" height="100">
            <h3 class="p2pstore-related-product-name">Related Item {{ i }}</h3>
            <div class="p2pstore-related-product-price">$19.99</div>
            <RouterLink to="/p2pstore" class="p2pstore-button p2pstore-button--small">
              View
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.p2pstore-product {
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

.p2pstore-link {
  color: #006400;
  text-decoration: underline;
}

.p2pstore-product-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #cccccc;
}

.p2pstore-product-title {
  font-size: 2rem;
  font-weight: bold;
  color: #006400;
  margin: 0 0 0.5rem 0;
}

.p2pstore-product-meta {
  font-size: 0.9rem;
  color: #666666;
}

.p2pstore-product-category {
  color: #006400;
  font-weight: bold;
}

.p2pstore-product-separator {
  margin: 0 0.5rem;
}

.p2pstore-product-main {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.p2pstore-product-image-container {
  flex-shrink: 0;
}

.p2pstore-product-image-container img {
  border: 1px solid #cccccc;
  background: #f0f0f0;
}

.p2pstore-product-info {
  flex: 1;
  background: #f5f5f5;
  padding: 1.5rem;
  border: 1px solid #cccccc;
}

.p2pstore-product-price-section {
  margin-bottom: 1.5rem;
}

.p2pstore-product-price {
  font-size: 2rem;
  font-weight: bold;
  color: #ff4500;
  margin-bottom: 0.5rem;
}

.p2pstore-product-stock {
  font-size: 0.9rem;
}

.p2pstore-product-stock-available {
  color: #006400;
  font-weight: bold;
}

.p2pstore-product-stock-unavailable {
  color: #ff4500;
  font-weight: bold;
}

.p2pstore-product-quantity {
  margin-bottom: 1.5rem;
}

.p2pstore-product-quantity label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.p2pstore-input {
  padding: 0.5rem;
  border: 1px solid #cccccc;
  width: 100px;
}

.p2pstore-product-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.p2pstore-button {
  display: inline-block;
  background: #006400;
  color: #ffffff;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  font-weight: bold;
  font-size: 0.9rem;
  border: 1px solid #004d00;
  transition: background 0.2s;
  cursor: pointer;
}

.p2pstore-button:hover {
  background: #ffd700;
  color: #006400;
}

.p2pstore-button--primary {
  background: #ff4500;
  border: 1px solid #cc3700;
}

.p2pstore-button--primary:hover {
  background: #ff6347;
  color: #ffffff;
}

.p2pstore-button:disabled {
  background: #cccccc;
  color: #666666;
  cursor: not-allowed;
}

.p2pstore-button--small {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.p2pstore-success-message {
  background: #98fb98;
  color: #006400;
  padding: 1rem;
  border: 1px solid #32cd32;
  margin-top: 1rem;
}

.p2pstore-product-description,
.p2pstore-product-seller-info,
.p2pstore-related-products {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid #cccccc;
  background: #f9f9f9;
}

.p2pstore-section-title {
  font-size: 1.3rem;
  font-weight: bold;
  color: #006400;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ffd700;
}

.p2pstore-description-content {
  line-height: 1.6;
  color: #333333;
}

.p2pstore-seller-details p {
  margin: 0.5rem 0;
  color: #333333;
}

.p2pstore-related-products-list {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.p2pstore-related-product {
  width: 150px;
  text-align: center;
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #cccccc;
}

.p2pstore-related-product img {
  margin-bottom: 0.5rem;
  border: 1px solid #cccccc;
  background: #f0f0f0;
}

.p2pstore-related-product-name {
  font-size: 0.9rem;
  font-weight: bold;
  margin: 0 0 0.5rem 0;
  color: #006400;
}

.p2pstore-related-product-price {
  font-size: 1rem;
  font-weight: bold;
  color: #ff4500;
  margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
  .p2pstore-product-main {
    flex-direction: column;
  }

  .p2pstore-product-image-container {
    align-self: center;
  }

  .p2pstore-product-actions {
    flex-direction: column;
  }

  .p2pstore-related-products-list {
    justify-content: center;
  }
}
</style>