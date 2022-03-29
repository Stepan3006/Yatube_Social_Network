from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Post, Group, User, Follow
from django.urls import reverse


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.user_follow = User.objects.create_user(username='follow ')
        cls.user_unfollow = User.objects.create_user(username='unfollow')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )
        cls.redirects_private = {
            f'/profile/{cls.user}/follow':
                f'/auth/login/?next=/profile/{cls.user}/follow/',
            f'/profile/{cls.user}/unfollow':
                f'/auth/login/?next=/profile/{cls.user}/unfollow/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.authorized_client_follow = Client()
        self.authorized_client_follow.force_login(self.user_follow)
        self.authorized_client_unfollow = Client()
        self.authorized_client_unfollow.force_login(self.user_unfollow)

    def test_redirect_anonymous_on_admin_login(self):
        """НеАвторизованный неможет
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

    def test_login_make_or_delete_follow(self):
        """Авторизованный может
        подписываться на других пользователей
        и удалять их из подписок.
        """
        follow_count = Follow.objects.count()
        self.response = self.authorized_client_follow.get(
            reverse(
                'posts:profile_follow', args=[self.user]
            ),
        )
        self.assertTrue(Follow.objects.filter(
            user=self.user_follow,
            author=self.user,
        ).exists()
        )
        self.assertEqual(follow_count + 1, Follow.objects.count())
        self.response = self.authorized_client_follow.get(
            reverse(
                'posts:profile_unfollow', args=[self.user]
            ),
        )
        self.assertEqual(follow_count, Follow.objects.count())

    def test_post_appears_follow_page(self):
        """Пост появляется на главной странице, подписчика"""
        """и не появляется у других."""
        self.response = self.authorized_client_follow.get(
            reverse(
                'posts:profile_follow', args=[self.user]
            ),
        )
        self.test_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.test_group
        )
        response_follow = self.authorized_client_follow.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            response_follow.context['page_obj'][0], self.test_post
        )
        response_unfollow = self.authorized_client_unfollow.get(
            reverse('posts:follow_index')
        )
        self.assertNotEqual(
            response_unfollow.content, response_follow.content
        )
