"""Offline checks for the loopback server and atomic GitHub snapshot refresh."""
import base64
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sync_github',ROOT/'local/sync_github.py')
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)
class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);(self.root/'site').mkdir()
        self.target=self.root/'site/snapshot.json';self.target.write_text('{"previous":true}')
        self.files={p:json.loads((ROOT/p).read_text(encoding='utf-8')) for p in sync.FILES}
    def tearDown(self):self.temp.cleanup()
    def getter(self,url,token):
        if '/commits/main' in url:return {'sha':'a'*40}
        path=url.split('/contents/')[1].split('?')[0]
        self.assertIn('ref='+'a'*40,url)
        return {'encoding':'base64','content':base64.b64encode(json.dumps(self.files[path]).encode()).decode()}
    def test_success_pins_revision_and_replaces_one_snapshot(self):
        with patch.object(sync,'ROOT',self.root),patch.object(sync,'get_json',side_effect=self.getter):
            result=sync.sync('test-only')
        self.assertEqual(len(result['catalog']['projects']),49)
        self.assertEqual(json.loads(self.target.read_text())['source']['commit'],'a'*40)
        self.assertFalse(list((self.root/'site').glob('*.tmp')))
    def test_invalid_source_preserves_previous_snapshot(self):
        self.files['catalog/projects.json']['projects']=[]
        with patch.object(sync,'ROOT',self.root),patch.object(sync,'get_json',side_effect=self.getter):
            with self.assertRaises(ValueError):sync.sync('test-only')
        self.assertEqual(self.target.read_text(),'{"previous":true}')
    def test_network_failure_preserves_previous_snapshot(self):
        with patch.object(sync,'ROOT',self.root),patch.object(sync,'get_json',side_effect=urllib.error.URLError('offline')):
            with self.assertRaises(urllib.error.URLError):sync.sync('test-only')
        self.assertEqual(self.target.read_text(),'{"previous":true}')
class LocalServerTests(unittest.TestCase):
    def test_serves_module_and_snapshot(self):
        for name in ['app.mjs','snapshot.json','styles.css']:
            with urllib.request.urlopen('http://127.0.0.1:8080/'+name) as r:self.assertEqual(r.status,200)
    def test_rejects_foreign_host(self):
        req=urllib.request.Request('http://127.0.0.1:8080/',headers={'Host':'external.example'})
        with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(req)
        self.assertEqual(e.exception.code,403)
    def test_cannot_serve_repo_files(self):
        for path in ['../catalog/projects.json','%2e%2e/README.md','/.env']:
            with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen('http://127.0.0.1:8080/'+path)
            self.assertIn(e.exception.code,[403,404])
if __name__=='__main__':unittest.main()
