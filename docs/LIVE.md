# Живые данные хаба

Хаб на https://vovan20.ru/admin/hub/ получает данные **на текущую минуту**. Всё только читается, на серверах ничего не меняется.

## Как устроено
```
сервер 198: vovan-os-live-push.timer (каждую минуту)
   collector/live.py server --push  →  78:/data/vovan-os-hub/live/server-198.json
сервер 78:  vovan-os-live.timer (каждую минуту)
   collector/live.py build
     ├─ состояние сервера 78 (нагрузка, память, диски, сервисы, контейнеры, таймеры, сертификаты, защита, пинг, скорость)
     ├─ + присланное с 198 (то же + VPN, сайт EEKLERA: посетители по журналу nginx, релиз, деплои; свежесть бэкапа 78)
     ├─ + источники проектов (базы и журналы, только чтение)
     └─ /data/vovan-os-hub/live/snapshot.json   → отдаётся как /admin/hub/snapshot.json
        /data/vovan-os-hub/live/projects.json   → /admin/hub/live/projects.json
```
Оба адреса закрыты входом админки (как и сам хаб). `server-*.json` наружу не отдаются.
Скрипты на серверах лежат в `/usr/local/lib/vovan-os/` (копия `collector/collect.py` + `collector/live.py`).

## snapshot.json
Тот же формат версии 1, что `hub/site/snapshot.json`, плюс:
- `servers.<id>`: `host`, `services`, `docker`, `timers`, `certs` — живые; `live.security` (fail2ban, файрвол, упавшие службы, открытые наружу порты), `live.net` (пинг, скорость скачивания раз в час), `live.stale` — данные 198 старше 5 минут;
- `catalog.projects[].services[].state` и `docker[].status` — живые (`base_state`/`base_status` — как было при инвентаризации);
- `catalog.projects[].live` — то же, что в projects.json;
- `source.live_at`, `source.mode = "live"`.

## projects.json → `projects.<id>`
| Поле | Что это |
|---|---|
| `updated` | время сбора (UTC) |
| `connected` | `true` — у проекта есть свой источник данных; `false` — только сервисы и проверка сайтов |
| `summary` | короткая строка для карточки: «2 онлайн · 4 игроков» |
| `metrics[]` | `{label, value, hint?, level?}`; `level`: `ok` / `warn` / `bad` |
| `alerts[]` | строки — что сломано прямо сейчас (для экрана «Ошибки») |
| `lists[]` | `{title, items[]}` — игроки, деплои, страницы, чаты |
| `series[]` | `{title, points[[дата, число]]}` — для графиков |
| `preview` | адрес сайта для предпросмотра (iframe) |
| `note` | пояснение, откуда цифры |

## Источники по проектам
| Проект | Откуда |
|---|---|
| Каблуковск | `kabluk.sqlite` (игроки, онлайн по `last_seen`, экономика, казна), история `kabluk-deploy`, бэкапы |
| Каблук-Сити | `pc_cities` |
| Terraria | журнал контейнера (входы и выходы с момента запуска), файл мира, бэкапы, `tshock.sqlite` (аккаунты, SSC), история `terraria-deploy` |
| EEKLERA — сайт | журнал nginx на 198 `/var/log/nginx/eeklera.access.log` (с 05.10.2026: страницы без ботов, уникальные устройства по дням), релиз и деплои `eeklera-deploy`, проверка ответа |
| EEKLERA — сервисы | `analytics.db` (события сайта) |
| Video2MD | API сервиса `127.0.0.1:3515` (`/api/status`, `/api/jobs`) |
| Sentra | Postgres `sentra`: чаты, боты, пользователи, сообщения за сутки и неделю, модерация (только счётчики, без текстов) |
| VPN | `awg show` на 198: ключи, подключено сейчас, за сутки, трафик; Xray |
| Бэкапы и защита | fail2ban, ufw, упавшие службы, открытые порты, сертификаты < 14 дней, диски > 90%, копия 78 на 198, пинг, скорость |
| Vovan OS | выкладки хаба |
| Остальные | состояние сервисов и контейнеров, память, перезапуски, ответ сайтов (код и время) |

Новый проект подключается функцией `c_<id>` в `collector/live.py` + строкой в `CONNECTORS`.

## Интерфейс
Пока Astra не встроила `live` в свой интерфейс, его показывает отдельный модуль `hub/site/live.mjs` + `live.css`
(значок «ЖИВЫЕ ДАННЫЕ», блок «Сейчас» в паспорте проекта, предпросмотр сайта). Код Astra он не меняет.
Что стоит взять в интерфейс Astra: `summary` на карточках, `alerts` всех проектов → «Ошибки», `lists` «деплои» → «Деплои», `servers.*.live` → раздел серверов.
