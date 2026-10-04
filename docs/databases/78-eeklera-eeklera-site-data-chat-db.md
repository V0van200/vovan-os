# /eeklera/eeklera_site/data/chat.db (сервер 78, sqlite)

Проект: —. Размер: 100.0 КБ.

## channel_members — 7 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| channel_id | INTEGER | да | PK → channels.id |
| user_id | INTEGER | да | PK → team_users.id |
| joined_at | TEXT | да |  |
| last_read_at | TEXT |  |  |

## channels — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| name | TEXT | да |  |
| type | TEXT | да |  |
| description | TEXT |  |  |
| created_by | INTEGER |  |  → team_users.id |
| created_at | TEXT | да |  |
| last_message_at | TEXT |  |  |

## chat_schema_version — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| version | INTEGER |  | PK |
| applied_at | TEXT | да |  |

## chat_sessions — 11 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| token | TEXT |  | PK |
| user_id | INTEGER | да |  → team_users.id |
| ip_address | TEXT |  |  |
| user_agent | TEXT |  |  |
| created_at | TEXT | да |  |
| expires_at | TEXT | да |  |

## messages — 49 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| channel_id | INTEGER | да |  → channels.id |
| user_id | INTEGER | да |  → team_users.id |
| content | TEXT | да |  |
| created_at | TEXT | да |  |
| edited_at | TEXT |  |  |
| deleted | INTEGER | да |  |

## team_invites — 3 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| code | TEXT | да |  |
| role | TEXT | да |  |
| note | TEXT |  |  |
| max_uses | INTEGER | да |  |
| used_count | INTEGER | да |  |
| expires_at | TEXT |  |  |
| created_by | INTEGER |  |  → team_users.id |
| created_at | TEXT | да |  |
| revoked_at | TEXT |  |  |

## team_users — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| login | TEXT | да |  |
| name | TEXT |  |  |
| role | TEXT | да |  |
| password_hash | TEXT | да |  |
| avatar_color | TEXT |  |  |
| bio | TEXT |  |  |
| is_active | INTEGER | да |  |
| created_at | TEXT | да |  |
| last_login_at | TEXT |  |  |
| last_seen_at | TEXT |  |  |
| nickname | TEXT |  |  |
| avatar_url | TEXT |  |  |
| email | TEXT |  |  |
| email_verified_at | TEXT |  |  |
| updated_at | TEXT |  |  |
| age | INTEGER |  |  |
| avatar | TEXT |  |  |
| status_text | TEXT |  |  |
