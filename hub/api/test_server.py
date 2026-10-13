import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from hub.api.server import observed_state, transition_events

API = Path(__file__).with_name("server.py")

class HubApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        cls.snapshot = root / "snapshot.json"
        cls.projects = root / "projects.json"
        cls.db = root / "hub.sqlite3"
        cls.snapshot.write_text('{"version":1,"servers":{"de":{"collected_at":"2026-10-13T10:00:00Z","services":[{"name":"nginx","state":"active"}],"docker":[]}}}', encoding="utf-8")
        cls.projects.write_text('{"projects":{"demo":{"alerts":[]}}}', encoding="utf-8")
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        cls.port = sock.getsockname()[1]
        sock.close()
        env = dict(os.environ, HUB_API_PORT=str(cls.port),
                   HUB_API_SNAPSHOT=str(cls.snapshot),
                   HUB_API_PROJECTS=str(cls.projects),
                   HUB_API_DB=str(cls.db))
        cls.proc = subprocess.Popen([sys.executable, str(API)], env=env,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cls.base = f"http://127.0.0.1:{cls.port}"
        for _ in range(50):
            try:
                with urlopen(cls.base + "/health", timeout=0.2) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(0.1)
        else:
            raise RuntimeError("API did not start")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=5)
        cls.temp.cleanup()

    def request_json(self, path, method="GET", body=None):
        data = None if body is None else json.dumps(body).encode()
        request = Request(self.base + path, data=data, method=method,
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read())

    def test_health_state_and_persistent_preferences(self):
        status, health = self.request_json("/health")
        self.assertEqual(status, 200)
        self.assertTrue(health["ok"])
        self.request_json("/preferences/server", "PUT", "de")
        self.request_json("/preferences/profile", "PUT", {"name": "Vovan", "about": "Hub"})
        _, state = self.request_json("/state")
        self.assertEqual(state["preferences"]["server"], "de")
        self.assertEqual(state["preferences"]["profile"]["name"], "Vovan")
        self.assertTrue(state["sources"]["snapshot"]["available"])

    def test_live_snapshot_endpoint_returns_latest_source_document(self):
        self.snapshot.write_text('{"version":1,"servers":{"de":{"ok":true}}}', encoding="utf-8")
        status, snapshot = self.request_json("/snapshot")
        self.assertEqual(status, 200)
        self.assertEqual(snapshot["version"], 1)
        self.assertIn("de", snapshot["servers"])
        self.snapshot.write_text('{"version":2,"servers":{"78":{}}}', encoding="utf-8")
        _, updated = self.request_json("/snapshot")
        self.assertEqual(updated["version"], 2)
        self.assertIn("78", updated["servers"])

    def test_custom_projects_tasks_and_project_status(self):
        self.request_json("/custom-projects", "PUT", [
            {"id": "local-demo", "name": "Demo", "kind": "app", "note": "next", "local": True}
        ])
        self.request_json("/tasks", "PUT", [
            {"id": "task-1", "title": "Connect source", "project": "demo", "done": False}
        ])
        self.request_json("/projects/demo", "PUT", {
            "status": "in_progress", "visible": True, "favorite": True,
            "next_step": "Add collector", "note": "Need credentials"
        })
        _, state = self.request_json("/state")
        self.assertEqual(state["custom_projects"][0]["id"], "local-demo")
        self.assertEqual(state["tasks"][0]["title"], "Connect source")
        self.assertEqual(state["project_meta"][0]["status"], "in_progress")
        _, changes = self.request_json("/changes?limit=20")
        categories = {event["category"] for event in changes["events"]}
        self.assertTrue({"task", "project"}.issubset(categories))
        actions = [event for event in changes["events"] if event["source"] == "owner_action"]
        self.assertTrue({"task", "project"}.issubset({event["category"] for event in actions}))
        project_event = next(event for event in actions if event["category"] == "project")
        self.assertNotIn("Need credentials", json.dumps(project_event))

    def test_empty_remote_collections_are_distinguishable_from_uninitialized(self):
        self.request_json("/custom-projects", "PUT", [])
        self.request_json("/tasks", "PUT", [])
        _, state = self.request_json("/state")
        self.assertTrue(state["custom_projects_initialized"])
        self.assertTrue(state["tasks_initialized"])
        self.assertEqual(state["custom_projects"], [])
        self.assertEqual(state["tasks"], [])

    def test_cross_origin_write_is_rejected(self):
        request = Request(self.base + "/preferences/server", data=b'"de"',
                          method="PUT", headers={"Content-Type": "application/json",
                                                 "Origin": "https://attacker.example"})
        with self.assertRaises(Exception) as error:
            urlopen(request, timeout=3)
        self.assertIn("403", str(error.exception))

    def test_invalid_project_status_is_rejected(self):
        request = Request(self.base + "/projects/demo", data=b'{"status":"unknown"}',
                          method="PUT", headers={"Content-Type": "application/json"})
        with self.assertRaises(Exception) as error:
            urlopen(request, timeout=3)
        self.assertIn("400", str(error.exception))

    def test_sse_emits_when_live_files_change(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        connection.request("GET", "/events")
        response = connection.getresponse()
        self.assertEqual(response.status, 200)
        stream = response.fp
        first = b""
        deadline = time.time() + 3
        while b"event: snapshot" not in first and time.time() < deadline:
            first += stream.readline()
        self.assertIn(b"event: snapshot", first)
        self.snapshot.write_text('{"version":2}', encoding="utf-8")
        second = b""
        deadline = time.time() + 4
        while b"event: snapshot" not in second and time.time() < deadline:
            second += stream.readline()
        self.assertIn(b"event: snapshot", second)
        self.request_json("/tasks", "PUT", [{"id": "sse-task", "title": "SSE journal event", "project": "demo"}])
        change = b""
        deadline = time.time() + 4
        while b"event: change" not in change and time.time() < deadline:
            change += stream.readline()
        self.assertIn(b"event: change", change)
        connection.close()

    def test_change_history_records_server_service_and_project_alert_transitions(self):
        next_snapshot = {"version": 2, "servers": {"de": {
            "collected_at": "2026-10-13T10:01:00Z",
            "services": [{"name": "nginx", "state": "failed"}], "docker": []
        }}}
        self.snapshot.write_text(json.dumps(next_snapshot), encoding="utf-8")
        self.projects.write_text(json.dumps({"projects": {"demo": {"alerts": ["Сайт не отвечает"]}}}), encoding="utf-8")
        deadline = time.time() + 4
        result = None
        while time.time() < deadline:
            _, result = self.request_json("/changes?limit=20")
            if len(result["events"]) >= 2:
                break
            time.sleep(0.1)
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["count"], 2)
        by_category = {event["category"]: event for event in result["events"]}
        self.assertEqual(by_category["service"]["server_id"], "de")
        self.assertEqual(by_category["service"]["before"], "active")
        self.assertEqual(by_category["service"]["after"], "failed")
        self.assertEqual(by_category["project"]["project_id"], "demo")
        self.assertIn("nginx", by_category["service"]["title"])

    def test_change_history_limit_is_bounded_and_validated(self):
        _, result = self.request_json("/changes?limit=999999")
        self.assertEqual(result["limit"], 200)
        request = Request(self.base + "/changes?limit=nope")
        with self.assertRaises(Exception) as error:
            urlopen(request, timeout=3)
        self.assertIn("400", str(error.exception))

    def test_container_uptime_text_does_not_create_repeated_events(self):
        def state(status):
            return observed_state({"servers": {"de": {"docker": [{"name": "web", "status": status}]}}}, {"projects": {}})
        before, after = state("Up 2 minutes"), state("Up 3 minutes")
        self.assertEqual(before["containers"]["de:web"]["state"], "running")
        self.assertEqual(transition_events(before, after), [])

    def test_stale_server_is_detected_even_when_live_flag_was_last_false(self):
        timestamp = lambda age: (datetime.now(timezone.utc) - timedelta(seconds=age)).isoformat().replace("+00:00", "Z")
        before = observed_state({"servers": {"de": {"collected_at": timestamp(120), "live": {"stale": False}}}}, {"projects": {}})
        after = observed_state({"servers": {"de": {"collected_at": timestamp(240), "live": {"stale": False}}}}, {"projects": {}})
        events = transition_events(before, after)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["category"], "server")
        self.assertEqual(events[0]["severity"], "warning")

if __name__ == "__main__":
    unittest.main()

