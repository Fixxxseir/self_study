from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Answer, Course, Material, Question, Test

User = get_user_model()


class CourseAPITestCase(APITestCase):
    """
    Тесты курсов, материалов и тестов
    """

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="adminpass",
            role="admin",
        )

        self.teacher = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="teacherpass",
            role="teacher",
        )

        self.student1 = User.objects.create_user(
            email="student1@example.com",
            username="student1",
            password="studentpass",
            role="student",
        )

        self.student2 = User.objects.create_user(
            email="student2@example.com",
            username="student2",
            password="studentpass",
            role="student",
        )

        self.course = Course.objects.create(
            title="Python Basics",
            description="Introduction to Python",
            owner=self.teacher,
        )

        self.material = Material.objects.create(
            course=self.course,
            title="Variables",
            content="About variables in Python",
            order=1,
        )

        self.test = Test.objects.create(
            material=self.material, title="Variables Test", passing_score=70
        )

        self.question1 = Question.objects.create(
            test=self.test, text="How to declare variable?", order=1
        )

        self.answer1_correct = Answer.objects.create(
            question=self.question1, text="x = 5", is_correct=True
        )

        self.answer1_wrong = Answer.objects.create(
            question=self.question1, text="5 = x", is_correct=False
        )

        self.question2 = Question.objects.create(
            test=self.test, text="What is None?", order=2
        )

        self.answer2_correct = Answer.objects.create(
            question=self.question2, text="Special object", is_correct=True
        )

        self.answer2_wrong = Answer.objects.create(
            question=self.question2, text="Zero", is_correct=False
        )

    # Тесты для курсов
    def test_course_create_as_admin(self):
        """Тест создания курса администратором"""
        self.client.force_authenticate(user=self.admin)
        data = {"title": "New Course", "description": "Test"}
        response = self.client.post(reverse("courses:course-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_create_as_teacher(self):
        """ТЕст создания курса преподавателем"""
        self.client.force_authenticate(user=self.teacher)
        data = {"title": "Teacher Course", "description": "Test"}
        response = self.client.post(reverse("courses:course-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_create_as_student(self):
        """Тест создания курса студентом"""
        self.client.force_authenticate(user=self.student1)
        data = {"title": "Student Course", "description": "Test"}
        response = self.client.post(reverse("courses:course-list"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enroll_as_student(self):
        """Тест записи студента на курс"""
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:course-enroll", args=[self.course.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            self.course.students.filter(id=self.student1.id).exists()
        )

    def test_enroll_as_teacher(self):
        """Тест записи преподавателя на курс"""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("courses:course-enroll", args=[self.course.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enroll_twice(self):
        """Тест записи студента дважды на один и тот же курс"""
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:course-enroll", args=[self.course.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_material_create_as_owner(self):
        """Тест создания материала владельцем курса"""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("courses:material-list")

        data = {
            "course": self.course.id,
            "title": "New Material",
            "content": "Content",
            "order": 2,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_material_create_as_non_owner(self):
        """Тест создания материала не владельцем курса"""
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:material-list")
        data = {
            "course": self.course.id,
            "title": "New Material",
            "content": "Content",
            "order": 2,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_test(self):
        """Тест отправки теста с правильными ответами"""
        self.client.force_authenticate(user=self.student1)
        print(f"Test ID: {self.test.id}")
        url = reverse("courses:test-submit", args=[self.test.id])

        data = {
            "user_answers": [
                {
                    "question": self.question1.id,
                    "answer": self.answer1_correct.id,
                },
                {
                    "question": self.question2.id,
                    "answer": self.answer2_correct.id,
                },
            ]
        }
        response = self.client.post(url, data, format="json")
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 100)
        self.assertTrue(response.data["passed"])

    def test_submit_test_partially_correct(self):
        """Тест отправки теста только с половиной правильных ответов"""
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:test-submit", args=[self.test.id])

        data = {
            "user_answers": [
                {
                    "question": self.question1.id,
                    "answer": self.answer1_correct.id,
                },
                {
                    "question": self.question2.id,
                    "answer": self.answer2_wrong.id,
                },
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 50)
        self.assertFalse(response.data["passed"])

    def test_submit_test_empty(self):
        """Тест отправки теста без ответов"""
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:test-submit", args=[self.test.id])

        data = {"user_answers": []}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 0)
        self.assertFalse(response.data["passed"])

    def test_submit_test_invalid_answers(self):
        """Тест отправки теста с неправильными ответами"""
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:test-submit", args=[self.test.id])

        data = {
            "user_answers": [
                {"question": self.question1.id, "answer": 999},
                {"question": 999, "answer": self.answer2_correct.id},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 0)
        self.assertEqual(response.data["correct_answers"], 0)
        self.assertEqual(response.data["total_questions"], 2)

    def test_submit_test_as_teacher(self):
        """Тест отправки теста преподавателем"""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("courses:test-submit", args=[self.test.id])

        data = {
            "user_answers": [
                {
                    "question": self.question1.id,
                    "answer": self.answer1_correct.id,
                }
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_list_as_anonymous(self):
        """Тест получения списка курсов анонимным пользователем"""
        self.client.logout()
        response = self.client.get(reverse("courses:course-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_retrieve_as_anonymous(self):
        """Тест получения деталей курса анонимным пользователем"""
        self.client.logout()
        url = reverse("courses:course-detail", args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_retrieve_as_student(self):
        """Тест получения деталей курса студентом"""
        self.course.students.add(self.student1)
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:course-detail", args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.course.title)

    def test_material_list_as_student(self):
        """Тест получения списка материалов студентом"""
        self.course.students.add(self.student1)
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:material-list")
        response = self.client.get(url, {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_material_retrieve_as_student(self):
        """Тест получения деталей материала студентом"""
        self.course.students.add(self.student1)

        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:material-detail", args=[self.material.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.material.title)

    def test_material_access_not_enrolled(self):
        """Тест доступа к материалу без записи на курс"""
        self.client.force_authenticate(user=self.student2)
        url = reverse("courses:material-detail", args=[self.material.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_update_as_owner(self):
        """Тест обновления курса владельцем"""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("courses:course-detail", args=[self.course.id])
        data = {"title": "Owner"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Owner")

    def test_course_update_as_admin(self):
        """Тест обновления курса администратором"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("courses:course-detail", args=[self.course.id])
        data = {"title": "Admin"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Admin")

    def test_course_update_as_student(self):
        """Тест попытки обновления курса студентом"""
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:course-detail", args=[self.course.id])
        data = {"title": "Student"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_delete_as_owner(self):
        """Тест удаления курса владельцем"""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("courses:course-detail", args=[self.course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_course_delete_as_admin(self):
        """Тест удаления курса админом"""
        new_course = Course.objects.create(
            title="Temp Course",
            description="To be deleted",
            owner=self.teacher,
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse("courses:course-detail", args=[new_course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_course_delete_as_student(self):
        """Тест попытки удаления курса студентом"""
        self.client.force_authenticate(user=self.student1)
        url = reverse("courses:course-detail", args=[self.course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class QuestionAPITestCase(APITestCase):
    """Тесты для управления вопросами в тестах"""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="adminpass",
            role="admin",
        )
        self.teacher = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="teacherpass",
            role="teacher",
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            username="student",
            password="studentpass",
            role="student",
        )

        self.course = Course.objects.create(
            title="Python Basics",
            description="Introduction to Python",
            owner=self.teacher,
        )
        self.material = Material.objects.create(
            course=self.course,
            title="Вопросс",
            content="About variables in Python",
            order=1,
        )
        self.test = Test.objects.create(
            material=self.material, title="Variables Test", passing_score=70
        )

    def test_question_create_as_teacher(self):
        """Тест создания вопроса преподавателем"""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("courses:question-list")
        data = {
            "test": self.test.id,
            "text": "Вопрос",
            "order": 1,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_question_create_as_admin(self):
        """Тест создания вопроса администратором"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("courses:question-list")
        data = {
            "test": self.test.id,
            "text": "Вопрос",
            "order": 1,
        }
        response = self.client.post(url, data)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_question_create_as_student(self):
        """Тест создания вопроса студентом"""
        self.client.force_authenticate(user=self.student)
        url = reverse("courses:question-list")
        data = {
            "test": self.test.id,
            "text": "Вопрос",
            "order": 1,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_question_retrieve_as_teacher(self):
        """Тест получения вопроса преподавателем"""
        self.client.force_authenticate(user=self.teacher)
        question = Question.objects.create(
            test=self.test, text="Вопрос", order=1
        )
        url = reverse("courses:question-detail", args=[question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_update_as_teacher(self):
        """Тест обновления вопроса преподавателем"""
        self.client.force_authenticate(user=self.teacher)
        question = Question.objects.create(
            test=self.test, text="Вопрос1", order=1
        )
        url = reverse("courses:question-detail", args=[question.id])
        data = {"text": "Вопрос1"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Вопрос1")

    def test_question_delete_as_teacher(self):
        """Тест удаления вопроса преподавателем"""
        self.client.force_authenticate(user=self.teacher)
        question = Question.objects.create(
            test=self.test, text="Вопрос1", order=1
        )
        url = reverse("courses:question-detail", args=[question.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=question.id).exists())

    def test_question_access_as_student(self):
        """Тест доступа к вопросу студентом"""
        self.client.force_authenticate(user=self.student)
        question = Question.objects.create(
            test=self.test, text="Вопрос1", order=1
        )
        url = reverse("courses:question-detail", args=[question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestAPITestCase(APITestCase):
    """Тесты для управления тестами"""

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="adminpass",
            role="admin",
        )

        self.teacher = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="teacherpass",
            role="teacher",
        )

        self.student = User.objects.create_user(
            email="student@example.com",
            username="student",
            password="studentpass",
            role="student",
        )

        self.course = Course.objects.create(
            title="Python Basics",
            description="Introduction to Python",
            owner=self.teacher,
        )

        self.material = Material.objects.create(
            course=self.course,
            title="Variables",
            content="About variables in Python",
            order=1,
        )

        self.test = Test.objects.create(
            material=self.material, title="Variables Test", passing_score=70
        )

    def test_test_create_as_teacher(self):
        """Тест создания теста преподавателем"""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("courses:test-list")
        data = {
            "material": self.material.id,
            "title": "New Test",
            "passing_score": 75,
        }
        response = self.client.post(url, data)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_test_create_as_admin(self):
        """Тест создания теста администратором"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("courses:test-list")
        data = {
            "material": self.material.id,
            "title": "New Test",
            "passing_score": 75,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_test_create_as_student(self):
        """Тест создания теста студентом"""
        self.client.force_authenticate(user=self.student)
        url = reverse("courses:test-list")
        data = {
            "material": self.material.id,
            "title": "New Test",
            "passing_score": 75,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AnswerAPITestCase(APITestCase):
    """Тесты для управления ответами на вопросы"""

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="adminpass",
            role="admin",
        )

        self.teacher = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="teacherpass",
            role="teacher",
        )

        self.student = User.objects.create_user(
            email="student@example.com",
            username="student",
            password="studentpass",
            role="student",
        )

        self.course = Course.objects.create(
            title="Python Basics",
            description="Introduction to Python",
            owner=self.teacher,
        )

        self.material = Material.objects.create(
            course=self.course,
            title="Variables",
            content="About variables in Python",
            order=1,
        )

        self.test = Test.objects.create(
            material=self.material, title="Variables Test", passing_score=70
        )

        self.question = Question.objects.create(
            test=self.test, text="What is a variable?", order=1
        )

    def test_answer_create_as_teacher(self):
        """Тест создания ответа преподавателем"""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("courses:answer-list")
        data = {
            "question": self.question.id,
            "text": "x = 5",
            "is_correct": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_answer_create_as_admin(self):
        """Тест создания ответа администратором"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("courses:answer-list")
        data = {
            "question": self.question.id,
            "text": "x = 5",
            "is_correct": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_answer_create_as_student(self):
        """Тест создания ответа студентом"""
        self.client.force_authenticate(user=self.student)
        url = reverse("courses:answer-list")
        data = {
            "question": self.question.id,
            "text": "x = 5",
            "is_correct": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
