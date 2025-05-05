##  Платформа для самообучения студентов
## Описание проекта
Платформа для самообучения студентов предоставляет возможность авторизации и аутентификации пользователей, управления учебными материалами и тестирования знаний. Проект реализован на Django с использованием Django Rest Framework (DRF) и PostgreSQL в качестве базы данных.

## Основные функции
- Авторизация и аутентификация с использованием JWT токенов

- Управление контентом (CRUD для разделов и материалов)

- Тестирование знаний с проверкой ответов на сервере

- Система ролей и прав доступа:

. Администраторы - полный доступ

. Преподаватели - управление своими курсами

.
## Технологии
- Python 3.x

- Django 4.x

- Django Rest Framework

- PostgreSQL

- Redis (для кэширования)

- Poetry (для управления зависимостями)

- Simple JWT (для аутентификации)

- Swagger (для документации API)

- Docker (опционально)

## Установка и запуск
# Предварительные требования
- Установленный Python 3.8+

- Установленный Poetry

- Установленный PostgreSQL

- Установленный Redis (если используется кэширование)

## Инструкции по установке
1. Клонируйте репозиторий:
```bash
git clone https://github.com/Fixxxseir/self_study.git
cd student-learning-platform
```
2. Создайте и активируйте виртуальное окружение:
```bash
pip add poetry
```
3. Установите зависимости через Poetry:
```bash
poetry install
```
4. Создайте файл .env в корне проекта со следующим содержимым:
```ini
SECRET_KEY="your-secret-key-here"
DEBUG=True

POSTGRES_DB='tracker'
POSTGRES_PASSWORD='your-postgres-password'

ENGINE='django.db.backends.postgresql_psycopg2'
DB_NAME='tracker'
DB_USER='postgres'
DB_PASSWORD='your-db-password'
DB_HOST='localhost'  # или 'db' для docker
DB_PORT='5432'

# Настройки email (опционально)
EMAIL_HOST='your-email-host'
EMAIL_PORT='your-email-port'
EMAIL_USE_TLS=True/False
EMAIL_USE_SSL=True/False
EMAIL_HOST_USER='your-email@example.com'
EMAIL_HOST_PASSWORD='your-email-password'
DEFAULT_FROM_EMAIL='noreply@example.com'

# Настройки Redis
REDIS_URL=redis://localhost:6379/0  # или redis:6379/0 для docker
LOCATION=redis://localhost:6379/0   # или redis:6379/0 для docker
```
5. Примените миграции:
```bash
python manage.py migrate
```
6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```
6. Запустите сервер:
```bash
python manage.py runserver
```
# Запуск с Docker (опционально)
- Убедитесь, что у вас установлены Docker и Docker Compose

Выполните:
```bash
docker-compose up --build
```
## Структура API
# Документация API доступна после запуска сервера по адресу:

- Swagger: http://localhost:8000/swagger/

- Redoc: http://localhost:8000/redoc/

# Основные эндпоинты:

- /api/v1/login/ - авторизация и аутентификация

- /api/v1/courses/ - управление курсами


## Тестирование
Для запуска тестов выполните:
```bash
python manage.py test
```
## Роли пользователей
# Проект поддерживает три основные роли:

- Администратор - полный доступ ко всем функциям

- Преподаватель - может создавать и управлять своими курсами

- Студент - может просматривать материалы и проходить тесты

## Настройки окружения
# Основные настройки проекта хранятся в файле .env:

- База данных: PostgreSQL с настройками подключения

- Кэширование: Redis (конфигурируется через REDIS_URL и LOCATION)

- Email: опциональные настройки для отправки email

- Режим отладки: DEBUG=True/False

## Лицензия
- MIT License