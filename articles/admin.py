from django.contrib import admin
from django.utils.html import format_html
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Article model.
    """
    
    list_display = [
        'title', 
        'author', 
        'status',
        'featured_badge',
        'view_count',
        'reading_time_display',
        'created_at',
        'published_at'
    ]
    
    list_filter = [
        'status',
        'featured', 
        'created_at',
        'published_at',
        'author'
    ]
    
    search_fields = [
        'title',
        'content', 
        'tags',
        'author__username',
        'author__first_name',
        'author__last_name'
    ]
    
    prepopulated_fields = {'slug': ('title',)}
    
    readonly_fields = [
        'view_count', 
        'created_at', 
        'updated_at',
        'reading_time_display',
        'word_count_display'
    ]
    
    fieldsets = (
        ('Article Content', {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('Metadata', {
            'fields': ('author', 'status', 'featured', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'reading_time_display', 'word_count_display'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'mark_as_published',
        'mark_as_draft', 
        'toggle_featured'
    ]
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def featured_badge(self, obj):
        """Display featured status as a badge."""
        if obj.featured:
            return format_html(
                '<span style="color: gold; font-weight: bold;">★ Featured</span>'
            )
        return '-'
    featured_badge.short_description = 'Featured'
    
    def reading_time_display(self, obj):
        """Display reading time with unit."""
        time = obj.reading_time
        return f"{time} min{'s' if time != 1 else ''}"
    reading_time_display.short_description = 'Reading Time'
    
    def word_count_display(self, obj):
        """Display word count."""
        return len(obj.content.split()) if obj.content else 0
    word_count_display.short_description = 'Word Count'
    
    def mark_as_published(self, request, queryset):
        """Admin action to mark articles as published."""
        from django.utils import timezone
        count = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{count} article(s) marked as published.')
    mark_as_published.short_description = 'Mark selected articles as published'
    
    def mark_as_draft(self, request, queryset):
        """Admin action to mark articles as draft."""
        count = queryset.update(status='draft', published_at=None)
        self.message_user(request, f'{count} article(s) marked as draft.')
    mark_as_draft.short_description = 'Mark selected articles as draft'
    
    def toggle_featured(self, request, queryset):
        """Admin action to toggle featured status."""
        for article in queryset:
            article.featured = not article.featured
            article.save(update_fields=['featured'])
        self.message_user(request, f'Featured status toggled for {queryset.count()} article(s).')
    toggle_featured.short_description = 'Toggle featured status'
