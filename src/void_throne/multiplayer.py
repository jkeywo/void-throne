"""Human-seat session. Only the local facilitator advances the rules engine.

Connection IDs are assigned by the host browser, never by a remote message.
Players receive explicit projections, never Session.public() or raw actions.
"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import html
import json
import secrets
from .session import Session, ROLES, ASSETS, NAV, SEC, ARTICLES, DEFAULTS, choice, boolean, ROOT

CHANNELS = {'table': ROLES, 'guild': ('GN','GS'), 'army': ('JN','JS'),
            'navigation': ('GN','JN','A'), 'security': ('GS','JS','A')}
ROLE_NAMES = {'GN':'Guild · Navigation','GS':'Guild · Security','JN':'Janissariat · Navigation',
              'JS':'Janissariat · Security','A':'Ascendant'}

def short(value, maximum=2000):
    if not isinstance(value,str) or len(value)>maximum:raise ValueError('Text is missing or too long.')
    return value.strip()

def moment():return datetime.now(timezone.utc).isoformat()

class Multiplayer:
    def __init__(self, path=None):
        self.path=Path(path) if path else None
        self.game=Session();self.room='void-'+secrets.token_hex(6)
        self.seats={};self.sheets={};self.chats=[];self.audit=[];self.revision=0
        self.live={};self.pending={};self.host_key=None;self.seen=[]
        if self.path and self.path.exists():
            saved=json.loads(self.path.read_text(encoding='utf8'))
            for action in saved['actions']:self.game.apply(action)
            for key in ('room','seats','sheets','chats','audit','revision','seen'):
                setattr(self,key,saved.get(key,getattr(self,key)))

    @property
    def epoch(self):return f'{self.room}:{len(self.game.actions)}:{self.game.round}:{self.game.stage}'

    def save(self):
        self.revision+=1
        if self.path:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            temp=self.path.with_suffix('.tmp')
            temp.write_text(json.dumps(self.backup(),ensure_ascii=False),encoding='utf8')
            temp.replace(self.path)

    def backup(self):
        return dict(version=1,actions=self.game.actions,**{k:deepcopy(getattr(self,k)) for k in
                    ('room','seats','sheets','chats','audit','revision','seen')})

    def export(self):
        data=self.backup()
        data['seats']={r:{'name':s['name']} for r,s in self.seats.items()}
        data.pop('seen',None)
        data['description']='Human-seat multiplayer record. Local save separately holds reconnect credentials.'
        return data

    def begin_host(self):
        self.host_key=secrets.token_urlsafe(32);self.live={};self.pending={}
        return dict(host_key=self.host_key,**self.envelope())

    def check_host(self,key):
        if not self.host_key or not secrets.compare_digest(str(key),self.host_key):
            raise ValueError('This host tab has been replaced. Use the newest facilitator tab.')

    def required(self):
        if self.game.stage=='vision':return ['A']
        if self.game.stage in ('trial-proposal','ceremony-proposal','ended'):return []
        return list(ROLES)

    def channels(self,role):
        return [c for c,roles in CHANNELS.items() if role in roles]+['facilitator-'+role]

    def status(self):
        return {r:dict(name=self.seats.get(r,{}).get('name','Unassigned'),
                       connected=r in self.live.values(),submitted=r in self.sheets,due=r in self.required()) for r in ROLES}

    def history(self,role):
        events=deepcopy(self.game.history)
        disclosed_rounds={e['round'] for e in events if e['event']=='Final faction sheets' and e.get('disclosed')}
        for event in events:
            if event['event']=='Foresight purchase' and role!='A':
                # A purchase's direction, answer and reason all remain private until disclosure.
                if event['round'] not in disclosed_rounds:
                    event.pop('private_answer',None);event.pop('choice',None);event.pop('notes',None)
            if event['event']=='Final faction sheets' and role!='A' and not event.get('disclosed'):
                event.get('notes',{}).pop('A',None)
        return events

    def view(self,role):
        g=self.game
        # Deliberate allowlist: raw actions and unpublished private cards never enter this value.
        out={k:deepcopy(getattr(g,k)) for k in ('state','round','stage','foresight','articles','pledges',
             'drafts','assignments','reserve','disclosed','trial','package','ballots','settlement')}
        public=g.public()
        out.update(role=role,epoch=self.epoch,revision=self.revision,seats=self.status(),
                   covers=public['covers'],leverage=public['leverage'],history=self.history(role),
                   selected_vision=deepcopy(g.vision) if role=='A' or g.disclosed else None,
                   own_sheet=deepcopy(self.sheets.get(role)),channels=self.channels(role),
                   chat=[c for c in self.chats if c['channel'] in self.channels(role)],
                   required=role in self.required())
        teammates=('GN','GS') if role.startswith('G') else ('JN','JS') if role.startswith('J') else ('A',)
        visible=teammates if g.stage in ('draft','commit') else (
            ('GN','JN','A') if role in ('GN','JN') else ('GS','JS','A') if role in ('GS','JS') else ROLES)
        if g.stage=='vision':visible=('A',) if role=='A' else ()
        if g.stage in ('trial-vote','ceremony-vote'):visible=(role,)
        out['working_sheets']={r:deepcopy(s) for r,s in self.sheets.items() if r in visible}
        # The Ascendant's commit sheet can contain private reasoning and disclosure intent.
        if role!='A':out['working_sheets'].pop('A',None) if g.stage=='commit' else None
        return out

    def envelope(self,direct=None):
        return dict(host=dict(game=self.game.public(),epoch=self.epoch,revision=self.revision,
                    room=self.room,seats=self.status(),pending=deepcopy(self.pending),
                    sheets=deepcopy(self.sheets),required=self.required(),chat=deepcopy(self.chats)),
                    peers={cid:self.view(role) for cid,role in self.live.items()},direct=direct or {})

    def approve(self,cid,role):
        choice(role,ROLES)
        if cid not in self.pending:raise ValueError('That player is no longer waiting.')
        if role in self.seats:raise ValueError('That seat is already reserved. Release it before replacing its player.')
        name=self.pending.pop(cid)['name'];token=secrets.token_urlsafe(32)
        self.seats[role]={'name':name,'token':token};self.live[cid]=role
        self.audit.append(dict(time=moment(),event='seat approved',role=role,name=name))
        self.save()
        return self.envelope({cid:dict(type='admitted',role=role,token=token)})

    def release(self,role):
        choice(role,ROLES)
        old=[cid for cid,r in self.live.items() if r==role]
        for cid in old:del self.live[cid]
        self.seats.pop(role,None);self.sheets.pop(role,None)
        self.audit.append(dict(time=moment(),event='seat released',role=role));self.save()
        return self.envelope({cid:dict(type='revoked',message='The facilitator released this seat.') for cid in old})

    def disconnect(self,cid):
        self.live.pop(cid,None);self.pending.pop(cid,None)
        return self.envelope()

    def receive(self,cid,message):
        short(cid,100)
        if not isinstance(message,dict) or len(json.dumps(message))>12000:raise ValueError('Message is too large.')
        kind=message.get('type');rid=short(message.get('id',''),100)
        if kind=='hello':
            if cid in self.live:return self.envelope()
            token=message.get('token')
            if isinstance(token,str) and token:
                role=next((r for r,s in self.seats.items() if secrets.compare_digest(s['token'],token)),None)
                if not role:raise ValueError('The saved seat is no longer valid. Clear it and request admission again.')
                old=[c for c,r in self.live.items() if r==role and c!=cid]
                for c in old:del self.live[c]
                self.live[cid]=role;self.pending.pop(cid,None)
                direct={c:dict(type='revoked',message='This seat reconnected in another tab.') for c in old}
                direct[cid]=dict(type='admitted',role=role,token=token)
                return self.envelope(direct)
            if len(self.pending)>=20 and cid not in self.pending:raise ValueError('The waiting room is full.')
            name=short(message.get('name',''),60)
            if not name:raise ValueError('Enter your name.')
            self.pending[cid]=dict(name=name,requested=choice(message.get('role'),ROLES))
            return self.envelope({cid:dict(type='waiting',message='Connected. Waiting for the facilitator to admit you.')})
        if cid not in self.live:raise ValueError('Wait for the facilitator to admit you.')
        role=self.live[cid]
        identity=role+':'+rid
        if not rid:raise ValueError('Message ID required.')
        if identity in self.seen:return self.envelope({cid:dict(type='ack',id=rid)})
        if kind=='sheet':
            if message.get('epoch')!=self.epoch:raise ValueError('The phase has closed. Read the current sheet before submitting again.')
            self.sheets[role]=self.validate_sheet(role,message.get('sheet'))
        elif kind=='chat':self.add_chat(role,message.get('channel'),message.get('text'))
        else:raise ValueError('Unknown player message.')
        self.seen=(self.seen+[identity])[-2000:];self.save()
        return self.envelope({cid:dict(type='ack',id=rid)})

    def validate_sheet(self,role,row):
        if role not in self.required():raise ValueError('There is no decision sheet for your seat in this phase.')
        if not isinstance(row,dict):raise ValueError('A sheet is required.')
        result={'note':short(row.get('note',''),4000)};stage=self.game.stage
        if stage=='draft':
            for a,opts in ASSETS.get(role,{}).items():result[a]=choice(row.get(a),opts)
            # Council intentions are spoken or discussed in chat; draft sheets only record assets.
        elif stage=='vision':result['choice']=choice(row.get('choice'),['None','Navigation','Security'])
        elif stage=='commit':
            if role=='A':
                result['reserve']=choice(row.get('reserve'),['Keep','Relief lift','Tender cover'])
                result['disclose']=boolean(row.get('disclose',False))
            else:
                for a,opts in ASSETS[role].items():result[a]=choice(row.get(a),opts)
        elif stage=='council':
            if role in ('GN','JN','A'):result['navigation']=choice(row.get('navigation'),NAV+['No agreement','Unsigned'])
            if role in ('GS','JS','A'):result['security']=choice(row.get('security'),SEC+['No agreement','Unsigned'])
            if role=='A':result['warrant']=boolean(row.get('warrant',False))
        elif stage=='trial-vote':
            for d in ('navigation','military'):
                if role=='A' or role in ({'navigation':('GN','JN'),'military':('GS','JS')}[d]):
                    result[d]=boolean(row.get(d,False))
            if role!='A':result['pledge']=boolean(row.get('pledge',False))
        elif stage=='ceremony-vote':result['approve']=boolean(row.get('approve',False))
        return result

    def add_chat(self,role,channel,text):
        allowed=list(CHANNELS)+['facilitator-'+r for r in ROLES] if role=='F' else self.channels(role)
        choice(channel,allowed);text=short(text)
        if not text:raise ValueError('Write a message first.')
        if len(self.chats)>=2000:raise ValueError('The conversation record is full. Export it before starting another session.')
        self.chats.append(dict(id=len(self.chats)+1,time=moment(),round=self.game.round,phase=self.game.stage,
                              epoch=self.epoch,role=role,name='Facilitator' if role=='F' else self.seats[role]['name'],
                              channel=channel,text=text))

    def advance(self,epoch,proposal=None,allow_missing=False):
        if epoch!=self.epoch:raise ValueError('This phase has already changed.')
        missing=[r for r in self.required() if r not in self.sheets]
        if missing and not allow_missing:raise ValueError('Still waiting for '+', '.join(missing)+'. Close with printed defaults only at the deadline.')
        stage=self.game.stage;s=self.sheets;p={'stage':stage,'notes':{r:x['note'] for r,x in s.items() if x.get('note')}}
        if stage=='ended':raise ValueError('The settlement is complete. Use table chat for the debrief and export the record.')
        if stage=='draft':
            p['proposals']={}
            for r in ROLES:
                row=dict(s.get(r,{}));row.pop('note',None)
                if not row:
                    row=dict(DEFAULTS['Guild' if r.startswith('G') else 'Janissariat']) if r!='A' else {'warrant':False}
                p['proposals'][r]=row
        elif stage=='vision':p['choice']=s.get('A',{}).get('choice','None')
        elif stage=='commit':
            p.update(assignments={r:{a:s.get(r,{}).get(a) for a in ASSETS[r]} for r in ROLES if r!='A' and r in s},
                     reserve=s.get('A',{}).get('reserve','Keep'),disclose=s.get('A',{}).get('disclose',False))
        elif stage=='council':
            p.update(navigation={r:s.get(r,{}).get('navigation','No agreement') for r in ('GN','JN','A')},
                     security={r:s.get(r,{}).get('security','No agreement') for r in ('GS','JS','A')},
                     warrant=s.get('A',{}).get('warrant',False))
        elif stage=='trial-vote':
            p['votes']={r:dict(navigation=s.get(r,{}).get('navigation',False),military=s.get(r,{}).get('military',False),
                Guild=r.startswith('G') and s.get(r,{}).get('pledge',False),Janissariat=r.startswith('J') and s.get(r,{}).get('pledge',False)) for r in ROLES}
        elif stage=='ceremony-vote':p['approvals']={r:s.get(r,{}).get('approve',False) for r in ROLES}
        elif stage in ('trial-proposal','ceremony-proposal'):
            if not isinstance(proposal,dict):raise ValueError('Record the exact proposal first.')
            p.update({k:deepcopy(proposal[k]) for k in ('articles','plan','pledges','package') if k in proposal})
        history_start=len(self.game.history)
        self.game.apply(p)
        self.audit.append(dict(time=moment(),event='phase closed',epoch=epoch,missing=missing,submitted=deepcopy(s),events=deepcopy(self.game.history[history_start:])))
        self.sheets={};self.save();return self.envelope()

    def dispatch(self,action,p):
        self.check_host(p.get('host_key'))
        if action=='message':return self.receive(p.get('connection'),p.get('message'))
        if action=='approve':return self.approve(p.get('connection'),p.get('role'))
        if action=='release':return self.release(p.get('role'))
        if action=='disconnect':return self.disconnect(p.get('connection'))
        if action=='advance':return self.advance(p.get('epoch'),p.get('proposal'),p.get('allow_missing') is True)
        if action=='chat':self.add_chat('F',p.get('channel'),p.get('text'));self.save();return self.envelope()
        if action=='reject':
            cid=p.get('connection');self.pending.pop(cid,None)
            return self.envelope({cid:dict(type='revoked',message='The facilitator declined admission.')})
        if action=='new':
            key=self.host_key;path=self.path
            # Preserve the complete previous session before beginning a new room.
            if path and path.exists():path.replace(path.with_name('multiplayer-'+secrets.token_hex(5)+'.json'))
            self.__init__(path);self.host_key=key;self.save();return self.envelope()
        raise ValueError('Unknown facilitator action.')

    def report(self):
        esc=html.escape
        def value(v):
            if isinstance(v,dict):return '<dl>'+''.join('<dt>'+esc('Stability · Sorenne’s Fall' if k=='communities' else str(k).replace('_',' '))+'</dt><dd>'+value(x)+'</dd>' for k,x in v.items())+'</dl>'
            if isinstance(v,list):return '<ul>'+''.join('<li>'+value(x)+'</li>' for x in v)+'</ul>'
            return esc(str(v))
        blocks=[]
        phase_number=0
        for phase in self.audit:
            if phase['event']!='phase closed':continue
            phase_number+=1
            epoch=phase['epoch'];_,_,round_,stage=epoch.rsplit(':',3)
            messages=[c for c in self.chats if c['epoch']==epoch]
            blocks.append(f'<section><h2>Round {round_} · {esc(stage)}</h2>')
            blocks.append('<div class="mechanics"><h3>Submitted sheets at the bell</h3><div class="grid">'+''.join('<article><h4>'+esc(ROLE_NAMES[r])+'</h4>'+value(v)+'</article>' for r,v in phase['submitted'].items())+'</div><p>Missing sheets: '+esc(', '.join(phase['missing']) or 'none')+'</p></div>')
            for event in phase.get('events',[]):
                blocks.append('<div class="mechanics"><h3>'+esc(event['event'])+'</h3>'+value({k:v for k,v in event.items() if k not in ('round','event','sequence','phase')})+'</div>')
            blocks.append('<div class="conversations"><div class="tabs" role="tablist">')
            channels=list(dict.fromkeys(c['channel'] for c in messages))
            for index,channel in enumerate(channels):
                blocks.append('<button role="tab" aria-selected="'+str(index==0).lower()+'" data-panel="p'+str(phase_number)+'c'+str(index)+'">'+esc(channel)+'</button>')
            blocks.append('</div>')
            for index,channel in enumerate(channels):
                blocks.append('<div role="tabpanel" id="p'+str(phase_number)+'c'+str(index)+'"'+(' hidden' if index else '')+'>'+''.join('<p><b>'+esc(c['name'])+' · '+esc(c['role'])+'</b>: '+esc(c['text'])+'</p>' for c in messages if c['channel']==channel)+'</div>')
            blocks.append('</div></section>')
        closed={x.get('epoch') for x in self.audit if x['event']=='phase closed'}
        remaining=[c for c in self.chats if c['epoch'] not in closed]
        if remaining:blocks.append('<h2>Current discussion / debrief</h2>'+value(remaining))
        return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>The Void Throne — multiplayer record</title><style>body{font:17px/1.6 system-ui;max-width:1200px;margin:auto;padding:28px;background:#f4f0e7;color:#20353d}h1,h2{font-family:Georgia}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.mechanics{background:#e0eae6;border-left:4px solid #387075;padding:20px;margin:24px 0}dt{font-weight:bold}dd{margin-left:12px}details{background:white;padding:16px;margin:8px 0}section{overflow-wrap:anywhere}.tabs{display:flex;gap:8px;flex-wrap:wrap}.tabs button{padding:8px 12px;cursor:pointer;background:white;color:#20353d;border:1px solid #8ea79b}.tabs button[aria-selected=true]{background:#20353d;color:white}[role=tabpanel]{background:white;padding:16px}[hidden]{display:none}@media print{[role=tabpanel][hidden]{display:block}.tabs{display:none}}</style><h1>The Void Throne</h1><p>Human-seat multiplayer record. Each remote seat submits its own decisions; the facilitator closes phases. This facilitator export includes private visions and faction conversations.</p>'+''.join(blocks)+"<script>document.querySelectorAll('[data-panel]').forEach(b=>b.onclick=()=>{const group=b.closest('.conversations');group.querySelectorAll('[data-panel]').forEach(x=>x.setAttribute('aria-selected',String(x===b)));group.querySelectorAll('[role=tabpanel]').forEach(x=>x.hidden=x.id!==b.dataset.panel);});</script></html>").encode('utf8')
