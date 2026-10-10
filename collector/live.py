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
    out['keys'], out['traffic'] = vpn_keys_history()
    return out

VPN_DB = '/var/lib/vovan-os/vpn.sqlite'   # почасовые приросты трафика по ключам (десятки КБ)

def _awg_counters():
    res = {}
    for line in sh('awg show awg0 dump 2>/dev/null').splitlines()[1:]:
        p = line.split('\t')
        if len(p) >= 7: res[p[3].split('/')[0]] = (int(p[5]), int(p[6]), int(p[4]) if p[4].isdigit() else 0)
    return res

def vpn_keys_history():
    """Счётчики AmneziaWG знают только «с перезапуска». Раз в минуту копим приросты по часам → 1 ч / 24 ч / 7 / 30 дней / всего;
    скорость «сейчас» — два замера с разницей 2 с. Ключи шифрования наружу не выдаются, только имена и цифры."""
    names = {'10.9.0.3': 'основной (твоё устройство)', '10.9.0.2': 'key-2 (первый)'}
    for f in glob.glob('/root/amnezia-clients/*.conf'):
        m = re.search(r'^Address\s*=\s*([\d.]+)', Path(f).read_text(errors='ignore'), re.M)
        if m: names[m.group(1)] = Path(f).stem
    a = _awg_counters(); time.sleep(2); b = _awg_counters(); now = time.time()
    os.makedirs(os.path.dirname(VPN_DB), exist_ok=True)
    db = sqlite3.connect(VPN_DB, timeout=5)
    db.executescript("""CREATE TABLE IF NOT EXISTS last(ip TEXT PRIMARY KEY, rx INT, tx INT, ts REAL);
                        CREATE TABLE IF NOT EXISTS hourly(hour INT, ip TEXT, rx INT, tx INT, PRIMARY KEY(hour, ip));
                        CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);""")
    db.execute("INSERT OR IGNORE INTO meta VALUES('since', ?)", (str(int(now)),))
    hour = int(now // 3600)
    for ip, (rx, tx, _) in b.items():
        row = db.execute('SELECT rx, tx FROM last WHERE ip=?', (ip,)).fetchone()
        if row:
            drx = rx - row[0] if rx >= row[0] else rx      # счётчик сбросился (перезапуск VPN) — считаем с нуля
            dtx = tx - row[1] if tx >= row[1] else tx
            if drx or dtx:
                db.execute('INSERT INTO hourly VALUES(?,?,?,?) ON CONFLICT(hour, ip) DO UPDATE SET rx=rx+excluded.rx, tx=tx+excluded.tx', (hour, ip, drx, dtx))
        db.execute('INSERT OR REPLACE INTO last VALUES(?,?,?,?)', (ip, rx, tx, now))
    db.execute('DELETE FROM hourly WHERE hour < ?', (hour - 24 * 90,))
    db.commit()
    since = int(db.execute("SELECT v FROM meta WHERE k='since'").fetchone()[0])
    def period(ip, hours):
        q = 'SELECT COALESCE(SUM(rx),0), COALESCE(SUM(tx),0) FROM hourly WHERE ip=?' + (' AND hour > ?' if hours else '')
        return db.execute(q, (ip, hour - hours) if hours else (ip,)).fetchone()
    keys, tot = [], {'h1': 0, 'd1': 0, 'd7': 0, 'd30': 0, 'all': 0, 'down_bps': 0, 'up_bps': 0}
    for ip, (rx, tx, hs) in b.items():
        prx, ptx, _ = a.get(ip, (rx, tx, 0))
        down, up = max(0, tx - ptx) / 2, max(0, rx - prx) / 2        # tx сервера = скачано клиентом, rx = отправлено клиентом
        stats = {k: sum(period(ip, h)) for k, h in (('h1', 1), ('d1', 24), ('d7', 168), ('d30', 720), ('all', 0))}
        hist = {r[0]: r[1] + r[2] for r in db.execute('SELECT hour, rx, tx FROM hourly WHERE ip=? AND hour > ?', (ip, hour - 24))}
        keys.append({'name': names.get(ip, ip), 'ip': ip, 'last': hs or None, 'online': bool(hs and now - hs < 180),
                     'rx': rx, 'tx': tx, 'down_bps': down, 'up_bps': up, **stats,
                     'hours24': [hist.get(h, 0) for h in range(hour - 23, hour + 1)]})
        for k in ('h1', 'd1', 'd7', 'd30', 'all'): tot[k] += stats[k]
        tot['down_bps'] += down; tot['up_bps'] += up
    tot['since'] = since
    tot['hours24'] = [sum(k['hours24'][i] for k in keys) for i in range(24)]
    db.close()
    return sorted(keys, key=lambda k: -(k['rx'] + k['tx'])), tot

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


def ai_costs(path='/root/.claude/metrics/costs.jsonl'):
    rows = []
    for line in tail(path, 20000):
        try:
            r = json.loads(line); rows.append((r['session_id'], r['timestamp'], float(r['estimated_cost_usd'])))
        except Exception: continue
    if not rows: return None
    rows.sort(key=lambda r: (r[0], r[1])); last = {}; by_day = {}
    for sid, ts, cost in rows:
        delta = max(0.0, cost - last.get(sid, 0.0)); last[sid] = cost
        by_day[ts[:10]] = by_day.get(ts[:10], 0.0) + delta
    day = lambda k: time.strftime('%Y-%m-%d', time.gmtime(NOW - k * 86400))
    s = lambda n: round(sum(v for d, v in by_day.items() if d >= day(n - 1)), 2)
    return {'today': s(1), 'week': s(7), 'month': s(30), 'since': min(by_day), 'sessions': len(last),
            'days': [[d, round(by_day.get(d, 0.0), 2)] for d in (day(k) for k in range(13, -1, -1))]}

def server_live(sid):
    other = '198.13.184.145' if sid == '78' else '78.17.19.43'
    d = {'collected_at': iso(), 'host': host_live(), 'services': services(), 'timers': timers(), 'docker': docker(), 'certs': certs(),
         'security': security(), 'net': net(other, f'/var/tmp/vos-speed-{sid}.json'), 'ai_costs': ai_costs()}
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

def _wld_header(path):
    """Шапка файла мира Terraria: имя, сид, размер, режим, особые миры. Только чтение начала файла."""
    import struct
    with open(path, 'rb') as f:
        ver = struct.unpack('<i', f.read(4))[0]
        f.read(8 + 4 + 8)                                   # relogic + тип, ревизия, избранное
        n = struct.unpack('<h', f.read(2))[0]; pos = struct.unpack(f'<{n}i', f.read(4 * n))
        f.seek(pos[0])
        def s():
            ln, shift = 0, 0
            while True:
                b = f.read(1)[0]; ln |= (b & 0x7F) << shift; shift += 7
                if b < 0x80: break
            return f.read(ln).decode('utf-8', 'replace')
        name, seed = s(), s(); f.read(8 + 16); wid = struct.unpack('<i', f.read(4))[0]; f.read(16)
        h, w, mode = struct.unpack('<iii', f.read(12))
        flags = list(f.read(8))
    special = [n for n, v in zip(['пьяный мир', 'for the worthy', '10-летие', "don't starve", 'not the bees', 'remix', 'без ловушек', 'zenith'], flags) if v == 1]
    size = {4200: 'маленький', 6400: 'средний', 8400: 'большой'}.get(w, 'свой')
    return {'version': ver, 'name': name, 'seed': seed, 'id': wid, 'width': w, 'height': h, 'size': size,
            'mode': {0: 'обычная', 1: 'эксперт', 2: 'мастер', 3: 'путешествие'}.get(mode, str(mode)), 'special': special}

def c_terraria(p, ctx):
    started = sh("docker inspect -f '{{.State.StartedAt}}' terraria")
    running = sh("docker inspect -f '{{.State.Running}}' terraria") == 'true'
    logs = sh(f"docker logs --timestamps --since '{started}' terraria 2>&1 | grep -aE 'has joined|has left|authenticated successfully|registered an account|on .* @ 0.0.0.0' | tail -n 4000", timeout=40) if running else ''
    online = {}; last_join = None; acct = {}; events = []
    for raw in logs.splitlines():
        ts = raw.split(' ', 1)[0]
        clean = re.sub(r'\x1b\[[0-9;]*m|[\x07\r]', '', raw.split(' ', 1)[-1])
        for seg in re.split(r'\x1b?\]0;.*?\(TShock for Terraria v[\d.]+\)', clean):
            seg = seg.strip()
            m = re.match(r'(.+?)(?: \([^()]*\))? has (joined|left)\.$', seg)
            if m:
                who, act = m.groups()
                if act == 'joined': online[who] = ts; last_join = ts; events.append((ts, f'{who} зашёл'))
                else: online.pop(who, None); acct.pop(who, None); events.append((ts, f'{who} вышел'))
                continue
            m = re.match(r'(.+?) authenticated successfully as user: (.+?)\.$', seg)
            if m: acct[m.group(1)] = m.group(2); events.append((ts, f'{m.group(1)} вошёл в аккаунт {m.group(2)}')); continue
            m = re.match(r'(.+?) registered an account: "(.+?)"\.?$', seg)
            if m: events.append((ts, f'{m.group(1)} зарегистрировал аккаунт {m.group(2)}'))
    world_file = '/data/terraria/worlds/Lera.wld'; saved = mtime(world_file)
    try: w = _wld_header(world_file)
    except Exception: w = {}
    nb, lb = files_info('/data/terraria/backups/*')
    cfg = {}
    try: cfg = json.loads(Path('/data/terraria/config/config.json').read_text())['Settings']
    except Exception: pass
    accounts = []
    try:
        tdb = ro('/data/terraria/config/tshock.sqlite')
        prof = {}
        try: prof = json.loads(Path(f"/data/terraria/config/lera-adventure-{w.get('id')}.json").read_text()).get('Profiles', {})
        except Exception: pass
        for uid, name, grp, reg, last, hp, mhp, mana, mmana, deaths in tdb.execute(
                'select u.ID, u.Username, u.Usergroup, u.Registered, u.LastAccessed, c.Health, c.MaxHealth, c.Mana, c.MaxMana, c.deathsPVE '
                'from Users u left join tsCharacter c on c.Account = u.ID order by u.LastAccessed desc'):
            pr = prof.get(str(uid)) or {}
            accounts.append({'name': name, 'group': grp, 'registered': reg, 'last': last, 'hp': hp, 'max_hp': mhp, 'mana': mana, 'max_mana': mmana,
                             'deaths': deaths, 'xp': pr.get('Experience'), 'expeditions': pr.get('Completed'),
                             'online': name in acct.values(), 'ssc_bypass': grp == 'superadmin'})
    except Exception: pass
    hist = deploy_history('/data/terraria/deploy/history.txt')
    pinned = os.path.exists('/data/terraria/deploy/PINNED')
    al = [] if not hist or hist[0]['state'] == 'OK' else [f"последний деплой: {hist[0]['state']}"]
    if not running: al.append('сервер Terraria остановлен')
    if pinned: al.append('автодеплой плагинов заморожен (terraria-deploy unpin)')
    for a in accounts:
        if a['ssc_bypass']: al.append(f"аккаунт {a['name']} в группе superadmin — его вещи не сохраняются (SSC обходится)")
    world = {'name': w.get('name'), 'seed': w.get('seed'), 'size': f"{w.get('size')} {w.get('width')}×{w.get('height')}" if w else None,
             'mode': w.get('mode'), 'special': w.get('special'), 'saved': iso(saved) if saved else None,
             'spawn_protection': cfg.get('SpawnProtectionRadius') if cfg.get('SpawnProtection') else 0,
             'require_login': cfg.get('RequireLogin'), 'address': '78.17.19.43:7777', 'max_players': cfg.get('MaxSlots') or 8}
    count = len(online)
    return {'summary': f'{count} онлайн' + (f" · мир «{w['name']}»" if w.get('name') else ''), 'alerts': al, 'world': world, 'accounts': accounts,
            'online_names': [f"{k} ({acct[k]})" if k in acct else k for k in online],
            'metrics': [M('Онлайн сейчас', f"{count} / {world['max_players']}", ', '.join(online) or None, 'ok' if count else None),
                        M('Мир', w.get('name') or '—', f"{world['size']} · сложность {w.get('mode')}" + (f" · {', '.join(w['special'])}" if w.get('special') else '') if w else None),
                        M('Сид', w.get('seed') or '—'),
                        M('Последний вход', ago(_ts(last_join)) if last_join else 'с запуска не было'),
                        M('Сохранение мира', ago(saved), 'при выходе игрока и автосохранении'),
                        M('Аккаунтов', len(accounts)), M('Защита спавна', f"{world['spawn_protection']} блоков" if world['spawn_protection'] else 'выключена'),
                        M('Вход по паролю', 'обязателен' if cfg.get('RequireLogin') else 'нет', level='ok' if cfg.get('RequireLogin') else 'warn'),
                        M('Бэкапы', nb, f'последний {ago(lb)}'), M('Сервер запущен', ago(_ts(started)) if running else 'остановлен', level=None if running else 'bad')],
            'lists': [{'title': 'Сейчас в игре', 'items': [f'{w_} — с {ago(_ts(t_))}' for w_, t_ in online.items()] or ['никого']},
                      {'title': 'Игроки', 'items': [f"{a['name']} · {a['group']} · ❤ {a['hp']}/{a['max_hp']} · ★ {a['mana']}/{a['max_mana']} · смертей {a['deaths'] or 0} · был {ago(_ts(a['last']))}" for a in accounts]},
                      {'title': 'События с запуска сервера', 'items': [f"{t_[5:16].replace('T', ' ')} · {e_}" for t_, e_ in events[-12:][::-1]]},
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


# ───────────────────────── для владельца: внимание, деньги, здоровье ─────────────────────────
def _cert_days(exp):
    try: return int((time.mktime(time.strptime(' '.join(exp.split()), '%b %d %H:%M:%S %Y %Z')) - NOW) // 86400)
    except Exception: return None

def _last_deploy(path):
    lines = [l for l in tail(path, 5) if l.strip()]
    return lines[-1] if lines else None

def owner_view(s78, s198, stale198, projects, catalog):
    att = []
    add = lambda level, title, detail='', where='': att.append({'level': level, 'title': title, 'detail': detail, 'where': where})
    if stale198: add('bad', 'Сервер 198 не присылает данные', 'больше 5 минут нет свежих данных — VPN и eeklera.online не видны', '198')
    health = []
    for sid, s in (('78', s78), ('198', s198)):
        h = s.get('host') or {}
        if not h: continue
        root = next((d for d in h.get('disks', []) if d['mount'] == '/'), None)
        disk = round(100 * root['used'] / root['size']) if root and root['size'] else None
        ram = round(100 * (1 - h['ram_available'] / h['ram_total'])) if h.get('ram_total') else None
        swap = round(100 * (1 - h['swap_free'] / h['swap_total'])) if h.get('swap_total') else None
        load = round(h['load'][0] / max(1, h.get('cpus') or 1) * 100) if h.get('load') else None
        svcs = s.get('services', []); failed = [x for x in (s.get('security') or {}).get('failed_units', [])]
        health.append({'id': sid, 'name': 'Основной (78)' if sid == '78' else 'VPN и сайт (198)', 'cpus': h.get('cpus'), 'load': load,
                       'ram': ram, 'ram_total': h.get('ram_total'), 'swap': swap, 'disk': disk, 'disk_free': root and root['avail'],
                       'uptime_s': h.get('uptime_s'), 'services': len(svcs), 'services_down': sum(1 for x in svcs if x.get('state') != 'active'),
                       'docker': len(s.get('docker', [])), 'failed': failed,
                       'banned': ((s.get('security') or {}).get('fail2ban') or {}).get('sshd', {}).get('banned_now')})
        if disk is not None and disk >= 85: add('bad' if disk >= 93 else 'warn', f'Диск сервера {sid} заполнен на {disk}%', f'свободно {round(root["avail"] / 1e9, 1)} ГБ', sid)
        if ram is not None and ram >= 90: add('warn', f'Память сервера {sid} занята на {ram}%', '', sid)
        if swap is not None and swap >= 75: add('warn', f'Подкачка сервера {sid} занята на {swap}%', 'сервер упирается в память — возможны тормоза', sid)
        if load is not None and load >= 150: add('warn', f'Сервер {sid} перегружен', f'нагрузка {load}% от процессоров', sid)
        for u in failed: add('bad', f'Служба {u} упала', f'сервер {sid}', sid)
        for c in s.get('certs', []):
            d = _cert_days(c.get('expires', ''))
            if d is not None and d < 21: add('bad' if d < 7 else 'warn', f'Сертификат {c["name"]} истекает через {d} дн', ', '.join(c.get('domains', [])[:3]), sid)
    deploys = []
    for name, path in (('CoreHub', '/data/corehub/deploy/history.txt'), ('Kabluk', '/data/kabluk/deploy/history.txt'),
                       ('Terraria', '/data/terraria/deploy/history.txt'), ('Хаб Vovan OS', '/data/vovan-os-hub/history.log')):
        l = _last_deploy(path)
        if not l: continue
        deploys.append({'name': name, 'line': l[:160]})
        if re.search(r'FAILED|ROLLED BACK|упал|откат', l): add('bad', f'Последний деплой {name} не прошёл', l[20:140], '78')
    x = (s198.get('extra') or {})
    vpn = x.get('vpn') or {}
    if s198 and vpn.get('xray') not in (None, 'active'): add('bad', 'VPN xray не работает', f'состояние: {vpn.get("xray")}', '198')
    b = (x.get('backup_78') or {}).get('latest_at')
    if s198 and (not b or NOW - b > 36 * 3600): add('warn', 'Бэкап сервера 78 старше 36 часов', f'последний: {ago(b)}', '198')
    names = {p['id']: p.get('name', p['id']) for p in catalog}
    xray_flagged = any('xray' in a['title'] for a in att)
    for pid, l in projects.items():
        for a in l.get('alerts', [])[:3]:
            if xray_flagged and 'xray' in a: continue          # уже есть общая тревога про xray
            add('warn', names.get(pid, pid), a, 'проект')
    seen = set(); att[:] = [a for a in att if not ((a['title'], a['detail']) in seen or seen.add((a['title'], a['detail'])))]
    att.sort(key=lambda a: a['level'] != 'bad')
    # деньги
    money = {}
    try:
        d = json.loads(Path('/var/lib/shopper/data.json').read_text())
        days = [float(v or 0) for v in d.get('dayAmounts', [])]; dates = d.get('incomeDates', [])
        today = time.strftime('%Y-%m-%d', time.gmtime(NOW + 3 * 3600))   # дата по Москве
        money['shopper'] = {'period': d.get('incomePeriod'), 'week': round(sum(days), 2), 'days': days, 'dates': dates,
                            'today': days[dates.index(today)] if today in dates and dates.index(today) < len(days) else None,
                            'tax_due': d.get('taxDue'), 'tax_debt': d.get('taxDebt'), 'tax_bonus': d.get('taxBonus'),
                            'available': (d.get('walletV2') or {}).get('available'), 'processing': (d.get('walletV2') or {}).get('processing'),
                            'source': 'админка Shopper (vovan20.ru/shopper/admin)'}
    except Exception as e: money['shopper_error'] = str(e)[:120]
    ai = {sid: s.get('ai_costs') for sid, s in (('78', s78), ('198', s198)) if s.get('ai_costs')}
    if ai:
        tot = lambda k: round(sum(v[k] for v in ai.values()), 2)
        days = {}
        for v in ai.values():
            for dd, c in v['days']: days[dd] = round(days.get(dd, 0) + c, 2)
        money['ai'] = {'today': tot('today'), 'week': tot('week'), 'month': tot('month'), 'by_server': ai,
                       'since': min(v['since'] for v in ai.values()), 'days': sorted(days.items()),
                       'source': 'учёт ECC в Claude Code, оценка по токенам; ведётся с 9 окт — первая запись включает всю сессию до этого'}
        if money['ai']['today'] >= 50: add('warn', f'ИИ сегодня: ${money["ai"]["today"]}', 'длинные сессии дорогие — для новых задач начинай новый чат', 'ИИ')
        att.sort(key=lambda a: a['level'] != 'bad')
    return {'attention': att, 'money': money, 'health': health, 'deploys': deploys,
            'vpn_keys': vpn.get('keys', []), 'vpn': {k: v for k, v in vpn.items() if k not in ('keys', 'traffic')}, 'vpn_traffic': vpn.get('traffic'), 'updated': iso()}

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
    try: owner = owner_view(s78, s198, stale198, projects, snap['catalog']['projects'])
    except Exception as e: owner = {'error': f'{type(e).__name__}: {str(e)[:160]}'}
    for name, obj in (('snapshot.json', snap), ('projects.json', {'updated': iso(), 'projects': projects, 'owner': owner})):
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
