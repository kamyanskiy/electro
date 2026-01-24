# СТ АВТО учет показаний эл. энергии

Система управления показаниями электросчётчиков.

## Быстрый старт

### Требования

- Python 3.10+
- PostgreSQL 13+
- Node.js 18+ (для фронтенда)

### Установка

1. Клонируйте репозиторий
2. Установите зависимости:

```bash
pdm install
```

3. Настройте переменные окружения:

```bash
cp backend/.env.example backend/.env
# Отредактируйте backend/.env и установите необходимые значения
```

4. Запустите миграции:

```bash
cd backend
alembic upgrade head
```

### Создание суперпользователя

После настройки базы данных создайте суперпользователя для управления системой.

**Способ 1: Автоматический (через .env)**

Раскомментируйте и заполните переменные `SUPERUSER_*` в файле `backend/.env`:

```bash
SUPERUSER_USERNAME=admin
SUPERUSER_PASSWORD=admin123
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PLOT_NUMBER=ADMIN-001
```

Затем запустите:

```bash
./create-superuser.sh
```

**Способ 2: Интерактивный**

```bash
cd backend
python cli.py create-superuser
```

Команда запросит необходимые данные для создания суперпользователя.

Подробнее о CLI командах см. в [CLI_USAGE.md](CLI_USAGE.md)

### Запуск приложения

#### Backend

```bash
cd backend
python main.py
```

API будет доступен по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен по адресу: http://localhost:3000

## Структура проекта

```
electro/
├── backend/          # FastAPI приложение
│   ├── alembic/     # Миграции БД
│   ├── app/         # Исходный код приложения
│   │   ├── adapters/   # Адаптеры (REST API, SQLAlchemy)
│   │   ├── core/       # Бизнес-логика
│   │   └── container.py # DI контейнер
│   ├── config/      # Конфигурация
│   └── cli.py       # CLI команды
├── frontend/        # React приложение
└── create-superuser.sh  # Скрипт создания суперпользователя
```

## Возможности

- Регистрация пользователей
- Система активации пользователей администратором
- Управление показаниями электросчётчиков
- JWT аутентификация
- Разделение прав доступа (USER/ADMIN)

## Разработка

Проект использует:
- **Backend**: FastAPI, SQLAlchemy, Alembic, dependency-injector
- **Frontend**: React, TypeScript
- **Database**: PostgreSQL
