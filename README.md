# Gym Bot 💪

Телеграм-бот — помощник для тренировок. Позволяет создавать тренировки, добавлять упражнения (с подходами, повторениями и весом) и просматривать свои записи.

## Установка и запуск (через Docker)

1. Установи Docker и Docker Compose.
2. Создай файл `.env` по примеру `.env.example` и заполни его:
   BOT_TOKEN=твой_токен_от_BotFather
   DATABASE_URL=postgresql+psycopg2://postgres:sadcatman123@db:5432/gym_bot_db
3. Запусти проект одной командой:
   docker compose up --build
   (Docker сам поднимет базу данных, применит миграции Alembic и запустит бота).

## Запуск без Docker (локально)

1. Установи зависимости:
   pip install -r requirements.txt
2. Настрой локальную PostgreSQL и создай базу данных.
3. Измени DATABASE_URL в .env на localhost:
   DATABASE_URL=postgresql+psycopg2://postgres:пароль@localhost:5432/gym_bot_db
4. Примени миграции:
   alembic upgrade head
5. Запусти бота:
   python main.py

## Функции

- Регистрация пользователя в базе данных
- Создание тренировок (свой список для каждого юзера)
- Добавление упражнений (подходы, повторения, вес)
- Просмотр всех тренировок и упражнений через Inline-кнопки
- Удаление тренировок (упражнения удаляются автоматически)

## Стек

- Python 3.12
- Aiogram (асинхронный Telegram-бот)
- PostgreSQL (база данных)
- SQLAlchemy (ORM, связи между таблицами)
- Alembic (миграции базы данных)
- Docker / Docker Compose (контейнеризация)
- python-dotenv (безопасное хранение секретов)
- Git

## Автор

Никита Безносиков - [GitHub](https://github.com/nikitabeznosikov112-sketch)