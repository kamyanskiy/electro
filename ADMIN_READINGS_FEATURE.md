# Функционал просмотра показаний для админа

## Описание
Добавлена новая функциональность для администратора:
- Просмотр списка всех показаний счетчиков
- Фильтрация показаний по месяцам
- Экспорт показаний в Excel файл

## Установка зависимостей

### Backend
```bash
cd backend
pdm install
```

Новая зависимость `openpyxl` уже добавлена в `pyproject.toml`.

### Frontend
Все необходимые зависимости уже установлены, дополнительная установка не требуется.

## API Эндпоинты

### 1. Получить все показания
**Endpoint:** `GET /api/admin/readings`

**Параметры запроса:**
- `year` (optional): Год для фильтрации
- `month` (optional): Месяц для фильтрации (1-12)

**Примеры:**
```bash
# Все показания
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/admin/readings

# Показания за январь 2026
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/admin/readings?year=2026&month=1
```

**Ответ:**
```json
{
  "readings": [
    {
      "id": 1,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "plot_number": "123",
      "username": "ivan",
      "day_reading": 123.45,
      "night_reading": 67.89,
      "reading_date": "2026-01-23"
    }
  ],
  "total": 1
}
```

### 2. Экспорт показаний в Excel
**Endpoint:** `GET /api/admin/readings/export`

**Параметры запроса:**
- `year` (optional): Год для фильтрации
- `month` (optional): Месяц для фильтрации (1-12)

**Примеры:**
```bash
# Экспорт всех показаний
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/admin/readings/export --output readings.xlsx

# Экспорт показаний за январь 2026
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/admin/readings/export?year=2026&month=1" --output readings_2026_01.xlsx
```

**Формат Excel файла:**
- Колонка A: № (порядковый номер)
- Колонка B: Участок
- Колонка C: Пользователь
- Колонка D: Дата
- Колонка E: День (кВт⋅ч)
- Колонка F: Ночь (кВт⋅ч)

## Frontend

### Использование
1. Войдите в систему как администратор
2. Перейдите на страницу `/admin`
3. Выберите вкладку "Показания счетчиков"
4. Используйте фильтры для выбора месяца и года, или установите галочку "Показать все показания"
5. Нажмите кнопку "Экспорт в Excel" для скачивания файла

### Компоненты
- **AdminPanel.jsx** - расширен двумя вкладками:
  - Активация пользователей (существующая функциональность)
  - Показания счетчиков (новая функциональность)

### Сервисы
- **adminService.js** - добавлены методы:
  - `getReadings(year, month)` - получение показаний
  - `exportReadings(year, month)` - экспорт в Excel

## Изменения в коде

### Backend
1. **pyproject.toml** - добавлена зависимость `openpyxl>=3.1.0`
2. **backend/app/core/ports/readings.py** - добавлены методы:
   - `get_all_by_month(year, month)` - получение показаний за месяц
   - `get_all_readings()` - получение всех показаний
3. **backend/app/adapters/sqla/repositories/readings.py** - реализация новых методов с JOIN на таблицу users
4. **backend/app/core/services/reading_service.py** - добавлены сервисные методы
5. **backend/app/adapters/rest_api/schemas/readings.py** - добавлены схемы:
   - `ReadingWithUserResponse` - показание с информацией о пользователе
   - `AdminReadingsListResponse` - список показаний для админа
6. **backend/app/adapters/rest_api/admin.py** - добавлены эндпоинты:
   - `GET /admin/readings` - получение показаний
   - `GET /admin/readings/export` - экспорт в Excel

### Frontend
1. **frontend/src/services/admin.js** - добавлены методы для работы с показаниями
2. **frontend/src/pages/AdminPanel.jsx** - добавлена вкладка с показаниями
3. **frontend/src/pages/AdminPanel.css** - добавлены стили для новых элементов

## Запуск

### Backend
```bash
cd backend
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

## Безопасность
- Все эндпоинты защищены проверкой роли администратора через `get_current_admin_user`
- Обычные пользователи не имеют доступа к этим эндпоинтам
