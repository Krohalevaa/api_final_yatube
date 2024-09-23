from posts.models import Post, Comment, Group, Follow
from .serializers import (
    PostSerializer, CommentSerializer, GroupSerializer, FollowSerializer)
from .permissions1 import IsOwnerOrReadOnly

from rest_framework import status, filters, viewsets, permissions, serializers
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ValidationError


class PostPagination(LimitOffsetPagination):
    """Класс, в котором происходит управление пангинацией в списке постов."""
    default_limit = 2  # Количество объектов по умолчанию
    max_limit = 10  # Максимальное возвращаемое количество объектов


class PostViewSet(viewsets.ModelViewSet):
    """Управление операциями CRUD с постами."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Возвращает queryset для списка постов + сортировка."""
        queryset = super().get_queryset()
        ordering = self.request.query_params.get(None)
        if ordering is not None:
            ordering = ordering.split(',')
            queryset = queryset.order_by(*ordering)
        return queryset

    def perform_create(self, serializer):
        """
        Создает новый пост, привязывая его к текущему
        авторизованному пользователю.
        """
        if self.request.user.is_anonymous:
            raise ValidationError("Пользователь должен быть авторизован.")
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления операциями CRUD с комментариями."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Создает новый комментарий для указанного поста,
        привязывая его к текущему пользователю.
        """
        post = Post.objects.get(id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)
        if self.request.user.is_anonymous:
            raise ValidationError("Пользователь должен быть авторизован.")
        serializer.save(author=self.request.user)

    def list(self, request, *args, **kwargs):
        """Возвращает список комментариев, поддерживая пагинацию."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)  # возвращаем список данных

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet только для чтения для управления группами."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        """Возвращает список всех групп."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FollowViewSet(viewsets.ModelViewSet):
    """ViewSet для управления операциями CRUD с подписками."""
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'following__username']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список подписок текущего пользователя.
        Фильтрует по полю `following__username`, если указан параметр поиска.
        """
        if self.request.user.is_anonymous:
            raise ValidationError("Пользователь должен быть авторизован.")
        queryset = Follow.objects.filter(user=self.request.user)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                following__username__icontains=search_query)
        return queryset

    def list(self, request, *args, **kwargs):
        """Возвращает список подписок текущего пользователя."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Создает новую подписку, проверяя, что пользователь не подписывается
        на себя и что подписка еще не существует.
        """
        following = serializer.validated_data.get('following')
        if not following:
            raise serializers.ValidationError()
        if following == self.request.user:
            raise serializers.ValidationError(
                "Вы не можете быть подписаным на самого себя.")

        # Проверяем, существует ли подписка
        if Follow.objects.filter(
            user=self.request.user, following=following).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя.")

        # Если всё хорошо, сохраняем данные
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
