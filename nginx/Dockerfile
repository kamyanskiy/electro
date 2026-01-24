# Multi-stage build: сборка фронтенда + nginx с статикой
FROM node:20-alpine AS frontend-build

WORKDIR /app

# Копируем frontend код
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Финальный образ с nginx (обычный nginx, не nginx-proxy)
FROM nginx:alpine

# Копируем собранную статику фронтенда
COPY --from=frontend-build /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443
