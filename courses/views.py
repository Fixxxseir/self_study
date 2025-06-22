from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from loguru import logger
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Answer,
    Course,
    Material,
    Question,
    Test,
    TestResult,
    UserAnswer,
)
from .permissions import (
    CanAccessCourse,
    CanCreateCourse,
    CanCreateMaterial,
    CanCreateTest,
    CanManageAnswer,
    CanManageMaterial,
    CanManageQuestion,
    CanManageTest,
    CanTakeTest,
    IsAdmin,
    IsCourseOwner,
    IsTeacher,
)
from .serializers import (
    AnswerSerializerCreate,
    CourseSerializer,
    MaterialSerializer,
    QuestionSerializer,
    TestResultSerializer,
    TestSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для управления курсами, включая запись студентов на курсы"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = "id"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        logger.debug(f"Получение прав доступа для действия: {self.action}")
        if self.action in ["list", "retrieve", "enroll"]:
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return [permissions.IsAuthenticated(), CanCreateCourse()]
        else:
            return [permissions.IsAuthenticated(), (IsCourseOwner | IsAdmin)()]

    def perform_create(self, serializer):
        logger.info(f"Создание курса пользователем: {self.request.user}")
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["POST"], url_path="enroll")
    def enroll(self, request, pk=None):
        course = self.get_object()
        if request.user.role != "student":
            logger.warning(
                f"Попытка записи на курс не студентом: {request.user}"
            )
            return Response(
                {"error": "Только студент может зарегистрироваться на курс"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if course.students.filter(id=request.user.id).exists():
            logger.warning(f"Повторная запись на курс: {request.user}")
            return Response(
                {"error": "Вы уже зарегистрированы на курс"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        course.students.add(request.user)
        logger.success(
            f"Пользователь {request.user} успешно записан на курс {course.id}"
        )
        return Response(
            {"status": "запись успешна"}, status=status.HTTP_200_OK
        )


class MaterialViewSet(viewsets.ModelViewSet):
    """ViewSet для управления материалами курсов"""

    serializer_class = MaterialSerializer
    queryset = Material.objects.all()
    filterset_fields = ["course"]
    lookup_field = "id"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        logger.debug(
            f"Проверка прав доступа для материалов, действие: {self.action}"
        )
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated(), CanAccessCourse()]
        elif self.action == "create":
            return [permissions.IsAuthenticated(), CanCreateMaterial()]
        else:
            return [permissions.IsAuthenticated(), CanManageMaterial()]

    def create(self, request, *args, **kwargs):
        logger.debug(
            f"Создание материала для курса {self.kwargs.get('course_id')}"
        )
        self.check_object_permissions(request=request, obj=None)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        logger.info(f"Создание материала для курса {course.id}")
        serializer.save(course=course)


class TestViewSet(viewsets.ModelViewSet):
    """ViewSet для управления тестами и обработки результатов тестирования"""

    serializer_class = TestSerializer
    queryset = Test.objects.select_related("material")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["material"]
    lookup_field = "id"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        logger.debug(
            f"Проверка прав доступа для тестов, действие: {self.action}"
        )
        if self.action == "submit":
            return [permissions.IsAuthenticated(), CanTakeTest()]
        elif self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated(), CanAccessCourse()]
        elif self.action == "create":
            return [permissions.IsAuthenticated(), CanCreateTest()]
        else:
            return [permissions.IsAuthenticated(), CanManageTest()]

    def perform_create(self, serializer):
        material_id = self.request.data.get("material")
        material = get_object_or_404(Material, pk=material_id)
        logger.info(f"Создание теста для материала {material.id}")
        serializer.save(material=material)

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, material_id=None, pk=None):
        logger.debug(f"Отправка теста {pk} пользователем {request.user}")
        test = get_object_or_404(Test, pk=pk)
        user_answers = request.data.get("user_answers", [])

        correct_answers = 0
        total_questions = test.questions.count()
        valid_answers = []

        logger.debug(f"Обработка {len(user_answers)} ответов пользователя")
        for answer_data in user_answers:
            question_id = answer_data.get("question")
            answer_id = answer_data.get("answer")

            try:
                answer = Answer.objects.get(
                    pk=answer_id, question_id=question_id, question__test=test
                )
                if answer.is_correct:
                    correct_answers += 1
                valid_answers.append(answer_data)
            except Answer.DoesNotExist:
                logger.warning(
                    f"Не найден ответ {answer_id} для вопроса {question_id}"
                )
                continue

        score = (
            int((correct_answers / total_questions) * 100)
            if total_questions > 0
            else 0
        )
        logger.info(
            f"Результат теста: {score}% (правильных:"
            f" {correct_answers}/{total_questions})"
        )

        test_result, created = TestResult.objects.update_or_create(
            user=request.user,
            test=test,
            defaults={
                "score": score,
                "is_passed": score >= test.passing_score,
            },
        )
        logger.debug(
            f"{'Создан' if created else 'Обновлен'} результат теста:"
            f" {test_result.id}"
        )

        test_result.user_answers.all().delete()
        for answer_data in valid_answers:
            UserAnswer.objects.create(
                test_result=test_result,
                question_id=answer_data["question"],
                answer_id=answer_data["answer"],
            )
        logger.debug(f"Сохранено {len(valid_answers)} ответов пользователя")

        return Response(
            {
                "score": score,
                "passed": score >= test.passing_score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
            },
            status=status.HTTP_201_CREATED,
        )


class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet для управления вопросами тестов"""

    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["test"]
    lookup_field = "id"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        logger.debug(
            f"Проверка прав доступа для вопросов, действие: {self.action}"
        )
        if self.action == "create":
            return [permissions.IsAuthenticated(), (IsAdmin | IsTeacher)()]
        else:
            return [permissions.IsAuthenticated(), CanManageQuestion()]

    def perform_create(self, serializer):
        test_id = self.request.data.get("test")
        test = get_object_or_404(Test, pk=test_id)
        logger.info(f"Создание вопроса для теста {test.id}")
        serializer.save(test=test)


class AnswerViewSet(viewsets.ModelViewSet):
    """ViewSet для управления вариантами ответов на вопросы"""

    serializer_class = AnswerSerializerCreate
    queryset = Answer.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["question"]
    lookup_field = "id"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        logger.debug(
            f"Проверка прав доступа для ответов, действие: {self.action}"
        )

        if self.action == "create":
            return [permissions.IsAuthenticated(), (IsAdmin | IsTeacher)()]
        else:
            return [permissions.IsAuthenticated(), CanManageAnswer()]

    def perform_create(self, serializer):
        question_id = self.request.data.get("question")
        question = get_object_or_404(Question, pk=question_id)
        logger.info(f"Создание ответа для вопроса {question.id}")
        serializer.save(question=question)


class TestResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet результатов тестов пользователя"""

    serializer_class = TestResultSerializer
    queryset = TestResult.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        user = self.request.user

        if user.role == "student":
            return self.queryset.filter(user=user)

        return self.queryset

    def get_permissions(self):
        logger.debug(
            f"Проверка прав доступа для ответов, действие: {self.action}"
        )
        return super().get_permissions()
