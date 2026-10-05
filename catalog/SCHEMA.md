# Формат базы проектов (`catalog/projects.json`)

Один файл со всем: проекты, их части и состояние. Хаб строится по нему.

```
{
  "generated_from": {"78": "<время снимка>", "198": "…"},
  "statuses":   {"running": "🟢 работает", "live": "🌐 сайт онлайн", "stopped": "🟡 не запущен", "repo-only": "📦 только GitHub", "lost": "🔴 файлы потеряны", "idea": "💡 идея/архив", "empty": "⚪ пусто"},
  "categories": {"game": "Игры", "site": "Сайты", …},
  "summary":    {"running": 22, …},
  "projects": [ ПРОЕКТ, … ],
  "unassigned": {"folders": [], "services": [], "databases": [], "repos": [], "docker": []}
}
```

## ПРОЕКТ
| Поле | Тип | Что это |
|---|---|---|
| id | строка | Постоянный идентификатор (адрес карточки: `/projects/<id>`) |
| name, category, category_name, tags[] | | Название и раздел меню (Игры, Сайты, Боты, ИИ-агенты…) |
| parent | id? | Если это часть другого проекта (Каблук-Сити → kabluk) |
| note | текст | Что это за проект, человеческим языком |
| people[] | строки | Кто им занимается |
| owner | {when, use, now, plan, extra, priority} | Ответы владельца: когда, зачем, что сейчас, планы, приоритет в хабе (1 — главный) |
| facts[] | строки? | Свежие факты: версия, число игроков, бэкапы, конфигурация |
| history[] | {date, text}? | Что и когда менялось (по возрастанию дат) |
| next[] | строки? | Что дальше по проекту |
| status, status_reason | | Статус (см. statuses) и почему |
| problems[] | строки | Что сломано: известные баги (вручную) + упавший сервис, удалённая папка, ненастроенный домен (автоматически) |
| links.web[], links.github[] | URL | Куда перейти |
| repos[] | {name, url, visibility, size, stack, description, readme, root_files[], exists} | Репозитории GitHub |
| folders[] | {server, path, real_path, size, files, last_change, stack[], package, description, readme, git, docker, has_env_file, top[]} или {broken, was} / {missing} | Папки на серверах |
| services[] | {server, name, state, ports[], memory, since, restarts} | Сервисы systemd (state=active — работает) |
| docker[] | {server, name, image, status} | Контейнеры |
| timers[] | {server, timer, last, description} | Регулярные задачи (деплой, бэкап) |
| domains[] | {name, routes[{server, path, to}]} | Домены и куда ведёт каждый путь |
| databases[] | {server, engine, name, tables, rows, size, doc} | Базы; doc — путь к странице схемы в `docs/databases/` |
| size_total, last_change, stack[] | | Итого по проекту |

## Как пользоваться в хабе
- **Главная:** счётчики из `summary`, карточки проектов по `category`, цвет — по `status`.
- **Карточка проекта:** всё из записи + схема базы по `databases[].doc`.
- **Проблемы:** собрать `problems[]` всех проектов в один список.
- **Поиск:** по name, note, tags, repos[].name, folders[].path, domains[].name.
- Живые значения (state сервисов, память, последние деплои) на этапе 2 будут приходить из API в тех же полях.

## Как обновить
```
python3 collector/collect.py > inventory/servers/server-<78|198>.json      # на каждом сервере
python3 collector/scan_projects.py > inventory/folders/server-<78|198>.json
python3 collector/build_docs.py && python3 collector/build_catalog.py
```
Новый проект или новая папка — добавить в `catalog/spec.json` и пересобрать. Всё, что не попало в проекты, появится в `catalog/UNASSIGNED.md`.
