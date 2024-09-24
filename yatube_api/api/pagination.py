from rest_framework.pagination import LimitOffsetPagination


class CommentPagination(LimitOffsetPagination):
    """Класс, в котором происходит управление пангинацией в списке постов."""
    default_limit = 2  # Количество объектов по умолчанию
    max_limit = 10  # Максимальное возвращаемое количество объектов
