"""Build one portable browser-hosted game for both facilitators and players."""
from pathlib import Path
import json,html,re
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'web/multiplayer'
def render(blocks):
    tags={'TITLE':'h1','HEADING_1':'h2','HEADING_2':'h3','HEADING_3':'h4'}
    out=[]
    for kind,text in blocks:
        safe=html.escape(text)
        if kind=='BULLET':out.append('<ul><li>'+safe+'</li></ul>')
        else:
            tag=tags.get(kind,'p');out.append(f'<{tag}>{safe}</{tag}>')
    return ''.join(out)
docs=json.loads((ROOT/'docs/drive-publication-blocks.json').read_text(encoding='utf8'))
briefs={};owner=None
for kind,text in docs['briefs']['blocks']:
    if kind=='HEADING_1':
        owner={'The Ductus Guild':'Guild','The Janissariat':'Janissariat','The Ascendant':'Ascendant'}[text];briefs[owner]=[]
    if owner:briefs[owner].append([kind,text])
reference='const REFERENCE='+json.dumps(dict(rules=render(docs['rulebook']['blocks']),components=render(docs['components']['blocks']),briefs={k:render(v) for k,v in briefs.items()}),ensure_ascii=False).replace('<','\\u003c')+';'
# The repository and game code are public. Only the host starts the engine;
# each connected player still receives the Multiplayer.view allowlist.
files = {}
for name in ('__init__', 'operations', 'settlement', 'charter', 'session', 'multiplayer', 'browser_host', 'presentation'):
    path = f'src/void_throne/{name}.py'
    files[path] = (ROOT/path).read_text(encoding='utf8')
for folder in ('private-cards', 'public-covers', 'player-visions'):
    for path in sorted((ROOT/'design'/folder).glob('*.json')):
        files[path.relative_to(ROOT).as_posix()] = path.read_text(encoding='utf8')
files['design/track-descriptions.json']=(ROOT/'design/track-descriptions.json').read_text(encoding='utf8')

def js(value): return json.dumps(value,ensure_ascii=False).replace('<', '\\u003c')
host_data = 'const HOST_FILES='+js(files)+';const HOST_WORKER='+js((SOURCE/'host-worker.js').read_text(encoding='utf8'))+';'
template=(SOURCE/'multiplayer.html').read_text(encoding='utf8')
result=template.replace('/* STYLE */',(SOURCE/'multiplayer.css').read_text(encoding='utf8')).replace('/* PEERJS */',(ROOT/'web/vendor/peerjs-1.5.5.min.js').read_text(encoding='utf8')).replace('/* REFERENCE */',reference).replace('/* HOST DATA */',host_data).replace('/* BROWSER HOST */',(SOURCE/'browser-host.js').read_text(encoding='utf8')).replace('/* APP */',(SOURCE/'multiplayer.js').read_text(encoding='utf8'))
result=result.replace('</head>', '<!-- PeerJS 1.5.5: '+(ROOT/'web/vendor/peerjs-LICENSE').read_text(encoding='utf8')+' --></head>')
for name in ('multiplayer.html','multiplayer-player.html'):
    (ROOT/'web'/name).write_text(result,encoding='utf8')
print('Built identical start-or-join pages with the shared browser rules engine.')
