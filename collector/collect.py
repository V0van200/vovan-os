#!/usr/bin/env python3
"""Vovan OS — сборщик инвентаря сервера. ТОЛЬКО ЧИТАЕТ, ничего не меняет.

Запуск на сервере:  sudo python3 collect.py > server.json
Что собирает: железо, сервисы systemd, порты, таймеры, Docker, сайты nginx, приложения (git, размер),
структуру баз (SQLite и Postgres: таблицы, поля, индексы, число строк — БЕЗ самих записей), бэкапы, сертификаты.
Чего НЕ собирает: значения .env, пароли, токены, ключи, содержимое таблиц, переписки, файлы пользователей.
Подозрительные на секрет строки маскируются (mask()).
"""
import json, os, re, socket, sqlite3, subprocess, time, glob, shutil
from pathlib import Path

def sh(cmd, timeout=30, inp=None):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, input=inp).stdout.strip()
    except Exception:
        return ''

SECRET = re.compile(r'(?i)((?:token|secret|password|passwd|pwd|api[_-]?key|auth|bearer|private[_-]?key|psk)[=: ]+)\S+')
LONG = re.compile(r'\b[A-Za-z0-9+/_\-]{32,}={0,2}\b')
URL_CRED = re.compile(r'(://)[^/@\s:]+:[^/@\s]+@')
def mask(s):
    if not isinstance(s, str):
        return s
    s = URL_CRED.sub(r'\1***:***@', s)
    s = SECRET.sub(r'\1***', s)
    return LONG.sub(lambda m: m.group(0) if '/' in m.group(0) and m.group(0).count('/') > 1 else '***', s)

def host():
    mem = dict(re.findall(r'(\w+):\s+(\d+) kB', Path('/proc/meminfo').read_text()))
    disks = []
    for line in sh("df -B1 --output=target,size,used,avail -x tmpfs -x devtmpfs -x squashfs -x overlay").splitlines()[1:]:
        t, size, used, avail = line.split()
        disks.append({'mount': t, 'size': int(size), 'used': int(used), 'avail': int(avail)})
    return {'hostname': socket.gethostname(), 'os': sh('. /etc/os-release && echo "$PRETTY_NAME"'), 'kernel': os.uname().release,
            'cpus': os.cpu_count(), 'ram_total': int(mem['MemTotal']) * 1024, 'ram_available': int(mem['MemAvailable']) * 1024,
            'load': os.getloadavg(), 'uptime_s': int(float(Path('/proc/uptime').read_text().split()[0])), 'disks': disks,
            'public_ip': sh("curl -s -m 5 https://api.ipify.org") or None}

# Системные сервисы, которые неинтересны для карты проектов
SYSTEM = re.compile(r'^(systemd|dbus|getty|serial|user@|polkit|ssh|cron|rsyslog|snapd|multipathd|ModemManager|udisks|networkd|unattended|packagekit|irqbalance|qemu|chrony|fwupd|accounts|atd|lvm|blk|apport|lxd|thermald|upower|wpa|NetworkManager|avahi|bolt|colord|cups|gdm|kerneloops|rtkit|switcheroo|power|setvtrgb|keyboard|console|plymouth|rpc|nfs|sysstat|e2scrub|man-db|motd|logrotate|apt-|dpkg|update-notifier|fstrim|systemd-|ua-|ubuntu|secureboot|finalrd|grub|emergency|rescue|modprobe|kmod|ifup|networking|resolv|containerd|cloud-|growroot|procps|udev|syslog|dmesg|open-iscsi|set-root-pw|ssl-cert|apparmor|multipath|open-vm|pollinate|vgauth|ufw|iscsid|lvm2|mdmonitor|vmtoolsd)')

def ports():
    out = {}
    for line in sh('ss -ltnupH').splitlines():
        m = re.search(r'\s(\S+):(\d+)\s.*users:\(\("([^"]+)",pid=(\d+)', line)
        if m:
            out.setdefault(int(m.group(4)), []).append({'addr': m.group(1), 'port': int(m.group(2)), 'proto': line.split()[0], 'proc': m.group(3)})
    return out

def pid_tree(pid):
    kids = sh(f'pgrep -P {pid}').split()
    res = {int(pid)}
    for k in kids:
        res |= pid_tree(k)
    return res

def services():
    lp = ports(); out = []
    units = sh("systemctl list-unit-files --type=service --no-legend --plain | awk '{print $1\" \"$2}'").splitlines()
    for line in units:
        name, enabled = (line.split() + [''])[:2]
        if SYSTEM.match(name) or '@' in name:
            continue
        p = dict(l.split('=', 1) for l in sh(f"systemctl show {name} -p ActiveState,SubState,MainPID,ExecStart,WorkingDirectory,User,Description,ActiveEnterTimestamp,MemoryCurrent,FragmentPath,NRestarts").splitlines() if '=' in l)
        if p.get('ActiveState') not in ('active', 'activating') and enabled != 'enabled':
            continue
        exe = re.search(r'argv\[\]=([^;]+)', p.get('ExecStart', ''))
        pid = int(p.get('MainPID') or 0)
        my_ports = []
        if pid:
            for q in pid_tree(pid):
                my_ports += lp.get(q, [])
        mem = p.get('MemoryCurrent', '')
        out.append({'name': name.removesuffix('.service'), 'description': p.get('Description'), 'enabled': enabled, 'state': p.get('ActiveState'), 'sub': p.get('SubState'),
                    'since': p.get('ActiveEnterTimestamp') or None, 'user': p.get('User') or 'root', 'workdir': p.get('WorkingDirectory') or None,
                    'exec': mask(exe.group(1).strip()) if exe else None, 'memory': int(mem) if mem.isdigit() else None,
                    'restarts': int(p.get('NRestarts') or 0), 'unit_file': p.get('FragmentPath'), 'ports': sorted({(x['port'], x['proto']) for x in my_ports})})
    return out

def timers():
    out = []
    for line in sh('systemctl list-timers --all --no-legend --plain').splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        unit, act = parts[-2], parts[-1]
        if SYSTEM.match(unit):
            continue
        p = dict(l.split('=', 1) for l in sh(f"systemctl show {unit} -p Description,LastTriggerUSec,NextElapseUSecRealtime").splitlines() if '=' in l)
        out.append({'timer': unit, 'runs': act, 'description': p.get('Description'), 'last': p.get('LastTriggerUSec') or None, 'next': p.get('NextElapseUSecRealtime') or None})
    return out

def docker():
    if not shutil.which('docker'):
        return []
    out = []
    for line in sh("docker ps -a --format '{{json .}}'").splitlines():
        d = json.loads(line)
        out.append({'name': d['Names'], 'image': d['Image'], 'status': d['Status'], 'ports': d.get('Ports'), 'created': d.get('CreatedAt')})
    return out

def blocks(txt, keyword):
    """Найти блоки «keyword ... { ... }» с учётом вложенных скобок. Возвращает [(заголовок, тело)]."""
    out = []
    for m in re.finditer(r'\b' + keyword + r'\b([^{;]*)\{', txt):
        depth, i = 1, m.end()
        while i < len(txt) and depth:
            depth += {'{': 1, '}': -1}.get(txt[i], 0); i += 1
        out.append((m.group(1).strip(), txt[m.end():i - 1]))
    return out

def nginx():
    sites = []
    for f in sorted(glob.glob('/etc/nginx/sites-enabled/*')):
        txt = re.sub(r'#.*', '', Path(f).read_text(errors='ignore'))
        for _, block in blocks(txt, 'server'):
            top = re.sub(r'\blocation\b[^{]*\{(?:[^{}]|\{[^{}]*\})*\}', '', block)
            names = re.findall(r'(?<![\w_])server_name\s+([^;]+);', top)
            listen = re.findall(r'(?<![\w_])listen\s+([^;]+);', top)
            locs = []
            for path, body in blocks(block, 'location'):
                pp = re.search(r'proxy_pass\s+([^;]+);', body); root = re.search(r'(?:root|alias)\s+([^;]+);', body); ret = re.search(r'return\s+([^;]+);', body)
                path = re.sub(r'/dl-[^/ ]+', '/dl-***', path)   # секретные ссылки для скачивания
                locs.append({'path': path, 'proxy': pp.group(1).strip() if pp else None, 'root': re.sub(r'/dl-[^/ ]+', '/dl-***', root.group(1).strip()) if root else None,
                             'return': ret.group(1).strip()[:80] if ret and not (pp or root) else None, 'auth': 'auth_request' in body or 'auth_basic' in body})
            root = re.search(r'(?<![\w_])root\s+([^;]+);', top)
            sites.append({'file': os.path.basename(f), 'names': ' '.join(names).split(), 'listen': listen, 'root': root.group(1) if root else None,
                          'locations': locs, 'redirect_only': bool(re.search(r'return\s+30[12]', top)) and not locs, 'auth': 'auth_request' in top or 'auth_basic' in top})
    return sites

def certs():
    out = []
    for d in glob.glob('/etc/letsencrypt/live/*/cert.pem'):
        end = sh(f"openssl x509 -enddate -noout -in {d}").replace('notAfter=', '')
        names = sh(f"openssl x509 -noout -ext subjectAltName -in {d} | tail -1")
        out.append({'name': d.split('/')[-2], 'expires': end, 'domains': [x.strip().removeprefix('DNS:') for x in names.split(',') if 'DNS:' in x]})
    return out

def du(path):
    v = sh(f"du -sb {path} 2>/dev/null | cut -f1", timeout=60)
    return int(v) if v.isdigit() else None

def git_info(path):
    if not os.path.isdir(os.path.join(path, '.git')):
        return None
    g = lambda c: sh(f"git -C {path} -c safe.directory='*' {c}")
    return {'remote': mask(g('remote get-url origin')) or None, 'branch': g('rev-parse --abbrev-ref HEAD') or None,
            'last_commit': g("log -1 --format='%h %cI %s'") or None, 'dirty_files': len(g('status --porcelain').splitlines())}

def detect_stack(path):
    p = Path(path); s = []
    if (p / 'package.json').exists():
        s.append('node')
        try:
            deps = json.loads((p / 'package.json').read_text()).get('dependencies', {})
            s += [k for k in ('next', 'react', 'express', 'fastify', 'telegraf', 'grammy', 'socket.io', 'three', 'drizzle-orm', 'prisma') if k in deps]
        except Exception:
            pass
    if (p / 'requirements.txt').exists() or (p / 'pyproject.toml').exists():
        s.append('python')
        try:
            req = ((p / 'requirements.txt').read_text(errors='ignore') if (p / 'requirements.txt').exists() else '').lower()
            s += [k for k in ('fastapi', 'flask', 'django', 'aiogram', 'python-telegram-bot', 'telethon', 'sqlalchemy', 'celery', 'openai', 'whisper') if k in req]
        except Exception:
            pass
    if (p / 'go.mod').exists(): s.append('go')
    if (p / 'Dockerfile').exists() or (p / 'docker-compose.yml').exists() or (p / 'compose.yaml').exists(): s.append('docker')
    return s

def apps(roots):
    out = []
    for root in roots:
        for d in sorted(glob.glob(os.path.join(root, '*'))):
            if not os.path.isdir(d) or os.path.basename(d).startswith(('.', '__')) or os.path.basename(d) in ('containerd', 'node24', 'pwtest', 'ffmpeg-static'):
                continue
            readme = next((f for f in ('README.md', 'readme.md', 'README') if os.path.exists(os.path.join(d, f))), None)
            first = ''
            if readme:
                for line in Path(d, readme).read_text(errors='ignore').splitlines():
                    line = line.strip('# ').strip()
                    if line and not line.startswith(('!', '[', '<', '`')):
                        first = mask(line)[:200]; break
            out.append({'path': d, 'name': os.path.basename(d), 'size': du(d), 'stack': detect_stack(d), 'git': git_info(d),
                        'has_env_file': any(os.path.exists(os.path.join(d, f)) for f in ('.env', '.env.local', '.env.production')), 'readme_first_line': first or None})
    return out

SKIP_DB = re.compile(r'/(\.cache|\.local|\.pki|\.codex|codex-backup|ms-playwright|sherlock-env|site-packages|node_modules|\.git|\.config|\.vscode-server)/|/var/cache/|/tmp/|/var/lib/(containerd|docker)/')
def sqlite_schema(path):
    try:
        con = sqlite3.connect(f'file:{path}?mode=ro', uri=True, timeout=5)
        tables = []
        for (name, sql) in con.execute("SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            cols = [{'name': r[1], 'type': r[2], 'notnull': bool(r[3]), 'pk': bool(r[5])} for r in con.execute(f'PRAGMA table_info("{name}")')]
            fks = [{'from': r[3], 'table': r[2], 'to': r[4]} for r in con.execute(f'PRAGMA foreign_key_list("{name}")')]
            try:
                rows = con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            except Exception:
                rows = None
            tables.append({'table': name, 'rows': rows, 'columns': cols, 'foreign_keys': fks})
        idx = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")]
        trig = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='trigger'")]
        con.close()
        return {'engine': 'sqlite', 'path': path, 'size': os.path.getsize(path), 'tables': tables, 'indexes': idx, 'triggers': trig}
    except Exception as e:
        return {'engine': 'sqlite', 'path': path, 'error': str(e)[:200]}

def sqlite_dbs():
    found = sh(r"find / -xdev \( -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.db' \) -size +4k 2>/dev/null", timeout=120).splitlines()
    out = []
    for f in sorted(set(found)):
        if SKIP_DB.search(f) or f.startswith(('/proc', '/usr', '/snap', '/var/lib/apt', '/var/lib/dpkg', '/var/lib/ubuntu', '/var/lib/fwupd', '/var/lib/PackageKit', '/var/lib/command-not-found', '/var/lib/plocate', '/var/lib/private', '/var/lib/fail2ban', '/data/backups')):
            continue
        if re.search(r'(/backups?/|\.bak|-before-|prodcopy)', f):
            continue
        out.append(sqlite_schema(f))
    return out

def postgres():
    out = []
    for c in (docker() if shutil.which('docker') else []):
        if 'postgres' not in c['image'] or not c['status'].startswith('Up'):
            continue
        def q(sql, db=None):
            d = db or '"$POSTGRES_DB"'
            return sh(f"""docker exec -i {c['name']} sh -c 'psql -U "$POSTGRES_USER" -d {d} -AtF "|" -q'""", timeout=60, inp=sql)
        for db in q("select datname from pg_database where not datistemplate;").splitlines():
            cols = {}
            for line in q("select table_schema,table_name,column_name,data_type,is_nullable from information_schema.columns where table_schema not in ('pg_catalog','information_schema') order by table_schema,table_name,ordinal_position;", db).splitlines():
                sch, t, col, typ, nul = line.split('|')
                cols.setdefault(f'{sch}.{t}', []).append({'name': col, 'type': typ, 'notnull': nul == 'NO'})
            rows = dict(l.split('|') for l in q("select schemaname||'.'||relname, n_live_tup from pg_stat_user_tables;", db).splitlines() if '|' in l)
            fks = []
            for line in q("select tc.table_schema||'.'||tc.table_name, kcu.column_name, ccu.table_schema||'.'||ccu.table_name, ccu.column_name from information_schema.table_constraints tc join information_schema.key_column_usage kcu on tc.constraint_name=kcu.constraint_name and tc.table_schema=kcu.table_schema join information_schema.constraint_column_usage ccu on ccu.constraint_name=tc.constraint_name and ccu.table_schema=tc.table_schema where tc.constraint_type='FOREIGN KEY';", db).splitlines():
                a, b, c2, d2 = line.split('|'); fks.append({'from': f'{a}.{b}', 'to': f'{c2}.{d2}'})
            size = q(f"select pg_database_size('{db}');", db)
            out.append({'engine': 'postgres', 'container': c['name'], 'database': db, 'size': int(size) if size.isdigit() else None,
                        'tables': [{'table': t, 'rows': int(rows.get(t, 0) or 0), 'columns': cs} for t, cs in cols.items()], 'foreign_keys': fks})
    return out

def redis():
    out = []
    for c in (docker() if shutil.which('docker') else []):
        if 'redis' in c['image'] and c['status'].startswith('Up'):
            info = sh(f"docker exec {c['name']} redis-cli info keyspace") + '\n' + sh(f"docker exec {c['name']} redis-cli info memory | grep used_memory_human")
            out.append({'engine': 'redis', 'container': c['name'], 'info': [l for l in info.splitlines() if l and not l.startswith('#')]})
    return out

def backups():
    out = []
    for d in ['/data/backups', '/data/kabluk/backups', '/data/backup', '/var/backups/vovan']:
        if os.path.isdir(d):
            files = [f for f in glob.glob(d + '/**/*', recursive=True) if os.path.isfile(f)]
            latest = max(files, key=os.path.getmtime) if files else None
            out.append({'dir': d, 'files': len(files), 'size': sum(os.path.getsize(f) for f in files),
                        'latest': os.path.basename(latest) if latest else None, 'latest_at': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(os.path.getmtime(latest))) if latest else None})
    return out

def vpn():
    out = {}
    if shutil.which('awg'):
        for iface in sh('awg show interfaces').split():
            peers = sh(f'awg show {iface} latest-handshakes').splitlines()
            out[iface] = {'peers': len(peers), 'active_24h': sum(1 for p in peers if p.split()[-1] != '0' and time.time() - int(p.split()[-1]) < 86400),
                          'port': sh(f'awg show {iface} listen-port')}
    if shutil.which('xray') or os.path.exists('/usr/local/bin/xray'):
        out['xray'] = {'running': sh('systemctl is-active xray') == 'active'}
    return out

if __name__ == '__main__':
    roots = [r for r in ('/home/claude/apps', '/opt', '/var/www', '/data/sites') if os.path.isdir(r)]
    print(json.dumps({'collected_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'host': host(), 'services': services(), 'timers': timers(),
                      'docker': docker(), 'nginx': nginx(), 'certs': certs(), 'apps': apps(roots), 'databases': sqlite_dbs() + postgres() + redis(),
                      'backups': backups(), 'vpn': vpn()}, ensure_ascii=False, indent=1, default=str))
