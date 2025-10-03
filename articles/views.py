from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Article
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer, 
    ArticleCreateSerializer,
    ArticleUpdateSerializer
)
from .filters import ArticleFilter
from .permissions import IsAuthorOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="List Articles",
        description="Retrieve a paginated list of articles with optional search, filtering, and ordering.",
        tags=["Articles"],
    ),
    create=extend_schema(
        summary="Create Article",
        description="Create a new article. Authentication required.",
        tags=["Articles"],
    ),
    retrieve=extend_schema(
        summary="Get Article",
        description="Retrieve a specific article by ID. Increments view count for published articles.",
        tags=["Articles"],
    ),
    update=extend_schema(
        summary="Update Article",
        description="Update an article. Only the author can update their articles.",
        tags=["Articles"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Article",
        description="Partially update an article. Only the author can update their articles.",
        tags=["Articles"],
    ),
    destroy=extend_schema(
        summary="Delete Article",
        description="Delete an article. Only the author can delete their articles.",
        tags=["Articles"],
    ),
)
class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing articles with full CRUD operations.
    
    Provides:
    - List articles with search, filtering, and pagination
    - Retrieve individual articles
    - Create new articles (authenticated users only)
    - Update articles (authors only)
    - Delete articles (authors only)
    - Additional actions for featured articles, user articles, etc.
    """
    
    queryset = Article.objects.select_related('author').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    # Search, filter, and ordering configuration
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'tags', 'author__username']
    ordering_fields = [
        'title', 'created_at', 'updated_at', 'published_at', 
        'view_count', 'status'
    ]
    ordering = ['-created_at']  # Default ordering
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action == 'create':
            return ArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ArticleUpdateSerializer
        else:
            return ArticleDetailSerializer
    
    def get_queryset(self):
        """
        Customize queryset based on user permissions and filters.
        """
        queryset = self.queryset
        
        # If user is not authenticated, only show published articles
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        else:
            # Authenticated users can see their own drafts + all published
            if not self.request.user.is_staff:
                queryset = queryset.filter(
                    Q(status='published') | Q(author=self.request.user)
                )
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve single article and increment view count.
        """
        instance = self.get_object()
        
        # Increment view count (only for published articles)
        if instance.status == 'published':
            Article.objects.filter(pk=instance.pk).update(
                view_count=F('view_count') + 1
            )
            # Refresh instance to get updated view_count
            instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """
        Create article with current user as author.
        """
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        """
        Update article with business logic.
        """
        # If publishing for the first time, set published_at
        instance = serializer.instance
        if (serializer.validated_data.get('status') == 'published' and 
            instance.status != 'published'):
            serializer.save(published_at=timezone.now())
        else:
            serializer.save()
    
    @extend_schema(
        summary="Featured Articles",
        description="Get a list of featured articles that are published.",
        tags=["Articles"],
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured articles.
        GET /api/articles/featured/
        """
        featured_articles = self.get_queryset().filter(
            featured=True, 
            status='published'
        )
        
        # Apply pagination
        page = self.paginate_queryset(featured_articles)
        if page is not None:
            serializer = ArticleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleListSerializer(featured_articles, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="My Articles",
        description="Get current user's articles (all statuses). Authentication required.",
        tags=["Articles"],
    )
    @action(detail=False, methods=['get'])
    def my_articles(self, request):
        """
        Get current user's articles (all statuses).
        GET /api/articles/my_articles/
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user_articles = Article.objects.select_related('author').filter(
            author=request.user
        )
        
        # Apply pagination
        page = self.paginate_queryset(user_articles)
        if page is not None:
            serializer = ArticleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleListSerializer(user_articles, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Articles by Author",
        description="Get published articles by a specific author.",
        parameters=[
            OpenApiParameter(
                name='author',
                description='Username of the author',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        tags=["Articles"],
    )
    @action(detail=False, methods=['get'])
    def by_author(self, request):
        """
        Get articles by specific author.
        GET /api/articles/by_author/?author=username
        """
        author_username = request.query_params.get('author')
        if not author_username:
            return Response(
                {'detail': 'Author username parameter required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        author_articles = self.get_queryset().filter(
            author__username=author_username,
            status='published'  # Only show published articles for public view
        )
        
        # Apply pagination
        page = self.paginate_queryset(author_articles)
        if page is not None:
            serializer = ArticleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleListSerializer(author_articles, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Articles by Tag",
        description="Get published articles containing a specific tag.",
        parameters=[
            OpenApiParameter(
                name='tag',
                description='Tag to filter by',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        tags=["Articles"],
    )
    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """
        Get articles by tag.
        GET /api/articles/by_tag/?tag=python
        """
        tag = request.query_params.get('tag')
        if not tag:
            return Response(
                {'detail': 'Tag parameter required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Case-insensitive tag search
        tagged_articles = self.get_queryset().filter(
            tags__icontains=tag,
            status='published'
        )
        
        # Apply pagination
        page = self.paginate_queryset(tagged_articles)
        if page is not None:
            serializer = ArticleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleListSerializer(tagged_articles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_featured(self, request, pk=None):
        """
        Toggle featured status of an article (staff only).
        POST /api/articles/{id}/toggle_featured/
        """
        if not request.user.is_staff:
            return Response(
                {'detail': 'Staff permission required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        article = self.get_object()
        article.featured = not article.featured
        article.save(update_fields=['featured'])
        
        return Response({
            'featured': article.featured,
            'message': f"Article {'featured' if article.featured else 'unfeatured'} successfully"
        })
    
    @extend_schema(
        summary="Article Statistics",
        description="Get comprehensive statistics about articles.",
        tags=["Articles"],
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get article statistics.
        GET /api/articles/stats/
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_articles': queryset.count(),
            'published_articles': queryset.filter(status='published').count(),
            'draft_articles': queryset.filter(status='draft').count(),
            'featured_articles': queryset.filter(featured=True).count(),
            'total_views': sum(queryset.values_list('view_count', flat=True)),
        }
        
        # Add user-specific stats if authenticated
        if request.user.is_authenticated:
            user_articles = queryset.filter(author=request.user)
            stats.update({
                'my_articles': user_articles.count(),
                'my_published': user_articles.filter(status='published').count(),
                'my_drafts': user_articles.filter(status='draft').count(),
            })
        
        return Response(stats)
