from rest_framework import filters, viewsets, permissions
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404

from posts.models import Post, Group
from .serializers import (
    PostSerializer, CommentSerializer, GroupSerializer, FollowSerializer)
from .permissions import IsOwnerOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """Управление операциями CRUD с постами."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Создает новый пост, привязывая его к текущему
        авторизованному пользователю.
        """
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления операциями CRUD с комментариями."""
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Возвращает список комментариев, отфильтрованный по посту.
        """
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return post.comments.all()

    def perform_create(self, serializer):
        """
        Создает новый комментарий для указанного поста,
        привязывая его к текущему пользователю.
        """
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet только для чтения для управления группами."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]


class FollowViewSet(viewsets.ModelViewSet):
    """ViewSet для управления операциями CRUD с подписками."""
    serializer_class = FollowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'following__username']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает список подписок текущего пользователя."""
        return self.request.user.follows.all()
