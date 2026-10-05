#!/usr/bin/env python3
"""Vovan OS — снимок данных для хаба Astra 6 (hub/site/snapshot.json).
Вход:  catalog/projects.json + inventory/*.json (после build_docs.py и build_catalog.py).
Выход: hub/site/snapshot.json — формат версии 1, который читает hub/site/model.mjs. Записей из баз в нём нет.
Запуск: python3 collector/build_hub.py
"""
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / 'inventory'
load = lambda p: json.loads(p.read_text(encoding='utf-8'))
commit = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip() or 'local'

data = {
    'version': 1,
    'catalog': load(ROOT / 'catalog' / 'projects.json'),
    'source': {'repository': 'V0van200/vovan-os', 'commit': commit},
    'links': load(INV / 'links.json'),
    'repos': load(INV / 'github-repos.json'),
    'graph': load(INV / 'system-graph.json'),
    'servers': {p.stem.removeprefix('server-'): load(p) for p in sorted((INV / 'servers').glob('server-*.json'))},
}
(ROOT / 'hub' / 'site' / 'snapshot.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f"hub ok: {len(data['catalog']['projects'])} проектов, {len(data['graph']['nodes'])} узлов, серверы {', '.join(data['servers'])}, база {commit[:7]}")
