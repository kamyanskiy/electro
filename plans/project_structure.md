# Структура проекта

## Бэкенд (FastAPI)
- `backend/`
  - `app/`
    - `main.py` - основной файл приложения
    - `models/` - модели данных
      - `user.py` - модель пользователя
      - `reading.py` - модель показаний
    - `schemas/` - схемы Pydantic
      - `user.py` - схема пользователя
      - `reading.py` - схема показаний
    - `crud/` - операции с базой данных
      - `user.py` - операции с пользователями
      - `reading.py` - операции с показаниями
    - `api/` - API маршруты
      - `users.py` - маршруты для пользователей
      - `readings.py` - маршруты для показаний
    - `database.py` - настройка базы данных

## Фронтенд (React)
- `frontend/`
  - `src/`
    - `components/`
      - `RegistrationForm.jsx` - форма регистрации
      - `ReadingForm.jsx` - форма ввода показаний
      - `StatusMessage.jsx` - компонент для отображения статуса
    - `pages/`
      - `HomePage.jsx` - главная страница
      - `Dashboard.jsx` - панель управления
    - `App.js` - основной компонент
    - `index.js` - точка входа

## Миграции базы данных
- `migrations/` - миграции Alembic

## Конфигурация
- `config/`
  - `database.ini` - конфигурация базы данных
  - `settings.py` - общие настройки

## Документация
- `docs/`
  - `api.md` - документация API
  - `setup.md` - инструкции по установке