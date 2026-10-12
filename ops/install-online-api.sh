#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ "$(id -u)" -eq 0 ] || { echo "Run as root." >&2; exit 1; }
BRANCH="$(git -C "$ROOT" branch --show-current)"
[ "$BRANCH" = main ] || { echo "Install only from main, current branch: $BRANCH" >&2; exit 1; }
[ -z "$(git -C "$ROOT" status --porcelain)" ] || { echo "Working tree must be clean." >&2; exit 1; }
API_ROOT=/opt/vovan-os-hub-api
RELEASE="$API_ROOT/releases/$(git -C "$ROOT" rev-parse --short=12 HEAD)"
STATE=/data/vovan-os-hub/state
UNIT=/etc/systemd/system/vovan-os-hub-api.service
DEPLOY_UNIT=/etc/systemd/system/vovan-os-hub-api-deploy.service
TIMER=/etc/systemd/system/vovan-os-hub-api-deploy.timer
BACKUP_UNIT=/etc/systemd/system/vovan-os-hub-api-backup.service
BACKUP_TIMER=/etc/systemd/system/vovan-os-hub-api-backup.timer
CONFIG=/etc/nginx/sites-enabled/vovan20.ru
CONFIG_REAL="$(readlink -f "$CONFIG")"
BACKUP="$CONFIG_REAL.codex-backup.$(date +%Y%m%d-%H%M%S)"
mkdir -p "$API_ROOT/releases" "$STATE" "$RELEASE"
install -m 0644 "$ROOT/hub/api/server.py" "$RELEASE/server.py"
python3 -m py_compile "$RELEASE/server.py"
chmod 0755 "$API_ROOT" "$API_ROOT/releases" "$RELEASE"
ln -sfn "$RELEASE" "$API_ROOT/current.next"
mv -Tf "$API_ROOT/current.next" "$API_ROOT/current"
chown -R root:root "$API_ROOT"
chown www-data:www-data "$STATE"
chmod 0750 "$STATE"

install -m 0644 "$ROOT/ops/vovan-os-hub-api.service" "$UNIT"
install -m 0755 "$ROOT/ops/vovan-os-hub-api-deploy.sh" /usr/local/sbin/vovan-os-hub-api-deploy
install -m 0644 "$ROOT/ops/vovan-os-hub-api-deploy.service" "$DEPLOY_UNIT"
install -m 0644 "$ROOT/ops/vovan-os-hub-api-deploy.timer" "$TIMER"
install -m 0644 "$ROOT/ops/vovan-os-hub-api-backup.service" "$BACKUP_UNIT"
install -m 0644 "$ROOT/ops/vovan-os-hub-api-backup.timer" "$BACKUP_TIMER"
install -d -m 0755 /usr/local/lib/vovan-os
install -m 0644 "$ROOT/ops/backup-hub-api.py" /usr/local/lib/vovan-os/backup-hub-api.py
install -m 0755 "$ROOT/ops/rollback-hub-api.sh" /usr/local/sbin/vovan-os-hub-api-rollback
systemctl daemon-reload
systemctl enable --now vovan-os-hub-api.service
systemctl restart vovan-os-hub-api.service
systemctl enable --now vovan-os-hub-api-deploy.timer
systemctl enable --now vovan-os-hub-api-backup.timer
systemctl start vovan-os-hub-api-deploy.service
curl --fail --silent --show-error http://127.0.0.1:3980/health >/dev/null

if ! grep -q 'VOVAN OS online API' "$CONFIG_REAL"; then
    cp -a "$CONFIG_REAL" "$BACKUP"
    python3 - "$CONFIG_REAL" "$ROOT/ops/nginx-hub-api.location.conf" <<'PY'
import os, sys, tempfile
config, snippet_path = sys.argv[1:]
text = open(config, encoding="utf-8").read()
snippet = open(snippet_path, encoding="utf-8").read()
anchor = "    location ^~ /admin/hub/ {"
if text.count(anchor) != 1:
    raise SystemExit("Expected exactly one /admin/hub location in Nginx config.")
fd, temp = tempfile.mkstemp(prefix=".vovan-os-hub-", dir=os.path.dirname(config))
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text.replace(anchor, snippet + anchor, 1))
    os.chmod(temp, os.stat(config).st_mode & 0o777)
    os.replace(temp, config)
finally:
    if os.path.exists(temp):
        os.unlink(temp)
PY
    if ! nginx -t; then
        cp -a "$BACKUP" "$CONFIG_REAL"
        echo "Nginx validation failed; original config restored." >&2
        exit 1
    fi
    if ! systemctl reload nginx; then
        cp -a "$BACKUP" "$CONFIG_REAL"
        nginx -t && systemctl reload nginx || true
        echo "Nginx reload failed; original config restored." >&2
        exit 1
    fi
fi

echo "Hub API health:"
curl --fail --silent --show-error http://127.0.0.1:3980/health
echo
echo "Service and update timer:"
systemctl --no-pager --full status vovan-os-hub-api.service vovan-os-hub-api-deploy.timer | sed -n '1,22p'
echo "Nginx config validated. Backup: ${BACKUP}"

