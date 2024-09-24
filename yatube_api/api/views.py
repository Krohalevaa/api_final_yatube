from rest_framework import status, filters, viewsets, permissions, serializers
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .pagination import CommentPagination
from posts.models import Post, Comment, Group, Follow
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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Создает новый комментарий для указанного поста,
        привязывая его к текущему пользователю.
        """
        post = Post.objects.get(id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)

    # не могу убрать эти методы, перестают проходить тесты
    def list(self, request, *args, **kwargs):
        """Возвращает список комментариев, поддерживая пагинацию."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  # тут возвращаем список данных


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet только для чтения для управления группами."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]


class FollowViewSet(viewsets.ModelViewSet):
    """ViewSet для управления операциями CRUD с подписками."""
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'following__id']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список подписок текущего пользователя.
        Фильтрует по полю `following__username`, если указан параметр поиска.
        """
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
        Создает новую подписку, проверяя, что подписка еще не существует.
        """
        following = serializer.validated_data.get('following')
        if Follow.objects.filter(
            user=self.request.user, following=following
        ).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя.")
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
