#!/usr/bin/env python3
"""Vovan OS — единая база всех проектов.
Вход:  catalog/spec.json (из чего состоит проект) + inventory/servers/*.json + inventory/folders/*.json + inventory/github-*.json
Выход: catalog/projects.json (одна база для хаба), catalog/README.md (оглавление), catalog/projects/<id>.md (карточки),
       catalog/UNASSIGNED.md (всё, что нашлось на серверах, но не входит ни в один проект — чтобы ничего не потерялось).
Запуск: python3 collector/build_catalog.py
"""
import json, glob, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INV, CAT = ROOT / 'inventory', ROOT / 'catalog'
spec = json.load(open(CAT / 'spec.json'))
servers = {Path(f).stem.replace('server-', ''): json.load(open(f)) for f in glob.glob(str(INV / 'servers' / '*.json'))}
folders = {Path(f).stem.replace('server-', ''): json.load(open(f))['folders'] for f in glob.glob(str(INV / 'folders' / '*.json'))}
repos = {r['name']: r for r in json.load(open(INV / 'github-repos.json'))}
gh = json.load(open(INV / 'github-readmes.json'))
(CAT / 'projects').mkdir(exist_ok=True)

def split(ref):
    srv, rest = ref.split(':', 1)
    return srv, rest
def size(n):
    if not n: return '—'
    for u in ['Б', 'КБ', 'МБ', 'ГБ']:
        if n < 1024: return f'{n:.0f} {u}' if u == 'Б' else f'{n:.1f} {u}'
        n /= 1024
    return f'{n:.1f} ТБ'
def db_key(srv, db):
    if db['engine'] == 'sqlite': return f"{srv}:{db['path']}"
    if db['engine'] == 'postgres': return f"{srv}:postgres:{db['database']}"
    return f"{srv}:redis:{db['container']}"
def db_doc(srv, db):
    if db['engine'] == 'sqlite': return 'docs/databases/' + re.sub(r'[^a-z0-9]+', '-', (srv + db['path']).lower()).strip('-') + '.md'
    return f"docs/databases/{srv}-{db['engine']}-{db.get('database') or db.get('container')}.md"

dbs = {db_key(s, db): (s, db) for s, d in servers.items() for db in d['databases']}
svcs = {f"{s}:{x['name']}": (s, x) for s, d in servers.items() for x in d['services']}
dock = {f"{s}:{c['name']}": (s, c) for s, d in servers.items() for c in d['docker']}
tims = {f"{s}:{t['timer']}": (s, t) for s, d in servers.items() for t in d['timers']}
fold = {f"{s}:{f['path']}": (s, f) for s, fs in folders.items() for f in fs}
nginx = [(s, site) for s, d in servers.items() for site in d['nginx'] if not site['redirect_only']]

def routes_for(domain):
    host = domain.split('/')[0].split(' ')[0]
    out = []
    for s, site in nginx:
        if host in site['names']:
            for l in site['locations']:
                if l['path'] == '/.well-known/acme-challenge/' or (l.get('return') or '').startswith('404'): continue
                out.append({'server': s, 'path': l['path'], 'to': l['proxy'] or l['root'] or l.get('return') or 'статика'})
            if site['root']: out.append({'server': s, 'path': '(корень)', 'to': site['root']})
    return out

used = {'folders': set(), 'services': set(), 'dbs': set(), 'repos': set(), 'docker': set()}
projects = []
for p in spec['projects']:
    e = {k: p.get(k) for k in ('id', 'name', 'category', 'tags', 'parent', 'note', 'people') if p.get(k) is not None}
    e['category_name'] = spec['categories'][p['category']]
    e['repos'] = []
    for r in p.get('repos', []):
        used['repos'].add(r); g = repos.get(r)
        e['repos'].append({'name': r, 'url': g['url'] if g else None, 'visibility': g and g['visibility'], 'size': g and g['size_kib'] * 1024,
                           'stack': g and g.get('stack_from_readme_or_paths'), 'description': g and g.get('description'),
                           'readme': gh['readmes'].get(r), 'root_files': gh['roots'].get(r), 'exists': bool(g)})
    e['folders'] = []
    for ref in p.get('paths', []):
        used['folders'].add(ref); s, path = split(ref); hit = fold.get(ref)
        if not hit:  # путь мог быть ссылкой на другую папку
            e['folders'].append({'server': s, 'path': path, 'missing': True}); continue
        f = hit[1]
        if f.get('broken_link_to'): e['folders'].append({'server': s, 'path': path, 'broken': True, 'was': f['broken_link_to']}); continue
        if f.get('link_to'):
            used['folders'].add(f"{s}:{f['link_to']}"); real = fold.get(f"{s}:{f['link_to']}")
            f = real[1] if real else f
        e['folders'].append({'server': s, 'path': path, 'real_path': f['path'] if f['path'] != path else None, 'size': f.get('size'), 'files': f.get('files'),
                             'last_change': f.get('last_change'), 'stack': f.get('stack'), 'package': (f.get('package') or {}).get('name'),
                             'description': (f.get('package') or {}).get('description'), 'readme': f.get('readme'), 'git': f.get('git'),
                             'docker': f.get('docker'), 'has_env_file': f.get('has_env_file'), 'top': f.get('top')})
    e['services'] = []
    for ref in p.get('services', []):
        used['services'].add(ref); hit = svcs.get(ref); s, n = split(ref)
        e['services'].append({'server': s, 'name': n, 'state': hit[1]['state'] if hit else 'not-found', 'ports': [x[0] for x in hit[1]['ports']] if hit else [],
                              'memory': hit[1]['memory'] if hit else None, 'since': hit[1]['since'] if hit else None, 'restarts': hit[1]['restarts'] if hit else None})
    e['docker'] = []
    for ref in p.get('docker', []):
        used['docker'].add(ref); hit = dock.get(ref); s, n = split(ref)
        e['docker'].append({'server': s, 'name': n, 'image': hit and hit[1]['image'], 'status': hit[1]['status'] if hit else 'not-found'})
    e['timers'] = [{'server': split(r)[0], 'timer': split(r)[1], 'last': (tims.get(r) or (0, {}))[1].get('last'), 'description': (tims.get(r) or (0, {}))[1].get('description')} for r in p.get('timers', [])]
    e['domains'] = [{'name': d, 'routes': routes_for(d)} for d in p.get('domains', [])]
    e['databases'] = []
    for ref in p.get('databases', []):
        used['dbs'].add(ref); hit = dbs.get(ref)
        if hit:
            s, db = hit; t = db.get('tables', [])
            e['databases'].append({'server': s, 'engine': db['engine'], 'name': db.get('path') or db.get('database') or db.get('container'), 'tables': len(t),
                                   'rows': sum((x.get('rows') or 0) for x in t), 'size': db.get('size'), 'doc': db_doc(s, db)})
        else:
            e['databases'].append({'ref': ref, 'missing': True})
    live = [f for f in e['folders'] if not f.get('broken') and not f.get('missing')]
    e['size_total'] = sum(f.get('size') or 0 for f in live)
    e['last_change'] = max([f['last_change'] for f in live if f.get('last_change')] or [None], key=lambda x: x or '')
    e['stack'] = sorted({x for f in live for x in (f.get('stack') or [])} | {r['stack'] for r in e['repos'] if r.get('stack')})
    running = [x for x in e['services'] if x['state'] == 'active'] + [x for x in e['docker'] if str(x['status']).startswith('Up')]
    served = [d for d in e['domains'] if d['routes']]
    broken = [f for f in e['folders'] if f.get('broken')]
    if running: e['status'], why = 'running', f"работает: {', '.join(x['name'] for x in running)}"
    elif served and p['category'] in ('site', 'app', 'game'): e['status'], why = 'live', 'сайт отдаётся: ' + ', '.join(d['name'] for d in served)
    elif live and any((f.get('size') or 0) > 4096 for f in live): e['status'], why = 'stopped', 'код есть на сервере, но не запущен'
    elif e['repos']: e['status'], why = 'repo-only', 'есть только в GitHub' + (' (локальные файлы удалены)' if broken else '')
    elif broken: e['status'], why = 'lost', 'папка удалена, репозитория не найдено'
    else: e['status'], why = 'empty', 'почти пусто'
    if p['category'] == 'idea' and e['status'] in ('repo-only', 'empty'): e['status'] = 'idea'
    e['status_reason'] = why
    stopped_svcs = [x for x in e['services'] if x['state'] != 'active']
    e['problems'] = ([f"сервис {x['name']} не работает ({x['state']})" for x in stopped_svcs] +
                     [f"папка {f['path']} удалена (была {f['was']})" for f in broken] +
                     [f"база {d['ref']} не найдена" for d in e['databases'] if d.get('missing')] +
                     [f"домен {d['name']} не настроен на серверах" for d in e['domains'] if not d['routes'] and '(' not in d['name']])
    e['links'] = {'github': [r['url'] for r in e['repos'] if r.get('url')], 'web': ['https://' + d['name'].split(' ')[0] for d in e['domains'] if d['routes'] and '.' in d['name'].split('/')[0]]}
    projects.append(e)

# всё, что не вошло ни в один проект
un = {'folders': [], 'services': [], 'databases': [], 'repos': [], 'docker': []}
for ref, (s, f) in fold.items():
    if ref in used['folders'] or f.get('link_to') and f"{s}:{f['link_to']}" in used['folders']: continue
    if any(ref.startswith(u + '/') for u in used['folders']): continue
    un['folders'].append({'ref': ref, 'size': f.get('size'), 'last_change': f.get('last_change'), 'broken': bool(f.get('broken_link_to')), 'readme': (f.get('readme') or '')[:160]})
un['services'] = [r for r in svcs if r not in used['services']]
un['databases'] = [r for r in dbs if r not in used['dbs'] and ':postgres:postgres' not in r]
un['repos'] = [r for r in repos if r not in used['repos']]
un['docker'] = [r for r in dock if r not in used['docker']]

STATUS = {'running': '🟢 работает', 'live': '🌐 сайт онлайн', 'stopped': '🟡 не запущен', 'repo-only': '📦 только GitHub', 'lost': '🔴 файлы потеряны', 'idea': '💡 идея/архив', 'empty': '⚪ пусто'}
summary = {k: sum(1 for p in projects if p['status'] == k) for k in STATUS}
json.dump({'generated_from': {s: d['collected_at'] for s, d in servers.items()}, 'statuses': STATUS, 'categories': spec['categories'], 'summary': summary,
           'projects': projects, 'unassigned': un}, open(CAT / 'projects.json', 'w'), ensure_ascii=False, indent=1)

md = ['# Все проекты', '', f"**{len(projects)} проектов**: " + ', '.join(f"{STATUS[k]} — {v}" for k, v in summary.items() if v) + '.', '',
      'Единая база для хаба — `catalog/projects.json` (формат — `catalog/SCHEMA.md`). Из чего состоит проект — `catalog/spec.json`; остальное собирается автоматически.', '']
for cat, title in spec['categories'].items():
    ps = [p for p in projects if p['category'] == cat]
    if not ps: continue
    md += [f'## {title}', '', '| Проект | Статус | Где | Сервисы | Базы | Размер | Изменён | Проблемы |', '|---|---|---|---|---|---|---|---|']
    for p in ps:
        where = ', '.join(sorted({f['server'] for f in p['folders'] if not f.get('broken')} | {s['server'] for s in p['services']})) or ('GitHub' if p['repos'] else '—')
        md.append(f"| [{p['name']}](projects/{p['id']}.md) | {STATUS[p['status']]} | {where} | {len(p['services']) + len(p['docker'])} | {len(p['databases'])} | {size(p['size_total'])} | {p['last_change'] or '—'} | {len(p['problems']) or ''} |")
    md.append('')
(CAT / 'README.md').write_text('\n'.join(md))

for p in projects:
    c = [f"# {p['name']}", '', f"**{p['category_name']}** · {STATUS[p['status']]} — {p['status_reason']}" + (f" · часть проекта [{p['parent']}]({p['parent']}.md)" if p.get('parent') else ''), '']
    if p.get('note'): c += [p['note'], '']
    if p.get('people'): c += ['**Кто работает:** ' + '; '.join(p['people']), '']
    if p['problems']: c += ['## ⚠ Проблемы', ''] + [f'- {x}' for x in p['problems']] + ['']
    if p['links']['web'] or p['links']['github']: c += ['## Ссылки', ''] + [f'- {u}' for u in p['links']['web'] + p['links']['github']] + ['']
    if p['services'] or p['docker']:
        c += ['## Что запущено', '', '| Сервис | Сервер | Состояние | Порты | Память |', '|---|---|---|---|---|']
        c += [f"| {s['name']} | {s['server']} | {s['state']} | {', '.join(map(str, s['ports'])) or '—'} | {size(s['memory'])} |" for s in p['services']]
        c += [f"| 🐳 {d['name']} | {d['server']} | {d['status']} | — | — |" for d in p['docker']] + ['']
    if p['domains']:
        c += ['## Домены', '']
        for d in p['domains']:
            c.append(f"- **{d['name']}**" + ('' if d['routes'] else ' — не настроен на серверах'))
            c += [f"  - `{r['path']}` → {r['to']} (сервер {r['server']})" for r in d['routes'][:12]]
        c.append('')
    if p['databases']:
        c += ['## Базы данных', '', '| База | Сервер | Движок | Таблиц | Строк | Схема |', '|---|---|---|---|---|---|']
        c += [f"| {d.get('name') or d.get('ref')} | {d.get('server', '—')} | {d.get('engine', '—')} | {d.get('tables', '—')} | {d.get('rows', '—')} | {f'[схема](../../{d['doc']})' if d.get('doc') else 'не найдена'} |" for d in p['databases']] + ['']
    if p['repos']:
        c += ['## Репозитории GitHub', '']
        for r in p['repos']:
            c += [f"### {r['name']}" + ('' if r['exists'] else ' (не найден на GitHub)'), '']
            if r.get('url'): c.append(f"{r['url']} · {r['visibility']} · {size(r['size'])} · {r.get('stack') or ''}")
            if r.get('description'): c.append(f"\n{r['description']}")
            if r.get('readme'): c += ['', '> ' + r['readme'].replace(' ⏎ ', '\n> ')]
            c.append('')
    if p['folders']:
        c += ['## Папки на серверах', '']
        for f in p['folders']:
            if f.get('broken'): c.append(f"- 🔴 `{f['server']}:{f['path']}` — **удалена** (вела в `{f['was']}`)"); continue
            if f.get('missing'): c.append(f"- ⚪ `{f['server']}:{f['path']}` — не найдена при сканировании"); continue
            c.append(f"- `{f['server']}:{f['path']}`" + (f" → `{f['real_path']}`" if f.get('real_path') else '') + f" — {size(f.get('size'))}, {f.get('files') or 0} файлов, изменена {f.get('last_change') or '—'}" + (f", стек: {', '.join(f['stack'])}" if f.get('stack') else '') + (', есть .env (значения не читались)' if f.get('has_env_file') else ''))
            if f.get('description'): c.append(f"  - {f['description']}")
            if f.get('readme'): c.append('  - README: ' + f['readme'][:400].replace(' ⏎ ', ' · '))
        c.append('')
    if p['timers']: c += ['## Регулярные задачи', ''] + [f"- {t['timer']} (сервер {t['server']}): {t.get('description') or ''}; последний запуск {t.get('last') or '—'}" for t in p['timers']] + ['']
    (CAT / 'projects' / f"{p['id']}.md").write_text('\n'.join(c))

u = ['# Не распределено по проектам', '', 'Всё, что нашлось на серверах и в GitHub, но не входит ни в один проект `catalog/spec.json`. Добавь в нужный проект — или оставь, если это служебное.', '']
if un['folders']: u += ['## Папки', ''] + [f"- `{x['ref']}` — {size(x['size'])}, изменена {x['last_change'] or '—'}" + (' 🔴 удалена' if x['broken'] else '') + (f" — {x['readme']}" if x['readme'] else '') for x in un['folders']] + ['']
for k, t in (('services', 'Сервисы'), ('docker', 'Контейнеры'), ('databases', 'Базы'), ('repos', 'Репозитории')):
    if un[k]: u += [f'## {t}', ''] + [f'- {x}' for x in un[k]] + ['']
(CAT / 'UNASSIGNED.md').write_text('\n'.join(u))
print('проектов', len(projects), summary, '| не распределено:', {k: len(v) for k, v in un.items()})
