#!/usr/bin/env python3
"""Vovan OS — живые данные для хаба. ТОЛЬКО ЧИТАЕТ, ничего не меняет на серверах.

  python3 live.py server [--push HOST:PATH]   состояние этого сервера (198 шлёт своё на 78 каждую минуту)
  python3 live.py build                       на 78: сервер 78 + присланный 198 + данные проектов →
                                              /data/vovan-os-hub/live/{snapshot.json, projects.json}

snapshot.json — тот же формат, что hub/site/snapshot.json, но сервисы, нагрузка, диски, контейнеры и таймеры —
на текущую минуту, а у каждого проекта каталога есть поле live (см. docs/LIVE.md).
В выход не попадают: IP-адреса посетителей, ключи, токены, тексты сообщений.
"""
import json, os, re, sqlite3, sys, time, glob, socket, subprocess, urllib.request, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import sh, services, timers, docker, certs, SYSTEM

NOW = time.time()
OUT = Path('/data/vovan-os-hub/live')
BASE_SNAPSHOT = Path('/var/www/vovan-os-hub/snapshot.json')
iso = lambda t=None: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW if t is None else t))

def ago(t):
    if not t: return 'никогда'
    s = int(NOW - t)
    if s < 90: return 'только что'
    if s < 3600: return f'{s // 60} мин назад'
    if s < 86400 * 2: return f'{s // 3600} ч назад'
    return f'{s // 86400} дн назад'

def M(label, value, hint=None, level=None):
    m = {'label': label, 'value': value}
    if hint: m['hint'] = hint
    if level: m['level'] = level      # ok | warn | bad
    return m

def ro(path):
    return sqlite3.connect(f'file:{path}?mode=ro', uri=True, timeout=3)

def tail(path, n):
    try: return Path(path).read_text(errors='ignore').splitlines()[-n:]
    except OSError: return []

def mtime(path):
    try: return os.path.getmtime(path)
    except OSError: return None

# ───────────────────────── сервер ─────────────────────────

def host_live():
    mem = dict(re.findall(r'(\w+):\s+(\d+) kB', Path('/proc/meminfo').read_text()))
    disks = []
    for line in sh('df -B1 --output=target,size,used,avail -x tmpfs -x devtmpfs -x squashfs -x overlay').splitlines()[1:]:
        t, size, used, avail = line.split()
        disks.append({'mount': t, 'size': int(size), 'used': int(used), 'avail': int(avail)})
    return {'hostname': socket.gethostname(), 'cpus': os.cpu_count(), 'ram_total': int(mem['MemTotal']) * 1024,
            'ram_available': int(mem['MemAvailable']) * 1024, 'swap_total': int(mem.get('SwapTotal', 0)) * 1024,
            'swap_free': int(mem.get('SwapFree', 0)) * 1024, 'load': list(os.getloadavg()),
            'uptime_s': int(float(Path('/proc/uptime').read_text().split()[0])), 'disks': disks}

def public_ports():
    out = set()
    for line in sh('ss -ltnupH').splitlines():
        f = line.split()
        if len(f) < 5: continue
        addr, _, port = f[4].rpartition(':')
        if addr in ('0.0.0.0', '*', '[::]') and port.isdigit():
            u = re.search(r'users:\(\("([^"]+)"', line)
            out.add((int(port), f[0], u.group(1) if u else '?'))
    return [{'port': p, 'proto': pr, 'proc': n} for p, pr, n in sorted(out)]

def security():
    jails = {}
    for j in re.findall(r'Jail list:\s*(.*)', sh('fail2ban-client status 2>/dev/null'))[:1]:
        for name in [x.strip() for x in j.split(',') if x.strip()]:
            st = sh(f'fail2ban-client status {name} 2>/dev/null')
            cur = re.search(r'Currently banned:\s*(\d+)', st); tot = re.search(r'Total banned:\s*(\d+)', st)
            jails[name] = {'banned_now': int(cur.group(1)) if cur else None, 'banned_total': int(tot.group(1)) if tot else None}
    ufw = sh('ufw status 2>/dev/null | head -1')
    failed = [u for u in (l.split()[0].removesuffix('.service') for l in sh('systemctl --failed --no-legend --plain').splitlines() if l.strip()) if not SYSTEM.match(u)]
    return {'fail2ban': jails, 'firewall': 'включён' if 'active' in ufw and 'inactive' not in ufw else ('выключен' if ufw else 'нет ufw'),
            'failed_units': failed, 'public_ports': public_ports()}

def ping(host):
    out = sh(f'ping -c 3 -i 0.3 -W 2 -q {host}', timeout=10)
    m = re.search(r'= [\d.]+/([\d.]+)/', out); loss = re.search(r'(\d+)% packet loss', out)
    return {'host': host, 'avg_ms': float(m.group(1)) if m else None, 'loss': int(loss.group(1)) if loss else 100}

def speed(cache):
    """Скорость скачивания: 10 МБ с Cloudflare, не чаще раза в час (кэш)."""
    try:
        c = json.loads(Path(cache).read_text())
        if NOW - c['at'] < 3600: return c
    except Exception: pass
    v = sh('curl -s -o /dev/null -m 30 -w "%{speed_download}" "https://speed.cloudflare.com/__down?bytes=10000000"', timeout=40)
    c = {'at': NOW, 'when': iso(), 'mbit': round(float(v) * 8 / 1e6, 1) if re.fullmatch(r'[\d.]+', v or '') else None}
    try: Path(cache).write_text(json.dumps(c))
    except OSError: pass
    return c

def net(other, cache):
    return {'ping_internet': ping('1.1.1.1'), 'ping_other_server': ping(other), 'download': speed(cache)}

# ── то, что есть только на сервере 198 ──
BOT_UA = re.compile(r'bot|crawl|spider|slurp|curl|wget|python|go-http|httpclient|scan|monitor|preview|facebookexternalhit|headless|java/|okhttp|axios|node-fetch|zgrab|masscan', re.I)
LOG_RE = re.compile(r'^(\S+) \S+ \S+ \[(\d\d)/(\w{3})/(\d{4}):[^\]]+\] "(\w+) ([^ ]*) [^"]*" (\d{3}) \d+ "([^"]*)" "([^"]*)"')
MON = {m: i for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(), 1)}

def site_visits(prefix='/var/log/nginx/eeklera.access.log'):
    """Посещения сайта по журналу nginx: только страницы (не файлы), без ботов. IP не выводятся — только счётчики."""
    import gzip
    days = {}; paths = {}; refs = {}; mobile = 0; pages_total = 0
    files = sorted(glob.glob(prefix + '*'), key=lambda f: -os.path.getmtime(f))[:31]
    for f in files:
        op = gzip.open if f.endswith('.gz') else open
        try:
            with op(f, 'rt', errors='ignore') as fh:
                for line in fh:
                    m = LOG_RE.match(line)
                    if not m: continue
                    ip, dd, mon, yy, meth, path, code, ref, ua = m.groups()
                    if meth != 'GET' or code not in ('200', '304') or BOT_UA.search(ua): continue
                    p = path.split('?')[0]
                    if re.search(r'\.\w{2,5}$', p) and not p.endswith('.html'): continue
                    day = f'{yy}-{MON[mon]:02d}-{dd}'
                    d = days.setdefault(day, {'views': 0, 'ips': set()}); d['views'] += 1; d['ips'].add(ip)
                    pages_total += 1; paths[p] = paths.get(p, 0) + 1
                    if 'Mobi' in ua or 'Android' in ua or 'iPhone' in ua: mobile += 1
                    host = re.sub(r'^https?://([^/]+).*', r'\1', ref) if ref.startswith('http') else ''
                    if host and 'eeklera.online' not in host: refs[host] = refs.get(host, 0) + 1
        except OSError: pass
    return {'since': min(days) if days else None, 'days': {k: {'views': v['views'], 'visitors': len(v['ips'])} for k, v in sorted(days.items())},
            'top_pages': sorted(paths.items(), key=lambda x: -x[1])[:8], 'top_refs': sorted(refs.items(), key=lambda x: -x[1])[:8],
            'mobile_share': round(mobile * 100 / pages_total) if pages_total else None}

def vpn_live():
    out = {}
    for itf in ('awg0', 'awg1'):
        dump = sh(f'awg show {itf} dump 2>/dev/null').splitlines()
        if not dump: continue
        peers = [l.split('\t') for l in dump[1:]]
        hs = [int(p[4]) for p in peers if len(p) > 6 and p[4].isdigit()]
        out[itf] = {'peers': len(peers), 'online': sum(1 for t in hs if t and NOW - t < 180),
                    'used_24h': sum(1 for t in hs if t and NOW - t < 86400), 'never': sum(1 for t in hs if not t),
                    'rx': sum(int(p[5]) for p in peers if len(p) > 6), 'tx': sum(int(p[6]) for p in peers if len(p) > 6)}
    out['xray'] = sh('systemctl is-active xray')
    return out

def extras_198():
    S = '/data/sites/eeklera-online'
    rel = os.path.basename(os.path.realpath(S + '/current'))
    log = []
    for r in sorted(os.listdir(S + '/releases'))[::-1][:8]:
        sha = r.rsplit('-', 1)[-1]
        msg = sh(f'git --git-dir={S}/repo.git log -1 --format=%s {sha} 2>/dev/null')[:120]
        log.append(f"{'▶ ' if r == rel else ''}{r[4:6]}.{r[6:8]} {r[9:11]}:{r[11:13]} · {sha} · {msg}")
    bfiles = [f for f in glob.glob('/data/backups/78.17.19.43/db/*') + glob.glob('/data/backups/78.17.19.43/snapshots/*')]
    return {'eeklera': {'release': rel, 'release_at': mtime(S + '/current'), 'deploy_log': log,
                        'pinned': os.path.exists(S + '/PINNED'), 'visits': site_visits()},
            'vpn': vpn_live(),
            'backup_78': {'files': len(bfiles), 'latest_at': max(map(os.path.getmtime, bfiles)) if bfiles else None}}

def server_live(sid):
    other = '198.13.184.145' if sid == '78' else '78.17.19.43'
    d = {'collected_at': iso(), 'host': host_live(), 'services': services(), 'timers': timers(), 'docker': docker(), 'certs': certs(),
         'security': security(), 'net': net(other, f'/var/tmp/vos-speed-{sid}.json')}
    if sid == '198': d['extra'] = extras_198()
    return d

# ───────────────────────── проекты (только на 78) ─────────────────────────

def http_check(url):
    t = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'VovanOS-monitor/1.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            return {'url': url, 'code': r.status, 'ms': int((time.time() - t) * 1000)}
    except urllib.error.HTTPError as e:
        return {'url': url, 'code': e.code, 'ms': int((time.time() - t) * 1000)}
    except Exception as e:
        return {'url': url, 'code': None, 'ms': None, 'error': type(e).__name__}

def deploy_history(path, n=6):
    out = []
    for l in reversed(tail(path, n)):
        m = re.match(r'(\S+ \S+) (\S+) (\S+) (.*)', l)
        if m: out.append({'when': m.group(1), 'state': m.group(2), 'sha': m.group(3)[:7], 'text': m.group(4)[:140]})
    return out

def dl(items): return [f"{'✓' if d['state'] == 'OK' else '⚠'} {d['when'][5:16]} · {d['sha']} · {d['text']}" for d in items]

def files_info(pattern):
    fs = [f for f in glob.glob(pattern) if os.path.isfile(f)]
    return len(fs), (max(map(os.path.getmtime, fs)) if fs else None)

def c_kabluk(p, ctx):
    db = ro('/var/lib/kabluk/kabluk.sqlite'); ms = NOW * 1000
    q = lambda s, *a: db.execute(s, a).fetchone()[0]
    total = q('select count(*) from players'); online = q('select count(*) from players where last_seen > ?', ms - 5 * 60e3)
    day = q('select count(*) from players where last_seen > ?', ms - 86400e3); new = q('select count(*) from players where created_at > ?', ms - 86400e3)
    tx = q('select count(*) from ledger where created_at > ?', ms - 86400e3)
    treasury = q("select coalesce(sum(balance),0) from accounts where owner_type='city'")
    biz = q('select count(*) from businesses'); parcels = q('select count(*) from parcels')
    players = db.execute('select nickname, last_seen from players order by last_seen desc limit 8').fetchall()
    hist = deploy_history('/data/kabluk/deploy/history.txt')
    nb, lb = files_info('/data/kabluk/backups/*')
    al = [] if not hist or hist[0]['state'] == 'OK' else [f"последний деплой: {hist[0]['state']}"]
    if lb and NOW - lb > 2 * 86400: al.append('бэкап базы старше 2 дней')
    return {'summary': f'{online} онлайн · {total} игроков', 'alerts': al,
            'metrics': [M('Онлайн сейчас', online, 'были в игре за 5 минут', 'ok' if online else None), M('Игроков всего', total), M('Заходили за сутки', day),
                        M('Новых за сутки', new), M('Операций в экономике за сутки', tx), M('Казна города', f'{treasury:,} ₽'.replace(',', ' ')),
                        M('Бизнесов / участков', f'{biz} / {parcels}'), M('Бэкапы базы', nb, f'последний {ago(lb)}', 'warn' if lb and NOW - lb > 2 * 86400 else 'ok')],
            'lists': [{'title': 'Игроки (последний заход)', 'items': [f'{n} — {ago(t / 1000)}' for n, t in players]},
                      {'title': 'Последние деплои', 'items': dl(hist)}]}

def c_kabluk_city(p, ctx):
    db = ro('/var/lib/kabluk/kabluk.sqlite')
    rows = db.execute('select nickname, population, level, last_at from pc_cities order by population desc limit 10').fetchall()
    return {'summary': f'{len(rows)} городов', 'metrics': [M('Городов игроков', len(rows)), M('Самый большой', f'{rows[0][1]} жителей' if rows else '—')],
            'lists': [{'title': 'Города', 'items': [f'{n}: {pop} жителей, уровень {lv}, был {ago(t / 1000)}' for n, pop, lv, t in rows]}]}

def c_terraria(p, ctx):
    started = sh("docker inspect -f '{{.State.StartedAt}}' terraria")
    logs = sh(f"docker logs --timestamps --since '{started}' terraria 2>&1 | grep -aE 'has joined|has left|on .* @ 0.0.0.0' | tail -n 4000", timeout=40)
    online = {}; last_join = None; title = None
    for raw in logs.splitlines():
        ts = raw.split(' ', 1)[0]
        clean = re.sub(r'\x1b\[[0-9;]*m|[\x07\r]', '', raw.split(' ', 1)[-1])
        for tt in re.findall(r'(\S+) - (\d+)/(\d+) on (.+?) @ 0\.0\.0\.0', clean): title = tt
        for seg in re.split(r'\x1b?\]0;.*?\(TShock for Terraria v[\d.]+\)', clean):
            m = re.match(r'\s*(.+?)(?: \([^()]*\))? has (joined|left)\.\s*$', seg)
            if not m: continue
            who, act = m.groups()
            if act == 'joined': online[who] = ts; last_join = ts
            else: online.pop(who, None)
    world = '/data/terraria/worlds/Lera.wld'; saved = mtime(world)
    nb, lb = files_info('/data/terraria/backups/*')
    users = chars = None
    try:
        tdb = ro('/data/terraria/config/tshock.sqlite')
        users = tdb.execute('select count(*) from Users').fetchone()[0]
        chars = tdb.execute('select count(*) from tsCharacter').fetchone()[0]
    except Exception: pass
    hist = deploy_history('/data/terraria/deploy/history.txt')
    count = len(online)
    return {'summary': f'{count} онлайн' + (f' · мир «{title[3]}»' if title else ''),
            'alerts': [] if not hist or hist[0]['state'] == 'OK' else [f"последний деплой: {hist[0]['state']}"],
            'metrics': [M('Онлайн сейчас', f"{count} / {title[2] if title else 8}", ', '.join(online) or None, 'ok' if count else None),
                        M('Последний вход', ago(_ts(last_join)) if last_join else 'с запуска не было'),
                        M('Сохранение мира', ago(saved), 'мир пишется при выходе игрока и автосохранении'),
                        M('Бэкапы', nb, f'последний {ago(lb)}'), M('Аккаунтов', users if users is not None else '—'),
                        M('Серверных персонажей (SSC)', chars if chars is not None else '—'), M('Сервер запущен', ago(_ts(started)))],
            'lists': [{'title': 'Сейчас в игре', 'items': [f'{w} — с {ago(_ts(t))}' for w, t in online.items()] or ['никого']},
                      {'title': 'Последние деплои плагинов', 'items': dl(hist)}]}

def _ts(s):
    try:
        from datetime import datetime
        return datetime.fromisoformat(s.rstrip('Z')[:26] + '+00:00').timestamp()
    except Exception: return None

def c_eeklera_site(p, ctx):
    e = (ctx['s198'].get('extra') or {}).get('eeklera') or {}
    v = e.get('visits') or {}; days = v.get('days') or {}
    today = time.strftime('%Y-%m-%d', time.gmtime(NOW))
    last = lambda n: [days[k] for k in days if k >= time.strftime('%Y-%m-%d', time.gmtime(NOW - (n - 1) * 86400))]
    s = lambda arr, k: sum(x[k] for x in arr)
    a_last = None
    try: a_last = ro('/home/claude/apps/eeklera-analytics/analytics.db').execute('select max(ts) from events').fetchone()[0]
    except Exception: pass
    al = []
    if a_last and NOW - a_last > 3 * 86400: al.append(f'аналитика EEKLERA не получает события с {time.strftime("%d.%m", time.gmtime(a_last))} — посещения считаются по журналу nginx')
    if e.get('pinned'): al.append('автовыкладка сайта заморожена (eeklera-deploy unpin)')
    rel = e.get('release') or '—'
    return {'summary': f"{days.get(today, {}).get('visitors', 0)} посетителей сегодня", 'alerts': al,
            'metrics': [M('Посетителей сегодня', days.get(today, {}).get('visitors', 0)), M('Просмотров сегодня', days.get(today, {}).get('views', 0)),
                        M('Посетителей за 7 дней', s(last(7), 'visitors'), 'сумма по дням'), M('Просмотров за 30 дней', s(last(30), 'views')),
                        M('С телефона', f"{v['mobile_share']}%" if v.get('mobile_share') is not None else '—'),
                        M('На сайте релиз', rel.split('-')[-1] if '-' in rel else rel, f"выложен {ago(e.get('release_at'))}")],
            'series': [{'title': 'Посетители по дням', 'points': [[k, d['visitors']] for k, d in days.items()]}],
            'lists': [{'title': 'Популярные страницы', 'items': [f'{p} — {n}' for p, n in v.get('top_pages', [])]},
                      {'title': 'Откуда приходят', 'items': [f'{h} — {n}' for h, n in v.get('top_refs', [])] or ['прямые заходы']},
                      {'title': 'Деплои сайта', 'items': e.get('deploy_log') or []}],
            'note': f"Счёт посетителей по журналу nginx с {v.get('since') or 'сегодня'}: страницы без ботов, уникальные устройства по дням.",
            'preview': 'https://eeklera.online/'}

def c_eeklera_services(p, ctx):
    db = ro('/home/claude/apps/eeklera-analytics/analytics.db')
    n, last = db.execute('select count(*), max(ts) from events').fetchone()
    return {'metrics': [M('Событий аналитики', n), M('Последнее событие', ago(last), level='warn' if last and NOW - last > 3 * 86400 else 'ok')]}

def c_video2md(p, ctx):
    try:
        st = json.loads(urllib.request.urlopen('http://127.0.0.1:3515/api/status', timeout=5).read())
        jobs = json.loads(urllib.request.urlopen('http://127.0.0.1:3515/api/jobs', timeout=5).read())
    except Exception as e:
        return {'summary': 'не отвечает', 'alerts': [f'API Video2MD не отвечает ({type(e).__name__})']}
    jobs = jobs if isinstance(jobs, list) else jobs.get('jobs', [])
    by = {}
    for j in jobs: by[j.get('status', '?')] = by.get(j.get('status', '?'), 0) + 1
    al = [] if st.get('key') else ['не задан ключ распознавания речи — новые видео не обработаются']
    return {'summary': f'{len(jobs)} задач', 'alerts': al,
            'metrics': [M('Задач всего', len(jobs)), M('По статусам', ', '.join(f'{k}: {v}' for k, v in by.items()) or '—'),
                        M('Модель распознавания', st.get('stt_model') or '—'), M('Ключ API', 'есть' if st.get('key') else 'нет', level='ok' if st.get('key') else 'bad'),
                        M('Свободно места', f"{st.get('disk_free_gb')} ГБ"), M('Макс. размер видео', f"{st.get('max_gb')} ГБ")],
            'lists': [{'title': 'Последние задачи', 'items': [f"{j.get('title') or j.get('name') or j.get('id')} — {j.get('status')}" for j in jobs[:8]] or ['задач пока нет']}]}

def pg(sql, container='sentra-postgres', db='sentra'):
    out = sh(f"""docker exec -i {container} sh -c 'psql -U "$POSTGRES_USER" -d {db} -AtF "|" -q'""", timeout=20, inp=sql)
    return [l.split('|') for l in out.splitlines() if l]

def c_sentra(p, ctx):
    r = pg("""select (select count(*) from chats), (select count(*) from bots), (select count(*) from bots where status='active'),
              (select count(*) from tg_users), (select count(*) from chat_members),
              (select count(*) from user_messages where ts > now() - interval '1 day'),
              (select coalesce(sum(count),0) from message_stats where day > current_date - 7),
              (select count(*) from mod_actions where created_at > now() - interval '7 days');""")
    if not r: return {'alerts': ['база Sentra не отвечает']}
    chats, bots, bots_on, users, members, msg24, msg7, mods = r[0]
    top = pg("""select coalesce(c.title, s.chat_id::text), sum(s.count) from message_stats s left join chats c on c.chat_id = s.chat_id
                where s.day > current_date - 7 group by 1 order by 2 desc limit 6;""")
    return {'summary': f'{chats} чатов · {msg24} сообщений за сутки',
            'metrics': [M('Чатов', chats), M('Ботов (активных)', f'{bots} ({bots_on})'), M('Пользователей Telegram', users), M('Участников в чатах', members),
                        M('Сообщений за сутки', msg24), M('Сообщений за 7 дней', msg7), M('Действий модерации за 7 дней', mods)],
            'lists': [{'title': 'Самые активные чаты за неделю', 'items': [f'{t} — {n}' for t, n in top]}]}

def c_vpn(p, ctx):
    v = (ctx['s198'].get('extra') or {}).get('vpn') or {}
    a = v.get('awg0') or {}
    gb = lambda b: f'{b / 1e9:.1f} ГБ'
    al = [] if v.get('xray') == 'active' else ['xray на 198 не работает']
    return {'summary': f"{a.get('online', 0)} подключено", 'alerts': al,
            'metrics': [M('Подключено сейчас', a.get('online', 0), 'устройства с активной связью за 3 минуты', 'ok'), M('Пользовались за сутки', a.get('used_24h', 0)),
                        M('Ключей выдано', a.get('peers', 0)), M('Ни разу не подключались', a.get('never', 0)),
                        M('Трафик (с запуска)', f"↓ {gb(a.get('tx', 0))} · ↑ {gb(a.get('rx', 0))}"), M('Xray', v.get('xray', '—'))]}

def c_ops(p, ctx):
    al = []; ms = []; lst = []
    for sid, s in (('78', ctx['s78']), ('198', ctx['s198'])):
        sec = s.get('security') or {}; n = s.get('net') or {}; h = s.get('host') or {}
        ban = sum((j.get('banned_now') or 0) for j in (sec.get('fail2ban') or {}).values())
        ms += [M(f'{sid}: пинг до интернета', f"{n.get('ping_internet', {}).get('avg_ms')} мс"),
               M(f'{sid}: скорость скачивания', f"{n.get('download', {}).get('mbit')} Мбит/с", f"замер {ago(n.get('download', {}).get('at'))}"),
               M(f'{sid}: заблокировано fail2ban', ban), M(f'{sid}: файрвол', sec.get('firewall', '—'), level='ok' if sec.get('firewall') == 'включён' else 'warn'),
               M(f'{sid}: открытых портов наружу', len(sec.get('public_ports') or []))]
        lst.append({'title': f'Сервер {sid}: открытые наружу порты', 'items': [f"{x['port']}/{x['proto']} — {x['proc']}" for x in sec.get('public_ports') or []]})
        if sec.get('failed_units'): al.append(f"{sid}: упавшие службы — {', '.join(sec['failed_units'])}")
        for d in h.get('disks') or []:
            if d['size'] and d['used'] / d['size'] > 0.9: al.append(f"{sid}: диск {d['mount']} заполнен на {round(d['used'] * 100 / d['size'])}%")
        for c in s.get('certs') or []:
            try:
                left = (time.mktime(time.strptime(c['expires'], '%b %d %H:%M:%S %Y %Z')) - NOW) / 86400
                if left < 14: al.append(f"{sid}: сертификат {c['name']} истекает через {int(left)} дн")
            except Exception: pass
    b = (ctx['s198'].get('extra') or {}).get('backup_78') or {}
    ms.append(M('Копия 78 на сервере 198', ago(b.get('latest_at')), f"{b.get('files', 0)} файлов", 'ok' if b.get('latest_at') and NOW - b['latest_at'] < 2 * 86400 else 'bad'))
    if not b.get('latest_at') or NOW - b['latest_at'] > 2 * 86400: al.append('ночная копия сервера 78 на 198 старше 2 дней')
    return {'summary': f'{len(al)} предупреждений' if al else 'всё в порядке', 'alerts': al, 'metrics': ms, 'lists': lst}

def c_vovan_os(p, ctx):
    rel = os.path.basename(os.path.realpath('/var/www/vovan-os-hub'))
    return {'metrics': [M('Хаб на сайте', rel.split('-')[-1], f'выложен {ago(mtime("/var/www/vovan-os-hub"))}'), M('Живые данные', 'обновляются каждую минуту', level='ok')],
            'lists': [{'title': 'Выкладки хаба', 'items': [l[:150] for l in reversed(tail('/data/vovan-os-hub/history.log', 5))]}]}

CONNECTORS = {'kabluk': c_kabluk, 'kabluk-city': c_kabluk_city, 'terraria': c_terraria, 'eeklera-site': c_eeklera_site,
              'eeklera-services': c_eeklera_services, 'video2md': c_video2md, 'sentra': c_sentra, 'vpn': c_vpn, 'ops': c_ops, 'vovan-os': c_vovan_os}

def generic(p, live_svc, live_dock, checks):
    ms, al = [], []
    # ждём работающими только то, что работало при инвентаризации (oneshot-задачи таймеров не в счёт)
    exp_s = [s for s in p['services'] if s.get('base_state') == 'active']
    exp_d = [d for d in p['docker'] if str(d.get('base_status', '')).startswith('Up')]
    svcs = [live_svc.get((s['server'], s['name'])) or {'name': s['name'], 'state': 'not-found'} for s in exp_s]
    docks = [live_dock.get((d['server'], d['name'])) or {'name': d['name'], 'status': 'not-found'} for d in exp_d]
    up = [s for s in svcs if s.get('state') == 'active'] + [d for d in docks if str(d.get('status', '')).startswith('Up')]
    if svcs or docks:
        ms.append(M('Запущено', f'{len(up)} из {len(svcs) + len(docks)}', level='ok' if len(up) == len(svcs) + len(docks) else ('bad' if not up else 'warn')))
        mem = sum(s.get('memory') or 0 for s in svcs)
        if mem: ms.append(M('Память', f'{mem / 2**20:.0f} МБ'))
        rs = sum(s.get('restarts') or 0 for s in svcs)
        if rs: ms.append(M('Перезапусков', rs, level='warn' if rs > 5 else None))
    for s in svcs:
        if s.get('state') != 'active': al.append(f"сервис {s['name']} сейчас не работает ({s.get('state')})")
    for d in docks:
        if not str(d.get('status', '')).startswith('Up'): al.append(f"контейнер {d['name']} не работает ({d.get('status')})")
    for c in checks:
        ok = c.get('code') and c['code'] < 400 or c.get('code') in (401, 403)
        ms.append(M(c['url'].replace('https://', ''), f"{c.get('code') or 'нет ответа'} · {c['ms']} мс" if c.get('ms') is not None else 'нет ответа', level='ok' if ok else 'bad'))
        if not ok: al.append(f"{c['url']} не отвечает ({c.get('code') or c.get('error')})")
    return ms, al

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    snap = json.loads(BASE_SNAPSHOT.read_text())
    s78 = server_live('78'); (OUT / 'server-78.json').write_text(json.dumps(s78, ensure_ascii=False, default=str))
    try: s198 = json.loads((OUT / 'server-198.json').read_text())
    except Exception: s198 = {}
    stale198 = not s198 or NOW - (mtime(OUT / 'server-198.json') or 0) > 300
    ctx = {'s78': s78, 's198': s198}
    for sid, live in (('78', s78), ('198', s198)):
        srv = snap['servers'].get(sid)
        if not srv or not live: continue
        srv['collected_at'] = live['collected_at']; srv['host'] = {**srv['host'], **live['host']}
        for k in ('services', 'timers', 'docker', 'certs'): srv[k] = live[k]
        srv['live'] = {'security': live.get('security'), 'net': live.get('net'), 'stale': sid == '198' and stale198}
    live_svc = {(sid, s['name']): s for sid, l in (('78', s78), ('198', s198)) for s in l.get('services', [])}
    live_dock = {(sid, d['name']): d for sid, l in (('78', s78), ('198', s198)) for d in l.get('docker', [])}
    urls = sorted({u for p in snap['catalog']['projects'] for u in p['links']['web'] if p['status'] in ('running', 'live')})
    with cf.ThreadPoolExecutor(8) as ex: checks = dict(zip(urls, ex.map(http_check, urls)))
    projects = {}
    for p in snap['catalog']['projects']:
        for s in p['services']:
            s['base_state'] = s.get('state'); l = live_svc.get((s['server'], s['name']))
            if l: s.update(state=l['state'], memory=l['memory'], since=l['since'], restarts=l['restarts'])
        for d in p['docker']:
            d['base_status'] = d.get('status'); l = live_dock.get((d['server'], d['name']))
            if l: d['status'] = l['status']
        ms, al = generic(p, live_svc, live_dock, [checks[u] for u in p['links']['web'] if u in checks])
        live = {'updated': iso(), 'metrics': [], 'alerts': [], 'lists': []}
        fn = CONNECTORS.get(p['id'])
        if fn:
            try: live.update({k: v for k, v in fn(p, ctx).items()})
            except Exception as e: live['alerts'] = [f'источник данных не прочитан: {type(e).__name__}: {str(e)[:120]}']
            live['connected'] = True
        else: live['connected'] = False
        live['metrics'] = live.get('metrics', []) + ms; live['alerts'] = live.get('alerts', []) + al
        p['live'] = live; projects[p['id']] = live
    snap['source']['live_at'] = iso(); snap['source']['mode'] = 'live'
    for name, obj in (('snapshot.json', snap), ('projects.json', {'updated': iso(), 'projects': projects})):
        tmp = OUT / (name + '.tmp'); tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':'), default=str)); tmp.replace(OUT / name)
    print(f"live ok: {sum(1 for x in projects.values() if x['connected'])} проектов с источниками, {len(checks)} сайтов проверено, 198 {'устарел' if stale198 else 'свежий'}")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if mode == 'server':
        sid = '78' if socket.gethostname().startswith('VM-379167') or os.path.exists('/data/kabluk') else '198'
        data = json.dumps(server_live(sid), ensure_ascii=False, default=str)
        if '--push' in sys.argv:
            host, path = sys.argv[sys.argv.index('--push') + 1].split(':', 1)
            r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', host, f'cat > {path}.tmp && mv {path}.tmp {path}'],
                               input=data, capture_output=True, text=True, timeout=60)
            sys.exit(r.returncode)
        print(data)
    else:
        build()
