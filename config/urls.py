"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Documentation (OpenAPI/Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Authentication endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # DRF Browsable API (for development)
    path('api-auth/', include('rest_framework.urls')),
    
    # Articles API
    path('', include('articles.urls')),
]

# Available API endpoints:
# ========================
# Authentication:
# POST /api/auth/token/          - Obtain JWT token pair (login)
# POST /api/auth/token/refresh/  - Refresh access token
# POST /api/auth/token/verify/   - Verify token validity
# 
# Articles:
# GET    /api/articles/                    - List articles with pagination, search, filtering
# POST   /api/articles/                    - Create new article (auth required)
# GET    /api/articles/{id}/               - Retrieve article details
# PUT    /api/articles/{id}/               - Update article (author only)
# PATCH  /api/articles/{id}/               - Partial update (author only)  
# DELETE /api/articles/{id}/               - Delete article (author only)
# GET    /api/articles/featured/           - Featured articles
# GET    /api/articles/my_articles/        - User's articles (auth required)
# GET    /api/articles/by_author/          - Articles by author (?author=username)
# GET    /api/articles/by_tag/             - Articles by tag (?tag=tagname)
# GET    /api/articles/stats/              - Article statistics
# POST   /api/articles/{id}/toggle_featured/ - Toggle featured (staff only)
