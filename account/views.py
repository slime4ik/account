from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import permissions
from http import HTTPMethod
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# Локальные импорты
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    DairySerializer,
)
from .services import UserAuthService
from .permissions import IsAuthenticatedAndActiveUser, IsDairyOwner
from .models import User, Diary

import logging

logger = logging.getLogger(__name__)


class UserAuthenticationViewSet(viewsets.ViewSet):
    """"""

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: None},
        description="Регистрация пользователя",
    )
    @action(detail=False, methods=[HTTPMethod.POST])
    def register(self, request: Request) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, error = UserAuthService.register_user(serializer.validated_data)
        if user is None:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Вы успешно зарегистрировались!",
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: None},
        description="Вход пользователя",
    )
    @action(detail=False, methods=[HTTPMethod.POST])
    def login(self, request: Request) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Отдает токены фронту
        response = UserAuthService.login_user(serializer.validated_data)
        return Response(response, status=status.HTTP_200_OK)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"refresh": {"type": "string"}},
            }
        },
        responses={204: None, 400: None},
        description="Выход из аккаунта",
    )
    @action(
        detail=False,
        methods=[HTTPMethod.POST],
        permission_classes=[permissions.IsAuthenticated],
    )
    def logout(self, request: Request) -> Response:
        """Выход с добавлением refresh токена в blacklist"""
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"Пользователь {request.user.username} вышел из аккаунта")
            return Response(
                {"message": "Выход выполнен успешно"}, status=status.HTTP_204_NO_CONTENT
            )
        except KeyError:
            logger.error(
                f"Отсутствует refresh токен для пользователя {request.user.username}"
            )
            return Response(
                {"error": "Refresh токен обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TokenError as e:
            logger.error(
                f"Неверный refresh токен для пользователя {request.user.username}: {e}"
            )
            return Response(
                {"error": "Неверный токен"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=[HTTPMethod.DELETE],
        permission_classes=[IsAuthenticatedAndActiveUser],
    )
    def delete(self, request: Request) -> Response:
        """Мягкое удаление аккаунта"""
        try:
            user = request.user
            user.soft_delete()

            try:
                refresh_token = request.data.get("refresh")
                if refresh_token:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
            except (
                TokenError,
                KeyError,
                AttributeError,
            ):  # Если нет токена просто отдаем респонс
                pass

            return Response(
                {"message": "Аккаунт успешно удален"}, status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Ошибка удаления аккаунта: {e}")
            return Response(
                {"error": "Ошибка при удалении аккаунта"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateProfileAPIView(APIView):
    """Обновление профиля"""

    permission_classes = [IsAuthenticatedAndActiveUser]

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: None},
        description="Обновление профиля",
    )
    def patch(self, request: Request) -> Response:
        serializer = UserProfileSerializer(
            instance=request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(
            {"message": "Профиль успешно обновлен", "user": serializer.data},
            status=status.HTTP_200_OK,
        )


class GetMyDiaryAPIView(APIView):
    permission_classes = [IsAuthenticatedAndActiveUser, IsDairyOwner]

    def get(self, request: Request, diary_id: int) -> Response:
        # Получение дневника в 1 запрос
        diary = get_object_or_404(Diary.objects.select_related("owner"), id=diary_id)
        # Выдаст 403 если пользователь не является владельцем дневника
        self.check_object_permissions(request, diary)
        serializer = DairySerializer(diary)
        return Response(serializer.data, status=status.HTTP_200_OK)
