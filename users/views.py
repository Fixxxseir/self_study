from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import UserRegisterSerializer


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
