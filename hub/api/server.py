#!/usr/bin/env python3
"""Small authenticated-by-front-proxy API for the online VOVAN OS hub."""
import hashlib, ipaddress, json, os, re, signal, socket, sqlite3, ssl, threading, time, uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote, parse_qs

HOST = os.environ.get("HUB_API_HOST", "127.0.0.1")
PORT = int(os.environ.get("HUB_API_PORT", "3980"))
SNAPSHOT = Path(os.environ.get("HUB_API_SNAPSHOT", "/data/vovan-os-hub/live/snapshot.json"))
PROJECTS = Path(os.environ.get("HUB_API_PROJECTS", "/data/vovan-os-hub/live/projects.json"))
DB = Path(os.environ.get("HUB_API_DB", "/data/vovan-os-hub/state/hub.sqlite3"))
DOMAIN_MAP = Path(os.environ.get("HUB_API_DOMAIN_MAP", "/var/www/vovan-os-hub/domain-map.json"))
DOMAIN_CHECK_INTERVAL = max(30, int(os.environ.get("HUB_API_DOMAIN_CHECK_INTERVAL", "60")))
DOMAIN_CHECK_TIMEOUT = max(1, min(8, int(os.environ.get("HUB_API_DOMAIN_CHECK_TIMEOUT", "4"))))
MAX_BODY = 256 * 1024
MAX_CLIENTS = int(os.environ.get("HUB_API_MAX_SSE_CLIENTS", "30"))
CHANGE_LIMIT = 1000
stopping = threading.Event()
clients = threading.BoundedSemaphore(MAX_CLIENTS)
domain_health_lock = threading.Lock()
domain_health = {"ok": True, "status": "checking", "updated_at": None, "domains": []}
PROJECT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,99}$")
PREF_KEYS = {"server", "compact", "appearance", "vl-open", "nav", "home-widgets", "project-filters", "profile"}

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=5)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    return db

def init_db():
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY, value_json TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS project_meta (
                project_id TEXT PRIMARY KEY, status TEXT, visible INTEGER NOT NULL DEFAULT 1,
                favorite INTEGER NOT NULL DEFAULT 0, next_step TEXT NOT NULL DEFAULT '',
                note TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY, project_id TEXT NOT NULL DEFAULT '', title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new', priority TEXT NOT NULL DEFAULT 'normal',
                details TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, event_key TEXT NOT NULL UNIQUE,
                occurred_at TEXT NOT NULL, category TEXT NOT NULL, severity TEXT NOT NULL,
                server_id TEXT NOT NULL DEFAULT '', project_id TEXT NOT NULL DEFAULT '',
                title TEXT NOT NULL, detail TEXT NOT NULL, before_json TEXT,
                after_json TEXT, next_step TEXT NOT NULL DEFAULT '', source TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS system_events_recent ON system_events(occurred_at DESC, id DESC);
            CREATE TABLE IF NOT EXISTS observer_state (
                id INTEGER PRIMARY KEY CHECK (id=1), generation_json TEXT NOT NULL,
                state_json TEXT NOT NULL, updated_at TEXT NOT NULL
            );
        """)
        db.commit()

def file_state(path):
    try:
        st = path.stat()
        return {"available": True, "updated_at": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"), "bytes": st.st_size}
    except OSError:
        return {"available": False, "updated_at": None, "bytes": None}

def source_generation():
    values = []
    for path in (SNAPSHOT, PROJECTS):
        try:
            st = path.stat()
            values.extend((st.st_mtime_ns, st.st_size))
        except OSError:
            values.extend((0, 0))
    return tuple(values)

def generation():
    with connect() as db:
        row = db.execute("SELECT COALESCE(MAX(id),0) AS latest FROM system_events").fetchone()
    return (*source_generation(), int(row["latest"]))

def read_preferences(db):
    return {row["key"]: json.loads(row["value_json"]) for row in db.execute("SELECT key,value_json FROM preferences")}

def read_tasks(db):
    return [dict(row) for row in db.execute("SELECT id,project_id,title,status,priority,details,created_at,updated_at FROM tasks ORDER BY created_at DESC")]

def record_event(db, event, source):
    key = hashlib.sha256((source + ":" + str(time.time_ns()) + ":" + str(uuid.uuid4())).encode()).hexdigest()
    db.execute("""INSERT INTO system_events
        (event_key,occurred_at,category,severity,server_id,project_id,title,detail,before_json,after_json,next_step,source)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (key, utc_now(), event["category"], event.get("severity", "ok"), event.get("server_id", ""), event.get("project_id", ""),
         event["title"], event.get("detail", ""), json.dumps(event.get("before"), ensure_ascii=False),
         json.dumps(event.get("after"), ensure_ascii=False), event.get("next_step", ""), source))
    db.execute("DELETE FROM system_events WHERE id NOT IN (SELECT id FROM system_events ORDER BY id DESC LIMIT ?)", (CHANGE_LIMIT,))

def json_file(path):
    try:
        with path.open(encoding="utf-8") as stream:
            value = json.load(stream)
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None

def domain_targets(document):
    """Read the fixed domain allowlist; never accept probe targets from a request."""
    if not isinstance(document, dict):
        return []
    web_names = {str(name).lower().rstrip(".") for name in document.get("https_names", []) if isinstance(name, str)}
    result = {}
    for record in document.get("records", []):
        if not isinstance(record, dict):
            continue
        expected_ip = record.get("ip")
        try:
            if not ipaddress.ip_address(expected_ip).is_global:
                expected_ip = None
        except (ValueError, TypeError):
            expected_ip = None
        for raw_name in record.get("names", []):
            if not isinstance(raw_name, str):
                continue
            name = raw_name.lower().rstrip(".")
            if re.fullmatch(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", name):
                result[name] = {"name": name, "expected_ip": expected_ip, "https": name in web_names}
    for raw_name in document.get("unresolved", []):
        if not isinstance(raw_name, str):
            continue
        name = raw_name.lower().rstrip(".")
        if re.fullmatch(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", name):
            result.setdefault(name, {"name": name, "expected_ip": None, "https": False})
    return [result[key] for key in sorted(result)]

def resolve_public_ips(host, timeout=DOMAIN_CHECK_TIMEOUT):
    # The names come only from the checked-in domain inventory. The result is
    # still validated before any connection is made to avoid probing private IPs.
    try:
        answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        if exc.errno == socket.EAI_NONAME:
            return []
        raise
    ips = set()
    for answer in answers:
        try:
            address = answer[4][0].split("%", 1)[0]
            parsed = ipaddress.ip_address(address)
            if parsed.is_global:
                ips.add(str(parsed))
        except (ValueError, IndexError, TypeError):
            continue
    return sorted(ips)

def probe_https(host, ip, timeout=DOMAIN_CHECK_TIMEOUT):
    """Validate TLS and make one bounded GET to /, connected only to the expected public IP."""
    try:
        address = ipaddress.ip_address(ip)
        if not address.is_global:
            return {"tls": {"status": "not_checked", "reason": "Адрес не является публичным"},
                    "http": {"status": "not_checked", "code": None}}
        raw = socket.create_connection((str(address), 443), timeout=timeout)
        with ssl.create_default_context().wrap_socket(raw, server_hostname=host) as connection:
            connection.settimeout(timeout)
            certificate = connection.getpeercert()
            expires = certificate.get("notAfter")
            expires_at = datetime.fromtimestamp(ssl.cert_time_to_seconds(expires), timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z") if expires else None
            days_left = (datetime.fromtimestamp(ssl.cert_time_to_seconds(expires), timezone.utc) - datetime.now(timezone.utc)).days if expires else None
            tls_status = "expired" if days_left is not None and days_left < 0 else "expiring" if days_left is not None and days_left <= 30 else "valid"
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: VovanHub-DomainCheck/1.0\r\nAccept: */*\r\nConnection: close\r\n\r\n".encode("ascii")
            connection.sendall(request)
            try:
                with connection.makefile("rb") as stream:
                    line = stream.readline(256).decode("latin-1", "replace").strip()
            except (OSError, TimeoutError):
                line = ""
            match = re.match(r"^HTTP/\d(?:\.\d)?\s+(\d{3})(?:\s|$)", line)
            code = int(match.group(1)) if match else None
            http_status = "protected" if code in (401, 403) else "available" if code is not None and 200 <= code < 400 else "client_error" if code is not None and 400 <= code < 500 else "server_error" if code is not None and code >= 500 else "no_response"
            return {"tls": {"status": tls_status, "expires_at": expires_at, "days_left": days_left, "reason": ""},
                    "http": {"status": http_status, "code": code}}
    except ssl.SSLCertVerificationError as exc:
        code = getattr(exc, "verify_code", None)
        reason = "Сертификат истёк" if code == 10 else "Домен не совпадает с сертификатом" if code == 62 else "Сертификат не подтверждён"
        return {"tls": {"status": "invalid", "expires_at": None, "days_left": None, "reason": reason},
                "http": {"status": "not_checked", "code": None}}
    except (OSError, ssl.SSLError, ValueError, TimeoutError):
        return {"tls": {"status": "unreachable", "expires_at": None, "days_left": None, "reason": "Не удалось установить HTTPS-соединение"},
                "http": {"status": "unavailable", "code": None}}

def check_domain_target(target, resolver=resolve_public_ips, probe=probe_https):
    name, expected = target["name"], target.get("expected_ip")
    try:
        resolved = resolver(name)
        dns_error = False
    except (OSError, socket.gaierror, TimeoutError):
        resolved, dns_error = [], True
    if dns_error:
        dns_status = "unavailable"
    elif expected and expected in resolved:
        dns_status = "ok"
    elif expected:
        dns_status = "mismatch" if resolved else "missing"
    else:
        dns_status = "unexpected_record" if resolved else "not_found"
    result = {"name": name, "expected_ip": expected, "resolved_ips": resolved, "dns": {"status": dns_status},
              "tls": {"status": "not_checked", "expires_at": None, "days_left": None, "reason": ""},
              "http": {"status": "not_checked", "code": None}}
    if target.get("https") and dns_status == "ok":
        result.update(probe(name, expected))
    return result

def refresh_domain_health():
    document = json_file(DOMAIN_MAP)
    if document is None:
        state = {"ok": False, "status": "unavailable", "updated_at": utc_now(), "domains": []}
    else:
        targets = domain_targets(document)
        with ThreadPoolExecutor(max_workers=min(8, max(1, len(targets)))) as pool:
            checked = list(pool.map(check_domain_target, targets))
        state = {"ok": True, "status": "ready", "updated_at": utc_now(), "domains": checked}
    with domain_health_lock:
        domain_health.clear()
        domain_health.update(state)
    return state

def observed_state(snapshot, projects):
    """Keep only stable, useful fields; volatile load and RAM do not become noisy events."""
    state = {"servers": {}, "services": {}, "containers": {}, "alerts": {}}
    for server_id, server in (snapshot.get("servers") or {}).items():
        if not isinstance(server, dict):
            continue
        collected = server.get("collected_at") or ""
        live = server.get("live") or {}
        stale = bool(live.get("stale"))
        if collected:
            try:
                dt = datetime.fromisoformat(collected.replace("Z", "+00:00"))
                stale = stale or (datetime.now(timezone.utc) - dt).total_seconds() > 180
            except (TypeError, ValueError):
                stale = bool(live.get("stale")) if live.get("stale") is not None else None
        elif live.get("stale") is None:
            stale = None
        state["servers"][str(server_id)] = {"stale": stale, "collected_at": collected}
        for service in server.get("services") or []:
            if isinstance(service, dict) and service.get("name"):
                key = f"{server_id}:{service['name']}"
                state["services"][key] = {"server": str(server_id), "name": str(service["name"]), "state": str(service.get("state") or "unknown")}
        for container in server.get("docker") or []:
            if isinstance(container, dict) and container.get("name"):
                key = f"{server_id}:{container['name']}"
                raw = str(container.get("status") or "unknown")
                normalized = "running" if raw.lower().startswith("up ") or raw.lower() == "up" else "exited" if raw.lower().startswith("exited") else raw
                state["containers"][key] = {"server": str(server_id), "name": str(container["name"]), "state": normalized}
    project_map = projects.get("projects") or {}
    if isinstance(project_map, dict):
        for project_id, project in project_map.items():
            if isinstance(project, dict):
                state["alerts"][str(project_id)] = sorted({str(item)[:300] for item in project.get("alerts", []) if item})
    return state

def transition_events(previous, current):
    events = []
    for server_id, now in current.get("servers", {}).items():
        old = previous.get("servers", {}).get(server_id)
        if old is None or old.get("stale") is None or now.get("stale") is None or old.get("stale") == now.get("stale"):
            continue
        status = "Нет свежей связи" if now["stale"] else "Связь восстановлена"
        events.append({"category": "server", "severity": "warning" if now["stale"] else "ok", "server_id": server_id,
                       "title": f"{status}: сервер {server_id}",
                       "detail": "Сборщик давно не присылал свежие данные." if now["stale"] else "Сборщик снова прислал актуальные данные.",
                       "before": old.get("stale"), "after": now.get("stale"),
                       "next_step": "Проверьте доступность сервера и сборщик данных." if now["stale"] else "Связь восстановилась; проверьте, не осталось ли связанных предупреждений."})
    for group, category, label in (("services", "service", "Сервис"), ("containers", "container", "Контейнер")):
        before = previous.get(group, {})
        after = current.get(group, {})
        for key in sorted(before.keys() & after.keys()):
            old, now = before[key], after[key]
            if old.get("state") == now.get("state"):
                continue
            down = now.get("state") not in {"active", "active/running", "running", "Up", "healthy"}
            events.append({"category": category, "severity": "warning" if down else "ok", "server_id": now.get("server", ""),
                           "title": f"{label} {now.get('name')} · {now.get('server')}: {old.get('state')} → {now.get('state')}",
                           "detail": "Состояние изменилось по данным серверной инвентаризации.",
                           "before": old.get("state"), "after": now.get("state"),
                           "next_step": "Откройте карточку сервера и проверьте журнал службы." if down else "Проверьте, что связанный проект снова отвечает."})
    for project_id, alerts in current.get("alerts", {}).items():
        before = set(previous.get("alerts", {}).get(project_id, []))
        after = set(alerts)
        for alert in sorted(after - before):
            events.append({"category": "project", "severity": "warning", "project_id": project_id,
                           "title": f"Новое предупреждение: {project_id}", "detail": alert,
                           "before": None, "after": alert, "next_step": "Проверьте источник данных и создайте задачу, если требуется исправление."})
        for alert in sorted(before - after):
            events.append({"category": "project", "severity": "ok", "project_id": project_id,
                           "title": f"Предупреждение снято: {project_id}", "detail": alert,
                           "before": alert, "after": None, "next_step": "Убедитесь, что метрика или проверка действительно восстановлена."})
    return events

def observe_snapshot():
    """Persist transitions even when no one has the dashboard open."""
    current_generation = source_generation()
    with connect() as db:
        row = db.execute("SELECT generation_json FROM observer_state WHERE id=1").fetchone()
    same_generation = row is not None and row["generation_json"] == json.dumps(current_generation)
    if not same_generation:
        time.sleep(0.35)
        if source_generation() != current_generation:
            return  # The collector replaces two files in sequence; wait for a stable pair.
    snapshot, projects = json_file(SNAPSHOT), json_file(PROJECTS)
    if source_generation() != current_generation:
        return  # The collector replaces two files in sequence; wait for a stable pair.
    if snapshot is None or projects is None:
        return
    current_state = observed_state(snapshot, projects)
    generation_json = json.dumps(current_generation)
    state_json = json.dumps(current_state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    with connect() as db:
        row = db.execute("SELECT generation_json,state_json FROM observer_state WHERE id=1").fetchone()
        previous = json.loads(row["state_json"]) if row else None
        if row and row["generation_json"] == generation_json and row["state_json"] == state_json:
            return
        if previous is not None:
            for event in transition_events(previous, current_state):
                canonical = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                digest = hashlib.sha256((generation_json + canonical).encode("utf-8")).hexdigest()
                db.execute("""INSERT OR IGNORE INTO system_events
                    (event_key,occurred_at,category,severity,server_id,project_id,title,detail,before_json,after_json,next_step,source)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (digest, utc_now(), event["category"], event["severity"], event.get("server_id", ""), event.get("project_id", ""),
                     event["title"], event["detail"], json.dumps(event.get("before"), ensure_ascii=False),
                     json.dumps(event.get("after"), ensure_ascii=False), event["next_step"], "server_snapshot"))
            db.execute("DELETE FROM system_events WHERE id NOT IN (SELECT id FROM system_events ORDER BY id DESC LIMIT ?)", (CHANGE_LIMIT,))
        db.execute("""INSERT INTO observer_state(id,generation_json,state_json,updated_at) VALUES(1,?,?,?)
            ON CONFLICT(id) DO UPDATE SET generation_json=excluded.generation_json,state_json=excluded.state_json,updated_at=excluded.updated_at""",
            (generation_json, state_json, utc_now()))
        db.commit()

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "VovanHubAPI/1"

    def log_message(self, fmt, *args):
        if urlsplit(self.path).path != "/events":
            print("%s %s" % (self.log_date_time_string(), fmt % args), flush=True)

    def send_json(self, status, value):
        body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("invalid_content_length")
        if size < 0 or size > MAX_BODY:
            raise ValueError("body_too_large")
        raw = self.rfile.read(size)
        try:
            return json.loads(raw or b"{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("invalid_json")

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            return self.send_json(200, {"ok": True, "service": "vovan-os-hub-api", "time": utc_now()})
        if path == "/state":
            with connect() as db:
                preferences = read_preferences(db)
                custom_projects = preferences.pop("custom_projects", [])
                preferences.pop("tasks_initialized", None)
                return self.send_json(200, {
                    "ok": True, "time": utc_now(),
                    "sources": {"snapshot": file_state(SNAPSHOT), "projects": file_state(PROJECTS)},
                    "generation": list(generation()),
                    "preferences": preferences,
                    "custom_projects": custom_projects,
                    "custom_projects_initialized": db.execute("SELECT 1 FROM preferences WHERE key='custom_projects'").fetchone() is not None,
                    "tasks_initialized": db.execute("SELECT 1 FROM preferences WHERE key='tasks_initialized'").fetchone() is not None,
                    "tasks": read_tasks(db),
                    "project_meta": [dict(row) for row in db.execute("SELECT * FROM project_meta ORDER BY project_id")],
                })
        if path == "/snapshot":
            snapshot = json_file(SNAPSHOT)
            if snapshot is None:
                return self.send_json(503, {"error": "snapshot_unavailable"})
            return self.send_json(200, snapshot)
        if path == "/domain-health":
            with domain_health_lock:
                return self.send_json(200 if domain_health.get("ok") else 503, dict(domain_health))
        if path == "/changes":
            try:
                limit = max(1, min(200, int(parse_qs(urlsplit(self.path).query).get("limit", ["100"])[0])))
            except (TypeError, ValueError):
                return self.send_json(400, {"error": "invalid_limit"})
            with connect() as db:
                rows = db.execute("""SELECT id,event_key,occurred_at,category,severity,server_id,project_id,title,detail,
                    before_json,after_json,next_step,source FROM system_events ORDER BY id DESC LIMIT ?""", (limit,)).fetchall()
            events = []
            for row in rows:
                item = dict(row)
                item["before"] = json.loads(item.pop("before_json") or "null")
                item["after"] = json.loads(item.pop("after_json") or "null")
                events.append(item)
            return self.send_json(200, {"ok": True, "events": events, "count": len(events), "limit": limit,
                                        "updated_at": utc_now(), "history_starts_at": events[-1]["occurred_at"] if events else None})
        if path == "/events":
            return self.events()
        return self.send_json(404, {"error": "not_found"})

    def do_PUT(self):
        origin = self.headers.get("Origin")
        if origin and origin not in {"https://vovan20.ru", "https://www.vovan20.ru"}:
            return self.send_json(403, {"error": "origin_not_allowed"})
        path = urlsplit(self.path).path
        try:
            value = self.read_body()
            if path.startswith("/preferences/"):
                key = unquote(path[len("/preferences/"):])
                if key not in PREF_KEYS:
                    return self.send_json(404, {"error": "unknown_preference"})
                with connect() as db:
                    db.execute("INSERT INTO preferences(key,value_json,updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at",
                               (key, json.dumps(value, ensure_ascii=False), utc_now()))
                    db.commit()
                return self.send_json(200, {"ok": True, "key": key, "updated_at": utc_now()})
            if path == "/custom-projects":
                if not isinstance(value, list) or len(value) > 200:
                    return self.send_json(400, {"error": "invalid_projects"})
                clean = []
                for p in value:
                    if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not PROJECT_ID.fullmatch(p["id"]) or not isinstance(p.get("name"), str) or not p["name"].strip():
                        return self.send_json(400, {"error": "invalid_project"})
                    clean.append({k: p.get(k) for k in ("id", "name", "kind", "note", "local")})
                with connect() as db:
                    old_row = db.execute("SELECT value_json FROM preferences WHERE key='custom_projects'").fetchone()
                    old_projects = {p["id"]: p for p in json.loads(old_row["value_json"])} if old_row else {}
                    new_projects = {p["id"]: p for p in clean}
                    for project_id, project in new_projects.items():
                        old = old_projects.get(project_id)
                        if old is None:
                            record_event(db, {"category": "project", "project_id": project_id,
                                "title": "Проект добавлен в каталог", "detail": "Создана карточка проекта в общем онлайн-хабе.",
                                "next_step": "Добавьте репозиторий, сервер и следующий шаг в карточку проекта."}, "owner_action")
                        elif any(old.get(key) != project.get(key) for key in ("name", "kind", "note")):
                            record_event(db, {"category": "project", "project_id": project_id,
                                "title": "Карточка проекта обновлена", "detail": "Изменены название, тип или заметка; текст заметки в журнал не копируется.",
                                "next_step": "Проверьте описание и связи проекта."}, "owner_action")
                    for project_id in old_projects.keys() - new_projects.keys():
                        record_event(db, {"category": "project", "project_id": project_id,
                            "title": "Личная карточка проекта удалена", "detail": "Карточка удалена из пользовательского каталога.",
                            "next_step": "Если проект всё ещё нужен, добавьте его заново."}, "owner_action")
                    db.execute("INSERT INTO preferences(key,value_json,updated_at) VALUES('custom_projects',?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at",
                               (json.dumps(clean, ensure_ascii=False), utc_now()))
                    db.commit()
                return self.send_json(200, {"ok": True, "count": len(clean), "updated_at": utc_now()})
            if path == "/tasks":
                if not isinstance(value, list) or len(value) > 1000:
                    return self.send_json(400, {"error": "invalid_tasks"})
                clean = []
                allowed_status = {"new", "needs_info", "queued", "working", "blocked", "review", "done"}
                for task in value:
                    if not isinstance(task, dict):
                        return self.send_json(400, {"error": "invalid_task"})
                    title = str(task.get("title", "")).strip()
                    if not title or len(title) > 250:
                        return self.send_json(400, {"error": "invalid_task_title"})
                    status = task.get("status", "done" if task.get("done") else "new")
                    if status not in allowed_status:
                        status = "new"
                    clean.append({
                        "id": str(task.get("id") or uuid.uuid4()), "project_id": str(task.get("project") or task.get("project_id") or ""),
                        "title": title, "status": status, "priority": str(task.get("priority") or "normal"),
                        "details": str(task.get("details") or "")[:4000],
                    })
                now = utc_now()
                with connect() as db:
                    db.execute("BEGIN")
                    old_tasks = {row["id"]: dict(row) for row in db.execute("SELECT id,project_id,title,status,priority,details FROM tasks")}
                    new_tasks = {task["id"]: task for task in clean}
                    for task_id, task in new_tasks.items():
                        old = old_tasks.get(task_id)
                        if old is None:
                            record_event(db, {"category": "task", "project_id": task["project_id"], "title": "Добавлена задача",
                                "detail": "Новая задача сохранена в общей онлайн-очереди.", "before": None, "after": task["status"],
                                "next_step": "Откройте раздел задач и назначьте следующий шаг."}, "owner_action")
                        elif any(old[field] != task[field] for field in ("project_id", "title", "status", "priority", "details")):
                            record_event(db, {"category": "task", "project_id": task["project_id"] or old["project_id"],
                                "title": "Задача обновлена", "detail": "Изменена задача в общей онлайн-очереди.",
                                "before": old["status"], "after": task["status"], "next_step": "Проверьте назначенный статус и связанный проект."}, "owner_action")
                    for task_id, old in old_tasks.items():
                        if task_id not in new_tasks:
                            record_event(db, {"category": "task", "project_id": old["project_id"], "title": "Задача удалена",
                                "detail": "Запись удалена из общей онлайн-очереди.", "before": old["status"], "after": None,
                                "next_step": "Если работа ещё нужна, добавьте её снова."}, "owner_action")
                    db.execute("DELETE FROM tasks")
                    db.execute("INSERT INTO preferences(key,value_json,updated_at) VALUES('tasks_initialized','true',?) ON CONFLICT(key) DO UPDATE SET value_json='true',updated_at=excluded.updated_at", (now,))
                    for task in clean:
                        db.execute("INSERT INTO tasks(id,project_id,title,status,priority,details,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                                   (task["id"], task["project_id"], task["title"], task["status"], task["priority"], task["details"], now, now))
                    db.commit()
                return self.send_json(200, {"ok": True, "count": len(clean), "updated_at": now})
            if path.startswith("/projects/"):
                project_id = unquote(path[len("/projects/"):])
                if not PROJECT_ID.fullmatch(project_id) or not isinstance(value, dict):
                    return self.send_json(400, {"error": "invalid_project"})
                status = value.get("status")
                allowed = {"idea", "planned", "in_progress", "paused", "working", "archived", "not_needed"}
                if status is not None and status not in allowed:
                    return self.send_json(400, {"error": "invalid_project_status"})
                visible = int(bool(value.get("visible", True)))
                favorite = int(bool(value.get("favorite", False)))
                next_step = str(value.get("next_step") or "")[:1000]
                note = str(value.get("note") or "")[:4000]
                now = utc_now()
                with connect() as db:
                    old = db.execute("SELECT status,visible,favorite,next_step,note FROM project_meta WHERE project_id=?", (project_id,)).fetchone()
                    db.execute("""INSERT INTO project_meta(project_id,status,visible,favorite,next_step,note,updated_at)
                        VALUES(?,?,?,?,?,?,?) ON CONFLICT(project_id) DO UPDATE SET
                        status=excluded.status,visible=excluded.visible,favorite=excluded.favorite,
                        next_step=excluded.next_step,note=excluded.note,updated_at=excluded.updated_at""",
                        (project_id, status, visible, favorite, next_step, note, now))
                    before = dict(old) if old else None
                    after = {"status": status, "visible": visible, "favorite": favorite, "next_step": next_step, "note": note}
                    if old is None or any(old[key] != val for key, val in after.items()):
                        labels = {"status": "статус", "visible": "видимость", "favorite": "избранное", "next_step": "следующий шаг", "note": "заметка"}
                        changed = [labels[key] for key, val in after.items() if old is None or old[key] != val]
                        before_status = before.get("status") if before else None
                        after_status = status if before_status != status else None
                        record_event(db, {"category": "project", "project_id": project_id, "title": "Обновлён паспорт проекта",
                            "detail": "Изменено: " + ", ".join(changed) + ". Содержимое заметок в истории не сохраняется.",
                            "before": before_status if after_status is not None else None, "after": after_status,
                            "next_step": "Проверьте карточку проекта и его следующий шаг."}, "owner_action")
                    db.commit()
                return self.send_json(200, {"ok": True, "project_id": project_id, "updated_at": now})
        except ValueError as exc:
            return self.send_json(400, {"error": str(exc)})
        except (sqlite3.Error, OSError) as exc:
            print("API storage error: %s" % type(exc).__name__, flush=True)
            return self.send_json(500, {"error": "storage_error"})
        return self.send_json(404, {"error": "not_found"})

    def events(self):
        if not clients.acquire(blocking=False):
            return self.send_json(503, {"error": "too_many_event_streams"})
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(b"retry: 2000\n\n")
            self.wfile.flush()
            previous = None
            heartbeat = time.monotonic()
            while not stopping.is_set():
                current = generation()
                if current != previous:
                    time.sleep(0.35)
                    current = generation()
                    payload = {"id": "-".join(map(str, current)), "time": utc_now(), "sources": {"snapshot": file_state(SNAPSHOT), "projects": file_state(PROJECTS)}}
                    event_name = "change" if previous is not None and current[:-1] == previous[:-1] else "snapshot"
                    frame = ("id: %s\nevent: %s\ndata: %s\n\n" % (payload["id"], event_name, json.dumps(payload, separators=(",", ":")))).encode("utf-8")
                    self.wfile.write(frame)
                    self.wfile.flush()
                    previous = current
                    heartbeat = time.monotonic()
                elif time.monotonic() - heartbeat >= 15:
                    self.wfile.write(b": keep-alive\n\n")
                    self.wfile.flush()
                    heartbeat = time.monotonic()
                time.sleep(1)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass
        finally:
            clients.release()

class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    init_db()
    observe_snapshot()  # First run becomes a baseline; it is not presented as a change.
    def watch():
        while not stopping.is_set():
            try:
                observe_snapshot()
            except (OSError, sqlite3.Error, ValueError) as exc:
                print("Snapshot observer error: %s" % type(exc).__name__, flush=True)
            stopping.wait(2)
    threading.Thread(target=watch, name="snapshot-observer", daemon=True).start()
    def check_domains():
        while not stopping.is_set():
            try:
                refresh_domain_health()
            except (OSError, ValueError, sqlite3.Error) as exc:
                print("Domain health check error: %s" % type(exc).__name__, flush=True)
                with domain_health_lock:
                    domain_health.update({"ok": False, "status": "unavailable", "updated_at": utc_now()})
            stopping.wait(DOMAIN_CHECK_INTERVAL)
    threading.Thread(target=check_domains, name="domain-health-check", daemon=True).start()
    httpd = Server((HOST, PORT), Handler)
    def stop(_signal, _frame):
        stopping.set()
        threading.Thread(target=httpd.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    print("VOVAN OS Hub API listening on %s:%d" % (HOST, PORT), flush=True)
    try:
        httpd.serve_forever(poll_interval=0.5)
    finally:
        httpd.server_close()

if __name__ == "__main__":
    main()

