# /root/data.db (сервер 78, sqlite)

Проект: —. Размер: 20.0 КБ.

## chat_log — 3 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| ts | REAL | да |  |
| sender | TEXT | да |  |
| text | TEXT | да |  |

## users — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| username | TEXT |  |  |
| first_name | TEXT |  |  |
| coins | INTEGER |  |  |
| messages | INTEGER |  |  |
| last_daily | INTEGER |  |  |
| last_earn | INTEGER |  |  |
| joined_at | INTEGER |  |  |
