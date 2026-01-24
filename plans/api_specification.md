# Спецификация API

## Регистрация пользователя
**POST** `/api/users/register`

**Request Body:**
```json
{
    "plot_number": "string",
    "username": "string",
    "password": "string",
    "email": "string"
}
```

**Responses:**
- `201 Created`: Пользователь успешно зарегистрирован
- `400 Bad Request`: Ошибка валидации данных
- `409 Conflict`: Пользователь с таким номером участка или email уже существует

## Вход пользователя
**POST** `/api/users/login`

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Responses:**
- `200 OK`: Успешный вход, возвращает токен
- `401 Unauthorized`: Неправильные учетные данные

## Добавление показаний
**POST** `/api/readings`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
    "day_reading": 123.45,
    "night_reading": 67.89
}
```

**Responses:**
- `201 Created`: Показания успешно сохранены
- `400 Bad Request`: Ошибка валидации данных
- `401 Unauthorized`: Неавторизованный доступ

## Получение показаний
**GET** `/api/readings`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit`: int (опционально, по умолчанию 10)
- `offset`: int (опционально, по умолчанию 0)

**Responses:**
- `200 OK`: Список показаний
- `401 Unauthorized`: Неавторизованный доступ