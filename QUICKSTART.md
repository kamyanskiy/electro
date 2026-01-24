# Быстрый старт

## Установка зависимостей

### 1. Backend
```bash
cd /Users/matrix/Projects/electro
pdm install
```

### 2. Frontend
```bash
cd /Users/matrix/Projects/electro/frontend
npm install
```

## Запуск приложения

### 1. Запуск базы данных (если не запущена)
```bash
cd /Users/matrix/Projects/electro
docker-compose up -d
```

### 2. Применение миграций
```bash
cd /Users/matrix/Projects/electro
pdm run alembic upgrade head
```

### 3. Создание суперпользователя (если еще не создан)
```bash
cd /Users/matrix/Projects/electro
pdm run create-superuser
```

### 4. Запуск Backend
```bash
cd /Users/matrix/Projects/electro
pdm run uvicorn backend.main:app --reload
```

Backend будет доступен по адресу: http://localhost:8000

### 5. Запуск Frontend (в новом терминале)
```bash
cd /Users/matrix/Projects/electro/frontend
npm run dev
```

Frontend будет доступен по адресу: http://localhost:5173

## Тестирование новой функциональности

1. Войдите в систему как администратор
2. Перейдите по адресу: http://localhost:5173/admin
3. Выберите вкладку "Показания счетчиков"
4. Используйте фильтры для выбора месяца и года
5. Нажмите "Экспорт в Excel" для скачивания файла

## API Documentation
Swagger UI доступен по адресу: http://localhost:8000/docs
