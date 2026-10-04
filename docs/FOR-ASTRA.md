# Для Astra 6: как строить сайт Vovan OS

Макет: `design/reference-dashboard.png` (и `design/board-09.png` — главный экран).
**Главное правило:** ни одной выдуманной цифры. Если у блока нет источника — карточка «нет данных», серым.
Сейчас данные лежат файлами в `inventory/` (снимок). На этапе 2 те же структуры будут отдаваться живым API — **рисуй сразу по этим форматам**.

## Что важно владельцу (ответы 2026-10-04)
Порядок на главной хаба:
1. **Рабочие сайты:** EEKLERA, vovan20.ru (Studio), cools1s.ru, os.eeklera.online.
2. **Мини-приложения и игры:** Каблуковск, Terraria, Каблук-Сити.
3. **Sentra-бот** (сообщества, может развиваться).
4. **Приложения:** Video2MD и подобные.
5. **Серверы:** оба сервера, скорость интернета, пинг, где проблемы, открытые порты, защита (безопасность), важная статистика.

Главные проекты (карточки сверху): **EEKLERA, Каблуковск, Terraria, Vovan App** (восстановить). Orion — позже. Приоритет — поле `owner.priority` (1 — главное).
Хаб пока только для владельца; видеть нужно **всё**.

## Главный источник — база проектов
`catalog/projects.json` — **все 49 проектов** со статусом, частями (репозитории, папки, сервисы, домены, базы), проблемами и ссылками. Формат — `catalog/SCHEMA.md`. Карточки для чтения — `catalog/projects/*.md`.
Разделы меню хаба = категории (`categories`): Игры, Сайты, Платформы, Приложения, Боты, ИИ-агенты, Инструменты, Панели, Контент, Инфраструктура, Идеи.

## Экраны и источники
| Блок макета | Сейчас (файл) | Живой API (этап 2) | Поля |
|---|---|---|---|
| Проекты (счётчик, карточки) | `inventory/links.json` → `groups` | `GET /api/os/projects` | name, kind, repo, server, services[], domains[], databases[], confidence, note |
| Сервисы онлайн | `inventory/servers/*.json` → `services` | `GET /api/os/services` | name, state, sub, ports[], memory, since, restarts, workdir |
| Хранилище | `host.disks` | `GET /api/os/metrics` | mount, size, used, avail |
| CPU / RAM / Диск (слева внизу) | `host.load`, `ram_total/ram_available`, `disks` | `GET /api/os/metrics` | + история за 24 ч (srv-watch) |
| Карта системы | `inventory/system-graph.json` | `GET /api/os/graph` | nodes[{id,type,label,…}], edges[{from,to,kind}] |
| Фильтры «Проекты / Сервисы / Агенты / Инфраструктура» | `node.type`, `project.kind` | — | type: server, service, container, domain, database, project; kind: game, site, bot, agents, infra… |
| Git / репозитории | `inventory/github-repos.json` | `GET /api/os/github` | name, url, visibility, последние коммиты |
| Деплои, «Последний деплой» | — | `GET /api/os/deploys` | проект, sha, сообщение, время, OK/ROLLED BACK (из kabluk-deploy, eeklera-deploy, terraria-deploy) |
| Логи сервера | — | `GET /api/os/logs?service=` | время, уровень, сообщение (без секретов) |
| Ошибки | — | `GET /api/os/alerts` | упавшие сервисы, неудачные деплои, сертификаты < 14 дней |
| Базы данных (раздел меню) | `docs/DATABASES.md`, `inventory/servers/*.json` → `databases` | `GET /api/os/databases` | engine, path/database, size, tables[{table, rows, columns[]}] |
| ИИ-агенты, AI Gateway, Очередь задач | нет источника | после подключения agent-hub / jarvis / orion | показывать «нет данных» |
| Карточки проектов: игроки, посетители | — | `GET /api/os/projects/:id/stats` | Каблук: игроки, города; EEKLERA: посещения (eeklera-analytics); Terraria: онлайн |

## Типы узлов карты → иконки
server 🖥 · service ⚙ · container 🐳 · domain 🌐 · database 🗄 · project ⬢ (kind: game 🎮, site 🌍, bot 🤖, agents 🧠, infra 🛡, app 📱, platform 🧩).
Связи: runs (сервер → сервис), routes (домен → сервис, с path), proxies (домен 198 → сервер 78), stores (сервер → база), has/uses (проект → сервис/домен/база).

## Состояния
- Сервис: `state=active` — зелёный; `activating` — жёлтый; иначе красный.
- Проект: зелёный, если все его сервисы active; жёлтый, если часть; серый, если сервисов нет (статика/архив).
- `confidence` low/medium в `links.json` — показывать маленький значок «связь не проверена».

## Где будет жить сайт
Предлагается сервер 78, отдельный поддомен с входом через уже работающий **auth-gateway** (так уже закрыты agents.vovan20.ru и vovan20.ru). Решение — за владельцем.
