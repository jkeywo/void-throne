from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote
import json, mimetypes, threading, webbrowser, argparse, html
from .session import ROOT
from .current_session import Session, from_actions
from .multiplayer import Multiplayer
from .orders_v04 import LABELS

LOCK=threading.Lock()
GAME=Session()
SAVE=ROOT/'.playtrace/browser-session.json'
MP=None

def restore(actions):
    if not isinstance(actions,list) or len(actions)>100:raise ValueError('Expected a session action list, at most 100 entries.')
    return from_actions(actions)

def save():
    SAVE.parent.mkdir(parents=True,exist_ok=True)
    temp=SAVE.with_suffix('.tmp');temp.write_text(json.dumps(GAME.actions,ensure_ascii=False),encoding='utf-8');temp.replace(SAVE)

def report(game):
    escape=html.escape
    def value_view(value):
        if value is None:return 'None'
        if isinstance(value,bool):return 'Yes' if value else 'No'
        if isinstance(value,list):return '<ul>'+''.join('<li>'+value_view(v)+'</li>' for v in value)+'</ul>' if value else 'None'
        if isinstance(value,dict):return '<dl>'+''.join('<dt><b>'+escape('Sorenne’s Fall · Stability' if k == 'communities' else str(k).replace('_',' ').capitalize())+'</b></dt><dd>'+value_view(v)+'</dd>' for k,v in value.items())+'</dl>'
        return escape(str(LABELS.get(value,value)))
    out=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>The Void Throne — browser playtest</title>',
         '<style>body{font:17px/1.6 system-ui;max-width:1100px;margin:auto;padding:30px;background:#f4f0e6;color:#192f38}h1,h2{font-family:Georgia}section{margin:2em 0}pre{white-space:pre-wrap;overflow-wrap:anywhere}.mechanics{background:#e6eff0;padding:22px;border-left:4px solid #5c8b8e}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}@media print{details{display:block}}</style>',
         '<h1>The Void Throne</h1><h2>Browser playtest record</h2><p>One tester controlled every seat. This is a mechanical test and authored decision record, not a six-agent or human-group playtest.</p>']
    for event in game.history:
        out.append(f'<section><h2>Round {event["round"]} · {escape(event["event"])}</h2>')
        for role,note in event.get('notes',{}).items():
            if note:out.append(f'<p><b>{escape(role)}</b> — {escape(note)}</p>')
        data={k:v for k,v in event.items() if k not in ('notes','round','event','sequence','phase')}
        out.append('<div class="grid">')
        for key,value in data.items():out.append(f'<div class="mechanics"><b>{escape(key.replace("_"," ").capitalize())}</b>{value_view(value)}</div>')
        out.append('</div></section>')
    return ''.join(out).encode('utf-8')

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def valid_host(self):return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
    def send(self,data,status=200,mime='application/json; charset=utf-8',filename=None):
        if not isinstance(data,bytes):data=json.dumps(data,ensure_ascii=False).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
        self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if not self.valid_host():return self.send({'error':'Loopback host required.'},403)
        path=unquote(urlparse(self.path).path)
        with LOCK:
            if path=='/api/mp/export':return self.send(MP.export(),filename='void-throne-multiplayer.json')
            if path=='/api/mp/report':return self.send(MP.report(),mime='text/html; charset=utf-8',filename='void-throne-multiplayer.html')
            if path=='/api/state':return self.send(GAME.public())
            if path=='/api/export':return self.send(GAME.public(),filename='void-throne-browser-playtest.json')
            if path=='/api/report':return self.send(report(GAME),mime='text/html; charset=utf-8',filename='void-throne-browser-playtest.html')
        if path in ('/','/index.html'):file=ROOT/'web/index.html'
        elif path in ('/multiplayer.html','/multiplayer-player.html'):file=ROOT/'web'/path[1:]
        elif path in ('/app.js','/style.css'):file=ROOT/'web'/path[1:]
        elif path.startswith(('/reports/','/docs/')):
            file=(ROOT/path[1:]).resolve()
            if not (file.is_relative_to(ROOT/'reports') or file.is_relative_to(ROOT/'docs')):return self.send({'error':'Not found'},404)
            if file.suffix not in ('.html','.txt','.json','.pdf'):return self.send({'error':'Not found'},404)
        else:return self.send({'error':'Not found'},404)
        if not file.is_file():return self.send({'error':'Not found'},404)
        self.send(file.read_bytes(),mime=mimetypes.guess_type(file)[0] or 'application/octet-stream')
    def do_POST(self):
        global GAME
        origin=self.headers.get('Origin')
        if not self.valid_host() or (origin and origin not in {f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}):
            return self.send({'error':'Same-origin local request required.'},403)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<0 or length>1000000:raise ValueError('Request too large.')
            if self.headers.get_content_type()!='application/json':raise ValueError('JSON request required.')
            payload=json.loads(self.rfile.read(length))
            with LOCK:
                if self.path.startswith('/api/mp/'):
                    action=self.path.rsplit('/',1)[-1]
                    return self.send(MP.begin_host() if action=='host' else MP.dispatch(action,payload))
                if self.path=='/api/action':GAME.apply(payload)
                elif self.path=='/api/new':GAME=Session()
                elif self.path=='/api/restore':GAME=restore(payload.get('actions'))
                else:return self.send({'error':'Not found'},404)
                save();self.send(GAME.public())
        except (ValueError,KeyError,TypeError,AssertionError) as exc:self.send({'error':str(exc) or 'Invalid decision sheet.'},400)

def main():
    global GAME,SAVE,MP
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8877);parser.add_argument('--no-open',action='store_true');parser.add_argument('--save',type=Path)
    parser.add_argument('--multiplayer',action='store_true');parser.add_argument('--mp-save',type=Path)
    args=parser.parse_args()
    MP=Multiplayer(args.mp_save or ROOT/f'.playtrace/multiplayer-session-{args.port}.json')
    if args.save:SAVE=args.save
    if SAVE.exists():
        try:GAME=restore(json.loads(SAVE.read_text(encoding='utf-8')))
        except (ValueError,KeyError,TypeError):print('Saved session could not be replayed; preserved on disk until the next successful action.')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    url=f'http://127.0.0.1:{server.server_port}'+('/multiplayer.html' if args.multiplayer else '')
    print('The Void Throne test bench: '+url,flush=True)
    if not args.no_open:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
