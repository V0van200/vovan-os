"""Package the read-only inventory for the local dashboard. No database records."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def build():
    inv = ROOT / 'inventory'
    data = {
        'version': 1,
        'catalog': json.loads((ROOT / 'catalog' / 'projects.json').read_text(encoding='utf-8')),
        'source': {'repository': 'V0van200/vovan-os', 'commit': '0e7ce2be16351c54e5d4dba39f2efb583a40b0c5'},
        'links': json.loads((inv / 'links.json').read_text(encoding='utf-8')),
        'repos': json.loads((inv / 'github-repos.json').read_text(encoding='utf-8')),
        'graph': json.loads((inv / 'system-graph.json').read_text(encoding='utf-8')),
        'servers': {p.stem.removeprefix('server-'): json.loads(p.read_text(encoding='utf-8')) for p in sorted((inv / 'servers').glob('server-*.json'))},
    }
    # Collector includes an empty system Postgres database; preserve it but label it in UI.
    (ROOT / 'site' / 'snapshot.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    return data
if __name__ == '__main__':
    d=build()
    print(f"Snapshot: {len(d['repos'])} repositories, {len(d['servers'])} servers")
