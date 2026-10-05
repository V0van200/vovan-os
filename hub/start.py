#!/usr/bin/env python3
"""Local-only Vovan OS. Python standard library, no install or network required."""
import argparse
import functools
import http.server
import ipaddress
from pathlib import Path
import threading
import urllib.parse
import webbrowser

ROOT=Path(__file__).resolve().parent
SITE=ROOT/'site'
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(SITE),**kw)
    def do_GET(self):
        # Prevent DNS rebinding. Only the loopback listener's own Host is accepted.
        host=self.headers.get('Host','').split(':')[0].lower()
        if host not in ('localhost','127.0.0.1'):
            self.send_error(403,'Local host only');return
        path=urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        target=(SITE/path.lstrip('/')).resolve()
        if not target.is_relative_to(SITE.resolve()) or any(p.startswith('.') for p in Path(path).parts if p not in ('/','')):
            self.send_error(403);return
        if target.is_dir() and not (target/'index.html').is_file():
            self.send_error(404);return
        super().do_GET()
    def do_HEAD(self):
        host=self.headers.get('Host','').split(':')[0].lower()
        if host not in ('localhost','127.0.0.1'):
            self.send_error(403);return
        super().do_HEAD()
    def end_headers(self):
        self.send_header('Cache-Control','no-cache')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        super().end_headers()
    def guess_type(self,path):
        if path.endswith('.mjs'):return 'text/javascript; charset=utf-8'
        return super().guess_type(path)
    def log_message(self,fmt,*args):
        if args and str(args[1] if len(args)>1 else '').startswith(('4','5')):super().log_message(fmt,*args)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8080)
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--sync',action='store_true',help='Try a read-only GitHub snapshot refresh before starting; requires GITHUB_TOKEN')
    args=parser.parse_args()
    if args.sync:
        from local.sync_github import main as sync_main
        sync_main()
    if not (SITE/'snapshot.json').is_file():
        from local.build_snapshot import build
        build()
    try:server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    except OSError as exc:
        print(f'Cannot open port {args.port}: {exc}. Try: python start.py --port 8081');raise SystemExit(1)
    url=f'http://127.0.0.1:{args.port}'
    print(f'VOVAN OS: {url}',flush=True)
    print('Local access only. Press Ctrl+C to stop.',flush=True)
    if not args.no_browser:threading.Timer(.5,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
