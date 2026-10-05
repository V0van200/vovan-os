# Graph

**Сайты** · 🟢 работает — работает: gate

Аналитика/визуализация. /graph/game, /fly, /live обслуживает сервис gate (3480).

## Ссылки

- https://vovan20.ru/graph
- https://github.com/V0van200/graph

## Что запущено

| Сервис | Сервер | Состояние | Порты | Память |
|---|---|---|---|---|
| gate | 78 | active | 3480 | 5.5 МБ |

## Домены

- **vovan20.ru/graph**
  - `= /__auth_panel` → http://127.0.0.1:3481/auth/check (сервер 78)
  - `= /__auth` → http://127.0.0.1:3481/auth/check (сервер 78)
  - `= /yandex_f595f91d0a6d4274.html` → /var/www/studio (сервер 78)
  - `= /robots.txt` → /var/www/studio (сервер 78)
  - `= /sitemap.xml` → /var/www/studio (сервер 78)
  - `= /favicon.ico` → /var/www/studio/assets/img/favicon.svg (сервер 78)
  - `= /favicon.svg` → /var/www/studio/assets/img/favicon.svg (сервер 78)
  - `^~ /dl/` → /var/www (сервер 78)
  - `= /graph` → 301 /graph/ (сервер 78)
  - `/graph/` → /var/www/graph/ (сервер 78)
  - `/graph/game/` → http://127.0.0.1:3480/game/ (сервер 78)
  - `/graph/fly/` → http://127.0.0.1:3480/fly/ (сервер 78)

## Репозитории GitHub

### graph

https://github.com/V0van200/graph · private · 1.4 МБ · HTML / JS / graph data

Локальные карты кода 2D/3D.

> # Карты кода — 2D и 3D
> **Что это:** страницы с интерактивными картами кода твоих проектов: узлы — файлы и функции, линии — связи. Сделаны по отчётам graphify (`graphify-out`) и нужны, чтобы видеть устройство проекта целиком.
> **Что внутри:**
> - `index.html` — «Карты кода — 2D и 3D», общий вход;
> - карты по проектам: `lera-app.html`, `eeklera-site.html`, `studio.html`, `twitch_manager.html`, `pomoshnik-bot.html`, `server-admin.html`, `gate.html`, `dashboard.html`, `station.html`, `ai-digest.html`, `pixel-agents.html`;
> - `all.html` — все проекты сразу (~4 МБ);
> - `fly.html`, `ui.html` — режимы просмотра, в том числе 3D-полёт;
> - библиотеки `three.min.js`, `3d-force-graph.min.js`, `vis-network.min.js` лежат рядом, интернет не нужен.
> Открывается просто в браузере. Бэкап от 23.07.2026.
> *Файлы, в которых нашлись ключи или токены, в репозиторий не попали; если такие были — их список в `SECRETS_REMOVED.txt`.*

## Папки на серверах

- `78:/www-static/graph` — 15.0 МБ, 40 файлов, изменена 2026-06-18
- `78:/home/claude/gate` — 154.1 КБ, 18 файлов, изменена 2026-10-04
- `78:/home/claude/graphify-out` — 29 Б, 3 файлов, изменена 2026-07-17
- `78:/home/claude/graphs-merged` — 9.1 МБ, 5 файлов, изменена 2026-06-14
