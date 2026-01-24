# Changelog - Админ панель для просмотра показаний

## Дата: 2026-01-24

### Добавлено

#### Backend (Python/FastAPI)
1. **Новая зависимость**: `openpyxl>=3.1.0` для генерации Excel файлов
   - Файл: `pyproject.toml`

2. **Расширение ReadingsRepository** (порт)
   - Файл: `backend/app/core/ports/readings.py`
   - Методы:
     - `get_all_by_month(year, month)` - получение показаний за месяц с информацией о пользователе
     - `get_all_readings()` - получение всех показаний с информацией о пользователе

3. **Реализация новых методов репозитория**
   - Файл: `backend/app/adapters/sqla/repositories/readings.py`
   - Реализованы методы с JOIN между таблицами `readings` и `users`
   - Сортировка по дате (desc) и номеру участка

4. **Расширение ReadingService**
   - Файл: `backend/app/core/services/reading_service.py`
   - Методы:
     - `get_all_readings_by_month(year, month)` - получение показаний за месяц
     - `get_all_readings()` - получение всех показаний

5. **Новые схемы Pydantic**
   - Файл: `backend/app/adapters/rest_api/schemas/readings.py`
   - Схемы:
     - `ReadingWithUserResponse` - показание с данными пользователя (участок, имя)
     - `AdminReadingsListResponse` - список показаний для админа

6. **Новые API эндпоинты**
   - Файл: `backend/app/adapters/rest_api/admin.py`
   - Эндпоинты:
     - `GET /api/admin/readings` - получение списка показаний (с фильтрацией по месяцам)
       - Query параметры: `year`, `month` (оба опциональны, но должны быть вместе)
       - Возвращает JSON с массивом показаний и total count
     - `GET /api/admin/readings/export` - экспорт показаний в Excel
       - Query параметры: `year`, `month` (оба опциональны)
       - Возвращает .xlsx файл с форматированной таблицей
       - Автоматическое именование файла по шаблону

#### Frontend (React)
1. **Расширение adminService**
   - Файл: `frontend/src/services/admin.js`
   - Методы:
     - `getReadings(year, month)` - получение показаний с сервера
     - `exportReadings(year, month)` - скачивание Excel файла

2. **Обновление AdminPanel**
   - Файл: `frontend/src/pages/AdminPanel.jsx`
   - Добавлены:
     - Система вкладок (tabs): "Активация пользователей" и "Показания счетчиков"
     - Фильтры по месяцам и годам
     - Чекбокс "Показать все показания"
     - Кнопка "Экспорт в Excel"
     - Таблица для отображения показаний с колонками:
       - Дата
       - Участок
       - Пользователь
       - День (кВт⋅ч)
       - Ночь (кВт⋅ч)
     - Автоматическое скачивание Excel файла при экспорте

3. **Новые стили**
   - Файл: `frontend/src/pages/AdminPanel.css`
   - Добавлены стили для:
     - Вкладок (tabs)
     - Фильтров (filters)
     - Таблицы показаний (readings-table)
     - Кнопки экспорта (btn-export)
     - Адаптивный дизайн для мобильных устройств

#### Документация
1. **ADMIN_READINGS_FEATURE.md** - подробное описание новой функциональности
2. **QUICKSTART.md** - инструкция по быстрому запуску проекта
3. **CHANGELOG_ADMIN_READINGS.md** - этот файл

### Технические детали

#### Безопасность
- Все новые эндпоинты защищены через `get_current_admin_user`
- Только пользователи с ролью `admin` имеют доступ

#### Особенности реализации
- **Фильтрация**: Если указаны `year` и `month`, показываются только показания за этот месяц
- **Валидация**: Месяц должен быть в диапазоне 1-12
- **Экспорт Excel**:
  - Красивое форматирование с заголовками
  - Автоматическая ширина колонок
  - Русский формат даты (дд.мм.гггг)
  - Автоматическое именование файла

#### База данных
- Используется JOIN между таблицами `readings` и `users`
- Фильтрация на уровне SQL через `extract('year', ...)` и `extract('month', ...)`
- Сортировка: сначала по дате (desc), затем по номеру участка

### Использование

1. Войдите как администратор
2. Откройте `/admin`
3. Перейдите на вкладку "Показания счетчиков"
4. Выберите месяц и год (или отметьте "Показать все")
5. Просмотрите таблицу или экспортируйте в Excel

### Установка

```bash
# Backend
cd /Users/matrix/Projects/electro
pdm install

# Frontend (если нужно)
cd frontend
npm install
```

### Запуск

```bash
# Backend
pdm run uvicorn backend.main:app --reload

# Frontend
cd frontend
npm run dev
```
