import factory
from django.contrib.auth.models import User
from faker import Faker
from .models import Article

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User
        
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'defaultpass123'
        self.set_password(password)
        self.save()


class ArticleFactory(factory.django.DjangoModelFactory):
    """Factory for creating test articles."""
    
    class Meta:
        model = Article
        
    title = factory.Faker('sentence', nb_words=4)
    content = factory.Faker('text', max_nb_chars=1000)
    author = factory.SubFactory(UserFactory)
    status = factory.Iterator(['draft', 'published', 'archived'])
    featured = factory.Faker('boolean', chance_of_getting_true=20)
    tags = factory.LazyFunction(lambda: ','.join(fake.words(nb=3)))
    
    @factory.post_generation
    def view_count(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.view_count = extracted
        elif self.status == 'published':
            self.view_count = fake.random_int(min=0, max=1000)


class PublishedArticleFactory(ArticleFactory):
    """Factory for published articles only."""
    status = 'published'


class FeaturedArticleFactory(ArticleFactory):
    """Factory for featured articles."""
    status = 'published'
    featured = True