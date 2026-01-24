# Nginx конфигурация

Эта папка содержит конфигурацию nginx для production развертывания.

## Файлы

### `Dockerfile`
Multi-stage build Docker образ:
1. Собирает React фронтенд (npm run build)
2. Копирует собранную статику в nginx
3. Настраивает nginx для раздачи статики и проксирования API

### `default.conf`
Конфигурация nginx для HTTP (без SSL):
- Раздача статики фронтенда
- Проксирование `/api/*` к backend
- Проксирование `/docs`, `/openapi.json`, `/redoc` к backend
- SPA fallback (все неизвестные маршруты -> index.html)
- Кэширование статических файлов (js, css, images)

### `default-ssl.conf`
Конфигурация nginx с SSL поддержкой:
- HTTP редирект на HTTPS
- SSL терминация
- Те же функции что и в default.conf

## Использование

### Development
В dev-режиме nginx НЕ используется. Фронтенд работает через Vite dev server:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production без SSL
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Production с SSL
1. Скопируйте SSL конфигурацию:
```bash
cp nginx/default-ssl.conf nginx/default.conf
```

2. Отредактируйте YOUR_DOMAIN в конфигурации:
```bash
nano nginx/default.conf
# Замените YOUR_DOMAIN на ваш реальный домен
```

3. Раскомментируйте certbot в docker-compose.prod.yml

4. Запустите:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Структура запросов

```
Клиент -> Nginx:80/443
           |
           ├─ /api/* ---------> Backend:8000
           ├─ /docs ----------> Backend:8000
           ├─ /health --------> Backend:8000
           └─ /* -------------> Статика (index.html, js, css)
```

## Оптимизация

Nginx уже настроен с:
- Gzip сжатием
- Кэшированием статических файлов (1 год)
- HTTP/2 поддержкой (в SSL версии)
- Правильными proxy headers

## Обновление фронтенда

При изменении фронтенда нужно пересобрать nginx образ:
```bash
docker-compose -f docker-compose.prod.yml build nginx
docker-compose -f docker-compose.prod.yml up -d nginx
```

Или с нуля:
```bash
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate nginx
```
