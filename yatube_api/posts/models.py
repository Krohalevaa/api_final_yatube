from django.contrib.auth import get_user_model
from django.db import models

from .constants import MAX_LENGTH

User = get_user_model()


class Post(models.Model):
    """Модель для хранения постов пользователей."""
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(
        upload_to='posts/', null=True, blank=True)
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель для хранения комментариев к постам."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)


class Follow(models.Model):
    """Модель для хранения подписок пользователей друг на друга."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follows')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'following')


class Group(models.Model):
    """Модель для хранения групп, к которым могут относиться посты."""
    title = models.CharField(MAX_LENGTH)
    slug = models.SlugField(unique=True, default='default-group')
    description = models.TextField()
