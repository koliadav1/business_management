# Веб-приложение для управления командой внутри компании

## Оглавление

- [Функционал](#функционал)
- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [Использование проекта](#использование-проекта)
- [Примеры запросов и ответов](#примеры-запросов-и-ответов)

---

## Функционал

### Пользователи
- Регистрация с email и паролем, необязательные поля - имя, фамилия, номер телефона
- Валидация пароля при регистрации, уникальность почты и номера телефона
- Авторизация с jwt-токенами: access и refresh
- Разделение по ролям: 
    User - пользователь без команды
    Admin - лидер команды
    Manager - менеджер команды
    Employee - работник команды
- Обновление профиля с возможностью безопасной смены пароля и почты
- Возможность удалить свой аккаунт
- Возможность привязаться к команде при помощи invite-кода, который можно получить у админа
### Команды
- Создание команды (при создании роль пользователя становится Admin)
- Добавление/удаление пользователей в команду для ее админа
- Просмотр состава команды для ее участников
- Назначение ролей при добалении в команду или отдельным запросом
### Задачи
- Создание задач админом и менеджерами с описание, дедлайном и исполнителем
- Переназначение исполнителя задачи
- Статусы задач: новая (new), в работе (in_pogress), сделана (done) и отменена (cancelled)
- Возможность изменять задачу для ее создателя и админа
- Возможность изменять статус для админа, создателя и исполнителя задачи (исполнитель может только менять статус на in_progress и done)
- Возможность добавлять/изменять/удалять комментарии к задаче
= Возможность получения своих задач, задач команды, конкретного пользователя и просроченных задач
### Оценки задач
- Возможность оценивать выполненные задачи админом или созателем задачи (комментарий к оценке и рейтинг от 1 до 5)
- Возможность просмотреть свои оценки
- Возможность получить статистику по оценкам (средний балл, количество оценок, их распределение)
### Встречи
- Создание встречи менеджерами и админом (дата, длительность, участники)
- Возможность изменение встречи админом или ее создателем
- Получение встреч пользователя, команды, ближайших встречи
- Возможность отменить встречу админом или ее создателем
### Календарь
- Возможность просмотреть задачи и встречи в календарном виде (по месяцам) и на конкретный день для себя и команды
- Возможность фильтровать задачи по статусу и отмененные/активные встречи
### Админ-панель
- Возможность редактирования/добавления/удаления/просмотра пользователей, команд, задач и встреч
- Возможность просмотра комментариев
### Дополнительно
- Пагинация
- Простой frontend-интерфейс для использования API
---

## Технологии

- **Backend:** FastAPI, fastapi-users, sqladmin
- **База данных:** PostgreSQL, SQLAlchemy, alembic, asyncpg
- **Контейнеризация:** Docker, docker-compose
- **Запуск:** uvicorn
- **Тесты:** pytest, pytest-asyncio, pytest-mock, pytest-cov
- **Форматтер:** black

---

## Структура проекта

```
migrations/
src/
  admin/
  api/
  auth/
  core/
  models/
  repositories/
  schemas/
  services/
  static/
  utils/
  main.py
scripts/
  setup_superuser.py
tests/
  integration_tests/
  unit_tests/
.env
.dockerignore
docker-compose.yml
Dockerfile
README.md
pyproject.toml
```

---

## Использование проекта
### 1. Скачать проект
```bash
git clone https://github.com/koliadav1/business_management
```
### 2. Перейти в директорию проекта
```bash
cd <your-path-to-project>/business_management-<version>
```
### 3. Создать .env.prod файл с секретными переменными, пример: .env.example файл
### 4. Запустить контейнеры Docker
```bash
docker-compose up --build
```
#### 4.1 Создать суперпользователя при необходимости (доступ к админ-панели):
```bash
docker compose exec web python scripts/setup_superuser.py
```

#### 4.2 Приложение будет доступно по адресу:
- Web-интерфейс и API: http://localhost:8000/
- Документация: http://localhost:8000/docs
- Админ-панель: http://localhost:8000/admin/

---

## Примеры запросов и ответов
### Регистрация /auth/register
- Запрос
```json
{
  "email": "user@example.com",
  "password": "string",
  "name": "string",
  "surname": "string",
  "phone_number": "812313"
}
```
- Ответ
```json
{
  "id": 0,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "team_id": 0,
  "role": "user",
  "name": "string",
  "surname": "string",
  "phone_number": "812313"
}
```
### Получение состава своей команды /teams/members с филтрацией по роли 
- Запрос
```curl
curl -X 'GET' \
  'http://localhost:8000/teams/members?role=employee' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3Nzk4ODQxfQ.OUxofhHzIx3ahvNzwi7IFwWJ2RmaY_1f09FTDlS_rjY'
```
- Ответ
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "is_active": true,
    "is_superuser": false,
    "is_verified": false,
    "team_id": 11,
    "role": "employee",
    "name": "string",
    "surname": "string",
    "phone_number": "898132332"
  }
]
```
### Удаление участника команды /teams/my-team/members/{user_id}
- Запрос
```curl
curl -X 'DELETE' \
  'http://localhost:8000/teams/my-team/members/1' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3Nzk4ODQxfQ.OUxofhHzIx3ahvNzwi7IFwWJ2RmaY_1f09FTDlS_rjY'
```
- Ответ
```json
code: 204
headers:
  content-type: application/json 
  date: Sun,03 May 2026 08:05:14 GMT 
  server: uvicorn 
```
### Изменение статуса задачи с ошибкой /tasks/{task_id}/status
- Запрос
```curl
curl -X 'PATCH' \
  'http://localhost:8000/tasks/999/status' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3Nzk4ODQxfQ.OUxofhHzIx3ahvNzwi7IFwWJ2RmaY_1f09FTDlS_rjY' \
  -H 'Content-Type: application/json' \
  -d '{
  "status": "new"
}'
```
- Ошибка
```json
{
  "detail": [
    {
      "msg": "Task not found",
      "type": "TaskNotFoundError"
    }
  ]
}
```
---