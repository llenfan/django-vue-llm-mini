import axios from 'axios'

// Base API configuration
const API_BASE_URL = 'http://189.90.231.233:8000/api'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
})

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          console.error('Authentication failed')
          break
        case 403:
          console.error('Access forbidden')
          break
        case 404:
          console.error('Resource not found')
          break
        case 500:
          console.error('Internal server error')
          break
        default:
          console.error('API Error:', data)
      }
      
      // Return error with formatted message
      error.message = data?.detail || data?.message || `HTTP ${status} Error`
    } else if (error.request) {
      // Network error
      error.message = 'Network error - please check your connection'
    }
    
    return Promise.reject(error)
  }
)

// Articles API endpoints
export const articlesApi = {
  // Get all articles with optional filters
  getArticles: (params = {}) => {
    return apiClient.get('/articles/', { params })
  },
  
  // Get single article by ID
  getArticle: (id) => {
    return apiClient.get(`/articles/${id}/`)
  },
  
  // Create new article (requires authentication)
  createArticle: (articleData) => {
    return apiClient.post('/articles/', articleData)
  },
  
  // Update article (requires authentication)
  updateArticle: (id, articleData) => {
    return apiClient.put(`/articles/${id}/`, articleData)
  },
  
  // Partially update article (requires authentication)
  patchArticle: (id, articleData) => {
    return apiClient.patch(`/articles/${id}/`, articleData)
  },
  
  // Delete article (requires authentication)
  deleteArticle: (id) => {
    return apiClient.delete(`/articles/${id}/`)
  },
  
  // Get featured articles
  getFeaturedArticles: (params = {}) => {
    return apiClient.get('/articles/featured/', { params })
  },
  
  // Get articles by author
  getArticlesByAuthor: (authorId, params = {}) => {
    return apiClient.get(`/articles/by_author/${authorId}/`, { params })
  },
  
  // Get articles by tag
  getArticlesByTag: (tag, params = {}) => {
    return apiClient.get(`/articles/by_tag/${tag}/`, { params })
  },
  
  // Get articles stats
  getArticlesStats: () => {
    return apiClient.get('/articles/stats/')
  },
  
  // Toggle featured status (requires authentication)
  toggleFeatured: (id) => {
    return apiClient.post(`/articles/${id}/toggle_featured/`)
  }
}

// Authentication API endpoints
export const authApi = {
  // Login
  login: (credentials) => {
    return apiClient.post('/auth/login/', credentials)
  },
  
  // Refresh token
  refreshToken: (refresh) => {
    return apiClient.post('/auth/token/refresh/', { refresh })
  },
  
  // Logout
  logout: () => {
    return apiClient.post('/auth/logout/')
  }
}

// Export the configured axios instance for custom requests
export { apiClient }

// Helper function to set auth token
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('access_token', token)
  } else {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
}

// Helper function to check if user is authenticated
export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token')
}