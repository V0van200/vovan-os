import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import live


class FreshnessTests(unittest.TestCase):
    def stamp(self, age):
        return datetime.fromtimestamp(live.NOW - age, timezone.utc).isoformat().replace("+00:00", "Z")

    def test_stale_uses_collected_at_five_minute_limit(self):
        self.assertFalse(live.is_stale({"collected_at": self.stamp(299)}))
        self.assertTrue(live.is_stale({"collected_at": self.stamp(301)}))
        self.assertTrue(live.is_stale({}))

    def test_live_de_is_added_when_baseline_snapshot_is_old(self):
        sample = {"collected_at": self.stamp(0), "host": {"hostname": "de", "cpus": 4},
                  "services": [{"name": "nginx"}], "timers": [], "docker": [], "certs": [],
                  "security": {"firewall": "включён"}, "net": {"ping": 1}}
        snapshot = {"servers": {"78": {"host": {"hostname": "nl"}}}}
        result = live.merge_live_servers(snapshot, {"78": {}, "198": {}, "de": sample})
        de = result["servers"]["de"]
        self.assertEqual(de["host"]["hostname"], "de")
        self.assertEqual(de["services"], sample["services"])
        self.assertFalse(de["live"]["stale"])
        self.assertEqual(de["live"]["security"], sample["security"])

    def test_existing_server_is_merged_without_dropping_inventory(self):
        sample = {"collected_at": self.stamp(0), "host": {"hostname": "de", "cpus": 4},
                  "services": [], "timers": [], "docker": [], "certs": []}
        snapshot = {"servers": {"de": {"host": {"ram_total": 8}, "nginx": [{"server_name": "x"}]}}}
        de = live.merge_live_servers(snapshot, {"de": sample})["servers"]["de"]
        self.assertEqual(de["host"], {"ram_total": 8, "hostname": "de", "cpus": 4})
        self.assertEqual(de["nginx"], [{"server_name": "x"}])

    def test_remote_sample_is_saved_for_next_build(self):
        sample = {"collected_at": self.stamp(0), "host": {"hostname": "de"}, "services": []}
        with tempfile.TemporaryDirectory() as directory, patch.object(live, "OUT", Path(directory)), patch.object(
            live.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout=json.dumps(sample))
        ):
            self.assertEqual(live.server_de_live(), sample)
            self.assertEqual(json.loads((Path(directory) / "server-de.json").read_text()), sample)

    def test_ssh_failure_keeps_last_good_sample(self):
        sample = {"collected_at": self.stamp(400), "host": {"hostname": "de"}, "services": []}
        with tempfile.TemporaryDirectory() as directory, patch.object(live, "OUT", Path(directory)), patch.object(
            live.subprocess, "run", return_value=SimpleNamespace(returncode=255, stdout="")
        ):
            (Path(directory) / "server-de.json").write_text(json.dumps(sample))
            self.assertEqual(live.server_de_live(), sample)
            self.assertTrue(live.is_stale(sample))

    def test_ssh_failure_without_cache_returns_empty_sample(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(live, "OUT", Path(directory)), patch.object(
            live.subprocess, "run", side_effect=TimeoutError()
        ):
            self.assertEqual(live.server_de_live(), {})


if __name__ == "__main__":
    unittest.main()
