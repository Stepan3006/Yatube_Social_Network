from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group, User
from django.core.cache import cache


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.not_author = User.objects.create_user(username='NoAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.not_author)

    def get_content(self):
        response = self.authorized_client.get(reverse('posts:index'))
        return response.content

    def test_cache(self):
        """Тестируем кэш"""
        self.test_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.test_group
        )
        post_exist = self.get_content()
        self.test_post.delete()
        post_deleted = self.get_content()
        self.assertEqual(post_exist, post_deleted)
        cache.clear()
        post_cleared = self.get_content()
        self.assertNotEqual(post_exist, post_cleared)
