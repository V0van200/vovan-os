# Lera Assistant

**Боты** · 📦 только GitHub — есть только в GitHub

Telegram-ассистент: Gemini, видео, Google, база знаний. На серверах не запущен.

## Ссылки

- https://github.com/V0van200/lera-assistant

## Репозитории GitHub

### lera-assistant

https://github.com/V0van200/lera-assistant · private · 72.8 МБ · Node.js / Telegram

Gemini, видео, Google, база знаний.

> # Lera Assistant — Telegram-бот-помощник Леры
> **Что это:** бот в Telegram (`bot.mjs`, Node.js), личный ассистент для EEKLERA. Работал от пользователя `orion`, папка `/home/orion/lera_assistant`.
> **Что умел:**
> - отвечать через Gemini (`gemini-flash-latest`) с поиском в интернете (Tavily);
> - **анализировать видео**, в том числе TikTok: `tools/gemini_video.mjs`, `tools/tiktok.mjs`;
> - работать с Google (Диск, Документы, Календарь): `tools/google.mjs`;
> - хранить базу знаний о Лере в `data/` (~840 файлов). Это та же база, что старый Obsidian-vault Леры, см. [lera-vault-old](../lera-vault-old): по аудиту синхронизировано 407 из 407 файлов;
> - пускать только разрешённых пользователей (`allowed_users`).
> **Состояние:** бэкап от 23.07.2026. `keys.json` (токен бота, ключи API) и Google-токены вырезаны — для запуска их нужно создать заново.
> *Файлы, в которых нашлись ключи или токены, в репозиторий не попали; если такие были — их список в `SECRETS_REMOVED.txt`.*
