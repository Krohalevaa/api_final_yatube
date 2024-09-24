from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.contrib.auth import get_user_model

from posts.models import Comment, Post, Group, Follow

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Post."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    post = serializers.ReadOnlyField(source='post.id')

    class Meta:
        fields = '__all__'
        model = Comment


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Group."""
    class Meta:
        fields = '__all__'
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""
    user = serializers.SlugRelatedField(read_only=True, slug_field='username')
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='username')

    class Meta:
        fields = '__all__'
        model = Follow

    def validate_following(self, value):
        """Проверка на то, что нельзя подписаться на самого себя."""
        request = self.context['request']
        if value == request.user:
            raise serializers.ValidationError(
                "Невозможно фолловить себя.")
        return value
