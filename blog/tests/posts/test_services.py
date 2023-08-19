import pytest

from posts.models import Post
from posts.services import create_post, delete_post, update_post


pytestmark = pytest.mark.django_db


def test_create_post(user_factory, category_factory, media_root):
    user = user_factory.create()
    category = category_factory.create()

    post = create_post(
        user=user,
        category=category,
        title='title 1',
        content='content 1',
        image='image 1',
        status=True,
        published_at='2023-03-03 01:00:00',
    )

    assert post.author == user
    assert post.category == category
    assert post.title == 'title 1'
    assert post.content == 'content 1'
    assert post.image == 'image 1'
    assert post.status is True
    assert post.published_at == '2023-03-03 01:00:00'


def test_update_post(post_factory, user_factory, media_root):
    author = user_factory.create()
    post = post_factory.create(author=author)

    validated_data = {
        'title': 'title 2',
        'content': 'content 2',
        'slug': 'new_slug',
        'image': 'new_image.jpg',
        'status': True,
        'published_at': '2023-03-03 01:00:00',
    }

    update_post(validated_data, author, post.slug)
    post.refresh_from_db()

    assert post.title == 'title 2'
    assert post.content == 'content 2'
    assert post.slug == 'new_slug'
    assert post.image == 'new_image.jpg'
    assert post.status is True
    assert post.published_at.strftime('%Y-%m-%d %H:%M:%S') == '2023-03-03 01:00:00'


def test_delete_post(post_factory, user_factory, media_root):
    author = user_factory.create()
    post = post_factory.create(author=author)
    delete_post(post.slug)

    with pytest.raises(Post.DoesNotExist):
        Post.objects.get(slug=post.slug)
