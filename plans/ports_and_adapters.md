# Архитектура портов и адаптеров

## Обзор

Архитектура портов и адаптеров (Hexagonal Architecture) позволяет изолировать бизнес-логику от внешних зависимостей, делая систему более гибкой и тестируемой.

## Основные компоненты

### 1. Ядро (Core)
- Содержит бизнес-логику и модели домена
- Не зависит от внешних систем
- Определяет интерфейсы (порты) для взаимодействия с внешним миром

### 2. Порты (Ports)
- Интерфейсы, которые определяет ядро
- Разделяются на:
  - **Driving Ports**: используются ядром для получения данных (входные порты)
  - **Driven Ports**: используются внешними системами для взаимодействия с ядром (выходные порты)

### 3. Адаптеры (Adapters)
- Реализации портов для конкретных технологий
- Преобразуют данные между форматами ядра и внешних систем

## Структура проекта

```
app/
├── core/                  # Ядро (бизнес-логика)
│   ├── models/            # Модели домена
│   ├── services/          # Сервисы бизнес-логики
│   └── ports/             # Интерфейсы портов
│
├── adapters/              # Адаптеры
│   ├── sqla/              # SQLAlchemy адаптеры
│   │   ├── repositories/  # Репозитории
│   │   └── mapping/       # Маппинг ORM
│   ├── rest_api/          # REST API адаптеры
│   └── ...                # Другие адаптеры
│
├── service_layer/         # Слой сервисов
│   ├── unit_of_work.py     # Unit of Work
│   └── ...                # Другие сервисы
│
└── container.py           # Контейнер зависимостей
```

## Пример для нашего проекта

### 1. Модели домена (core/models)

```python
# core/models/user.py
from dataclasses import dataclass
from uuid import UUID

@dataclass
class User:
    id: UUID
    plot_number: str
    username: str
    email: str
    password_hash: str

# core/models/reading.py
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class Reading:
    id: int
    user_id: UUID
    day_reading: Decimal
    night_reading: Decimal
    reading_date: date
```

### 2. Порты (core/ports)

```python
# core/ports/users.py
from abc import ABC, abstractmethod
from uuid import UUID

class UsersRepository(ABC):
    @abstractmethod
    async def get(self, id: UUID) -> User | None:
        ...
    
    @abstractmethod
    async def get_by_plot_number(self, plot_number: str) -> User | None:
        ...
    
    @abstractmethod
    async def add(self, user: User):
        ...

# core/ports/readings.py
from abc import ABC, abstractmethod
from uuid import UUID

class ReadingsRepository(ABC):
    @abstractmethod
    async def add(self, reading: Reading):
        ...
    
    @abstractmethod
    async def get_by_user(self, user_id: UUID, limit: int = 10) -> list[Reading]:
        ...
```

### 3. Адаптеры (adapters/sqla)

```python
# adapters/sqla/repositories/users.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User
from app.core.ports import UsersRepository

class SqlAlchemyUsersRepository(UsersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: UUID) -> User | None:
        # Реализация получения пользователя
        ...
    
    async def get_by_plot_number(self, plot_number: str) -> User | None:
        # Реализация получения пользователя по номеру участка
        ...
    
    async def add(self, user: User):
        # Реализация добавления пользователя
        ...
```

### 4. Сервисы бизнес-логики (core/services)

```python
# core/services/registration.py
from app.core.models import User
from app.core.ports import UsersRepository

class RegistrationService:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo
    
    async def register_user(self, plot_number: str, username: str, email: str, password: str):
        # Проверка уникальности номера участка
        existing = await self.users_repo.get_by_plot_number(plot_number)
        if existing:
            raise ValueError("Plot number already exists")
        
        # Хеширование пароля
        password_hash = hash_password(password)
        
        # Создание пользователя
        user = User(
            id=UUID(),
            plot_number=plot_number,
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        # Сохранение
        await self.users_repo.add(user)
        
        return user
```

### 5. Контейнер зависимостей

```python
# container.py
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton

from app.adapters.sqla import SqlAlchemyUsersRepository, SqlAlchemyReadingsRepository
from app.core.services import RegistrationService, ReadingService

class Container(DeclarativeContainer):
    # Репозитории
    users_repo = Factory(SqlAlchemyUsersRepository, session_factory)
    readings_repo = Factory(SqlAlchemyReadingsRepository, session_factory)
    
    # Сервисы
    registration_service = Factory(RegistrationService, users_repo=users_repo)
    reading_service = Factory(ReadingService, readings_repo=readings_repo)
```

## Преимущества

1. **Изоляция бизнес-логики**: Ядро не зависит от базы данных, фреймворков или других внешних систем
2. **Легкость тестирования**: Можно тестировать бизнес-логику с mock-реализациями портов
3. **Гибкость**: Легко заменить одну технологию на другую (например, SQLAlchemy на Django ORM)
4. **Чистая архитектура**: Четкое разделение ответственности между слоями