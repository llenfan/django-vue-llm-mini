import django_filters
from django.db.models import Q
from .models import Article


class ArticleFilter(django_filters.FilterSet):
    """
    Advanced filtering for Article model.
    Provides multiple filter options for flexible article queries.
    """
    
    # Title filtering (case-insensitive contains)
    title = django_filters.CharFilter(
        field_name='title', 
        lookup_expr='icontains',
        help_text="Filter by title (case-insensitive partial match)"
    )
    
    # Content filtering (case-insensitive contains)
    content = django_filters.CharFilter(
        field_name='content', 
        lookup_expr='icontains',
        help_text="Filter by content (case-insensitive partial match)"
    )
    
    # Author filtering
    author = django_filters.CharFilter(
        field_name='author__username', 
        lookup_expr='iexact',
        help_text="Filter by author username (exact match)"
    )
    
    author_contains = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='icontains',
        help_text="Filter by author username (partial match)"
    )
    
    # Status filtering
    status = django_filters.ChoiceFilter(
        choices=Article.STATUS_CHOICES,
        help_text="Filter by publication status"
    )
    
    # Featured articles
    featured = django_filters.BooleanFilter(
        help_text="Filter by featured status"
    )
    
    # Tag filtering
    tags = django_filters.CharFilter(
        method='filter_tags',
        help_text="Filter by tags (comma-separated for multiple tags)"
    )
    
    # Date range filtering
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter articles created after this date"
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter articles created before this date"
    )
    
    published_after = django_filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='gte',
        help_text="Filter articles published after this date"
    )
    
    published_before = django_filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='lte',
        help_text="Filter articles published before this date"
    )
    
    # View count filtering
    min_views = django_filters.NumberFilter(
        field_name='view_count',
        lookup_expr='gte',
        help_text="Filter articles with minimum view count"
    )
    
    max_views = django_filters.NumberFilter(
        field_name='view_count',
        lookup_expr='lte',
        help_text="Filter articles with maximum view count"
    )
    
    # Combined search across multiple fields
    search = django_filters.CharFilter(
        method='filter_search',
        help_text="Search across title, content, tags, and author"
    )

    class Meta:
        model = Article
        fields = []  # We define custom fields above

    def filter_tags(self, queryset, name, value):
        """
        Filter articles by tags.
        Supports multiple tags separated by commas.
        """
        if not value:
            return queryset
        
        # Split tags and clean them
        tags = [tag.strip().lower() for tag in value.split(',') if tag.strip()]
        
        # Create Q objects for each tag
        q_objects = Q()
        for tag in tags:
            q_objects |= Q(tags__icontains=tag)
        
        return queryset.filter(q_objects)

    def filter_search(self, queryset, name, value):
        """
        Perform a comprehensive search across multiple fields.
        """
        if not value:
            return queryset
        
        # Search across multiple fields
        return queryset.filter(
            Q(title__icontains=value) |
            Q(content__icontains=value) |
            Q(tags__icontains=value) |
            Q(author__username__icontains=value) |
            Q(author__first_name__icontains=value) |
            Q(author__last_name__icontains=value)
        ).distinct()


class PublishedArticleFilter(ArticleFilter):
    """
    Filter for published articles only.
    Useful for public-facing views.
    """
    
    class Meta(ArticleFilter.Meta):
        model = Article

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Always filter for published articles
        self.queryset = self.queryset.filter(status='published')