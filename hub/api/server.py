#!/usr/bin/env python3
"""Small authenticated-by-front-proxy API for the online VOVAN OS hub."""
import json, os, re, signal, sqlite3, threading, time, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote

HOST = os.environ.get("HUB_API_HOST", "127.0.0.1")
PORT = int(os.environ.get("HUB_API_PORT", "3980"))
SNAPSHOT = Path(os.environ.get("HUB_API_SNAPSHOT", "/data/vovan-os-hub/live/snapshot.json"))
PROJECTS = Path(os.environ.get("HUB_API_PROJECTS", "/data/vovan-os-hub/live/projects.json"))
DB = Path(os.environ.get("HUB_API_DB", "/data/vovan-os-hub/state/hub.sqlite3"))
MAX_BODY = 256 * 1024
MAX_CLIENTS = int(os.environ.get("HUB_API_MAX_SSE_CLIENTS", "30"))
stopping = threading.Event()
clients = threading.BoundedSemaphore(MAX_CLIENTS)
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
        """)
        db.commit()

def file_state(path):
    try:
        st = path.stat()
        return {"available": True, "updated_at": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"), "bytes": st.st_size}
    except OSError:
        return {"available": False, "updated_at": None, "bytes": None}

def generation():
    values = []
    for path in (SNAPSHOT, PROJECTS):
        try:
            st = path.stat()
            values.extend((st.st_mtime_ns, st.st_size))
        except OSError:
            values.extend((0, 0))
    return tuple(values)

def read_preferences(db):
    return {row["key"]: json.loads(row["value_json"]) for row in db.execute("SELECT key,value_json FROM preferences")}

def read_tasks(db):
    return [dict(row) for row in db.execute("SELECT id,project_id,title,status,priority,details,created_at,updated_at FROM tasks ORDER BY created_at DESC")]

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
                    db.execute("""INSERT INTO project_meta(project_id,status,visible,favorite,next_step,note,updated_at)
                        VALUES(?,?,?,?,?,?,?) ON CONFLICT(project_id) DO UPDATE SET
                        status=excluded.status,visible=excluded.visible,favorite=excluded.favorite,
                        next_step=excluded.next_step,note=excluded.note,updated_at=excluded.updated_at""",
                        (project_id, status, visible, favorite, next_step, note, now))
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
                    frame = ("id: %s\nevent: snapshot\ndata: %s\n\n" % (payload["id"], json.dumps(payload, separators=(",", ":")))).encode("utf-8")
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

