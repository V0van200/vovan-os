# EEKLERA OS + база знаний /neuro

**Сайты** · 🌐 сайт онлайн — сайт отдаётся: os.eeklera.online, os.vovan20.ru

Рабочий стол EEKLERA OS и зашифрованная база знаний о Лере (/neuro: файлы как в Obsidian + 3D-нейросеть). Собирается из Obsidian-vault в GitHub Eeklera_file. Работает в России без VPN.

## Ссылки

- https://os.eeklera.online
- https://os.vovan20.ru
- https://github.com/V0van200/Eeklera_file
- https://github.com/V0van200/lera-vault-old
- https://github.com/V0van200/eeklera-obsidian
- https://github.com/V0van200/obsidian-systems

## Домены

- **os.eeklera.online**
  - `= /neuro` → 301 /neuro/ (сервер 198)
  - `^~ /neuro/` → /var/www/eeklera-neuro/ (сервер 198)
  - `/` → статика (сервер 198)
  - `~* \.(css|js|html)$` → статика (сервер 198)
  - `= /img/desktop.png` → 403 (сервер 198)
  - `~* \.(jpg|jpeg|png|webp|svg|woff2)$` → статика (сервер 198)
  - `~* \.(mp3|m4a|ogg|wav)$` → статика (сервер 198)
  - `(корень)` → /var/www/eeklera-os (сервер 198)
  - `/` → 301 https://$host$request_uri (сервер 198)
- **os.vovan20.ru**
  - `= /neuro` → 301 /neuro/ (сервер 198)
  - `^~ /neuro/` → /var/www/eeklera-neuro/ (сервер 198)
  - `/` → статика (сервер 198)
  - `~* \.(css|js|html)$` → статика (сервер 198)
  - `= /img/desktop.png` → 403 (сервер 198)
  - `~* \.(jpg|jpeg|png|webp|svg|woff2)$` → статика (сервер 198)
  - `~* \.(mp3|m4a|ogg|wav)$` → статика (сервер 198)
  - `(корень)` → /var/www/eeklera-os (сервер 198)
  - `/` → 301 https://$host$request_uri (сервер 198)

## Репозитории GitHub

### Eeklera_file

https://github.com/V0van200/Eeklera_file · private · 291.1 МБ · Код + медиа + архив ПК

Obsidian, video2md, редизайн и codex.

> # EEKLERA — архив (восстановлено 23.09.2026)
> Данные, вытащенные с VPS 78.17.19.43 (копия папки codex с ПК от 22.09.2026).
> | Папка | Что это |
> | `obsidian/` | хранилище Obsidian: раздел EEKLERA (заметки, моменты, мысли, досье, кадры), `.obsidian` с плагинами и настройками, `.smart-env` |
> | `video2md/` | проект конвейера video2md: `results/` (кадры, расшифровки, хроники), `export/`, `neuro/`, `neuro-web/`, промпты, код |
> | `eeklera_redesign/` | новый сайт (редизайн), как лежал на сервере — открывался по https://eeklera.online/redesign/ |
> | `eeklera-new/` | та же сборка с ПК, плюс `_work/` (исходник AI-портрета, промпт, проверки) |
> | `_redesign/` | бриф для GPT: факты, страницы, дизайн, промпты по этапам, макеты |
> Сайт открывается без сервера: `eeklera_redesign/index.html` двойным кликом.
> ## `codex/` — полная копия папки codex с ПК (22.09.2026)
> Всё содержимое: `Eeklera`, `Проекты`, `Программы`, `Blender`, `claude-data`, `Для GPT`, `Скрипты установки`,
> `EEKLERA-obsidian.zip` (+ `.bak`).
> Не залито:
> - `Программы/LM Studio` и файлы самой программы Obsidian (`Obsidi

### lera-vault-old

https://github.com/V0van200/lera-vault-old · private · 72.8 МБ · Markdown / Obsidian

Старый vault и отчёт качества заметок.

> # Старая база Obsidian о Лере (EEKLERA VAULT)
> **Что это:** первая версия базы знаний Obsidian о Валерии Колягиной (EEKLERA), до нынешней большой базы с моментами, мыслями и портретом. Лежала на сервере в `_archive/lera-vault`.
> **Что внутри:**
> - ~440 заметок в `EEKLERA/`: профиль «Валерия Колягина», музыка, роли и другие разделы (94 папки);
> - `EEKLERA_VAULT_AUDIT.md` — полный аудит базы:
> - 42% заметок с содержанием, 58% — только шапка;
> - 30+ пар дублей;
> - синхронизация с `lera_assistant/data` — 407 из 407.
> **Связь:** этой базой пользовался бот [lera-assistant](../lera-assistant). Нынешняя база живёт в Obsidian на телефоне (`EEKLERA-obsidian`) и собирается программой video2md.
> Бэкап от 23.07.2026. Файл `lera-vault-eeklera.zip` (205 МБ) сюда не влез — он больше лимита GitHub в 100 МБ.
> *Файлы, в которых нашлись ключи или токены, в репозиторий не попали; если такие были — их список в `SECRETS_REMOVED.txt`.*

### eeklera-obsidian

https://github.com/V0van200/eeklera-obsidian · private · — · Пустой репозиторий

GitHub size = 0; содержимое не получено.

### obsidian-systems

https://github.com/V0van200/obsidian-systems · private · — · Пустой репозиторий

GitHub size = 0; содержимое не получено.

## Папки на серверах

- `198:/var/www/eeklera-os` — 203.0 МБ, 93 файлов, изменена 2026-09-22
- `198:/var/www/eeklera-neuro` — 503.4 МБ, 1440 файлов, изменена 2026-10-02
- `198:/root/gh/vault` — 131.1 МБ, 3095 файлов, изменена 2026-10-02
- `198:/root/gh/uzly` — 1.9 МБ, 16 файлов, изменена 2026-09-24
- `78:/var/www/eeklera-os` — 19.8 МБ, 78 файлов, изменена 2026-09-15
- `78:/var/www/eeklera-neuro` — 17.8 МБ, 599 файлов, изменена 2026-09-22
- `78:/home/claude/eeklera-neuro-web` — 17.8 МБ, 601 файлов, изменена 2026-09-22
- `78:/home/claude/apps/eeklera-os` — 28.7 МБ, 175 файлов, изменена 2026-09-21
- `78:/root/obsidian` — 34.0 МБ, 729 файлов, изменена 2026-05-19
