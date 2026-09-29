# Auth Service

Сервис аутентификации: регистрация, вход и выдача JWT-токенов. Остальные сервисы валидируют JWT локально через общий `JWT_SECRET`.

## Стек

- Python 3.13, FastAPI, SQLAlchemy (async), PostgreSQL
- JWT (HS256) — access + refresh токены
- bcrypt — хэширование паролей
- Alembic — миграции
- uv — управление зависимостями

## Быстрый старт

```bash
# Зависимости
uv sync

# PostgreSQL
docker compose up -d

# Переменные окружения
cp .env.example .env  # или отредактировать .env

# Миграции
make migrate

# Запуск
make run
```

Сервер стартует на `http://localhost:8000`.

## Переменные окружения

| Переменная               | По умолчанию                                                    | Описание                        |
|--------------------------|-----------------------------------------------------------------|---------------------------------|
| `DATABASE_URL`           | `postgresql+asyncpg://postgres:postgres@localhost:5433/auth_db` | Строка подключения к PostgreSQL |
| `JWT_SECRET`             | `change-me`                                                     | Секрет для подписи JWT          |
| `JWT_ALGORITHM`          | `HS256`                                                         | Алгоритм подписи                |
| `JWT_EXPIRE_HOURS`       | `24`                                                            | Время жизни access-токена (ч)   |
| `JWT_REFRESH_EXPIRE_DAYS`| `30`                                                            | Время жизни refresh-токена (д)  |

## API

### Публичные эндпоинты (`/auth`)

| Метод  | Путь              | Описание                          | Auth   |
|--------|--------------------|----------------------------------|--------|
| `POST` | `/auth/register`   | Регистрация                      | Нет    |
| `POST` | `/auth/login`      | Вход, выдача пары токенов        | Нет    |
| `POST` | `/auth/refresh`    | Обновление токенов по refresh    | Нет    |
| `GET`  | `/auth/users/me`   | Текущий пользователь             | Bearer |

### Внутренние эндпоинты (`/internal`)

Не прокидываются в Ingress, доступны только внутри кластера.

| Метод    | Путь                        | Описание                    | Auth |
|----------|-----------------------------|-----------------------------|------|
| `GET`    | `/internal/users/{user_id}` | Публичные данные по user_id | Нет  |
| `DELETE` | `/internal/users/{user_id}` | Удаление пользователя       | Нет  |

## Make-команды

| Команда                          | Описание                          |
|----------------------------------|-----------------------------------|
| `make run`                       | Запуск сервера                    |
| `make check`                     | Линтинг + форматирование (ruff)   |
| `make test`                      | Запуск unit-тестов                |
| `make lint`                      | `ruff check --fix`                |
| `make format`                    | `ruff format`                     |
| `make migrate`                   | Применить миграции                |
| `make migrate-create name="..."` | Сгенерировать миграцию            |

## Структура проекта

```
src/
  settings.py                          # Конфигурация (pydantic-settings + .env)
  fastapi.py                           # Фабрика приложения
  domain/
    entities.py                        # User, TokenPair
    jwt.py                             # AccessTokenPayload, RefreshTokenPayload (TypedDict)
  application/
    exceptions.py                      # Доменные ошибки
    ports/
      repositories.py                  # UserRepository (ABC)
      uow.py                           # UnitOfWork (ABC)
      usecases.py                      # Порты юзкейсов (ABC)
    usecases/
      register_user.py                 # Регистрация
      login_user.py                    # Вход + выдача токенов
      refresh_token.py                 # Обновление токенов
      get_user.py                      # Получение пользователя
  presentation/
    api/
      schemas.py                       # Pydantic-схемы запросов/ответов
      dependencies.py                  # FastAPI Depends (UoW, юзкейсы, JWT)
      routes/
        public.py                      # /auth/*
        internal.py                    # /internal/*
  infrastructure/
    persistence/
      database.py                      # Engine + session factory
      models.py                        # SQLAlchemy-модели
      repositories.py                  # SQLAlchemyUserRepository
      uow.py                          # SQLAlchemyUnitOfWork
bin/
  api.py                               # Точка входа (uvicorn)
migrations/                            # Alembic-миграции
```
