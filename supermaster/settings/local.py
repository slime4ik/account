from .base import *

SECRET_KEY = "django-insecure-x#l_qijzh@(777q#2+t&z&0kf*qtcq%-vv4b!h69!mm(jg9rk0"

ALLOWED_HOSTS = ["*"]

MIDDLEWARE += [
    'silk.middleware.SilkyMiddleware',
]

INSTALLED_APPS += [
    "drf_spectacular",
    "silk"
]

# Локальная БД для разработки
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "account",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Account API",
    "DESCRIPTION": "Простой свагер для теста системы авторизации",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
