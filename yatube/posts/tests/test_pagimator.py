from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    first_page_contains = 10
    second_page_contains = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.test_post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост' + str(i),
                group=cls.test_group
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.not_author = User.objects.create_user(username='NoAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.not_author)

    def test_first_page_contains_ten_records(self):
        """Проверка паджинатора первой страницы."""
        templates_pages_name = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'Test-slug'}),
            reverse('posts:profile', kwargs={'username': 'test_author'}),
        ]
        for adress in templates_pages_name:
            response = self.authorized_client.get(adress)
            self.assertEqual(len(
                response.context['page_obj']), self.first_page_contains
            )

    def test_second_page_contains_three_records(self):
        """Проверка паджинатора второй страницы."""
        templates_pages_name = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'Test-slug'}),
            reverse('posts:profile', kwargs={'username': 'test_author'}),
        ]
        for adress in templates_pages_name:
            response = self.authorized_client.get(adress + '?page=2')
            self.assertEqual(len(
                response.context['page_obj']), self.second_page_contains
            )
