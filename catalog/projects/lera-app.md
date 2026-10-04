# Lera App

**Приложения** · 📦 только GitHub — есть только в GitHub (локальные файлы удалены)

Telegram Mini App: сообщество, платежи, игры. Локальная папка удалена — код в GitHub. На 78 в nginx остался блок eeklera.online/app, указывающий на удалённую папку.

## ⚠ Проблемы

- папка /opt/lera-app удалена (была /srv/projects/lera-app)

## Ссылки

- https://github.com/V0van200/lera-app

## Репозитории GitHub

### lera-app

https://github.com/V0van200/lera-app · private · 1.5 МБ · FastAPI / React / SQLite

Telegram Mini App: сообщество, платежи, игры.

> # EEKlera App — Telegram Mini App для сообщества Леры
> **Что это:** приложение внутри Telegram для зрителей стримерши EEKLERA (Валерия Колягина). Открывалось из бота, фронт лежал на `https://eeklera.online/app/`. Это «приложение как ТГ» — социальная площадка фанатов.
> **Что умело:**
> - группы и личные сообщения (WebSocket-чаты), посты;
> - подарки, монеты, лидерборды, игры (в `changelogs/` есть сессия про Мафию);
> - профили и авторизация через подпись Telegram;
> - оплата через ЮMoney, звонки (TURN-сервер);
> - админка: `/api/admin/*`.
> **Как было устроено** (подробно — в `CLAUDE.md`):
> - `backend/` — Python 3.11, FastAPI, SQLite (`lera.db`), systemd-сервис `lera-backend`;
> - `routers/` — `admin.py`, `auth.py`, `chat.py` и другие;
> - `bot_orig.py` — Telegram-бот, отдельный сервис `lera-bot`;
> - «Бобёр-бот» с монетами и сообщениями, база `/opt/bober-bot/data.db`;
> - `frontend/`, `frontend-v2/` — React + Vite;
> - nginx отдавал всё по адресу `/app/`, файлы — из `/app/uploads/`.
> **Прочее:** `changelogs/` — журналы работы (июнь 2026), `graphify-out/` — карта кода.

## Папки на серверах

- 🔴 `78:/opt/lera-app` — **удалена** (вела в `/srv/projects/lera-app`)
