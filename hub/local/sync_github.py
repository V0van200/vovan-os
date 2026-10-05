#!/usr/bin/env python3
"""Download a consistent private GitHub inventory; never run collectors or deploys."""
import base64
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
REPO='V0van200/vovan-os'
FILES=['catalog/projects.json','inventory/links.json','inventory/github-repos.json','inventory/system-graph.json','inventory/servers/server-78.json','inventory/servers/server-198.json']

def get_json(url,token):
    req=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','Authorization':'Bearer '+token,'User-Agent':'Vovan-OS-local','X-GitHub-Api-Version':'2022-11-28'})
    with urllib.request.urlopen(req,timeout=30) as response:
        content=response.read(16*1024*1024+1)
        if len(content)>16*1024*1024:raise ValueError('Response exceeds size limit')
        return json.loads(content)

def validate_sources(files):
    catalog=files['catalog/projects.json']
    if not isinstance(catalog.get('projects'),list) or not catalog['projects']:raise ValueError('Empty or invalid project catalogue')
    if not isinstance(files['inventory/github-repos.json'],list):raise ValueError('Invalid repository inventory')
    for sid in ('78','198'):
        server=files[f'inventory/servers/server-{sid}.json']
        if not isinstance(server.get('services'),list) or not isinstance(server.get('databases'),list) or not isinstance(server.get('host'),dict):raise ValueError('Invalid server inventory')
    graph=files['inventory/system-graph.json'];ids={n['id'] for n in graph['nodes']}
    if any(e['from'] not in ids or e['to'] not in ids for e in graph['edges']):raise ValueError('Invalid graph references')
    if not isinstance(files['inventory/links.json'].get('groups'),dict):raise ValueError('Invalid project links')

def sync(token):
    commit=get_json(f'https://api.github.com/repos/{REPO}/commits/main',token)['sha']
    if not re.fullmatch(r'[0-9a-f]{40}',commit):raise ValueError('Invalid revision')
    files={}
    for path in FILES:
        blob=get_json(f'https://api.github.com/repos/{REPO}/contents/{urllib.parse.quote(path)}?ref={commit}',token)
        if blob.get('encoding')!='base64':raise ValueError('Unsupported file encoding')
        files[path]=json.loads(base64.b64decode(blob['content']).decode('utf-8'))
    validate_sources(files)
    snapshot={'version':1,'source':{'repository':REPO,'commit':commit},'catalog':files['catalog/projects.json'],'repos':files['inventory/github-repos.json'],'links':files['inventory/links.json'],'graph':files['inventory/system-graph.json'],'servers':{sid:files[f'inventory/servers/server-{sid}.json'] for sid in ('78','198')}}
    # Single atomic replacement: a failed fetch/validation never changes the existing snapshot.
    target=ROOT/'site'/'snapshot.json'
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=target.parent,suffix='.tmp',delete=False) as f:
        json.dump(snapshot,f,ensure_ascii=False,separators=(',',':'));tmp=Path(f.name)
    try:os.replace(tmp,target)
    finally:tmp.unlink(missing_ok=True)
    return snapshot

def main():
    token=os.environ.get('GITHUB_TOKEN')
    if not token:
        print('GITHUB_TOKEN is not configured. The saved snapshot remains available. Use JSON import or set a read-only GitHub token in your terminal environment.');return 1
    try:
        snapshot=sync(token)
        print(f"Updated: {len(snapshot['catalog']['projects'])} projects, revision {snapshot['source']['commit'][:7]}. In the dashboard click Refresh snapshot.")
        return 0
    except urllib.error.HTTPError as exc:
        print(f'GitHub returned HTTP {exc.code}. Check read access to {REPO}. Existing snapshot was preserved.');return 1
    except (ValueError,KeyError,OSError,urllib.error.URLError):
        print('Update failed: network unavailable or snapshot format invalid. Existing snapshot was preserved.');return 1
if __name__=='__main__':raise SystemExit(main())
