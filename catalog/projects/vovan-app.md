# Vovan App

**Приложения** · 🟡 не запущен — код есть на сервере, но не запущен

Соцсеть: чаты, посты, звонки, игры, роли (FastAPI + React). Сервис не запущен; база vovan.db — 80 таблиц.

## Со слов владельца

- **Когда:** давно, ещё на старых серверах
- **Для чего:** веб-приложение, похожее на Telegram
- **Сейчас:** архив (бэкап в GitHub)
- **Планы:** восстановить и развивать
- **Приоритет в хабе:** 1

## ⚠ Проблемы

- папка /opt/vovan-app удалена (была /srv/projects/vovan-app)

## Ссылки

- https://github.com/V0van200/vovan-app

## Базы данных

| База | Сервер | Движок | Таблиц | Строк | Схема |
|---|---|---|---|---|---|
| /home/claude/apps/agent-hub/projects/vovan-app/backend/vovan.db | 78 | sqlite | 80 | 409 | [схема](../../docs/databases/78-home-claude-apps-agent-hub-projects-vovan-app-backend-vovan-db.md) |
| /home/claude/apps/agent-hub/projects/vovan-app/backend/demo.db | 78 | sqlite | 14 | 130 | [схема](../../docs/databases/78-home-claude-apps-agent-hub-projects-vovan-app-backend-demo-db.md) |
| /home/claude/apps/agent-hub/projects/vovan-app/push_subscriptions.db | 78 | sqlite | 1 | 0 | [схема](../../docs/databases/78-home-claude-apps-agent-hub-projects-vovan-app-push-subscriptions-db.md) |

## Репозитории GitHub

### vovan-app

https://github.com/V0van200/vovan-app · private · 693.0 КБ · FastAPI / React / SQLite

Соцсеть: чаты, посты, звонки, игры, роли.

> # Vovan — соцсеть «всё в одном»
> **Что это:** собственная веб-соцсеть / супер-приложение на `vovan20.ru/app` — попытка собрать в одном месте Discord, VK и Twitch. Отдельный проект, **не Telegram** и без бренда EEKLERA. Код вырос из [lera-app](../lera-app) (чаты, группы, игры перенесены оттуда).
> **Что умело (по коду и `PROJECT_NOTES.md`):**
> - чаты, личка, группы, Discord-подобные серверы с каналами;
> - посты, лента, сторис, комментарии, реакции;
> - голосовые комнаты, звонки, просмотр стримов и их расписание;
> - игры: Мафия, Бункер, колесо;
> - XP, уровни, задания, лидерборды, магазин, косметика, 3D-подарки;
> - музыкальный плеер, редактор фото, планировщик;
> - админка: роли, модерация, экономика, рассылки;
> - push-уведомления (`push_subscriptions.db`).
> **Как было устроено:**
> - `backend/` — Python, FastAPI, SQLite (`vovan.db`);
> - `frontend/` — React + Vite;
> - `uploads/` — загруженные пользователями файлы;
> - сборки для телефона и ПК раздавались с сервера: `Vovan.apk`, `Vovan-Setup.exe`, `Vovan-portable.exe`.

## Папки на серверах

- `78:/home/claude/apps/agent-hub/projects/vovan-app` — 316.1 МБ, 357 файлов, изменена 2026-10-05
  - README: # vovan-app · Проект агентной системы.
- 🔴 `78:/opt/vovan-app` — **удалена** (вела в `/srv/projects/vovan-app`)
