from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешение, которое предоставляет доступ только владельцу объекта
    для изменения данных. Чтение разрешено всем пользователям.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthenticatedAndOwnerOrReadOnly(BasePermission):
    """
    Разрешение, которое позволяет доступ только аутентифицированным
    пользователям, а изменения объекта могут делать только его владельцы.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
