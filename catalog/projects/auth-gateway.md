# Auth Gateway

**Инфраструктура** · 🟢 работает — работает: auth-gateway

Единый вход: закрывает agents.vovan20.ru и vovan20.ru (/__auth). Подходит и для панели Vovan OS.

## Ссылки

- https://github.com/V0van200/auth-gateway

## Что запущено

| Сервис | Сервер | Состояние | Порты | Память |
|---|---|---|---|---|
| auth-gateway | 78 | active | 3481 | 4.1 МБ |

## Репозитории GitHub

### auth-gateway

https://github.com/V0van200/auth-gateway · private · 3.3 МБ · Python / nginx auth_request

Старый SSO и файловый портал.

> # Auth *** — единый вход во все сервисы vovan20.ru
> **Что это:** центральная авторизация (SSO) для всего сервера: один логин — доступ к админке, ModBot, нейросети, обменнику, файлам и остальному. nginx спрашивал у него «пустить или нет» (`auth_request`).
> **Что внутри:**
> - `auth-gateway.py` — сервер на Python (`http.server`): логин, сессии, проверка доступа;
> - страницы портала: `index.html` (плитки сервисов), `files.html` (файловый менеджер), `photos.html` (фото с превью, кэш `.thumb_cache/`), `nexus.html`, `twin.html`, `claude.html`;
> - `config.json` — настройки;
> - `pending_deletes.json` — очередь удалений.
> **Вырезано:** `users.json` и `sessions.json` (логины, хеши паролей, сессии).
> Бэкап от 23.07.2026.
> *Файлы, в которых нашлись ключи или токены, в репозиторий не попали; если такие были — их список в `SECRETS_REMOVED.txt`.*

## Папки на серверах

- `78:/home/claude/auth-gateway` — 4.3 МБ, 426 файлов, изменена 2026-10-02
