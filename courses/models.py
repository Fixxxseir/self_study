from django.contrib.auth import get_user_model
from django.db import models
from packaging.utils import _


class Course(models.Model):
    """
    Модель представления курса
    """

    title = models.CharField(
        _("Название"),
        max_length=256,
        help_text="Название курса",
    )
    description = models.TextField(
        _("Описание"),
        help_text="Описание курса",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        get_user_model(),
        verbose_name=_("Создатель"),
        on_delete=models.CASCADE,
        related_name="courses",
        limit_choices_to={"role": "teacher"},
    )
    students = models.ManyToManyField(
        get_user_model(),
        verbose_name=_("Студент"),
        related_name="enrolled_courses",
        blank=True,
        limit_choices_to={"role": "student"},
    )
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
        help_text="Дата создания курса",
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
        help_text="Дата обновления курса",
    )

    class Meta:
        verbose_name = _("Курс")
        verbose_name_plural = _("Курсы")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Material(models.Model):
    """
    Модель представления материала
    """

    course = models.ForeignKey(
        Course,
        verbose_name=_("Курс"),
        on_delete=models.CASCADE,
        related_name="materials",
    )
    title = models.CharField(
        _("Название"),
        max_length=256,
        help_text="Название материала",
    )
    content = models.TextField(
        _("Контент"),
        help_text="Контент",
        null=True,
        blank=True,
    )
    order = models.PositiveIntegerField(
        _("Порядковый номер"), default=0, help_text="Порядковый номер"
    )
    created_at = models.DateTimeField(
        _("Дата создания"), auto_now_add=True, help_text="Дата создания"
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"), auto_now=True, help_text="Дата обновления"
    )

    class Meta:
        verbose_name = _("Материал")
        verbose_name_plural = _("Материалы")
        ordering = ["order"]
        unique_together = ["course", "order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Test(models.Model):
    """
    Модель представления теста
    """

    material = models.ForeignKey(
        Material,
        verbose_name=_("Материал"),
        on_delete=models.CASCADE,
        related_name="tests",
        help_text="Материал",
    )
    title = models.CharField(
        _("Название"),
        max_length=256,
        help_text="Название",
    )
    description = models.TextField(
        _("Описание"), null=True, blank=True, help_text="Описание"
    )
    passing_score = models.PositiveIntegerField(
        _("Проходной балл"), default=70, help_text="Проходной балл"
    )

    class Meta:
        verbose_name = _("Тест")
        verbose_name_plural = _("Тесты")

    def __str__(self):
        return f"Test for {self.material.title}"


class Question(models.Model):
    """
    Модель представления вопроса
    """

    test = models.ForeignKey(
        Test,
        verbose_name=_("Тест"),
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="Тест",
    )
    text = models.TextField(
        _("Описание"),
        help_text="Описание вопроса",
    )
    order = models.PositiveIntegerField(
        _("Порядковый номер"),
        default=0,
        help_text="Порядковый номер",
    )

    class Meta:
        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")
        ordering = ["order"]

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    """
    Модель представления ответа
    """

    question = models.ForeignKey(
        Question,
        verbose_name=_("Вопрос"),
        on_delete=models.CASCADE,
        related_name="answers",
    )
    text = models.CharField(
        _("Описание ответа"), max_length=256, help_text="Описание ответа"
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Ответ")
        verbose_name_plural = _("Ответы")

    def __str__(self):
        return f"{self.text} ({'✓' if self.is_correct else '✗'})"


class TestResult(models.Model):
    """
    Модель представления результата теста
    """

    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_("Студент"),
        on_delete=models.CASCADE,
        related_name="test_results",
        help_text="Студент",
    )
    test = models.ForeignKey(
        Test,
        verbose_name=_("Тест"),
        on_delete=models.CASCADE,
        related_name="results",
        help_text="Тест",
    )
    score = models.PositiveIntegerField(_("Оценка"), help_text="Оценка")
    is_passed = models.BooleanField(
        _("Статус прохождения"), default=False, help_text="Статус прохождения"
    )
    completed_at = models.DateTimeField(
        _("Статус завершения"),
        auto_now_add=True,
        help_text="Статус завершения",
    )

    class Meta:
        verbose_name = _("Результат теста")
        verbose_name_plural = _("Результаты теста")
        unique_together = ["user", "test"]

    def __str__(self):
        return f"{self.user.username} - {self.test.title} ({self.score}%)"


class UserAnswer(models.Model):
    """
    Модель представления ответов юзера
    """

    test_result = models.ForeignKey(
        TestResult,
        verbose_name=_("Результат тестирования"),
        on_delete=models.CASCADE,
        related_name="user_answers",
        help_text="Результат тестирования",
    )
    question = models.ForeignKey(
        Question,
        verbose_name=_("Вопрос"),
        on_delete=models.CASCADE,
        help_text="Вопрос",
    )
    answer = models.ForeignKey(
        Answer,
        verbose_name=_("Ответ"),
        on_delete=models.CASCADE,
        help_text="Ответ",
    )

    class Meta:
        verbose_name = _("Ответ студента")
        verbose_name_plural = _("Ответы студентов")
        unique_together = ["test_result", "question"]

    def __str__(self):
        return (
            f"{self.test_result.user.username}'s answer to"
            f" {self.question.text[:20]}"
        )
