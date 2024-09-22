from django.contrib.auth import get_user_model
from django.db import models

# from posts.constant import MAX_LENGTH

User = get_user_model()


class Post(models.Model):
    # title = models.CharField(max_length=100)
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True)
    # update_date = models.DateTimeField(
    #     'Дата обновления публикации', auto_now=True)
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
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
    # updated = models.DateTimeField(
    #     'Дата обновления комментария', auto_now=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follows')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'following')


class Group(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, default='default-group')
    description = models.TextField()

    # def __str__(self):
    #     return self.title
# default='default-group
#


# from django.db import models

# class Group(models.Model):
#     title = models.CharField(max_length=200)
#     slug = models.SlugField(unique=True)  # Поле slug должно быть определено
#     description = models.TextField()

#     def __str__(self):
#         return self.title
