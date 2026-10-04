# Sentra

**Платформы** · 🟢 работает — работает: sentra-api, sentra-worker, sentra2-api, sentra-postgres, sentra-redis

Платформа управления Telegram-сообществами: модульный монолит + воркеры. Sentra V2 — пересборка на той же базе. Ежедневный дамп тянется на сервер 198.

## Со слов владельца

- **Для чего:** управление ботами Telegram-сообществ
- **Сейчас:** работает: бот подключён к одной группе («Купидончик»)
- **Планы:** возможно развивать
- **Ещё:** Магазин shop.eeklera.online связан с Sentra; магазин для Леры позже собран отдельно. ChatGuard — предшественник Sentra.
- **Приоритет в хабе:** 2

## Ссылки

- https://sentra.vovan20.ru
- https://shop.eeklera.online
- https://github.com/V0van200/sentra

## Что запущено

| Сервис | Сервер | Состояние | Порты | Память |
|---|---|---|---|---|
| sentra-api | 78 | active | 3600 | 21.6 МБ |
| sentra-worker | 78 | active | — | 45.8 МБ |
| sentra2-api | 78 | active | 3601 | 12.4 МБ |
| 🐳 sentra-postgres | 78 | Up 6 days (healthy) | — | — |
| 🐳 sentra-redis | 78 | Up 6 days (healthy) | — | — |

## Домены

- **sentra.vovan20.ru**
  - `/` → https://78.17.19.43/sentra/ (сервер 198)
  - `/` → 301 https://$host$request_uri (сервер 198)
- **shop.eeklera.online**
  - `/` → https://78.17.19.43/sentra/ (сервер 198)
  - `/` → 301 https://$host$request_uri (сервер 198)

## Базы данных

| База | Сервер | Движок | Таблиц | Строк | Схема |
|---|---|---|---|---|---|
| sentra | 78 | postgres | 102 | 5910 | [схема](../../docs/databases/78-postgres-sentra.md) |
| sentra_test | 78 | postgres | 103 | 84646 | [схема](../../docs/databases/78-postgres-sentra_test.md) |
| sentra-redis | 78 | redis | 0 | 0 | [схема](../../docs/databases/78-redis-sentra-redis.md) |

## Репозитории GitHub

### sentra

https://github.com/V0van200/sentra · private · — · Пустой репозиторий

GitHub size = 0; содержимое не получено.

## Папки на серверах

- `78:/home/claude/apps/sentra` — 72.6 МБ, 442 файлов, изменена 2026-09-28, стек: node, fastify, docker, есть .env (значения не читались)
  - Sentra — платформа управления Telegram-сообществами (перестройка). Модульный монолит + workers.
  - README: # Sentra · Перестройка Sentra как платформы управления Telegram-сообществами. Модульный монолит + workers, PostgreSQL (истина), Redis (очереди). · Полная спецификация — в [`docs/`](docs/) (Obsidian-вейл). Порядок работ: `docs/00_CONTROL_TOWER/02_PHASE_TRACKER.md`. · ## Стек · Node 20 (ESM) · Fastify · PostgreSQL (`pg`) · Redis (`ioredis`). Инфраструктура для разработки — в Docker. · ## Запуск лока
- `78:/home/claude/apps/sentra2` — 10.4 МБ, 270 файлов, изменена 2026-09-14, стек: node, fastify, есть .env (значения не читались)
  - README: # Sentra V2 — пересборка · Полная пересборка Sentra: та же база данных (`sentra-postgres`, ничего не мигрируем), · полностью новый код и дизайн. Старая версия (`/home/claude/apps/sentra`) продолжает · работать всё время переезда — переключение происходит модуль за модулем, не разом. · Архитектура — расширение `/home/claude/apps/ARCHITECTURE.md`, проверено на реальных · практиках 2026 года (Combot 
- `78:/root/test-sentra` — 1.1 МБ, 83 файлов, изменена 2026-09-05
