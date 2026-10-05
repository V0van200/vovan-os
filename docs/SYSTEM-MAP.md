# Карта системы Vovan OS

Собрано автоматически `collector/collect.py` → `collector/build_docs.py`. Только чтение, без секретов.

## Сервер 198 — 198.13.184.145 (server)

- Система: Ubuntu 24.04.4 LTS, ядро 6.8.0-142-generic; CPU: 1; RAM: 961.5 МБ (свободно 290.6 МБ); нагрузка 0.20, 0.09, 0.02
- Диски: / 4.2 ГБ из 4.8 ГБ (86%); /data 1.8 ГБ из 4.8 ГБ (37%)
- Снимок: 2026-10-05T13:37:29+0000

### Сервисы

| Сервис | Состояние | Порты | Память | Папка | Описание |
|---|---|---|---|---|---|
| claude-rc | active/running | — | 499.6 МБ | /root/server-admin | Claude Code Remote Control (server-198) |
| fail2ban | active/running | — | 25.0 МБ | — | Fail2Ban Service |
| nginx | active/running | 80, 443 | 16.0 МБ | — | A high performance web server and a reverse proxy server |
| watchdog | active/running | — | 580.0 КБ | — | watchdog daemon |
| xray | active/running | 2053, 2087, 8443 | 12.1 МБ | — | Xray Service |

### Домены и маршруты (nginx)

**eeklera.online, www.eeklera.online** — корень `/data/sites/eeklera-online/current`
- `= /redesign` → ответ 301 /redesign/
- `^~ /redesign/` → файлы /data/sites/eeklera-online/current/redesign/
- `~* \.(jpg|jpeg|png|webp|svg|ico|css|js|mp3|mp4|woff2?)$` → статика
- `/` → статика

**eeklera.online, www.eeklera.online**
- `/` → ответ 301 https://eeklera.online$request_uri

**os.eeklera.online, os.vovan20.ru** — корень `/var/www/eeklera-os`
- `= /neuro` → ответ 301 /neuro/
- `^~ /neuro/` → файлы /var/www/eeklera-neuro/
- `/` → статика
- `~* \.(css|js|html)$` → статика
- `= /img/desktop.png` → ответ 403
- `~* \.(jpg|jpeg|png|webp|svg|woff2)$` → статика
- `~* \.(mp3|m4a|ogg|wav)$` → статика

**os.eeklera.online, os.vovan20.ru**
- `/` → ответ 301 https://$host$request_uri

**sentra.vovan20.ru**
- `/` → прокси → https://78.17.19.43/sentra/

**sentra.vovan20.ru**
- `/` → ответ 301 https://$host$request_uri

**shop.eeklera.online**
- `/` → прокси → https://78.17.19.43/sentra/

**shop.eeklera.online**
- `/` → ответ 301 https://$host$request_uri

**vovan20.ru, www.vovan20.ru**
- `/` → прокси → https://78.17.19.43

**vovan20.ru, www.vovan20.ru**
- `/` → ответ 301 https://$host$request_uri

### Таймеры (регулярные задачи)

- **eeklera-deploy.timer** → eeklera-deploy.service: Проверять main каждую минуту; последний запуск Mon 2026-10-05 13:36:53 UTC
- **certbot.timer** → certbot.service: Run certbot twice daily; последний запуск Mon 2026-10-05 08:46:53 UTC
- **pull-backup-78.timer** → pull-backup-78.service: Каждую ночь в 03:30 по Алматы; последний запуск Sun 2026-10-04 22:31:15 UTC

### Сертификаты HTTPS

- sentra.vovan20.ru: до Dec  7 03:22:47 2026 GMT — sentra.vovan20.ru
- os.eeklera.online: до Dec 14 10:23:20 2026 GMT — os.eeklera.online
- shop.eeklera.online: до Dec  7 03:34:34 2026 GMT — shop.eeklera.online

### Бэкапы

- `/data/backups`: 30439 файлов, 5.6 ГБ; последний `sentra-2026-10-04.sql.gz` (2026-10-04T22:31:26)

### VPN (только счётчики, без ключей)

- awg1: {"peers": 1, "active_24h": 0, "port": "443"}
- awg0: {"peers": 5, "active_24h": 3, "port": "51820"}
- xray: {"running": true}

## Сервер 78 — 78.17.19.43 (VM-379167)

- Система: Ubuntu 24.04.5 LTS, ядро 6.8.0-139-generic; CPU: 2; RAM: 1.9 ГБ (свободно 857.0 МБ); нагрузка 0.49, 0.64, 0.67
- Диски: / 34.5 ГБ из 57.1 ГБ (60%); /boot 116.6 МБ из 880.4 МБ (13%); /boot/efi 6.1 МБ из 104.3 МБ (5%)
- Снимок: 2026-10-05T13:37:30+0000

### Сервисы

| Сервис | Состояние | Порты | Память | Папка | Описание |
|---|---|---|---|---|---|
| agent-hub | active/running | 3495 | 2.1 МБ | /opt/agent-hub | Vovan Claude - агентная система (веб поверх Claude Code) |
| auth-gateway | active/running | 3481 | 4.1 МБ | /home/claude/auth-gateway | Auth Gateway Service |
| beaver-api | active/running | 3701 | 2.7 МБ | /home/claude/apps/beaver | Beaver API (HTTP, вход и статика) |
| beaver-realtime | active/running | 3702 | 25.7 МБ | /home/claude/apps/beaver | Beaver Realtime (WebSocket, такт мира) |
| blenderq | active/running | 3520 | 3.1 МБ | /home/claude/blenderq | Blender job queue (agent on owner PC pulls jobs over HTTPS) |
| casting-engine | active/running | 3503 | 24.5 МБ | /home/claude/apps/casting-engine | Casting opportunities monitoring engine for Valeria Kolyagina |
| docker | active/running | 5433, 6380, 7777 | 49.3 МБ | — | Docker Application Container Engine |
| drop | active/running | 3530 | 2.1 МБ | — | Drop - simplest file upload for Vovan |
| eeklera-admin | active/running | 3505 | 12.7 МБ | /home/claude/apps/eeklera-admin | EEKLERA admin — кабинет Валерии Колягиной |
| eeklera-analytics | active/running | 3610 | 1.8 МБ | /home/claude/apps/eeklera-analytics | EEKLERA analytics (self-hosted stats for eeklera.online) |
| eeklera-chat | active/running | 3011 | 2.9 МБ | /var/www/eeklera_site/chat | EEKLERA Team Chat Backend |
| eeklera-inquiries | active/running | 3504 | 2.0 МБ | /home/claude/apps/eeklera-inquiries | EEKLERA spheres — inquiry form backend (acting/modeling/streaming) |
| eeklera-sub-bot | active/running | — | 13.7 МБ | /opt/eeklera-sub-bot | EEKLERA Subscription Bot (Telegram private channel sales) |
| exchange | active/running | 3497 | 2.2 МБ | /home/claude/exchange | Exchange - file/chat drop between Vovan and Claude |
| fail2ban | active/running | — | 42.9 МБ | — | Fail2Ban Service |
| gate | active/running | 3480 | 5.5 МБ | /home/claude/gate | GATE — WireGuard VPN management panel |
| jarvis | active/running | 7070 | 2.1 МБ | /opt/jarvis | JARVIS — обзорная панель сервера |
| kabluk | active/running | 8091 | 63.3 МБ | /data/kabluk/current | Kabluk game |
| mediamtx | active/running | 1935, 8000, 8001, 8189, 8554, 8888, 8889, 8890, 8892, 8892 | 25.9 МБ | /opt/mediamtx | MediaMTX streaming ingest server (Lera stream relay) |
| modbot | active/running | 3485 | 10.0 МБ | /home/claude/modbot | ModBot - Twitch moderator bots site |
| nginx | active/running | 80, 443, 7443 | 11.0 МБ | — | A high performance web server and a reverse proxy server |
| pomoshnik-bot | active/running | — | 12.9 МБ | /opt/pomoshnik-bot | Помощник — Personal AI Telegram Bot |
| sentra-api | active/running | 3600 | 25.0 МБ | /home/claude/apps/sentra | Sentra API |
| sentra-worker | active/running | — | 46.3 МБ | /home/claude/apps/sentra | Sentra worker (авто-подключение чатов) |
| sentra2-api | active/running | 3601 | 12.5 МБ | /home/claude/apps/sentra2 | Sentra2 API (rebuild) |
| srv-watch | activating/start | — | 1.3 МБ | — | Сторож сервера (srv-watch) |
| strike | active/running | 3498 | 2.2 МБ | /home/claude/strike | Strike - маленький FPS-мультиплеер для друзей |
| stunnel4 | active/running | — | 3.2 МБ | — | LSB: Start or stop stunnel 4.x (TLS tunnel for network daemons) |
| video2md-cloud | active/running | 3515 | 3.5 МБ | /opt/video2md-cloud | Video2MD Cloud (vovan20.ru/admin/video2md) |
| webos | active/running | 3502 | 2.1 МБ | /home/claude/apps/webos | VOVAN OS — web desktop admin shell |
| wstunnel | active/running | 8087 | 4.3 МБ | — | wstunnel (WireGuard внутри HTTPS — обход фильтрации по типу трафика) |
| xray | active/running | 2053 | 17.4 МБ | — | Xray Service |

### Домены и маршруты (nginx)

**agents.vovan20.ru**
- `= /__auth` → сервис **auth-gateway** (:3481)
- `/` → порт 3456 ⚠ никто не слушает 🔒

**claw.vovan20.ru**

**cools1s.online, www.cools1s.online**
- `/` → порт 3001 ⚠ никто не слушает

**cools1s.ru, www.cools1s.ru** — корень `/var/www/cools1s`
- `/` → статика
- `= /roulette` → ответ 302 /wheel.html
- `= /wheel.html` → статика

**213.148.25.57, _**
- `/city` → порт 3457 ⚠ никто не слушает 🔒
- `/api/mb/` → порт 3457 ⚠ никто не слушает 🔒
- `/dl-***/` → файлы /srv/lera-dl/dl-***/ 🔒
- `/` → порт 3457 ⚠ никто не слушает 🔒
- `/orion/` → порт 3459 ⚠ никто не слушает
- `/commons/` → порт 3460 ⚠ никто не слушает

**eeklera.online** — корень `/var/www/eeklera_new`
- `= /yandex_d00ad3613ce129ae.html` → файлы /var/www/eeklera_new
- `= /yandex_6e058bae072a1cd5.html` → файлы /var/www/eeklera_site
- `= /stats/collect` → сервис **eeklera-analytics** (:3610)
- `^~ /stats` → сервис **eeklera-analytics** (:3610) 🔒
- `= /v2` → ответ 301 /v2/ 🔒
- `^~ /v2/` → файлы /var/www/eeklera_v2/ 🔒
- `^~ /q/` → порт 8090 ⚠ никто не слушает
- `^~ /app/api/` → сервис **mediamtx** (:8000)
- `^~ /app/ws/` → сервис **mediamtx** (:8000)
- `^~ /app/uploads/` → файлы /opt/lera-app/uploads/
- `^~ /app/assets/` → файлы /opt/lera-app/frontend/dist/assets/
- `= /wheel` → ответ 301 /wheel/
- `^~ /wheel/` → файлы /opt/lera-app/wheel-site/
- `= /party` → ответ 301 /party/
- `^~ /party/` → файлы /opt/lera-app/wheel-site/
- `~ ^/mafia(/.*)?$` → файлы /opt/lera-app/mafia-landing/index.html
- `= /demo` → ответ 301 /demo/
- `^~ /demo/` → файлы /opt/lera-app/demo-landing/
- `^~ /beta/assets/` → файлы /opt/lera-app/frontend-v2/dist/assets/
- `^~ /beta/` → файлы /opt/lera-app/frontend-v2/dist/
- `= /app` → ответ 301 /app/$is_args$args
- `^~ /app/` → файлы /opt/lera-app/frontend/dist/
- `= /admin` → ответ 301 /admin/
- `^~ /admin/` → сервис **eeklera-admin** (:3505)
- `^~ /casting` → статика
- `= /control` → файлы /var/www/eeklera_site/public/authorization
- `= /dashboard` → файлы /var/www/eeklera_site/public/authorization
- `= /pages` → файлы /var/www/eeklera_site/public/authorization
- `= /files` → файлы /var/www/eeklera_site/public/authorization
- `= /server` → файлы /var/www/eeklera_site/public/authorization
- `= /team` → ответ 301 /chat/
- `= /authorization` → ответ 301 /authorization/
- `^~ /authorization/` → файлы /var/www/eeklera_site/public/authorization/
- `= /chat` → ответ 301 /chat/
- `^~ /chat/` → файлы /var/www/eeklera_site/public
- `^~ /content/` → файлы /var/www/eeklera_site/content/
- `^~ /assets/` → файлы /var/www/eeklera_new/assets/
- `^~ /api/chat/` → сервис **eeklera-chat** (:3011)
- `= /api/pay/webhook` → сервис **mediamtx** (:8000)
- `^~ /spheres/api/` → сервис **eeklera-inquiries** (:3504)
- `/api/` → порт 3010 ⚠ никто не слушает
- `= /join` → ответ 301 /join/
- `^~ /join/` → статика
- `/` → статика
- `~ \.html$` → ответ 301 /$1$2

**eeklera.online, www.eeklera.online**
- `= /yandex_6e058bae072a1cd5.html` → файлы /var/www/eeklera_site
- `/` → ответ 301 https://eeklera.online$request_uri

**_** 🔒 вход
- `/` → сервис **jarvis** (:7070)

**kabluk.78-17-19-43.sslip.io**
- `/` → ответ 301 https://$host$request_uri

**kabluk.78-17-19-43.sslip.io**
- `/` → сервис **kabluk** (:8091)

**kursis.ru, www.kursis.ru** — корень `/var/www/cools1s`
- `/` → статика

**vovan20.ru, www.vovan20.ru**
- `= /__auth_panel` → сервис **auth-gateway** (:3481)
- `= /__auth` → сервис **auth-gateway** (:3481)
- `= /yandex_f595f91d0a6d4274.html` → файлы /var/www/studio
- `= /robots.txt` → файлы /var/www/studio
- `= /sitemap.xml` → файлы /var/www/studio
- `= /favicon.ico` → файлы /var/www/studio/assets/img/favicon.svg
- `= /favicon.svg` → файлы /var/www/studio/assets/img/favicon.svg
- `^~ /dl/` → файлы /var/www 🔒
- `= /graph` → ответ 301 /graph/
- `/graph/` → файлы /var/www/graph/ 🔒
- `/graph/game/` → сервис **gate** (:3480) 🔒
- `/graph/fly/` → сервис **gate** (:3480) 🔒
- `= /graph/live` → сервис **gate** (:3480) 🔒
- `= /gate` → ответ 301 /gate/
- `/gate/` → сервис **gate** (:3480) 🔒
- `= /modbot` → ответ 301 /modbot/
- `/modbot/` → сервис **modbot** (:3485) 🔒
- `@modbot_login` → ответ 302 /admin/
- `= /gate/u` → ответ 301 /gate/u/
- `^~ /gate/u/` → сервис **gate** (:3480)
- `= /ai` → ответ 301 /ai/
- `/ai/` → файлы /var/www/ai/
- `= /studio` → ответ 301 /studio/
- `= /studio/ai` → сервис **gate** (:3480)
- `= /studio/track` → сервис **gate** (:3480)
- `= /studio/statsdata` → сервис **gate** (:3480) 🔒
- `= /studio/stats` → сервис **gate** (:3480) 🔒
- `/studio/` → файлы /var/www/studio/
- `= /shopper` → ответ 301 /shopper/
- `/shopper/api/` → порт 3499 ⚠ никто не слушает 🔒
- `= /shopper/admin` → файлы /var/www/shopper/admin.html 🔒
- `/shopper/` → файлы /var/www/shopper/ 🔒
- `= /3d` → ответ 301 /3d/
- `/3d/` → файлы /var/www/3d/
- `= /hub` → ответ 301 /portal/
- `/hub/` → ответ 301 /portal/
- `= /portal` → ответ 301 /portal/
- `/portal/` → сервис **auth-gateway** (:3481)
- `/status/` → файлы /home/claude/status-app/
- `= /jarvis` → ответ 301 /jarvis/
- `^~ /jarvis/` → сервис **jarvis** (:7070) 🔒
- `= /admin` → ответ 301 /admin/
- `/admin/` → сервис **auth-gateway** (:3481)
- `= /sentra` → ответ 301 /sentra/app
- `= /chatguard` → ответ 301 /chatguard/app
- `/chatguard/internal/` → ответ 403
- `/chatguard/` → сервис **sentra-api** (:3600)
- `/beaver/ws` → сервис **beaver-realtime** (:3702)
- `/beaver/` → сервис **beaver-api** (:3701)
- `/sentra2/internal/` → ответ 403
- `/sentra2/` → сервис **sentra2-api** (:3601)
- `/sentra/internal/` → ответ 403
- `/sentra/` → сервис **sentra-api** (:3600)
- `= /bot` → ответ 301 /bot/
- `/bot/` → порт 3470 ⚠ никто не слушает 🔒
- `= /api/auth/sso` → порт 3001 ⚠ никто не слушает 🔒
- `= /panel` → порт 3001 ⚠ никто не слушает 🔒
- `@admin_login` → ответ 302 /admin/
- `/api/auth/login` → порт 3001 ⚠ никто не слушает
- `/api/` → порт 3001 ⚠ никто не слушает
- `= /team` → ответ 301 /team/
- `/team/` → порт 3492 ⚠ никто не слушает 🔒
- `= /exchange` → ответ 301 /exchange/
- `/bf2f49708c138f52` → сервис **wstunnel** (:8087)
- `/drop9k2/` → сервис **drop** (:3530)
- `/eeklera/` → статика
- `= /eeklera` → ответ 301 https://os.eeklera.online/
- `/blender/` → сервис **blenderq** (:3520)
- `/exchange/` → сервис **exchange** (:3497) 🔒
- `= /strike` → ответ 301 /strike/
- `/strike/` → сервис **strike** (:3498)
- `= /admin/forge` → ответ 301 /admin/forge/
- `/admin/forge/` → порт 3499 ⚠ никто не слушает 🔒
- `= /admin/trends` → ответ 301 /admin/trends/
- `/admin/trends/` → порт 3500 ⚠ никто не слушает 🔒
- `= /admin/backup` → ответ 301 /admin/backup/
- `/admin/backup/` → порт 3900 ⚠ никто не слушает 🔒
- `/ab18f79705e9d07cca1b648685dd6a9ac97fd4d960c12683` → порт 3901 ⚠ никто не слушает
- `/admin/dl/` → файлы /downloads/ 🔒
- `= /admin/os` → ответ 301 /admin/os/
- `/admin/os/` → сервис **webos** (:3502) 🔒
- `= /admin/os/linux2vnc` → ответ 301 /admin/os/linux2vnc/
- `= /websockify` → порт 6080 ⚠ никто не слушает 🔒
- `/admin/os/linux2vnc/` → порт 6080 ⚠ никто не слушает 🔒
- `= /admin/os/linux2vnc-audio` → ответ 301 /admin/os/linux2vnc-audio/
- `/admin/os/linux2vnc-audio/` → порт 4715 ⚠ никто не слушает 🔒
- `= /linux` → ответ 301 /linux/
- `/linux/` → порт 3510 ⚠ никто не слушает
- `= /tasks` → ответ 301 /tasks/
- `/tasks/` → порт 3490 ⚠ никто не слушает 🔒
- `= /app` → ответ 301 /app/$is_args$args
- `^~ /app/api/` → порт 8100 ⚠ никто не слушает
- `^~ /app/ws/` → порт 8100 ⚠ никто не слушает
- `^~ /app/uploads/` → файлы /opt/vovan-app/uploads/
- `~ \.m3u8$` → статика
- `~ \.ts$` → статика
- `= /app/index.html` → файлы /opt/vovan-app/frontend/dist/index.html
- `^~ /app/` → файлы /opt/vovan-app/frontend/dist/
- `= /` → статика
- `= /tg` → ответ 301 /tg/
- `^~ /tg/` → прокси → https://$tg_upstream/
- `/` → порт 3001 ⚠ никто не слушает
- `= /agents` → ответ 301 /agents/
- `/agents/` → порт 3486 ⚠ никто не слушает 🔒
- `@agents_login` → ответ 302 /admin/
- `/agents/t/0/` → порт 7681 ⚠ никто не слушает 🔒
- `/agents/t/1/` → порт 7682 ⚠ никто не слушает 🔒
- `/agents/t/2/` → порт 7683 ⚠ никто не слушает 🔒
- `/agents/t/3/` → порт 7684 ⚠ никто не слушает 🔒
- `/agents/t/4/` → порт 7685 ⚠ никто не слушает 🔒
- `/agents/t/5/` → порт 7686 ⚠ никто не слушает 🔒
- `/agents/t/6/` → порт 7687 ⚠ никто не слушает 🔒
- `= /claude` → ответ 301 /claude/
- `/claude/` → сервис **agent-hub** (:3495)
- `= /.well-known/assetlinks.json` → файлы /var/www/well-known/assetlinks.json
- `= /airrock` → ответ 301 /airrock/
- `/airrock/` → файлы /opt/bdc-airrock/dist/

### Docker

| Контейнер | Образ | Состояние | Порты |
|---|---|---|---|
| terraria | ghcr.io/pryaxis/tshock:latest | Up 4 days | 0.0.0.0:7777->7777/tcp, [::]:7777->7777/tcp, 7878/tcp |
| mtg | nineseconds/mtg:2 | Exited (0) 11 days ago |  |
| sentra-postgres | postgres:16-alpine | Up 7 days (healthy) | 127.0.0.1:5433->5432/tcp |
| sentra-redis | redis:7-alpine | Up 7 days (healthy) | 127.0.0.1:6380->6379/tcp |

### Таймеры (регулярные задачи)

- **eeklera-deploy.timer** → eeklera-deploy.service: Проверять git на новые коммиты раз в минуту; последний запуск Mon 2026-10-05 13:36:46 UTC
- **terraria-deploy.timer** → terraria-deploy.service: Terraria GitHub deploy every minute; последний запуск Mon 2026-10-05 13:36:46 UTC
- **kabluk-deploy.timer** → kabluk-deploy.service: Kabluk deploy poll; последний запуск Mon 2026-10-05 13:36:46 UTC
- **certbot.timer** → certbot.service: Run certbot twice daily; последний запуск Mon 2026-10-05 05:10:51 UTC
- **kabluk-backup.timer** → kabluk-backup.service: Kabluk daily DB backup; последний запуск Mon 2026-10-05 04:30:01 UTC
- **srv-watch.timer** → srv-watch.service: Сторож сервера каждые 5 минут; последний запуск Mon 2026-10-05 13:37:30 UTC

### Сертификаты HTTPS

- vovan20-vpn-rsa: до Dec  7 02:03:49 2026 GMT — vovan20.ru
- cools1s.ru: до Dec  6 15:16:33 2026 GMT — cools1s.ru, www.cools1s.ru
- eeklera.online: до Dec  6 15:16:50 2026 GMT — eeklera.online, www.eeklera.online
- vovan20.ru: до Dec  6 15:17:05 2026 GMT — vovan20.ru, www.vovan20.ru
- kabluk.78-17-19-43.sslip.io: до Dec 30 14:33:22 2026 GMT — kabluk.78-17-19-43.sslip.io
- agents.vovan20.ru: до Dec  6 15:16:01 2026 GMT — agents.vovan20.ru
- claw.vovan20.ru: до Dec  6 15:16:18 2026 GMT — claw.vovan20.ru

### Бэкапы

- `/data/backups`: 1 файлов, 668.0 КБ; последний `kabluk-before-bank-reset-20261002-181841.sqlite` (2026-10-02T18:18:42)
- `/data/kabluk/backups`: 40 файлов, 2.5 МБ; последний `db-20261005-043002-daily.sqlite.gz` (2026-10-05T04:30:02)

### VPN (только счётчики, без ключей)

- xray: {"running": true}
