#!/usr/bin/env bash
# Проверка перед коммитом: нет ли секретов и файлов баз. Установка: ln -s ../../scripts/check-secrets.sh .git/hooks/pre-commit
set -e
files=$(git diff --cached --name-only --diff-filter=ACM)
[ -z "$files" ] && exit 0
bad=0
for f in $files; do
  case "$f" in *.sqlite|*.sqlite3|*.db|*.sql|*.sql.gz|*.dump|*.pem|*.key|.env|.env.*|*/.env) echo "✖ запрещённый тип файла: $f"; bad=1;; esac
  [ -f "$f" ] || continue
  if grep -nIE '[0-9]{8,10}:[A-Za-z0-9_-]{30,}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[abp]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,}' "$f" >/dev/null 2>&1; then
    echo "✖ похоже на секрет в $f:"; grep -nIoE '.{0,20}([0-9]{8,10}:[A-Za-z0-9_-]{6}|sk-[A-Za-z0-9_-]{6}|ghp_[A-Za-z0-9]{6}|github_pat_[A-Za-z0-9_]{6}|AKIA[0-9A-Z]{6}|-----BEGIN [A-Z ]*PRIVATE KEY|xox[abp]-|AIza[0-9A-Za-z_-]{6})' "$f" | head -3; bad=1
  fi
done
[ $bad = 0 ] || { echo "Коммит остановлен. Убери секрет/файл базы (docs/SECURITY.md)."; exit 1; }
