# Generated by Django 2.2.6 on 2022-03-27 06:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0004_auto_20220326_1447'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Здесь будет текст поста, пиши же ну', verbose_name='Текст комментария')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Дата создания чуда', verbose_name='Дата комментария')),
                ('author', models.ForeignKey(help_text='Великий и ужасный', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('post', models.ForeignKey(blank=True, help_text='Сдал, пост принял', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='posts.Post', verbose_name='Пост')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ('-created',),
            },
        ),
    ]
