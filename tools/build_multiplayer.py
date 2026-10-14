"""Build the host page and portable player HTML without bundling any private cards."""
from pathlib import Path
import json,html,re
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'web/multiplayer'
def render(blocks):
    tags={'TITLE':'h1','HEADING_1':'h2','HEADING_2':'h3'}
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
reference='const REFERENCE='+json.dumps(dict(rules=render(docs['rulebook']['blocks']),briefs={k:render(v) for k,v in briefs.items()}),ensure_ascii=False).replace('<','\\u003c')+';'
template=(SOURCE/'multiplayer.html').read_text(encoding='utf8')
for mode,name in [('host','multiplayer.html'),('player','multiplayer-player.html')]:
    result=template.replace('data-mode="MODE"',f'data-mode="{mode}"').replace('/* STYLE */',(SOURCE/'multiplayer.css').read_text(encoding='utf8')).replace('/* PEERJS */',(ROOT/'web/vendor/peerjs-1.5.5.min.js').read_text(encoding='utf8')).replace('/* REFERENCE */',reference).replace('/* APP */',(SOURCE/'multiplayer.js').read_text(encoding='utf8'))
    result=result.replace('</head>', '<!-- PeerJS 1.5.5: '+(ROOT/'web/vendor/peerjs-LICENSE').read_text(encoding='utf8')+' --></head>')
    (ROOT/'web'/name).write_text(result,encoding='utf8')
print('Built host and standalone player pages; only public rules and role briefs embedded.')
