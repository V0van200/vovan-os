# EEKLERA — сервисы

**Платформы** · 🟢 работает — работает: eeklera-admin, eeklera-analytics, eeklera-chat, eeklera-inquiries, eeklera-sub-bot

Кабинет Леры (admin, порт 3505), аналитика посещений (3610), чат (3011), заявки (3504), бот подписки.

## Ссылки

- https://github.com/V0van200/Eeklera_new_site

## Что запущено

| Сервис | Сервер | Состояние | Порты | Память |
|---|---|---|---|---|
| eeklera-admin | 78 | active | 3505 | 12.3 МБ |
| eeklera-analytics | 78 | active | 3610 | 2.0 МБ |
| eeklera-chat | 78 | active | 3011 | 2.1 МБ |
| eeklera-inquiries | 78 | active | 3504 | 1.6 МБ |
| eeklera-sub-bot | 78 | active | — | 13.6 МБ |

## Базы данных

| База | Сервер | Движок | Таблиц | Строк | Схема |
|---|---|---|---|---|---|
| /home/claude/apps/eeklera-admin/admin.db | 78 | sqlite | 5 | 514 | [схема](../../docs/databases/78-home-claude-apps-eeklera-admin-admin-db.md) |
| /home/claude/apps/eeklera-analytics/analytics.db | 78 | sqlite | 2 | 1484 | [схема](../../docs/databases/78-home-claude-apps-eeklera-analytics-analytics-db.md) |
| /eeklera/eeklera_site/data/chat.db | 78 | sqlite | 7 | 77 | [схема](../../docs/databases/78-eeklera-eeklera-site-data-chat-db.md) |
| /home/claude/apps/agent-hub/projects/Eeklera/site/eeklera_site/data/chat.db | 78 | sqlite | 7 | 77 | [схема](../../docs/databases/78-home-claude-apps-agent-hub-projects-eeklera-site-eeklera-site-data-chat-db.md) |
| eeklera | 78 | postgres | 11 | 42 | [схема](../../docs/databases/78-postgres-eeklera.md) |
| eeklera_test | 78 | postgres | 11 | 30 | [схема](../../docs/databases/78-postgres-eeklera_test.md) |

## Репозитории GitHub

### Eeklera_new_site

https://github.com/V0van200/Eeklera_new_site · public · 25.5 МБ · HTML / CSS / JS

acting, modeling, blog, media, UI-kit.

## Папки на серверах

- `78:/home/claude/apps/eeklera-admin` — 32.6 МБ, 25 файлов, изменена 2026-10-04, стек: node, есть .env (значения не читались)
  - README: # EEKLERA admin — кабинет Леры · Порт 3505, адрес после публикации — `eeklera.online/admin/`. **Пока не задеплоен.** · node test.cjs            # самопроверка: импорт находок идемпотентен · ADMIN_DEV=1 node server.cjs   # локальный запуск без nginx · ## Как это масштабируется · Четыре решения, из-за которых новые разделы не потребуют переделки: · 1. **Одна SQLite вместо россыпи JSON.** Раньше данн
- `78:/home/claude/apps/eeklera-analytics` — 31.9 МБ, 6 файлов, изменена 2026-09-28, стек: node
- `78:/home/claude/apps/eeklera-inquiries` — 7.3 КБ, 2 файлов, изменена 2026-07-28
- `78:/eeklera/eeklera_site` — 414.8 МБ, 385 файлов, изменена 2026-10-04
- `78:/eeklera/eeklera-sub-bot` — 553.0 МБ, 5 файлов, изменена 2026-10-04, есть .env (значения не читались)
