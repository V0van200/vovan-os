# Помощник-бот

**Боты** · 🟢 работает — работает: pomoshnik-bot

Задачи для Claude Code из Telegram, голосовые, Google OAuth.

## Со слов владельца

- **Сейчас:** работает, владелец пользуется
- **Приоритет в хабе:** 2

## Ссылки

- https://github.com/V0van200/pomoshnik-bot

## Что запущено

| Сервис | Сервер | Состояние | Порты | Память |
|---|---|---|---|---|
| pomoshnik-bot | 78 | active | — | 12.9 МБ |

## Базы данных

| База | Сервер | Движок | Таблиц | Строк | Схема |
|---|---|---|---|---|---|
| /home/claude/apps/pomoshnik-bot/session.db | 78 | sqlite | 4 | 11 | [схема](../../docs/databases/78-home-claude-apps-pomoshnik-bot-session-db.md) |

## Репозитории GitHub

### pomoshnik-bot

https://github.com/V0van200/pomoshnik-bot · private · 1.8 МБ · Python / Telegram

Задачи Claude Code, голосовые, Google OAuth.

> # Помощник — персональный ИИ-агент в Telegram на базе Claude Code
> **Что это:** Telegram-бот (`bot.py`, Python, python-telegram-bot), через который Вован (@Vovann200) управлял Claude Code на сервере прямо из Telegram. Вторым пользователем была EEKLERA (@eeklera_men) — она давала задачи по сайту.
> **Что умел:**
> - принимать текст, **голосовые** и файлы и передавать их Claude Code как задачи;
> - отвечать с кнопками (inline-клавиатура), проверять права (`permissions.json`, `is_allowed`);
> - работать с Google через OAuth ***
> - `inbox/`, `relay_inbox.txt` — входящие задачи; `vault/` — заметки.
> **Состояние:** бэкап от 23.07.2026. Вырезано: `.env`, `session.db` (сессия Telegram), Google-токены и credentials — для запуска нужно авторизоваться заново.
> *Файлы, в которых нашлись ключи или токены, в репозиторий не попали; если такие были — их список в `SECRETS_REMOVED.txt`.*

## Папки на серверах

- `78:/home/claude/apps/pomoshnik-bot` — 720.8 МБ, 63 файлов, изменена 2026-10-05, есть .env (значения не читались)
- ⚪ `78:/opt/pomoshnik-bot` — не найдена при сканировании
