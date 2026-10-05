# Agent Hub

**ИИ-агенты** · 🟢 работает — работает: agent-hub

Хаб агентов с проектами (vovan-app, Eeklera, GPT, тесты…). Вход через auth-gateway. Папки agents/team/tasker удалены.

## ⚠ Проблемы

- папка /home/claude/agents удалена (была /srv/projects/agents)
- папка /home/claude/team удалена (была /srv/projects/team)
- папка /home/claude/tasker удалена (была /srv/projects/tasker)

## Ссылки

- https://agents.vovan20.ru
- https://github.com/V0van200/server-misc

## Что запущено

| Сервис | Сервер | Состояние | Порты | Память |
|---|---|---|---|---|
| agent-hub | 78 | active | 3495 | 2.1 МБ |

## Домены

- **agents.vovan20.ru**
  - `= /__auth` → http://127.0.0.1:3481/auth/check (сервер 78)
  - `/` → http://127.0.0.1:3456 (сервер 78)

## Репозитории GitHub

### server-misc

https://github.com/V0van200/server-misc · private · 706.0 КБ · Python / Node / HTML

13 папок сервисов со старого сервера.

> # Мелкие сервисы со старого сервера vovan20.ru
> Сборник небольших проектов, которые жили на сервере рядом с основными. У каждого своя папка.
> | Папка | Что это и зачем |
> | `bday-quest/` | **Квест EEKLERA**: Telegram Mini App с квестом, судя по названию — ко дню рождения Леры. Python (`app.py`) + `static/index.html`, прохождения хранились в `quest.db`. |
> | `gate/` | Шлюз-сборщик статистики и VPN-доступа (`server.cjs`, `collector.py`, аналитика). Списки VPN-пользователей и сессии вырезаны. |
> | `linux-academy/` | Интерактивный курс по Linux: уроки (`content-*.js`) и эмулятор терминала в браузере (`terminal.js`). |
> | `agents/` | Панель команды ИИ-агентов: общая рабочая папка `ws/_shared`, лог команды, сообщения оркестратору, дизайн. |
> | `server-admin/` | Простая веб-панель администрирования сервера с логином (Node). |
> | `www-misc/` | Мелкие страницы сервера: 3D-страница, AI-лента, хаб, колесо и страницы cools1s, `assetlinks.json` для Android-приложения. |
> | `shopper/`, `shopper-www/` | Копия сервиса «Shopper»: витрина + админка, данные в `data.json`, API на Python. |
> | 

## Папки на серверах

- `78:/home/claude/apps/agent-hub` — 1004.3 МБ, 1023 файлов, изменена 2026-10-05
- ⚪ `78:/opt/agent-hub` — не найдена при сканировании
- 🔴 `78:/home/claude/agents` — **удалена** (вела в `/srv/projects/agents`)
- 🔴 `78:/home/claude/team` — **удалена** (вела в `/srv/projects/team`)
- 🔴 `78:/home/claude/tasker` — **удалена** (вела в `/srv/projects/tasker`)
- `78:/home/claude/apps/agent-hub/projects/123` — 322.9 КБ, 6 файлов, изменена 2026-09-14
  - README: # 123 · Проект пользователя vovan.
- `78:/home/claude/apps/agent-hub/projects/GPT` — 750.2 КБ, 9 файлов, изменена 2026-08-05
  - README: # GPT · Проект агентной системы.
- `78:/home/claude/apps/agent-hub/projects/Test` — 518.7 КБ, 25 файлов, изменена 2026-08-06
  - README: # Test — тестовый проект агентной системы
- `78:/home/claude/apps/agent-hub/projects/site` — 143.2 КБ, 8 файлов, изменена 2026-08-08
  - README: # site · Проект пользователя vovan200.
- `78:/home/claude/apps/agent-hub/projects/маршрут с мск до Питера на велике` — —, 0 файлов, изменена —
  - README: # маршрут с мск до Питера на велике · Проект пользователя vovan.
