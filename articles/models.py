from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinLengthValidator


class Article(models.Model):
    """
    Article model with comprehensive fields for a blog-like system.
    Includes title, content, author, timestamps, and status management.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Article title (5-200 characters)"
    )
    
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="URL-friendly version of title (auto-generated if empty)"
    )
    
    content = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text="Article content (minimum 10 characters)"
    )
    
    excerpt = models.CharField(
        max_length=500,
        blank=True,
        help_text="Brief description or excerpt (auto-generated from content if empty)"
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        help_text="Article author"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Article publication status"
    )
    
    featured = models.BooleanField(
        default=False,
        help_text="Mark as featured article"
    )
    
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times article has been viewed"
    )
    
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags (e.g., 'python,django,api')"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when article was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when article was last updated"
    )
    
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when article was published"
    )

    class Meta:
        ordering = ['-created_at']  # Newest first by default
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['featured']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug and excerpt.
        """
        # Auto-generate slug from title if not provided
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            # Ensure slug uniqueness
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        # Auto-generate excerpt from content if not provided
        if not self.excerpt:
            # Take first 150 words and add ellipsis
            words = self.content.split()[:30]
            self.excerpt = ' '.join(words)
            if len(self.content.split()) > 30:
                self.excerpt += '...'
        
        super().save(*args, **kwargs)

    @property
    def reading_time(self):
        """
        Calculate estimated reading time based on word count.
        Assumes average reading speed of 200 words per minute.
        """
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    def get_tags_list(self):
        """
        Return tags as a list.
        """
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def is_published(self):
        """
        Check if article is published.
        """
        return self.status == 'published'
