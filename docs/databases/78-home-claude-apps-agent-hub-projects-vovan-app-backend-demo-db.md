# /home/claude/apps/agent-hub/projects/vovan-app/backend/demo.db (сервер 78, sqlite)

Проект: —. Размер: 104.0 КБ.

## channel_messages — 32 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| channel_id | INTEGER | да |  |
| author_id | INTEGER | да |  |
| text | TEXT |  |  |
| created_at | TIMESTAMP |  |  |

## gifts — 7 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| name | TEXT | да |  |
| description | TEXT |  |  |
| rarity | INTEGER |  |  |
| price | INTEGER |  |  |
| emoji | TEXT |  |  |

## group_messages — 41 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| group_id | INTEGER | да |  |
| author_id | INTEGER | да |  |
| text | TEXT |  |  |
| created_at | TIMESTAMP |  |  |

## groups — 5 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| name | TEXT | да |  |
| description | TEXT |  |  |
| type | TEXT |  |  |
| member_count | INTEGER |  |  |
| created_at | TIMESTAMP |  |  |

## post_likes — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| post_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| created_at | TIMESTAMP |  |  |

## post_saves — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| post_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| created_at | TIMESTAMP |  |  |

## posts — 20 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| author_id | INTEGER | да |  |
| text | TEXT |  |  |
| image_url | TEXT |  |  |
| likes_count | INTEGER |  |  |
| comments_count | INTEGER |  |  |
| moderation_status | TEXT |  |  |
| is_deleted | INTEGER |  |  |
| created_at | TIMESTAMP |  |  |

## server_categories — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| server_id | INTEGER | да |  |
| name | TEXT | да |  |
| position | INTEGER |  |  |

## server_channels — 10 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| server_id | INTEGER | да |  |
| category_id | INTEGER |  |  |
| name | TEXT | да |  |
| type | TEXT |  |  |
| position | INTEGER |  |  |

## servers — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| name | TEXT | да |  |
| description | TEXT |  |  |
| member_count | INTEGER |  |  |
| owner_id | INTEGER |  |  |
| created_at | TIMESTAMP |  |  |

## stories — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| author_id | INTEGER | да |  |
| image_url | TEXT |  |  |
| text | TEXT |  |  |
| created_at | TIMESTAMP |  |  |
| expires_at | TIMESTAMP |  |  |

## task_completions — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| task_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| completed_at | TIMESTAMP |  |  |

## user_gifts — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| gift_id | INTEGER | да |  |
| from_user_id | INTEGER |  |  |
| received_at | TIMESTAMP |  |  |

## users — 6 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| username | TEXT |  |  |
| first_name | TEXT |  |  |
| balance | INTEGER |  |  |
| profile_image | TEXT |  |  |
| bio | TEXT |  |  |
| joined_at | TIMESTAMP |  |  |
| is_demo | INTEGER |  |  |
| is_seed | INTEGER |  |  |
