from django.contrib.auth import get_user_model
from packaging.utils import _
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CustomPasswordChangeSerializer,
    CustomUserSerializer,
    UserRegisterSerializer,
)

User = get_user_model()


class UserRegisterAPIView(generics.CreateAPIView):
    """
    Представление регистрации нового пользователя
    """

    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """Метод обработки POST-запроса для регистрации пользователя.
        Метод возвращает информацию о созданном пользователе пропущенную через
        сериалайзер для корректной выдачи информации.
        Два токена, access - для авторизации, и refresh - для обновления
        access токена.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        return Response(tokens)


class CustomPasswordChange(APIView):
    """Кастомный класс для изменения пароля пользователя."""

    permission_classes = (IsAuthenticated,)
    serializer_class = CustomPasswordChangeSerializer

    def post(self, request, format=None):
        """Обрабатывает POST-запрос для изменения пароля пользователя."""
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = request.user

            new_password = serializer.data["new_password"]
            user.set_password(new_password)
            user.save()

            content = {"success": _("Пароль успешно изменен.")}
            return Response(content, status=status.HTTP_200_OK)

        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class UserMe(APIView):
    """Профиль юзера"""

    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer

    def get(self, request, format=None):
        return Response(self.serializer_class(request.user).data)
