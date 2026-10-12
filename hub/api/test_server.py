import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

API = Path(__file__).with_name("server.py")

class HubApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        cls.snapshot = root / "snapshot.json"
        cls.projects = root / "projects.json"
        cls.db = root / "hub.sqlite3"
        cls.snapshot.write_text('{"version":1}', encoding="utf-8")
        cls.projects.write_text('{"projects":{}}', encoding="utf-8")
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
        _, state = self.request_json("/state")
        self.assertEqual(state["preferences"]["server"], "de")
        self.assertTrue(state["sources"]["snapshot"]["available"])

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
        connection.close()

if __name__ == "__main__":
    unittest.main()

