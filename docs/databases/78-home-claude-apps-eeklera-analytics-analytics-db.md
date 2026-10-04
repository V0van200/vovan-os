# /home/claude/apps/eeklera-analytics/analytics.db (сервер 78, sqlite)

Проект: EEKLERA — сервисы. Размер: 156.0 КБ.

## catalog — 202 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| cat | TEXT | да | PK |
| name | TEXT | да | PK |

## events — 1282 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| ts | INTEGER | да |  |
| type | TEXT | да |  |
| name | TEXT | да |  |
| secs | INTEGER | да |  |
| sid | TEXT | да |  |
| cat | TEXT | да |  |
