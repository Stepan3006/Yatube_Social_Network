from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


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
            group=cls.test_group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.not_author = User.objects.create_user(username='NoAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.not_author)

    def check_post(self, post):
        """Принимаем обьект поста и проверяем атрибуты"""
        self.post = post
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': 'Test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'test_author'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.test_post.pk}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.test_post.pk}'}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        posts_from_context = response.context['page_obj'][0]
        self.check_post(posts_from_context)
        posts = Post.objects.all()[0]
        self.assertEqual(posts_from_context, posts)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:group_posts', kwargs={'slug': 'Test-slug'}
            )
        )
        posts_from_context = response.context['page_obj'][0]
        self.check_post(posts_from_context)
        posts = Post.objects.filter(group_id='1')[0]
        self.assertEqual(posts_from_context, posts)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'test_author'},
            )
        )
        posts_from_context = response.context['page_obj'][0]
        self.check_post(posts_from_context)
        posts = Post.objects.filter(author='1')[0]
        self.assertEqual(posts_from_context, posts)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.test_post.pk}'}
            )
        )
        post_from_context = response.context.get('post')
        self.check_post(post_from_context)

    def test_post_appears_index__post_detail_profile_page(self):
        """Пост появляется на главной странице, странице"""
        """пользователя и в профиле пользователя."""
        templates_pages_name = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'Test-slug'}),
            reverse('posts:profile', kwargs={'username': 'test_author'}),
        ]
        posts = Post.objects.filter(group_id='1')[0]
        for adress in templates_pages_name:
            response = self.authorized_client.get(adress)
            self.assertEqual(response.context['page_obj'][0], posts)

    def test_post_create_page_show_correct_context(self):
        """Проверка - контекста страницы создания поста,коректная форма"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for fields, expected_type in form_fields.items():
            with self.subTest(fields=fields):
                form_field = response.context['form'].fields[fields]
                self.assertIsInstance(form_field, expected_type)

    def test_post_edit_page_show_correct_context(self):
        """Проверка контекста страницы редактирования поста,корректная форма"""
        response = self.authorized_client_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.test_post.pk}'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for fields, expected_type in form_fields.items():
            with self.subTest(fields=fields):
                form_field = response.context['form'].fields[fields]
                self.assertIsInstance(form_field, expected_type)
