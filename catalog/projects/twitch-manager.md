# Twitch Manager

**Боты** · 🟡 не запущен — код есть на сервере, но не запущен

Панель агентов Twitch (README: IRC не доделан). Не запущен; папка twitch_manager удалена.

## ⚠ Проблемы

- папка /home/claude/twitch_manager удалена (была /srv/projects/twitch_manager)

## Ссылки

- https://github.com/V0van200/twitch-manager

## Репозитории GitHub

### twitch-manager

https://github.com/V0van200/twitch-manager · private · 1.0 МБ · Node / React / SQLite

Панель агентов Twitch; README отмечает недоделки IRC.

> # Twitch Agent Manager — ИИ-зрители для Twitch-чата
> **Что это:** панель управления ИИ-агентами, которые сидят в чате Twitch как зрители. Агенты смотрят, что происходит на стриме и в чате, и пишут реплики.
> **Как работало** (подробно — в `wiki/` и `CLAUDE.md`):
> - `backend/server.js` — Node.js, Express, Socket.io, база better-sqlite3 (`data.sqlite`), порт 3001, только локально;
> - агенты подключаются к Twitch IRC и генерируют сообщения по таймеру и по событиям: упоминание, вопрос стримера, всплеск чата;
> - есть антиповтор, кулдауны и «режим одобрения»: сообщение ждёт твоего ✅ или уходит само (`auto_approve`);
> - модели через OpenRouter (по умолчанию Claude Sonnet 4.5), запасной вариант — Gemini;
> - `frontend/` — React + Vite + Tailwind: страница агента, вкладки, живые сообщения;
> - синхронизация заметок через Syncthing и Obsidian (`wiki/sync.md`).
> **Состояние на момент бэкапа** (из `wiki/index.md`):
> - агенты стояли на тестовом канале `#basila`;
> - автофолловинг через GQL сломан;
> - отправка в IRC не доделана.
> Бэкап от 23.07.2026.
> *Файлы, в которых нашлись ключи или 

## Папки на серверах

- `78:/home/claude/twitch_bot` — 64.6 КБ, 9 файлов, изменена 2026-06-08
- 🔴 `78:/home/claude/twitch_manager` — **удалена** (вела в `/srv/projects/twitch_manager`)
