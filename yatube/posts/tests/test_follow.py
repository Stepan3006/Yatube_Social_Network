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
        cls.redirects_private = {
            f'/profile/{cls.user}/follow':
                f'/auth/login/?next=/profile/{cls.user}/follow/',
            f'/profile/{cls.user}/unfollow':
                f'/auth/login/?next=/profile/{cls.user}/unfollow/',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_redirect_anonymous_on_admin_login(self):
        """Авторизованный может
        подписываться на других пользователей
        и удалять их из подписок.
        """
        for adress, template in self.redirects_private.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(
                    response, template,
                    status_code=HTTPStatus.MOVED_PERMANENTLY,
                    target_status_code=HTTPStatus.OK,
                )

    def test_post_appears_follow_page(self):
        """Пост появляется на главной странице, подписчика"""
        """и не появляется у других."""
