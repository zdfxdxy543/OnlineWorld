const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  }
  
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  }
  
  try {
    const response = await fetch(url, mergedOptions)
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

export async function getProducts(category = null, limit = 20) {
  const params = new URLSearchParams()
  if (category) params.append('category', category)
  if (limit) params.append('limit', limit)
  
  const response = await fetchApi(`/p2pstore/products?${params.toString()}`)
  return response.products || []
}

export async function getProduct(productId) {
  const response = await fetchApi(`/p2pstore/products/${productId}`)
  return response.product || null
}

export async function getCategories() {
  const response = await fetchApi('/p2pstore/categories')
  return response.categories || []
}

export async function createOrder(productId, quantity = 1) {
  const response = await fetchApi('/p2pstore/orders', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, quantity }),
  })
  return response.order || null
}

export async function getOrders() {
  const response = await fetchApi('/p2pstore/orders')
  return response.orders || []
}