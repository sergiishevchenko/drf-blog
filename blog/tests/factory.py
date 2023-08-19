import factory
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from posts.models import Category, Comment, Like, Post
from users.models import User


fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: '%s@example.org' % n)
    first_name = fake.first_name()
    last_name = fake.last_name()

    class Meta:
        model = User


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.LazyAttribute(lambda _: f'{fake.text(max_nb_chars=5)}')

    class Meta:
        model = Category


class PostFactory(factory.django.DjangoModelFactory):
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    title = factory.Sequence(lambda n: 'test_name_%d' % n)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
    content = factory.Sequence(lambda n: 'test_content_%d' % n)
    image = factory.django.ImageField(filename='test_image.jpg', width=800, height=800, color='green', format='JPEG')
    status = True
    published_at = timezone.now()

    class Meta:
        model = Post


class LikeFactory(factory.django.DjangoModelFactory):
    like_user = factory.SubFactory(UserFactory)
    like_post = factory.SubFactory(PostFactory)

    class Meta:
        model = Like


class CommentFactory(factory.django.DjangoModelFactory):
    comment_user = factory.SubFactory(UserFactory)
    comment_post = factory.SubFactory(PostFactory)
    comment = factory.lazy_attribute(lambda _: f'{fake.text(max_nb_chars=5)}')

    class Meta:
        model = Comment
