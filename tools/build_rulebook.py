from pathlib import Path
import re,json,html,statistics
BASE=Path(__file__).resolve().parents[1]
SOURCE=BASE/'docs/rulebook-source.txt'
OUT=BASE/'.playtrace/rulebook-build'
OUT.mkdir(parents=True,exist_ok=True)
blocks=[]
for raw in SOURCE.read_text(encoding='utf-8').splitlines():
    raw=raw.strip()
    if not raw:continue
    if raw.startswith('~ '):kind,text='SUBTITLE',raw[2:]
    elif raw.startswith('### '):kind,text='HEADING_2',raw[4:]
    elif raw.startswith('## '):kind,text='HEADING_1',raw[3:]
    elif raw.startswith('# '):kind,text='TITLE',raw[2:]
    elif raw.startswith('- '):kind,text='BULLET',raw[2:]
    elif raw.startswith('> '):kind,text='EXAMPLE',raw[2:]
    else:kind,text='NORMAL_TEXT',raw
    blocks.append([kind,text])
title=next(text for kind,text in blocks if kind=='TITLE')
toc=[];body=[];section=0;in_contents=False
for kind,text in blocks:
    safe=html.escape(text)
    if text=='Read your faction’s objectives and guidance in the separate Player Briefs.':
        safe='Read your faction’s objectives and guidance in the separate <a href="player-briefs.html">Player Briefs</a>.'
    if kind=='NORMAL_TEXT':
        safe=re.sub(r'Component Reference', '<a href="component-reference.html">Component Reference</a>',safe)
        safe=re.sub(r'Player Brief(?!s)', '<a href="player-briefs.html">Player Brief</a>',safe)
    if kind=='SUBTITLE':body.append('<p class="eyebrow">'+safe+'</p>')
    elif kind=='TITLE':body.append('<header><h1>'+safe+'</h1></header>')
    elif kind=='HEADING_1':
        if in_contents:body.append('</div>');in_contents=False
        section+=1;toc.append(f'<a href="#section-{section}">{safe}</a>');body.append(f'<h2 id="section-{section}">{safe}</h2>')
    elif kind=='HEADING_2':
        if text=='Contents':body.append('<div class="print-contents">');in_contents=True
        body.append('<h3>'+safe+'</h3>')
    elif kind=='EXAMPLE':body.append('<aside class="example"><p>'+safe+'</p></aside>')
    elif kind=='BULLET':
        safe=re.sub(r'^([^:]{1,45}:)',r'<b>\1</b>',safe)
        body.append('<ul class="rule"><li>'+safe+'</li></ul>')
    else:body.append('<p>'+safe+'</p>')
style='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f4f0e7;color:#20353d;font:18px/1.65 system-ui,sans-serif}main{max-width:1360px;margin:auto;display:grid;grid-template-columns:260px minmax(0,850px);gap:44px;padding:36px 28px}nav{position:sticky;top:24px;align-self:start;font-size:14px}nav a{display:block;padding:6px 0;color:#285861;text-decoration:none}nav a:hover{text-decoration:underline}article{min-width:0}h1,h2,h3{font-family:Georgia,serif;line-height:1.2}h1{font-size:46px;margin:14px 0}h2{font-size:32px;margin:2.2em 0 .8em;border-top:2px solid #b9c9c5;padding-top:24px;scroll-margin-top:22px}h3{font-size:24px;margin-top:1.5em}p{margin:.8em 0}header{padding:24px;background:#17343f;color:#fff7e7}.eyebrow{font:11px system-ui;letter-spacing:.16em}.example{background:#e0eae6;border-left:5px solid #387075;padding:10px 22px;margin:24px 0}.example p{margin:.6em 0}.rule{background:#fffaf0;padding:8px 18px 8px 38px;margin:8px 0;border:1px solid #e0d8c8}.toolbar{font-size:14px;margin-bottom:24px}a{color:#235963}@media(max-width:900px){main{display:block;padding:20px}nav{position:static;columns:2;margin-bottom:30px}h1{font-size:36px}}@media(max-width:500px){nav{columns:1}body{font-size:17px}}@media print{body{background:white;font:11pt/1.4 Arial,sans-serif}main{display:block;padding:0;max-width:none}nav,.toolbar{display:none}header{background:white;color:#20353d;padding:0}h1{font-size:26pt}h2{font-size:18pt}h3{font-size:14pt}h2,h3{break-after:avoid}.rule,.example{break-inside:avoid}p{orphans:3;widows:3}@page{size:A4;margin:18mm}}'''
style+='.print-contents{display:none}@media print{.print-contents{display:block}}'
rendered=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{style}</style></head><body><main><nav aria-label="Contents"><b>Contents</b>'+''.join(toc)+'</nav><article>'+''.join(body)+'</article></main></body></html>'
(OUT/'rulebook.html').write_text(rendered,encoding='utf-8')
(OUT/'rulebook.txt').write_text('\n\n'.join(b[1] for b in blocks)+'\n',encoding='utf-8')
(OUT/'rulebook-blocks.json').write_text(json.dumps({'title':'The Void Throne — Player Rulebook, draft v0.3','blocks':blocks},ensure_ascii=False,indent=2),encoding='utf-8')
# Google Docs positions are UTF-16 code units. This manuscript uses BMP text only.
assert all(ord(c)<=65535 for _,t in blocks for c in t)
index=1;styles=[];text=''
for kind,line in blocks:
    length=len(line)+1
    styles.append({'kind':kind,'start':index,'end':index+length})
    index+=length;text+=line+'\n'
(OUT/'native-content.json').write_text(json.dumps({'text':text,'styles':styles},ensure_ascii=False),encoding='utf-8')
prose=[t for k,t in blocks if k in ('NORMAL_TEXT','EXAMPLE')]
sentences=[s for p in prose for s in re.split(r'(?<=[.!?])\s+',p) if s.strip()]
metrics={'words':len(re.findall(r"\b[\w’'-]+\b",text)),'sections':section,'average_prose_sentence_words':round(statistics.mean(len(s.split()) for s in sentences),1),'worked_examples':sum(k=='EXAMPLE' for k,_ in blocks),'full_round_walkthrough':any('Example of play' in t for k,t in blocks)}
(OUT/'writing-checks.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics))

# Refresh offline views only; read current Drive revision before publishing.
import shutil
for name in ('rulebook.html','rulebook.txt'):
    shutil.copyfile(OUT/name,BASE/'docs'/name)
