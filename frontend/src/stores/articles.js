import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { articlesApi } from '../services/api'

export const useArticlesStore = defineStore('articles', () => {
  // State
  const articles = ref([])
  const currentArticle = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    count: 0,
    next: null,
    previous: null,
    page: 1,
    pageSize: 10,
    totalPages: 0
  })

  // Getters
  const featuredArticles = computed(() => 
    articles.value.filter(article => article.featured)
  )
  
  const publishedArticles = computed(() => 
    articles.value.filter(article => article.status === 'published')
  )

  const hasArticles = computed(() => 
    articles.value.length > 0
  )

  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)

  // Actions
  const fetchArticles = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await articlesApi.getArticles(params)
      articles.value = response.results
      pagination.value = {
        count: response.count,
        next: response.next,
        previous: response.previous,
        page: params.page || 1,
        pageSize: params.page_size || 10,
        totalPages: Math.ceil(response.count / (params.page_size || 10))
      }
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Failed to fetch articles'
      console.error('Failed to fetch articles:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchArticle = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await articlesApi.getArticle(id)
      currentArticle.value = response
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Failed to fetch article'
      console.error('Failed to fetch article:', err)
    } finally {
      loading.value = false
    }
  }

  const searchArticles = async (searchQuery, params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const searchParams = {
        ...params,
        search: searchQuery
      }
      const response = await articlesApi.getArticles(searchParams)
      articles.value = response.results
      pagination.value = {
        count: response.count,
        next: response.next,
        previous: response.previous,
        page: params.page || 1,
        pageSize: params.page_size || 10,
        totalPages: Math.ceil(response.count / (params.page_size || 10))
      }
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Failed to search articles'
      console.error('Failed to search articles:', err)
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const resetStore = () => {
    articles.value = []
    currentArticle.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      count: 0,
      next: null,
      previous: null,
      page: 1,
      pageSize: 10,
      totalPages: 0
    }
  }

  return {
    // State
    articles,
    currentArticle,
    loading,
    error,
    pagination,
    
    // Getters
    featuredArticles,
    publishedArticles,
    hasArticles,
    isLoading,
    hasError,
    
    // Actions
    fetchArticles,
    fetchArticle,
    searchArticles,
    clearError,
    resetStore
  }
})