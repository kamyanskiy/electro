FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка PDM
RUN pip install --no-cache-dir pdm

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml pdm.lock* ./

# Установка зависимостей через PDM
RUN pdm install --prod --no-lock --no-editable

# Копирование кода приложения
COPY backend/ ./backend/
COPY alembic.ini ./

# Создание скрипта для запуска миграций и приложения
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Waiting for database..."\n\
while ! pg_isready -h $DB_HOST -p 5432 -U $POSTGRES_USER; do\n\
  sleep 1\n\
done\n\
echo "Database is ready!"\n\
echo "Running migrations..."\n\
pdm run alembic upgrade head\n\
echo "Starting application..."\n\
pdm run uvicorn backend.main:app --host 0.0.0.0 --port 8000\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
