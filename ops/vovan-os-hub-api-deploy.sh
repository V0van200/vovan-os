#!/usr/bin/env bash
set -euo pipefail
BASE=/data/vovan-os-hub/api
REPO=/data/vovan-os-hub/repo.git
REL=$BASE/releases
LOG=$BASE/history.log
LIVE=/opt/vovan-os-hub-api
mkdir -p "$REL"
exec 9>"$BASE/.lock"
flock -n 9 || exit 0
sha=$(git --git-dir="$REPO" rev-parse refs/heads/main 2>/dev/null || true)
[ -n "$sha" ] || { echo "$(date -Is) FAIL no main ref" >> "$LOG"; exit 1; }
seen=$(cat "$BASE/seen" 2>/dev/null || true)
[ "$seen" = "$sha" ] && exit 0
name="$(date +%Y%m%d-%H%M%S)-${sha:0:7}"
tmp="$REL/.tmp-$name"
rm -rf "$tmp"
mkdir -p "$tmp"
if ! git --git-dir="$REPO" archive "$sha" hub/api | tar -x -C "$tmp" --strip-components=2; then
  echo "$(date -Is) FAIL ${sha:0:10} archive" >> "$LOG"
  rm -rf "$tmp"
  exit 1
fi
if [ ! -s "$tmp/server.py" ] || ! /usr/bin/python3 -m py_compile "$tmp/server.py"; then
  echo "$(date -Is) FAIL ${sha:0:10} API source invalid" >> "$LOG"
  rm -rf "$tmp"
  exit 1
fi
chmod 755 "$tmp" "$tmp/server.py"
mv "$tmp" "$REL/$name"
previous=$(readlink -f "$LIVE/current" 2>/dev/null || true)
ln -sfn "$REL/$name" "$LIVE/current.next"
mv -Tf "$LIVE/current.next" "$LIVE/current"
if ! systemctl restart vovan-os-hub-api.service; then
  if [ -n "$previous" ]; then
    ln -sfn "$previous" "$LIVE/current.rollback"
    mv -Tf "$LIVE/current.rollback" "$LIVE/current"
    systemctl restart vovan-os-hub-api.service || true
  fi
  echo "$(date -Is) FAIL ${sha:0:10} service restart; rolled back" >> "$LOG"
  exit 1
fi
if ! curl --fail --silent --show-error --max-time 3 http://127.0.0.1:3980/health >/dev/null; then
  if [ -n "$previous" ]; then
    ln -sfn "$previous" "$LIVE/current.rollback"
    mv -Tf "$LIVE/current.rollback" "$LIVE/current"
    systemctl restart vovan-os-hub-api.service || true
  fi
  echo "$(date -Is) FAIL ${sha:0:10} health check; rolled back" >> "$LOG"
  exit 1
fi
echo "$sha" > "$BASE/seen"
echo "$(date -Is) OK ${sha:0:10} API deployed" >> "$LOG"
ls -1d "$REL"/2* 2>/dev/null | sort | head -n -6 | xargs -r rm -rf

