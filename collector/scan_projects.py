#!/usr/bin/env python3
"""Vovan OS — опись папок-проектов на сервере (только чтение).
Для каждой папки: размер, число файлов, когда последний раз меняли, стек, описание из package.json/README, git, связанный сервис.
Личные папки (Desktop, Music…), зависимости и кэши пропускаются. Секреты маскируются (collect.mask).
Запуск: python3 scan_projects.py > projects-<server>.json
"""
import json, os, re, glob, time, subprocess
from pathlib import Path
from collect import sh, mask, detect_stack, git_info

SKIP_NAMES = {'Desktop', 'Documents', 'Downloads', 'Music', 'Pictures', 'Public', 'Templates', 'Videos', 'Sync', 'node_modules', 'sherlock-env',
              'codex-backup', 'bin', 'xfer', 'xfer2', 'quarantine', 'containerd', 'node24', 'pwtest', 'ffmpeg-static', '__pycache__', 'lost+found', 'snap', 'go', 'well-known', 'html'}
ROOTS = ['/home/claude', '/home/claude/apps', '/home/claude/apps/agent-hub/projects', '/opt', '/var/www', '/www-static', '/www-static/www-misc', '/eeklera', '/srv', '/root', '/root/gh', '/data', '/data/sites']

def newest(path):
    v = sh(f"find {path} -maxdepth 5 \\( -name node_modules -o -name .git -o -name venv -o -name .venv -o -name __pycache__ \\) -prune -o -type f -printf '%T@\\n' 2>/dev/null | sort -n | tail -1", timeout=60)
    try: return time.strftime('%Y-%m-%d', time.localtime(float(v)))
    except Exception: return None

def files(path):
    v = sh(f"find {path} \\( -name node_modules -o -name .git -o -name venv -o -name .venv \\) -prune -o -type f -print 2>/dev/null | wc -l", timeout=60)
    return int(v) if v.isdigit() else None

def readme(path):
    for f in ('README.md', 'readme.md', 'README.txt', 'README', 'ARCHITECTURE.md', 'CLAUDE.md', 'AGENTS.md'):
        p = Path(path, f)
        if p.exists():
            lines = [l.strip() for l in p.read_text(errors='ignore').splitlines()]
            keep = [l for l in lines if l and not l.startswith(('```', '![', '<', '|---', '---'))][:14]
            return f, mask(' ⏎ '.join(keep))[:900]
    return None, None

def pkg(path):
    p = Path(path, 'package.json')
    if p.exists():
        try:
            d = json.loads(p.read_text())
            return {'name': d.get('name'), 'description': mask(d.get('description') or '') or None, 'scripts': sorted((d.get('scripts') or {}).keys())[:10],
                    'deps': sorted((d.get('dependencies') or {}).keys())[:25]}
        except Exception:
            return None
    return None

def services_by_dir():
    out = {}
    for line in sh("systemctl show '*' -p Id,WorkingDirectory,ActiveState --type=service 2>/dev/null", timeout=60).split('\n\n'):
        p = dict(l.split('=', 1) for l in line.splitlines() if '=' in l)
        if p.get('WorkingDirectory'):
            out.setdefault(p['WorkingDirectory'].rstrip('/'), []).append({'service': p['Id'].removesuffix('.service'), 'state': p.get('ActiveState')})
    return out

if __name__ == '__main__':
    svc = services_by_dir(); seen = set(); out = []
    for root in ROOTS:
        if not os.path.isdir(root): continue
        for d in sorted(glob.glob(root + '/*')):
            name = os.path.basename(d)
            if os.path.islink(d) and not os.path.exists(d):   # ссылка в пустоту: проект был, файлов больше нет
                out.append({'path': d, 'name': name, 'broken_link_to': os.readlink(d)}); continue
            if os.path.islink(d):
                real = os.path.realpath(d)
                if real not in seen: out.append({'path': d, 'name': name, 'link_to': real})
                continue
            if not os.path.isdir(d) or name.startswith(('.', '_')) or name in SKIP_NAMES or d in ROOTS or os.path.realpath(d) in seen: continue
            seen.add(os.path.realpath(d))
            rf, rt = readme(d)
            linked = [s for k, v in svc.items() if k == d or k.startswith(d + '/') for s in v]
            top = sorted(re.sub(r'^dl-.{6,}', 'dl-***', x) for x in os.listdir(d) if not x.startswith('.'))[:18]   # секретные ссылки скачивания
            out.append({'path': d, 'name': name, 'size': int(sh(f"du -sb {d} 2>/dev/null | cut -f1", timeout=90) or 0), 'files': files(d), 'last_change': newest(d),
                        'stack': detect_stack(d), 'package': pkg(d), 'readme_file': rf, 'readme': rt, 'git': git_info(d),
                        'has_env_file': any(os.path.exists(os.path.join(d, f)) for f in ('.env', '.env.local', '.env.production')),
                        'docker': any(os.path.exists(os.path.join(d, f)) for f in ('Dockerfile', 'docker-compose.yml', 'compose.yaml')),
                        'services': linked, 'top': top})
    print(json.dumps({'collected_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'folders': out}, ensure_ascii=False, indent=1))
