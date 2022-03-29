from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Post, Group, User


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
        cls.test_post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.public_url = {
            f'/group/{cls.test_group.slug}/': 'posts/group_list.html',
            '/': 'posts/index.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.test_post.id}/': 'posts/post_detail.html',
        }
        cls.private_url = {
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.test_post.id}/edit/': 'posts/create_post.html',
        }
        cls.redirects_private = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{cls.test_post.id}/edit/':
            f'/auth/login/?next=/posts/{cls.test_post.id}/edit/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.not_author = User.objects.create_user(username='NoAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.not_author)

    def test_public_url_exists_at_desired_location(self):
        """Страница /group/Test-slug,/,/profile/<username>,/posts_id"""
        for adress in self.public_url:
            response = self.guest_client.get(adress)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def unexisting_page_url_exists_at_desired_location(self):
        """Страница /unexisting_page доступна любому пользователю."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_on_admin_login(self):
        """Страница /create/,/posts/posts_id/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        for adress, template in self.redirects_private.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(
                    response, template)

    def test_private_url_exists_at_desired_location(self):
        """Страница /create/,/posts/posts_id/edit/ доступна автору."""
        for adress in self.private_url:
            response = self.authorized_client_author.get(adress)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_public_uses_correct_template(self):
        """URL-адрес публичный использует соответствующий шаблон."""
        for adress, template in self.public_url.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_private_uses_correct_template(self):
        """URL-адрес приватный использует соответствующий шаблон."""
        for adress, template in self.private_url.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_post_create_url_redirect_anonymous_on_author_login(self):
        """Страница /posts/posts_id/edit/ перенаправит не автора
        на страницу поста.
        """
        response = self.authorized_client.get(
            f'/posts/{self.test_post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.test_post.id}/')

    def unexisting_page_url_exists_at_desired_location(self):
        """Проверяем несуществующую страницу."""
        response = self.guest_client.get('/none_url')
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
