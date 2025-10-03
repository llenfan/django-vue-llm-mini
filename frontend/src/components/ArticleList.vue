<template>
  <div class="articles-container">
    <!-- Header Section -->
    <div class="header">
      <h1 class="title">Articles</h1>
      <div class="stats" v-if="hasArticles && !isLoading">
        <span class="stat-item">
          {{ pagination.count }} {{ pagination.count === 1 ? 'article' : 'articles' }} total
        </span>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="controls">
      <div class="search-container">
        <input
          v-model="searchQuery"
          @keyup.enter="handleSearch"
          type="text"
          placeholder="Search articles..."
          class="search-input"
        />
        <button @click="handleSearch" class="search-btn" :disabled="isLoading">
          {{ isLoading ? 'Searching...' : 'Search' }}
        </button>
      </div>
      
      <div class="filters">
        <select v-model="selectedStatus" @change="handleFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="published">Published</option>
          <option value="draft">Draft</option>
        </select>
        
        <select v-model="sortOrder" @change="handleFilter" class="filter-select">
          <option value="-created_at">Newest First</option>
          <option value="created_at">Oldest First</option>
          <option value="-updated_at">Recently Updated</option>
          <option value="title">Title A-Z</option>
          <option value="-title">Title Z-A</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && !hasArticles" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading articles...</p>
    </div>

    <!-- Error State -->
    <div v-if="hasError && !isLoading" class="error-container">
      <div class="error-content">
        <h3 class="error-title">Oops! Something went wrong</h3>
        <p class="error-message">{{ error }}</p>
        <button @click="handleRetry" class="retry-btn">
          Try Again
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!hasArticles && !isLoading && !hasError" class="empty-container">
      <div class="empty-content">
        <h3 class="empty-title">No articles found</h3>
        <p class="empty-message">
          {{ searchQuery ? 'Try adjusting your search terms or filters.' : 'There are no articles to display yet.' }}
        </p>
        <button v-if="searchQuery" @click="clearSearch" class="clear-btn">
          Clear Search
        </button>
      </div>
    </div>

    <!-- Articles Grid -->
    <div v-if="hasArticles" class="articles-grid">
      <article
        v-for="article in articles"
        :key="article.id"
        class="article-card"
        :class="{ 'featured': article.featured }"
      >
        <!-- Featured Badge -->
        <div v-if="article.featured" class="featured-badge">
          ⭐ Featured
        </div>

        <!-- Article Content -->
        <div class="article-content">
          <h2 class="article-title">{{ article.title }}</h2>
          
          <p class="article-excerpt" v-if="article.excerpt">
            {{ article.excerpt }}
          </p>
          
          <div class="article-meta">
            <span class="author" v-if="article.author_name">
              👤 {{ article.author_name }}
            </span>
            <span class="date">
              📅 {{ formatDate(article.created_at) }}
            </span>
            <span class="status" :class="`status-${article.status}`">
              {{ article.status }}
            </span>
            <span class="views" v-if="article.view_count">
              👁️ {{ article.view_count }} {{ article.view_count === 1 ? 'view' : 'views' }}
            </span>
          </div>

          <div class="article-tags" v-if="article.tags && article.tags.length">
            <span
              v-for="tag in article.tags"
              :key="tag"
              class="tag"
              @click="filterByTag(tag)"
            >
              #{{ tag }}
            </span>
          </div>

          <div class="article-reading-time" v-if="article.reading_time">
            ⏱️ {{ article.reading_time }} min read
          </div>
        </div>
      </article>
    </div>

    <!-- Pagination -->
    <div v-if="hasArticles && pagination.totalPages > 1" class="pagination">
      <button
        @click="goToPage(pagination.page - 1)"
        :disabled="!pagination.previous || isLoading"
        class="page-btn"
      >
        « Previous
      </button>

      <div class="page-info">
        Page {{ pagination.page }} of {{ pagination.totalPages }}
      </div>

      <button
        @click="goToPage(pagination.page + 1)"
        :disabled="!pagination.next || isLoading"
        class="page-btn"
      >
        Next »
      </button>
    </div>

    <!-- Loading overlay for pagination -->
    <div v-if="isLoading && hasArticles" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useArticlesStore } from '../stores/articles'

export default {
  name: 'ArticleList',
  setup() {
    // Store
    const articlesStore = useArticlesStore()

    // Local state
    const searchQuery = ref('')
    const selectedStatus = ref('')
    const sortOrder = ref('-created_at')

    // Computed properties from store
    const articles = computed(() => articlesStore.articles)
    const isLoading = computed(() => articlesStore.isLoading)
    const hasError = computed(() => articlesStore.hasError)
    const error = computed(() => articlesStore.error)
    const hasArticles = computed(() => articlesStore.hasArticles)
    const pagination = computed(() => articlesStore.pagination)

    // Methods
    const loadArticles = async (params = {}) => {
      const searchParams = {
        page: 1,
        page_size: 10,
        ordering: sortOrder.value,
        ...params
      }

      if (selectedStatus.value) {
        searchParams.status = selectedStatus.value
      }

      if (searchQuery.value) {
        await articlesStore.searchArticles(searchQuery.value, searchParams)
      } else {
        await articlesStore.fetchArticles(searchParams)
      }
    }

    const handleSearch = () => {
      loadArticles({ page: 1 })
    }

    const handleFilter = () => {
      loadArticles({ page: 1 })
    }

    const handleRetry = () => {
      articlesStore.clearError()
      loadArticles()
    }

    const clearSearch = () => {
      searchQuery.value = ''
      selectedStatus.value = ''
      sortOrder.value = '-created_at'
      loadArticles()
    }

    const goToPage = (page) => {
      if (page >= 1 && page <= pagination.value.totalPages) {
        loadArticles({ page })
      }
    }

    const filterByTag = (tag) => {
      loadArticles({ tags: tag, page: 1 })
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Lifecycle
    onMounted(() => {
      loadArticles()
    })

    return {
      // State
      searchQuery,
      selectedStatus,
      sortOrder,
      
      // Computed
      articles,
      isLoading,
      hasError,
      error,
      hasArticles,
      pagination,
      
      // Methods
      handleSearch,
      handleFilter,
      handleRetry,
      clearSearch,
      goToPage,
      filterByTag,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Container */
.articles-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header */
.header {
  margin-bottom: 30px;
  text-align: center;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.stats {
  color: #7f8c8d;
  font-size: 1rem;
}

/* Controls */
.controls {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  align-items: center;
}

.search-container {
  display: flex;
  gap: 10px;
  flex: 1;
  min-width: 300px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.search-btn {
  padding: 12px 24px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-btn:hover:not(:disabled) {
  background: #2980b9;
}

.search-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.filters {
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 12px 16px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 16px;
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Error State */
.error-container {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.error-content {
  text-align: center;
  max-width: 400px;
}

.error-title {
  color: #e74c3c;
  font-size: 1.5rem;
  margin-bottom: 12px;
}

.error-message {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.5;
}

.retry-btn {
  padding: 12px 24px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background: #c0392b;
}

/* Empty State */
.empty-container {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.empty-content {
  text-align: center;
  max-width: 400px;
}

.empty-title {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 12px;
}

.empty-message {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.5;
}

.clear-btn {
  padding: 12px 24px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-btn:hover {
  background: #7f8c8d;
}

/* Articles Grid */
.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.article-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  border: 2px solid transparent;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.article-card.featured {
  border-color: #f39c12;
}

.featured-badge {
  position: absolute;
  top: -8px;
  right: 16px;
  background: #f39c12;
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 600;
}

.article-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
  line-height: 1.3;
}

.article-excerpt {
  color: #5a6c7d;
  line-height: 1.5;
  margin-bottom: 16px;
  font-size: 0.95rem;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 0.85rem;
  color: #7f8c8d;
}

.status {
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
}

.status-published {
  background: #d5f4e6;
  color: #27ae60;
}

.status-draft {
  background: #fef9e7;
  color: #f39c12;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.tag {
  background: #ecf0f1;
  color: #2c3e50;
  padding: 4px 8px;
  border-radius: 16px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.tag:hover {
  background: #bdc3c7;
}

.article-reading-time {
  color: #95a5a6;
  font-size: 0.85rem;
  font-style: italic;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.page-btn {
  padding: 12px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #2980b9;
}

.page-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.page-info {
  font-weight: 600;
  color: #2c3e50;
}

/* Responsive Design */
@media (max-width: 768px) {
  .articles-container {
    padding: 16px;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    min-width: auto;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .articles-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}
</style>