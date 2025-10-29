from rest_framework.permissions import BasePermission


class IsAuthenticatedAndActiveUser(BasePermission):
    """Проверяет что пользователь залогинен и аккаунт активен - 401 если нет"""

    message = "Требуется авторизация или аккаунт не активен"

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active
        )


class IsDairyOwner(BasePermission):
    """Проверяет что пользователь является владельцем дневника - 403 если нет"""

    message = "Вы не являетесь владельцем дневника"

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
