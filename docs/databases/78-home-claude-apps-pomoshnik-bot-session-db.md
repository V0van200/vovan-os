# /home/claude/apps/pomoshnik-bot/session.db (сервер 78, sqlite)

Проект: Помощник-бот. Размер: 192.0 КБ.

## session — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| model | TEXT |  |  |
| effort | TEXT |  |  |
| history | TEXT |  |  |
| updated_at | TIMESTAMP |  |  |

## sessions — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| model | TEXT |  |  |
| effort | TEXT |  |  |
| claude_session_id | TEXT |  |  |
| history | TEXT |  |  |
| updated_at | TIMESTAMP |  |  |

## tasks — 7 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| title | TEXT | да |  |
| due_dt | TEXT |  |  |
| status | TEXT |  |  |
| created_at | TIMESTAMP |  |  |

## user_settings — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| home_address | TEXT |  |  |
| home_lon | REAL |  |  |
| home_lat | REAL |  |  |
