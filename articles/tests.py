import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import json

from .models import Article
from .serializers import ArticleDetailSerializer, ArticleListSerializer


class ArticleModelTest(TestCase):
    """Test Article model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
    def test_article_creation(self):
        """Test basic article creation."""
        article = Article.objects.create(
            title='Test Article',
            content='This is a test article content that is long enough.',
            author=self.user,
            status='published',
            tags='django,test'
        )
        
        self.assertEqual(article.title, 'Test Article')
        self.assertEqual(article.author, self.user)
        self.assertEqual(article.status, 'published')
        self.assertTrue(article.slug)  # Auto-generated slug
        self.assertTrue(article.excerpt)  # Auto-generated excerpt
        
    def test_slug_auto_generation(self):
        """Test automatic slug generation from title."""
        article = Article.objects.create(
            title='My Amazing Django Tutorial',
            content='Content here that meets minimum length requirement.',
            author=self.user
        )
        
        self.assertEqual(article.slug, 'my-amazing-django-tutorial')
        
    def test_slug_uniqueness(self):
        """Test slug uniqueness handling."""
        # Create first article
        article1 = Article.objects.create(
            title='Same Title',
            content='First article content that is long enough.',
            author=self.user
        )
        
        # Create second article with same title
        article2 = Article.objects.create(
            title='Same Title',
            content='Second article content that is long enough.',
            author=self.user
        )
        
        self.assertEqual(article1.slug, 'same-title')
        self.assertEqual(article2.slug, 'same-title-1')
        
    def test_excerpt_auto_generation(self):
        """Test automatic excerpt generation."""
        long_content = ' '.join(['word'] * 50)  # 50 words
        article = Article.objects.create(
            title='Test Article',
            content=long_content,
            author=self.user
        )
        
        # Should take first 30 words + ellipsis
        expected_excerpt = ' '.join(['word'] * 30) + '...'
        self.assertEqual(article.excerpt, expected_excerpt)
        
    def test_reading_time_calculation(self):
        """Test reading time calculation."""
        content_200_words = ' '.join(['word'] * 200)
        article = Article.objects.create(
            title='Test Article',
            content=content_200_words,
            author=self.user
        )
        
        self.assertEqual(article.reading_time, 1)  # 200 words / 200 wpm = 1 min
        
    def test_get_tags_list(self):
        """Test tags parsing into list."""
        article = Article.objects.create(
            title='Test Article',
            content='Content here that meets minimum length requirement.',
            author=self.user,
            tags='django, python, api, rest'
        )
        
        expected_tags = ['django', 'python', 'api', 'rest']
        self.assertEqual(article.get_tags_list(), expected_tags)
        
    def test_is_published(self):
        """Test publication status check."""
        draft_article = Article.objects.create(
            title='Draft Article',
            content='Content here that meets minimum length requirement.',
            author=self.user,
            status='draft'
        )
        
        published_article = Article.objects.create(
            title='Published Article',
            content='Content here that meets minimum length requirement.',
            author=self.user,
            status='published'
        )
        
        self.assertFalse(draft_article.is_published())
        self.assertTrue(published_article.is_published())


class ArticleAPITest(APITestCase):
    """Test Article API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            email='other@example.com'
        )
        
        # Create test articles
        self.published_article = Article.objects.create(
            title='Published Test Article',
            content='This is a published test article with enough content.',
            author=self.user,
            status='published',
            tags='django,test'
        )
        
        self.draft_article = Article.objects.create(
            title='Draft Test Article',
            content='This is a draft test article with enough content.',
            author=self.user,
            status='draft',
            tags='django,draft'
        )
        
    def get_jwt_token(self, user):
        """Helper method to get JWT token for user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
        
    def test_list_articles_anonymous(self):
        """Test listing articles as anonymous user (only published)."""
        url = reverse('article-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only published
        self.assertEqual(response.data['results'][0]['title'], 'Published Test Article')
        
    def test_list_articles_authenticated(self):
        """Test listing articles as authenticated user (own drafts + published)."""
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('article-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Both articles visible
        
    def test_retrieve_article(self):
        """Test retrieving a specific article."""
        url = reverse('article-detail', kwargs={'pk': self.published_article.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Published Test Article')
        
        # Check if view count was incremented
        self.published_article.refresh_from_db()
        self.assertEqual(self.published_article.view_count, 1)
        
    def test_create_article_anonymous(self):
        """Test creating article as anonymous user (should fail)."""
        url = reverse('article-list')
        data = {
            'title': 'New Article',
            'content': 'New article content that meets minimum requirements.',
            'status': 'published'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_article_authenticated(self):
        """Test creating article as authenticated user."""
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('article-list')
        data = {
            'title': 'New Authenticated Article',
            'content': 'New article content that meets minimum requirements and is long enough.',
            'status': 'published',
            'tags': 'new,authenticated,test'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Authenticated Article')
        self.assertEqual(response.data['author']['username'], 'testuser')
        
    def test_update_own_article(self):
        """Test updating own article."""
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('article-detail', kwargs={'pk': self.draft_article.pk})
        data = {'title': 'Updated Article Title'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Article Title')
        
    def test_update_other_user_article(self):
        """Test updating another user's article (should fail)."""
        token = self.get_jwt_token(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('article-detail', kwargs={'pk': self.draft_article.pk})
        data = {'title': 'Hacked Title'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_own_article(self):
        """Test deleting own article."""
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('article-detail', kwargs={'pk': self.draft_article.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Article.objects.filter(pk=self.draft_article.pk).exists())
        
    def test_search_articles(self):
        """Test searching articles."""
        url = reverse('article-list')
        response = self.client.get(url, {'search': 'Published'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('Published', response.data['results'][0]['title'])
        
    def test_filter_articles_by_status(self):
        """Test filtering articles by status."""
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('article-list')
        response = self.client.get(url, {'status': 'draft'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'draft')
        
    def test_order_articles(self):
        """Test ordering articles."""
        url = reverse('article-list')
        response = self.client.get(url, {'ordering': 'title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be ordered alphabetically by title
        
    def test_featured_articles_endpoint(self):
        """Test featured articles custom endpoint."""
        # Make an article featured
        self.published_article.featured = True
        self.published_article.save()
        
        url = reverse('article-featured')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['featured'])
        
    def test_my_articles_endpoint(self):
        """Test my articles custom endpoint."""
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('article-my-articles')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Both user's articles
        
    def test_articles_by_author_endpoint(self):
        """Test articles by author endpoint."""
        url = reverse('article-by-author')
        response = self.client.get(url, {'author': 'testuser'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only published ones
        
    def test_articles_by_tag_endpoint(self):
        """Test articles by tag endpoint."""
        url = reverse('article-by-tag')
        response = self.client.get(url, {'tag': 'django'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only published with django tag
        
    def test_article_stats_endpoint(self):
        """Test article statistics endpoint."""
        url = reverse('article-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_articles', response.data)
        self.assertIn('published_articles', response.data)
        self.assertIn('draft_articles', response.data)
        
        
class ArticleSerializerTest(TestCase):
    """Test Article serializers."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.article_data = {
            'title': 'Test Article',
            'content': 'Test content that meets minimum length requirements.',
            'status': 'published',
            'tags': 'test,serializer'
        }
        
    def test_article_serialization(self):
        """Test article serialization."""
        article = Article.objects.create(
            author=self.user,
            **self.article_data
        )
        
        serializer = ArticleDetailSerializer(article)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Article')
        self.assertEqual(data['author']['username'], 'testuser')
        self.assertIn('reading_time', data)
        self.assertIn('word_count', data)
        
    def test_title_validation(self):
        """Test title validation."""
        # Test short title
        data = self.article_data.copy()
        data['title'] = 'Hi'  # Too short
        
        serializer = ArticleDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
    def test_content_validation(self):
        """Test content validation."""
        # Test short content
        data = self.article_data.copy()
        data['content'] = 'Short'  # Too short
        
        serializer = ArticleDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
        
    def test_tags_validation(self):
        """Test tags validation and cleaning."""
        data = self.article_data.copy()
        data['tags'] = 'tag1, tag2, tag1, TAG2'  # Duplicates and case issues
        
        serializer = ArticleDetailSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['tags'], 'tag1,tag2')


@pytest.mark.django_db
class TestArticleAPI:
    """Pytest-style tests for Article API."""
    
    def test_article_creation_with_factory(self):
        """Test using factory for article creation."""
        from django.contrib.auth.models import User
        
        user = User.objects.create_user(username='factoryuser', password='pass')
        article = Article.objects.create(
            title='Factory Article',
            content='Content created using factory pattern for testing purposes.',
            author=user,
            status='published'
        )
        
        assert article.title == 'Factory Article'
        assert article.author.username == 'factoryuser'
        assert article.is_published() == True
