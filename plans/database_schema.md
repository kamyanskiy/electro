# Схема базы данных

## Таблица пользователей (users)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    plot_number VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Таблица показаний (readings)
```sql
CREATE TABLE readings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    day_reading DECIMAL(10, 2) NOT NULL,
    night_reading DECIMAL(10, 2) NOT NULL,
    reading_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Индексы
```sql
CREATE INDEX idx_readings_user_id ON readings(user_id);
CREATE INDEX idx_readings_date ON readings(reading_date);