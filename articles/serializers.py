from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article
from django.utils import timezone


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for User model when used as article author.
    Only includes safe, public information.
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Serializer for Article list view.
    Includes essential fields and computed properties for overview.
    """
    author = AuthorSerializer(read_only=True)
    reading_time = serializers.ReadOnlyField()
    tags_list = serializers.ReadOnlyField(source='get_tags_list')
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'status', 
            'featured', 'view_count', 'tags', 'tags_list', 
            'reading_time', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'view_count', 'reading_time', 
            'created_at', 'updated_at', 'published_at'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Article detail view (create, retrieve, update).
    Includes all fields with comprehensive validation.
    """
    author = AuthorSerializer(read_only=True)
    reading_time = serializers.ReadOnlyField()
    tags_list = serializers.ReadOnlyField(source='get_tags_list')
    
    # Additional computed fields
    is_published = serializers.ReadOnlyField()
    word_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author', 
            'status', 'featured', 'view_count', 'tags', 'tags_list',
            'reading_time', 'word_count', 'is_published',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'view_count', 'reading_time',
            'word_count', 'is_published', 'created_at', 'updated_at'
        ]

    def get_word_count(self, obj):
        """Calculate word count for the article content."""
        return len(obj.content.split()) if obj.content else 0

    def validate_title(self, value):
        """
        Validate article title.
        """
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        
        # Check for duplicate titles (case-insensitive)
        instance = getattr(self, 'instance', None)
        existing = Article.objects.filter(title__iexact=value.strip())
        if instance:
            existing = existing.exclude(pk=instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("An article with this title already exists.")
        
        return value.strip()

    def validate_content(self, value):
        """
        Validate article content.
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return value.strip()

    def validate_tags(self, value):
        """
        Validate and clean tags.
        """
        if value:
            # Clean and validate tags
            tags = [tag.strip().lower() for tag in value.split(',') if tag.strip()]
            if len(tags) > 10:
                raise serializers.ValidationError("Maximum 10 tags allowed.")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_tags = []
            for tag in tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)
            
            return ','.join(unique_tags)
        return value

    def validate(self, attrs):
        """
        Cross-field validation.
        """
        # If status is being changed to published, set published_at timestamp
        if attrs.get('status') == 'published':
            instance = getattr(self, 'instance', None)
            if not instance or instance.status != 'published':
                attrs['published_at'] = timezone.now()
        
        return attrs

    def create(self, validated_data):
        """
        Create article with current user as author.
        """
        # Get the current user from the request context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update article with additional business logic.
        """
        # If changing from published to draft, clear published_at
        if (validated_data.get('status') == 'draft' and 
            instance.status == 'published'):
            validated_data['published_at'] = None
        
        return super().update(instance, validated_data)


class ArticleCreateSerializer(ArticleDetailSerializer):
    """
    Serializer specifically for article creation.
    Excludes certain fields that shouldn't be set during creation.
    """
    
    class Meta(ArticleDetailSerializer.Meta):
        read_only_fields = ArticleDetailSerializer.Meta.read_only_fields + ['published_at']


class ArticleUpdateSerializer(ArticleDetailSerializer):
    """
    Serializer specifically for article updates.
    Allows partial updates and includes all editable fields.
    """
    
    class Meta(ArticleDetailSerializer.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional for partial updates
        if kwargs.get('partial', False):
            for field_name, field in self.fields.items():
                if field_name not in self.Meta.read_only_fields:
                    field.required = False