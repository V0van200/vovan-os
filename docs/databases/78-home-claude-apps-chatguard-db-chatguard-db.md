# /home/claude/apps/chatguard/db/chatguard.db (сервер 78, sqlite)

Проект: ChatGuard. Размер: 212.0 КБ.

## admin_audit — 13 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER |  |  |
| actor | TEXT |  |  |
| action | TEXT | да |  |
| detail | TEXT |  |  |
| created_at | INTEGER | да |  |

## banned_words — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER | да |  |
| word | TEXT | да |  |
| created_at | INTEGER | да |  |

## bot_api_keys — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| bot_id | INTEGER | да |  |
| provider | TEXT | да |  |
| label | TEXT |  |  |
| key_value | TEXT | да |  |
| created_at | INTEGER | да |  |

## bots — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| owner_id | INTEGER | да |  |
| token | TEXT | да |  |
| username | TEXT |  |  |
| name | TEXT |  |  |
| ai_moderation | INTEGER | да |  |
| ai_translation | INTEGER | да |  |
| target_lang | TEXT | да |  |
| active | INTEGER | да |  |
| created_at | INTEGER | да |  |

## custom_commands — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER | да |  |
| trigger | TEXT | да |  |
| response | TEXT | да |  |
| created_at | INTEGER | да |  |

## dashboard_access — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| chat_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| granted_by | INTEGER | да |  |
| created_at | INTEGER | да |  |

## group_admins — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| chat_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| username | TEXT |  |  |
| full_name | TEXT |  |  |

## group_detectors — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| chat_id | INTEGER | да | PK |
| detector | TEXT | да | PK |
| enabled | INTEGER | да |  |
| sensitivity | TEXT | да |  |
| config_json | TEXT |  |  |

## group_members — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| chat_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| bot_id | INTEGER |  |  |
| username | TEXT |  |  |
| full_name | TEXT |  |  |
| first_seen | INTEGER |  |  |
| last_seen | INTEGER |  |  |
| msg_count | INTEGER | да |  |

## groups — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| chat_id | INTEGER |  | PK |
| bot_id | INTEGER | да |  |
| title | TEXT | да |  |
| username | TEXT |  |  |
| bot_enabled | INTEGER | да |  |
| welcome_text | TEXT |  |  |
| rules_text | TEXT |  |  |
| added_at | INTEGER | да |  |
| welcome_enabled | INTEGER | да |  |
| antiflood_enabled | INTEGER | да |  |
| antiflood_count | INTEGER | да |  |
| antiflood_secs | INTEGER | да |  |
| links_filter | INTEGER | да |  |
| forward_filter | INTEGER | да |  |
| warn_limit | INTEGER | да |  |
| smart_stopwords | INTEGER | да |  |
| ai_text_moderation | INTEGER | да |  |
| ai_text_sensitivity | TEXT | да |  |
| ai_image_moderation | INTEGER | да |  |
| ai_voice_moderation | INTEGER | да |  |
| newbie_guard | INTEGER | да |  |
| cmd_synonyms | INTEGER | да |  |
| log_chat_id | INTEGER |  |  |

## invite_codes — 5 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| code | TEXT |  | PK |
| created_by | INTEGER |  |  |
| used_by | INTEGER |  |  |
| created_at | INTEGER | да |  |
| used_at | INTEGER |  |  |

## message_stats — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| chat_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| username | TEXT |  |  |
| full_name | TEXT |  |  |
| day | TEXT | да | PK |
| count | INTEGER | да |  |

## mod_actions — 7 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER | да |  |
| action | TEXT | да |  |
| target_id | INTEGER |  |  |
| target_name | TEXT |  |  |
| moderator_id | INTEGER |  |  |
| moderator_name | TEXT |  |  |
| reason | TEXT |  |  |
| until | INTEGER |  |  |
| created_at | INTEGER | да |  |

## moderation_events — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER | да |  |
| message_id | INTEGER |  |  |
| user_id | INTEGER |  |  |
| detector | TEXT |  |  |
| category | TEXT |  |  |
| confidence | REAL |  |  |
| reason | TEXT |  |  |
| action | TEXT |  |  |
| sla_ms | INTEGER |  |  |
| latency_ms | INTEGER |  |  |
| created_at | INTEGER | да |  |

## processed_updates — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| bot_id | INTEGER | да | PK |
| update_id | INTEGER | да | PK |
| processed_at | INTEGER | да |  |

## referral_links — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| chat_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| invite_link | TEXT | да |  |
| created_at | INTEGER | да |  |

## referrals — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER | да |  |
| inviter_id | INTEGER | да |  |
| invited_id | INTEGER | да |  |
| created_at | INTEGER | да |  |

## user_messages — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| text | TEXT |  |  |
| ts | INTEGER | да |  |

## user_notes — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| author | TEXT |  |  |
| note | TEXT | да |  |
| created_at | INTEGER | да |  |

## users — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| username | TEXT | да |  |
| password_hash | TEXT | да |  |
| password_salt | TEXT | да |  |
| session_token | TEXT |  |  |
| is_admin | INTEGER | да |  |
| created_at | INTEGER | да |  |
| last_seen | INTEGER |  |  |
| telegram_id | INTEGER |  |  |

## warnings — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| chat_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| count | INTEGER | да |  |
