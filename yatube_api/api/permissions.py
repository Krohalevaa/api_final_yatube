from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешение, которое предоставляет доступ только владельцу объекта
    для изменения данных. Чтение разрешено всем пользователям.
    """
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IsAuthenticatedAndOwnerOrReadOnly(BasePermission):
    """
    Разрешение, которое позволяет доступ только аутентифицированным
    пользователям, а изменения объекта могут делать только его владельцы.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method
