from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Регистрация модели в админ панели
    """

    list_display = ("email", "username", "role", "is_staff")
    list_filter = ("role",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("username", "phone_number", "country", "avatar")},
        ),
        (
            "Permissions",
            {
                "fields": ("role", "is_active", "is_staff", "is_superuser"),
            },
        ),
    )
