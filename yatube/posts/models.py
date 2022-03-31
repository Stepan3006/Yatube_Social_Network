from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название группы",
        help_text="Здесь будет название группы, пиши же ну",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Это слаг",
        help_text="Этому доходяге уже ничего не поможет",
    )
    description = models.TextField(
        verbose_name="Описание группы",
        help_text="Здесь будет описание группы, пиши же ну",
        max_length=300,
    )

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Здесь будет текст поста, пиши же ну",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        help_text="Все мы очень ждем",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор",
        help_text="Великий и ужасный",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name="Группа",
        help_text="Крови на рукаве",
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор",
        help_text="Великий и ужасный",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name="Пост",
        help_text="Сдал, пост принял",
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Здесь будет текст поста, пиши же ну",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата комментария",
        help_text="Дата создания чуда",
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор",
        help_text="Буду постить",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
        help_text="Буду читать",
    )
