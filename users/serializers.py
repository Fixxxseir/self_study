from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания и изменения пользователя
    """

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "phone_number",
            "avatar",
            "country",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.role = "student"
        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)
        return {
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }


class CustomPasswordChangeSerializer(serializers.Serializer):
    """
    Кастомный сериализатор для изменения пароля пользователя.
    Проверяет старый пароль и устанавливает новый.
    """

    old_password = serializers.CharField(required=True, max_length=128)
    new_password = serializers.CharField(required=True, max_length=128)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not authenticate(username=user.email, password=value):
            raise serializers.ValidationError("Старый пароль неверный.")
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "email",
            "password",
            "phone_number",
            "avatar",
            "country",
            "is_staff",
            "is_active",
            "is_superuser",
        ]
        read_only_fields = [
            "id",
            "date_joined",
        ]
