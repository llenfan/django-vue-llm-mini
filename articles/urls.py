from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

# URL patterns for the articles app
urlpatterns = [
    # DRF router URLs
    path('api/', include(router.urls)),
    
    # Alternative: if you want articles directly under /api/ without the app prefix
    # path('', include(router.urls)),
]

# Available endpoints:
# GET    /api/articles/                    - List all articles
# POST   /api/articles/                    - Create new article
# GET    /api/articles/{id}/               - Retrieve specific article
# PUT    /api/articles/{id}/               - Update article (full)
# PATCH  /api/articles/{id}/               - Update article (partial)
# DELETE /api/articles/{id}/               - Delete article
# GET    /api/articles/featured/           - Featured articles
# GET    /api/articles/my_articles/        - Current user's articles
# GET    /api/articles/by_author/          - Articles by author (?author=username)
# GET    /api/articles/by_tag/             - Articles by tag (?tag=tagname)
# GET    /api/articles/stats/              - Article statistics
# POST   /api/articles/{id}/toggle_featured/ - Toggle featured status