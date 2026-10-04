#!/usr/bin/env python3
"""Vovan OS — генератор документации из инвентаря.
Вход:  inventory/servers/*.json (collect.py), inventory/links.json (ручные связи), inventory/github-repos.json (каталог GitHub).
Выход: docs/SYSTEM-MAP.md, docs/PROJECTS.md, docs/DATABASES.md, docs/databases/*.md, inventory/system-graph.json.
Запуск: python3 collector/build_docs.py   (из корня репозитория)
"""
import json, glob, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INV, DOCS = ROOT / 'inventory', ROOT / 'docs'
servers = {Path(f).stem.replace('server-', ''): json.load(open(f)) for f in sorted(glob.glob(str(INV / 'servers' / '*.json')))}
links = json.load(open(INV / 'links.json'))
repos = {r['name']: r for r in json.load(open(INV / 'github-repos.json'))}
(DOCS / 'databases').mkdir(parents=True, exist_ok=True)

def size(n):
    if n is None: return '—'
    for u in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if n < 1024: return f'{n:.0f} {u}' if u == 'Б' else f'{n:.1f} {u}'
        n /= 1024
def esc(s): return str(s if s is not None else '—').replace('|', '\\|')
def port_owner(srv, port):
    for s in servers[srv]['services']:
        if any(p[0] == port for p in s['ports']): return s['name']
    for c in servers[srv]['docker']:
        if c.get('ports') and f':{port}->' in c['ports']: return 'docker:' + c['name']
    return None
def route_target(srv, loc):
    if loc['proxy']:
        m = re.search(r'https?://(127\.0\.0\.1|localhost):(\d+)', loc['proxy'])
        if m:
            own = port_owner(srv, int(m.group(2)))
            return f"сервис **{own}** (:{m.group(2)})" if own else f"порт {m.group(2)} ⚠ никто не слушает"
        return 'прокси → ' + loc['proxy']
    if loc['root']: return 'файлы ' + loc['root']
    if loc.get('return'): return 'ответ ' + loc['return']
    return 'статика'

# ---------- SYSTEM-MAP ----------
out = ['# Карта системы Vovan OS', '', f"Собрано автоматически `collector/collect.py` → `collector/build_docs.py`. Только чтение, без секретов.", '']
for srv, d in servers.items():
    h = d['host']
    out += [f"## Сервер {srv} — {h['public_ip']} ({h['hostname']})", '',
            f"- Система: {h['os']}, ядро {h['kernel']}; CPU: {h['cpus']}; RAM: {size(h['ram_total'])} (свободно {size(h['ram_available'])}); нагрузка {', '.join(f'{x:.2f}' for x in h['load'])}",
            f"- Диски: " + '; '.join(f"{x['mount']} {size(x['used'])} из {size(x['size'])} ({x['used']*100//max(1,x['size'])}%)" for x in h['disks']),
            f"- Снимок: {d['collected_at']}", '',
            '### Сервисы', '', '| Сервис | Состояние | Порты | Память | Папка | Описание |', '|---|---|---|---|---|---|']
    for s in sorted(d['services'], key=lambda x: x['name']):
        out.append(f"| {s['name']} | {s['state']}/{s['sub']} | {', '.join(str(p[0]) for p in s['ports']) or '—'} | {size(s['memory'])} | {esc(s['workdir'])} | {esc(s['description'])} |")
    out += ['', '### Домены и маршруты (nginx)', '']
    for site in d['nginx']:
        if site['redirect_only'] or not site['names'] and not site['locations']: continue
        out.append(f"**{', '.join(site['names']) or '(по IP / по умолчанию)'}**" + (f" — корень `{site['root']}`" if site['root'] else '') + (' 🔒 вход' if site['auth'] else ''))
        for l in site['locations']:
            if l['path'] in ('/.well-known/acme-challenge/',) or (l.get('return') or '').startswith('404'): continue
            out.append(f"- `{l['path']}` → {route_target(srv, l)}" + (' 🔒' if l['auth'] else ''))
        out.append('')
    if d['docker']:
        out += ['### Docker', '', '| Контейнер | Образ | Состояние | Порты |', '|---|---|---|---|'] + [f"| {c['name']} | {c['image']} | {c['status']} | {esc(c['ports'])} |" for c in d['docker']] + ['']
    out += ['### Таймеры (регулярные задачи)', ''] + [f"- **{t['timer']}** → {t['runs']}: {esc(t['description'])}; последний запуск {esc(t['last'])}" for t in d['timers']] + ['']
    out += ['### Сертификаты HTTPS', ''] + [f"- {c['name']}: до {c['expires']} — {', '.join(c['domains'])}" for c in d['certs']] + ['']
    out += ['### Бэкапы', ''] + [f"- `{b['dir']}`: {b['files']} файлов, {size(b['size'])}; последний `{b['latest']}` ({b['latest_at']})" for b in d['backups']] + ['']
    if d.get('vpn'):
        out += ['### VPN (только счётчики, без ключей)', ''] + [f"- {k}: {json.dumps(v, ensure_ascii=False)}" for k, v in d['vpn'].items()] + ['']
(DOCS / 'SYSTEM-MAP.md').write_text('\n'.join(out))

# ---------- DATABASES ----------
dbs = []
for srv, d in servers.items():
    for db in d['databases']:
        if db['engine'] == 'postgres' and db['database'] == 'postgres': continue
        dbs.append((srv, db))
def db_id(srv, db):
    if db['engine'] == 'sqlite': return re.sub(r'[^a-z0-9]+', '-', (srv + db['path']).lower()).strip('-')
    return f"{srv}-{db['engine']}-{db.get('database') or db.get('container')}"
def owner(srv, db):
    key = db.get('path') or (f"postgres:{db['database']}" if db['engine'] == 'postgres' else f"redis:{db['container']}")
    for gid, g in links['groups'].items():
        if key in g.get('databases', []): return g['name']
    return '—'
idx = ['# Базы данных', '', 'Только структура и число строк. **Самих данных здесь нет и не будет** (см. SECURITY.md).', '',
       '| База | Где | Движок | Таблиц | Строк | Размер | Проект |', '|---|---|---|---|---|---|---|']
for srv, db in dbs:
    i = db_id(srv, db); tables = db.get('tables', [])
    name = db.get('path') or db.get('database') or db.get('container')
    idx.append(f"| [{esc(os.path.basename(name) if db['engine']=='sqlite' else name)}](databases/{i}.md) | {srv} | {db['engine']} | {len(tables)} | {sum((t.get('rows') or 0) for t in tables)} | {size(db.get('size'))} | {owner(srv, db)} |")
    page = [f"# {name} (сервер {srv}, {db['engine']})", '', f"Проект: {owner(srv, db)}. Размер: {size(db.get('size'))}." + (f" Ошибка чтения: {db['error']}" if db.get('error') else ''), '']
    if db['engine'] == 'redis':
        page += ['```', *db.get('info', []), '```']
    fks = db.get('foreign_keys', [])
    if db['engine'] == 'postgres' and fks:
        page += ['## Связи', '', '```mermaid', 'erDiagram'] + [f"  {f['from'].rsplit('.',1)[0].replace('.','_')} }}o--|| {f['to'].rsplit('.',1)[0].replace('.','_')} : \"{f['from'].rsplit('.',1)[1]}\"" for f in fks[:150]] + ['```', '']
    for t in tables:
        tf = t.get('foreign_keys') or []
        page += [f"## {t['table']} — {t.get('rows') if t.get('rows') is not None else '?'} строк", '', '| Поле | Тип | Обязательное | Ключ |', '|---|---|---|---|']
        page += [f"| {c['name']} | {c.get('type') or ''} | {'да' if c.get('notnull') else ''} | {'PK' if c.get('pk') else ''}{' → ' + next((f['table']+'.'+f['to'] for f in tf if f['from']==c['name']), '') if any(f['from']==c['name'] for f in tf) else ''} |" for c in t['columns']]
        page.append('')
    (DOCS / 'databases' / f'{i}.md').write_text('\n'.join(page))
(DOCS / 'DATABASES.md').write_text('\n'.join(idx) + '\n')

# ---------- PROJECTS ----------
pr = ['# Проекты', '', 'Каталог 26 репозиториев GitHub (V0van200) и что из них реально работает на серверах. Связи — `inventory/links.json` (поле confidence: насколько точно).', '',
      '| Проект | Тип | Репозиторий | Сервер | Сервисы / контейнеры | Домены | Базы | Точность |', '|---|---|---|---|---|---|---|---|']
used = set()
for gid, g in links['groups'].items():
    r = g.get('repo'); used.add(r)
    state = []
    for s in g.get('services', []):
        srv = g['server'] if g['server'] in servers else '78'
        found = next((x for x in servers.get(srv, {}).get('services', []) if x['name'] == s), None)
        state.append(f"{s} {'🟢' if found and found['state']=='active' else '🔴'}")
    state += [f"🐳{c}" for c in g.get('docker', [])]
    pr.append(f"| **{g['name']}** | {g['kind']} | {f'[{r}]({repos[r]['url']})' if r in repos else (r or '—')} | {g['server']} | {', '.join(state) or '—'} | {', '.join(g.get('domains', [])) or '—'} | {len(g.get('databases', []))} | {g['confidence']} |")
pr += ['', '## Репозитории без работающей части на серверах', ''] + [f"- **{k}** — {v}" for k, v in links['repos_without_runtime'].items()]
missing = [n for n in repos if n not in used and n not in links['repos_without_runtime']]
if missing: pr += ['', '## Не сопоставлены', ''] + [f"- {n}: {esc(repos[n].get('description'))}" for n in missing]
pr += ['', '## Все репозитории', '', '| Репозиторий | Видимость | Размер | Стек | Описание |', '|---|---|---|---|---|'] + [f"| [{r['name']}]({r['url']}) | {r['visibility']} | {size(r['size_kib']*1024)} | {esc(r.get('stack_from_readme_or_paths'))} | {esc(r.get('description'))} |" for r in repos.values()]
(DOCS / 'PROJECTS.md').write_text('\n'.join(pr) + '\n')

# ---------- граф для «Карты системы» ----------
nodes, edges = [], []
for srv, d in servers.items():
    nodes.append({'id': f'server:{srv}', 'type': 'server', 'label': f"Сервер {srv}", 'ip': d['host']['public_ip'], 'cpus': d['host']['cpus'], 'ram': d['host']['ram_total']})
    for s in d['services']:
        nodes.append({'id': f'service:{srv}:{s["name"]}', 'type': 'service', 'label': s['name'], 'state': s['state'], 'ports': [p[0] for p in s['ports']], 'memory': s['memory']})
        edges.append({'from': f'server:{srv}', 'to': f'service:{srv}:{s["name"]}', 'kind': 'runs'})
    for c in d['docker']:
        nodes.append({'id': f'docker:{srv}:{c["name"]}', 'type': 'container', 'label': c['name'], 'state': c['status']}); edges.append({'from': f'server:{srv}', 'to': f'docker:{srv}:{c["name"]}', 'kind': 'runs'})
    for site in d['nginx']:
        for n in site['names']:
            if n in ('_',) or site['redirect_only']: continue
            nid = f'domain:{n}'
            if not any(x['id'] == nid for x in nodes): nodes.append({'id': nid, 'type': 'domain', 'label': n, 'server': srv})
            for l in site['locations']:
                m = re.search(r'https?://(?:127\.0\.0\.1|localhost):(\d+)', l['proxy'] or '')
                own = port_owner(srv, int(m.group(1))) if m else None
                if own: edges.append({'from': nid, 'to': f'service:{srv}:{own}' if not own.startswith('docker:') else f'docker:{srv}:{own[7:]}', 'kind': 'routes', 'path': l['path']})
                elif (l['proxy'] or '').startswith('https://78.17.19.43'): edges.append({'from': nid, 'to': 'server:78', 'kind': 'proxies', 'path': l['path']})
    for db in d['databases']:
        if db['engine'] == 'postgres' and db['database'] == 'postgres': continue
        did = 'db:' + db_id(srv, db); nodes.append({'id': did, 'type': 'database', 'engine': db['engine'], 'label': os.path.basename(db.get('path') or '') or db.get('database') or db.get('container'), 'tables': len(db.get('tables', [])), 'rows': sum((t.get('rows') or 0) for t in db.get('tables', []))})
        edges.append({'from': f'server:{srv}', 'to': did, 'kind': 'stores'})
for gid, g in links['groups'].items():
    nodes.append({'id': f'project:{gid}', 'type': 'project', 'label': g['name'], 'kind': g['kind'], 'repo': g.get('repo'), 'repo_url': repos.get(g.get('repo') or '', {}).get('url'), 'confidence': g['confidence'], 'note': g.get('note')})
    srv = g['server'] if g['server'] in servers else '78'
    for s in g.get('services', []): edges.append({'from': f'project:{gid}', 'to': f'service:{srv}:{s}', 'kind': 'has'})
    for c in g.get('docker', []): edges.append({'from': f'project:{gid}', 'to': f'docker:{srv}:{c}', 'kind': 'has'})
    for dom in g.get('domains', []):
        if any(x['id'] == f'domain:{dom}' for x in nodes): edges.append({'from': f'project:{gid}', 'to': f'domain:{dom}', 'kind': 'has'})
    for dbk in g.get('databases', []):
        for x in nodes:
            if x['type'] == 'database' and (dbk.endswith(x['label']) or dbk.split(':')[-1] == x['label']): edges.append({'from': f'project:{gid}', 'to': x['id'], 'kind': 'uses'})
ids = {n['id'] for n in nodes}
edges = [e for e in edges if e['from'] in ids and e['to'] in ids]
json.dump({'generated_from': {k: v['collected_at'] for k, v in servers.items()}, 'nodes': nodes, 'edges': edges}, open(INV / 'system-graph.json', 'w'), ensure_ascii=False, indent=1)
print('docs ok:', len(dbs), 'баз,', len(nodes), 'узлов,', len(edges), 'связей')
