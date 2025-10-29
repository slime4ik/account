from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# локальные импорты
from .models import User, Diary


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Серилизатор для регистрации пользователя
    принимает username, password, password2"""

    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Пользователь с таким логином уже существует",
            )
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Пользователь с таким email уже существует",
            )
        ]
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value: str):
        if len(value) > 15:
            raise serializers.ValidationError(
                "Имя пользователя не должно быть больше 15 символов"
            )
        if len(value) < 3:
            raise serializers.ValidationError(
                "Имя пользователя должно содержать хотябы 3 символа"
            )
        return value

    def validate(self, data):
        if " " in data["password"]:
            raise serializers.ValidationError("Пароль не может содержать пробелы")
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return data


class UserLoginSerializer(serializers.Serializer):
    """Серилизатор для входа принимает username, password
    проверяет правильность ввода логина и пароля и активен ли аккаунт"""

    email = serializers.EmailField(max_length=100, write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Проверка правильно ли пользователь ввел данные от аккаунта(не сработает с is_active=False)
        при неверных данных всегда вернет неверный логин или пароль в целях безопасности
        """
        try:
            user = User.objects.get(email=data["email"])
            if not user.check_password(data["password"]):
                raise User.DoesNotExist()

            if user.is_deleted():
                raise User.DoesNotExist()

        except User.DoesNotExist:
            raise serializers.ValidationError("Неверная почта или пароль")

        data["user"] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = ["id", "username", "date_joined"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate_first_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Имя должно содержать минимум 3 символа.")
        return value.strip()

    def validate_last_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Фамилия должна содержать минимум 3 символа."
            )
        return value.strip()


class DairySerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()  # Для отображение __str__ вместо id

    class Meta:
        model = Diary
        fields = ["owner", "title"]
