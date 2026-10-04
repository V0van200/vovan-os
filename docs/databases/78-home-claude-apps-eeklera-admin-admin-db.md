# /home/claude/apps/eeklera-admin/admin.db (сервер 78, sqlite)

Проект: EEKLERA — сервисы. Размер: 804.0 КБ.

## applications — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| find_id | INTEGER |  |  → finds.id |
| title | TEXT | да |  |
| submitted_at | INTEGER | да |  |
| result | TEXT | да |  |
| updated_at | INTEGER | да |  |

## events — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| kind | TEXT | да |  |
| title | TEXT | да |  |
| starts_at | INTEGER | да |  |
| ends_at | INTEGER |  |  |
| place | TEXT |  |  |
| note | TEXT |  |  |
| link | TEXT |  |  |
| source | TEXT |  |  |
| source_id | TEXT |  |  |
| created_at | INTEGER | да |  |

## finds — 491 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| source | TEXT | да |  |
| source_id | TEXT | да |  |
| title | TEXT | да |  |
| org | TEXT |  |  |
| link | TEXT |  |  |
| category | TEXT |  |  |
| confidence | TEXT |  |  |
| deadline | INTEGER |  |  |
| payload | TEXT |  |  |
| found_at | INTEGER | да |  |
| status | TEXT | да |  |

## meta — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| k | TEXT |  | PK |
| v | TEXT |  |  |

## notifications — 22 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| kind | TEXT | да |  |
| text | TEXT | да |  |
| send_at | INTEGER | да |  |
| sent_at | INTEGER |  |  |
