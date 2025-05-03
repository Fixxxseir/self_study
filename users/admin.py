from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Регистрация модели в админ панели
    """

    list_display = ("id", "email", "username")