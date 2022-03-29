import shutil
import tempfile

from ..forms import PostForm
from ..models import Post, Group, User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
            group=cls.test_group,
            image='posts/small.gif',
        )
        cls.test_form = PostForm()
        cls.templates_page_names = {
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'test_author'}),
            reverse(
                'posts:group_posts', kwargs={'slug': 'Test-slug'}
            ),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

    def test_image_appears_post(self):
        """Проверяем при отправке PostForm с картинкой"""
        """создается запись в базе данных"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': uploaded,
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
        self.assertTrue(
            Post.objects.filter(
                text=self.test_post.text,
                group=self.test_group.pk,
                image='posts/small.gif',
            ).exists()
        )

    def check_post(self, post):
        """Принимаем обьект поста и проверяем атрибут изображение"""
        self.post = post
        self.assertEqual(post.image, 'posts/small.gif')

    def test_page_show_image_context(self):
        """Изображение передается в словаре"""
        for adress in self.templates_page_names:
            response = self.guest_client.get(adress)
            posts_from_context = response.context['page_obj'][0]
            self.check_post(posts_from_context)

    def test_page_post_detail_show_image_context(self):
        """Изображение передается в словаре на страницу поста"""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.test_post.pk}'}
            )
        )
        posts_from_context = response.context.get('post')
        self.check_post(posts_from_context)
