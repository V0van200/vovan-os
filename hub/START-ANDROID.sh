#!/data/data/com.termux/files/usr/bin/bash
set -eu
cd -- "$(dirname -- "$0")"
if ! command -v python >/dev/null 2>&1; then
  echo 'Установите Python: pkg install python'
  exit 1
fi
printf '\nVOVAN OS: откройте http://127.0.0.1:8090 в браузере.\nОставьте Termux работающим. Остановка: Ctrl+C.\n\n'
exec python start.py --no-browser --port 8090
