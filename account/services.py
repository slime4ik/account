from .models import User
from typing import Tuple, Optional, Dict, Any
from django.db import IntegrityError
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

import logging

logger = logging.getLogger(__name__)


class UserAuthService:
    @staticmethod
    def register_user(
        validated_data: Dict[str, Any],
    ) -> Tuple[Optional[User], Optional[str]]:
        """Регистрация по логину и паролю"""
        validated_data.pop("password2", None)
        try:
            user = User.objects.create_user(**validated_data)
            logger.info(
                f"Пользователь с username: '{validated_data['username']}' создан"
            )
            return user, None
        # Проверка уникальности обязательно
        except IntegrityError as e:
            logger.error(
                f"Ошибка уникальности при регистрации {validated_data['username']}: {e}"
            )
            return None, "Пользователь с таким именем уже существует"
        except Exception as e:
            logger.error(f"Ошибка регистрации пользователя {validated_data}", e)
            return None, str(e)

    @staticmethod
    def login_user(validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Вход по логину и паролю отдает токены"""
        user = validated_data["user"]
        # Делаем и возвращаем токены пользователю
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        logger.info(f"Пользователь {validated_data['email']} вошел в аккаунт")
        # Можно переделать httponly cookie если делаем для веба
        return {
            "tokens": {
                "refresh": str(refresh),
                "access": str(access),
            },
            # "user": user, # Если хотим вернуть обьект пользователя фронту
            "message": "Вход выполнен успешно",
        }
