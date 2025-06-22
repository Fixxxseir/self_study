# apps/courses/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Answer,
    Course,
    Material,
    Question,
    Test,
    TestResult,
    UserAnswer,
)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    min_num = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    inlines = [AnswerInline]
    show_change_link = True


class TestInline(admin.StackedInline):
    model = Test
    extra = 0
    inlines = [QuestionInline]
    show_change_link = True


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1
    inlines = [TestInline]
    show_change_link = True
    ordering = ("order",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "students_count")
    list_filter = ("created_at", "owner")
    search_fields = ("title", "description", "owner__username")
    filter_horizontal = ("students",)
    inlines = [MaterialInline]

    def students_count(self, obj):
        return obj.students.count()

    students_count.short_description = "Students"


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "created_at")
    list_filter = ("course", "created_at")
    search_fields = ("title", "content", "course__title")
    list_editable = ("order",)
    inlines = [TestInline]
    raw_id_fields = ("course",)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "material_link",
        "passing_score",
        "questions_count",
    )
    list_filter = ("material__course",)
    search_fields = ("title", "description")
    inlines = [QuestionInline]

    def material_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f"/admin/courses/material/{obj.material.id}/change/",
            obj.material.title,
        )

    material_link.short_description = "Material"

    def questions_count(self, obj):
        return obj.questions.count()

    questions_count.short_description = "Questions"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "test_link", "order")
    list_filter = ("test__material__course",)
    search_fields = ("text",)
    list_editable = ("order",)
    inlines = [AnswerInline]

    def test_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f"/admin/courses/test/{obj.test.id}/change/",
            obj.test.title,
        )

    test_link.short_description = "Test"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("text", "is_correct", "question_link")
    list_filter = ("question__test__material__course", "is_correct")
    search_fields = ("text",)
    list_editable = ("is_correct",)

    def question_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f"/admin/courses/question/{obj.question.id}/change/",
            obj.question.text[:50],
        )

    question_link.short_description = "Question"


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ("question", "answer")


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "test_link",
        "score",
        "passed_status",
        "completed_at",
    )
    list_filter = ("test__material__course", "completed_at")
    search_fields = ("user__username", "test__title")
    readonly_fields = (
        "user",
        "test",
        "score",
        "completed_at",
        "passed_status",
    )
    inlines = [UserAnswerInline]

    def test_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f"/admin/courses/test/{obj.test.id}/change/",
            obj.test.title,
        )

    test_link.short_description = "Test"

    def passed_status(self, obj):
        return obj.is_passed

    passed_status.boolean = True
    passed_status.short_description = "Passed"


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "test_result_link",
        "question_text",
        "answer_text",
        "is_correct",
    )
    list_filter = ("test_result__test__material__course",)
    readonly_fields = ("test_result", "question", "answer")

    def test_result_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f"/admin/courses/testresult/{obj.test_result.id}/change/",
            f"Result #{obj.test_result.id}",
        )

    test_result_link.short_description = "Test Result"

    def question_text(self, obj):
        return obj.question.text[:100]

    question_text.short_description = "Question"

    def answer_text(self, obj):
        return obj.answer.text

    answer_text.short_description = "Answer"

    def is_correct(self, obj):
        return obj.answer.is_correct

    is_correct.boolean = True
    is_correct.short_description = "Correct?"
