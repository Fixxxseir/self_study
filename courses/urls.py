from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .apps import CoursesConfig
from .views import (
    AnswerViewSet,
    CourseViewSet,
    MaterialViewSet,
    QuestionViewSet,
    TestResultViewSet,
    TestViewSet,
)

app_name = CoursesConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"materials", MaterialViewSet, basename="material")
router.register(r"tests", TestViewSet, basename="test")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"answers", AnswerViewSet, basename="answer")
router.register(r"test-results", TestResultViewSet, basename="testresult")

urlpatterns = [
    path("", include(router.urls)),
]
