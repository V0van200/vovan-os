#!/usr/bin/env bash
set -euo pipefail
LIVE=/opt/vovan-os-hub-api
current=$(readlink -f "$LIVE/current" 2>/dev/null || true)
target=${1:-}
if [ -z "$target" ]; then
  target=$(find /data/vovan-os-hub/api/releases -mindepth 1 -maxdepth 1 -type d -name '2*' -print | sort | grep -Fvx "$current" | tail -1 || true)
fi
[ -n "$target" ] && [ -f "$target/server.py" ] || { echo "No valid API release found." >&2; exit 1; }
ln -sfn "$target" "$LIVE/current.rollback"
mv -Tf "$LIVE/current.rollback" "$LIVE/current"
if ! systemctl restart vovan-os-hub-api.service || ! curl --fail --silent --show-error --max-time 3 http://127.0.0.1:3980/health >/dev/null; then
  if [ -n "$current" ]; then ln -sfn "$current" "$LIVE/current.rollback"; mv -Tf "$LIVE/current.rollback" "$LIVE/current"; systemctl restart vovan-os-hub-api.service || true; fi
  echo "Rollback health check failed; previous current release restored." >&2
  exit 1
fi
echo "VOVAN OS Hub API rolled back to $target"

