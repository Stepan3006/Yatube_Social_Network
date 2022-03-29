from ..forms import PostForm, CommentForm
from ..models import Post, Group, User, Comment
from django.test import Client, TestCase
from django.urls import reverse


class PostCreateFormTests(TestCase):
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
            group=cls.test_group
        )
        cls.test_form = PostForm()
        cls.test_comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.test_post,
        )
        cls.comment_form = CommentForm(
            data={
                'text': 'Тестовый комментарий',
            }
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': self.test_post.text,
            'group': self.test_group.pk,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.test_post.author}
        )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.test_post.text,
                group=self.test_group.pk,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирования записи в Post."""
        form_data = {
            'text': self.test_post.text,
            'group': self.test_group.pk,
        }
        response = self.authorized_client_author.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.test_post.pk}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.test_post.pk}'}
        )
        )
        self.assertTrue(
            Post.objects.filter(
                text=self.test_post.text,
                group=self.test_group.pk,
            ).exists()
        )

    def test_user_add_comment(self):
        """Проверяем может ли авторизированный юзер"""
        """ оставлять комментарии и запись появляется в базе"""
        response = self.authorized_client_author.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{self.test_post.pk}'}
            ),
            data=self.comment_form.data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.test_post.pk}'}
        )
        )
        self.assertEqual(
            self.test_comment.text, self.comment_form.data['text']
        )
        response_guest = self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{self.test_post.pk}'}
            ),
            data=self.comment_form.data,
            follow=True
        )
        self.assertRedirects(
            response_guest, '/auth/login/?next=/posts/1/comment/'
        )
