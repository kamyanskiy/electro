# Руководство по развертыванию

## Требования

- Docker и Docker Compose установлены на сервере
- Открытые порты: 80 (HTTP), 443 (HTTPS, опционально)

## Шаги развертывания

### 1. Клонирование репозитория

```bash
git clone <your-repo-url> electro
cd electro
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
nano .env
```

**Важно:** Обязательно измените следующие параметры:
- `POSTGRES_PASSWORD` - надежный пароль для базы данных
- `SECRET_KEY` - случайная строка для JWT (можно сгенерировать: `openssl rand -hex 32`)
- `FRONTEND_URL` - URL вашего домена (например, `http://your-domain.com` или `https://your-domain.com`)

### 3. Сборка и запуск контейнеров

```bash
# Сборка образов
docker-compose build

# Запуск в фоновом режиме
docker-compose up -d
```

### 4. Проверка статуса

```bash
# Просмотр логов
docker-compose logs -f

# Проверка статуса контейнеров
docker-compose ps
```

### 5. Создание суперпользователя

Если вы не указали параметры суперпользователя в `.env`, создайте его вручную:

```bash
docker-compose exec backend pdm run python -m backend.cli create-superuser
```

## Доступ к приложению

- **Фронтенд:** http://your-server-ip или http://your-domain.com
- **API документация:** http://your-server-ip/docs
- **API:** http://your-server-ip/api

## Управление

### Остановка приложения

```bash
docker-compose down
```

### Остановка с удалением данных

```bash
docker-compose down -v
```

### Перезапуск сервисов

```bash
docker-compose restart
```

### Обновление приложения

```bash
git pull
docker-compose build
docker-compose up -d
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Выполнение миграций вручную

```bash
docker-compose exec backend pdm run alembic upgrade head
```

### Резервное копирование базы данных

```bash
docker-compose exec postgres pg_dump -U postgres electro_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Восстановление базы данных

```bash
docker-compose exec -T postgres psql -U postgres electro_db < backup_file.sql
```

## Настройка HTTPS с Let's Encrypt (опционально)

Для production рекомендуется использовать HTTPS. Добавьте nginx-proxy и certbot:

```bash
# Создайте docker-compose.prod.yml с nginx-proxy и certbot
# Или используйте Traefik для автоматического SSL
```

## Мониторинг

### Health checks

```bash
# Backend health
curl http://localhost/health

# Database
docker-compose exec postgres pg_isready -U postgres
```

## Устранение неполадок

### Контейнер не запускается

```bash
docker-compose logs <service-name>
```

### База данных недоступна

```bash
docker-compose exec postgres psql -U postgres -d electro_db -c "SELECT 1"
```

### Сброс окружения

```bash
docker-compose down -v
docker-compose up -d
```

## Безопасность

1. Всегда используйте сильные пароли
2. Настройте firewall (разрешите только порты 80, 443, 22)
3. Используйте HTTPS в production
4. Регулярно обновляйте Docker образы
5. Делайте регулярные резервные копии базы данных

## Production рекомендации

1. Используйте reverse proxy (nginx-proxy, Traefik)
2. Настройте SSL/TLS сертификаты
3. Настройте мониторинг (Prometheus, Grafana)
4. Настройте логирование (ELK stack или Loki)
5. Настройте автоматические резервные копии
6. Используйте Docker secrets для чувствительных данных
