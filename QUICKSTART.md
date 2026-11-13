# Быстрый старт

Все команды ниже выполняются из корня репозитория. Настройки берутся из корневого `.env` (см. `.env.example`).

## Установка зависимостей

### 1. Backend
```bash
pdm install
```

### 2. Frontend
```bash
cd frontend
npm install
```

## Запуск приложения

### 1. Запуск базы данных (если не запущена)
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres
```

### 2. Применение миграций
```bash
cd backend
pdm run alembic -c ../alembic.ini upgrade head
```

### 3. Создание суперпользователя (если еще не создан)
```bash
pdm run create-superuser
```

Для локальной разработки можно заполнить базу демо-данными (пароль у всех демо-пользователей `demo12345`):
```bash
cd backend
pdm run python cli.py seed-demo
```

### 4. Запуск Backend
```bash
cd backend
pdm run uvicorn main:app --reload
```

Backend будет доступен по адресу: http://localhost:8000

### 5. Запуск Frontend (в новом терминале)
```bash
cd frontend
npm run dev
```

Frontend будет доступен по адресу: http://localhost:3000 (запросы `/api` проксируются на backend)

## Тестирование новой функциональности

1. Войдите в систему как администратор
2. Перейдите по адресу: http://localhost:3000/admin
3. Выберите вкладку "Показания счетчиков"
4. Используйте фильтры для выбора месяца и года
5. Нажмите "Экспорт в Excel" для скачивания файла

## API Documentation
Swagger UI доступен по адресу: http://localhost:8000/docs
