from rest_framework import serializers

from users.serializers import UserRegisterSerializer

from .models import (
    Answer,
    Course,
    Material,
    Question,
    Test,
    TestResult,
    UserAnswer,
)


class AnswerSerializerCreate(serializers.ModelSerializer):
    """Сериализатор ответа создание"""

    class Meta:
        model = Answer
        fields = ("id", "text", "is_correct")
        read_only_fields = ("id",)


class AnswerSerializerPublish(serializers.ModelSerializer):
    """Сериализатор ответа"""

    class Meta:
        model = Answer
        fields = ("id", "text")
        read_only_fields = ("id",)


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор вопроса"""

    answers = AnswerSerializerPublish(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "test", "text", "order", "answers")
        read_only_fields = ("id",)


class TestSerializer(serializers.ModelSerializer):
    """Сериализатор тестирования"""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = (
            "id",
            "material",
            "title",
            "description",
            "passing_score",
            "questions",
        )
        read_only_fields = ("id",)


class MaterialSerializer(serializers.ModelSerializer):
    """Сериализатор материала"""

    test = TestSerializer(read_only=True)

    class Meta:
        model = Material
        fields = (
            "id",
            "course",
            "title",
            "content",
            "order",
            "test",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса"""

    owner = UserRegisterSerializer(read_only=True)
    materials = MaterialSerializer(many=True, read_only=True)
    students = UserRegisterSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "owner",
            "students",
            "materials",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class UserAnswerSerializer(serializers.ModelSerializer):
    """Сериализатор ответа юзера"""

    class Meta:
        model = UserAnswer
        fields = ("question", "answer")


class TestResultSerializer(serializers.ModelSerializer):
    """Сериализатор результатов юзера"""

    user_answers = UserAnswerSerializer(many=True)

    class Meta:
        model = TestResult
        fields = (
            "id",
            "user",
            "test",
            "score",
            "is_passed",
            "completed_at",
            "user_answers",
        )
        read_only_fields = (
            "user",
            "test",
            "score",
            "completed_at",
            "is_passed",
        )
