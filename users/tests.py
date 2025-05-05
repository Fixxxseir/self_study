from rest_framework.test import APITestCase

from users.models import User


class TestEmailUserManagerAddProf(APITestCase):
    def test_create_superuser_is_incorrect(self):
        """Создаем первого superuser"""
        User.objects.create_superuser(
            email="email@emial.ru",
            username="superuser",
            password="superuser",
        )
        user = User.objects.get(email="email@emial.ru")
        self.assertEqual(user.email, "email@emial.ru")
        self.assertEqual(user.role, "admin")

        User.objects.create_superuser(
            email="email2@emial.ru",
            username="superuser",
            password="superuser",
        )
        user = User.objects.get(email="email2@emial.ru")
        self.assertEqual(user.email, "email2@emial.ru")

        User.objects.create_user(
            email="email3@emial.ru",
            username="student",
            password="student",
        )
        user = User.objects.get(email="email3@emial.ru")
        self.assertEqual(user.email, "email3@emial.ru")
        self.assertEqual(user.role, "student")
