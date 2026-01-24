# Руководство по развертыванию

## Требования

- Docker и Docker Compose установлены на сервере
- Открытые порты: 80 (HTTP), 443 (HTTPS для production)

## Production развертывание (с SSL и nginx-proxy)

### 1. Остановить и удалить старые контейнеры (если есть)

```bash
cd ~/electro
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### 2. Удалить старый volume PostgreSQL (ТОЛЬКО если нужна чистая БД)

**⚠️ ВНИМАНИЕ**: Это удалит все данные базы данных!

```bash
docker volume rm electro_postgres_data
```

### 3. Создать .env файл в корне проекта

```bash
nano .env
```

Добавить следующие переменные:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=electro_db

# Backend
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
FRONTEND_URL=https://your-domain.com

# Superuser (опционально - создастся автоматически при запуске)
SUPERUSER_USERNAME=admin
SUPERUSER_PASSWORD=admin_password
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PLOT_NUMBER=ADMIN-001

# Production - nginx-proxy и Let's Encrypt
VIRTUAL_HOST=your-domain.com
LETSENCRYPT_HOST=your-domain.com
LETSENCRYPT_EMAIL=your-email@example.com
```

**Важно:**
- Замените `your_secure_password_here` на надежный пароль
- Сгенерируйте SECRET_KEY: `openssl rand -hex 32`
- Укажите ваш реальный домен вместо `your-domain.com`
- DNS запись домена должна указывать на IP сервера

### 4. Запустить контейнеры в production режиме

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 5. Проверить статус и логи

```bash
# Статус контейнеров
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Логи всех сервисов
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Логи конкретного сервиса
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f nginx-proxy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f letsencrypt
```

### 6. Создать суперпользователя (если не используете .env)

```bash
docker exec -it electro_backend pdm run python -m backend.cli create-superuser
```

## Development развертывание (локальная разработка)

### 1. Создать .env файл

```bash
cp .env.example .env
# Отредактировать .env с настройками для разработки
```

### 2. Запустить в режиме разработки

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

**Доступ:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

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
