from posts.models import Post, Comment, Group, Follow
from .serializers import (
    PostSerializer, CommentSerializer, GroupSerializer, FollowSerializer)
from .permissions1 import IsOwnerOrReadOnly

from rest_framework import status, filters, viewsets, permissions
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ValidationError


class PostPagination(LimitOffsetPagination):
    default_limit = 2  # Количество объектов по умолчанию
    max_limit = 10   


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', None)
        if ordering is not None:
            ordering = ordering.split(',')
            queryset = queryset.order_by(*ordering)
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise ValidationError("User must be authenticated.")
        serializer.save(author=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise ValidationError("User must be authenticated.")
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'following__username']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise ValidationError("User must be authenticated.")
        return Follow.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)  # many=True для возврата списка
        return Response(serializer.data)

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise ValidationError("User must be authenticated.")
        following = serializer.validated_data.get('following')
        if following == self.request.user:
            raise serializers.ValidationError("You cannot follow yourself.")
        serializer.save(user=self.request.user)
