from loguru import logger
from rest_framework import permissions, status


class IsAdmin(permissions.BasePermission):
    """Проверка на администратора"""

    message = {"forbidden": "Требуются права администратора"}
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        return request.user.role == "admin"


class IsTeacher(permissions.BasePermission):
    """Проверка на преподавателя"""

    message = {"forbidden": "Требуются права преподавателя"}
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        return request.user.role == "teacher"


class IsStudent(permissions.BasePermission):
    """Проверка на студента"""

    message = {"forbidden": "Требуются права студента"}
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        return request.user.role == "student"


class CanCreateCourse(permissions.BasePermission):
    """Права на создание курса (админ или преподаватель)"""

    message = {"forbidden": "Недостаточно прав для создания курса"}
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        return request.user.role in ["admin", "teacher"]


class CanAccessCourse(permissions.BasePermission):
    """
    Права доступа к курсу
    - Админ: полный доступ
    - Преподаватель: доступ к своим курсам
    - Студент: доступ к записанным курсам
    """

    message = {"forbidden": "Доступ к курсу запрещен"}
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, obj):
        course = getattr(obj, "course", obj)
        logger.debug(
            f"Проверка доступа к курсу {course.id} для {request.user}"
        )

        if request.user.role == "admin":
            return True

        if request.user.role == "teacher":
            return course.owner == request.user

        if request.user.role == "student":
            return course.students.filter(id=request.user.id).exists()

        return False


class IsCourseOwner(permissions.BasePermission):
    """
    Проверка, что пользователь является владельцем курса (для преподавателей)
    """

    message = {"forbidden": "Вы не являетесь владельцем этого курса"}
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, course):
        if request.user.role == "admin":
            return True

        if request.user.role == "teacher":
            if not course:
                return
            return course.owner == request.user


class CanCreateMaterial(permissions.BasePermission):
    """Права на создание материалов (админ или преподаватель)"""

    message = {"forbidden": "Недостаточно прав для создания материала"}
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        return request.user.role in ["admin", "teacher"]


class CanManageMaterial(permissions.BasePermission):
    """Права на управление материалом (админ или владелец курса)"""

    message = {"forbidden": "Недостаточно прав для управления материалом"}
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True

        if request.user.role == "teacher":
            return obj.course.owner == request.user

        return False


class CanCreateTest(permissions.BasePermission):
    """Права на создание тестов (админ или преподаватель)"""

    message = {"forbidden": "Недостаточно прав для создания теста"}
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        return request.user.role in ["admin", "teacher"]


class CanManageTest(permissions.BasePermission):
    """Права на управление тестом (админ или владелец курса)"""

    message = {"forbidden": "Недостаточно прав для управления тестом"}
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True

        if request.user.role == "teacher":
            return obj.material.course.owner == request.user

        return False


class CanTakeTest(permissions.BasePermission):
    """Права на прохождение теста (только студенты записанные на курс)"""

    message = {"forbidden": "Недостаточно прав для прохождения теста"}
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        return request.user.role == "student"

    def has_object_permission(self, request, view, obj):
        if request.user.role != "student":
            return False

        return obj.material.course.students.filter(id=request.user.id).exists()


class CanManageQuestion(permissions.BasePermission):
    """Права на управление вопросами (админ или владелец курса)"""

    message = {"forbidden": "Недостаточно прав для управления вопросами"}
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True

        if request.user.role == "teacher":
            return obj.test.material.course.owner == request.user

        return False


class CanManageAnswer(permissions.BasePermission):
    """Права на управление ответами (админ или владелец курса)"""

    message = {"forbidden": "Недостаточно прав для управления ответами"}
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True

        if request.user.role == "teacher":
            return obj.question.test.material.course.owner == request.user

        return False


class CanViewTestResults(permissions.BasePermission):
    """Права на просмотр результатов тестов"""

    message = {"forbidden": "Недостаточно прав для просмотра результатов"}
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True

        if request.user.role == "teacher":
            return obj.test.material.course.owner == request.user

        if request.user.role == "student":
            return obj.user == request.user

        return False
