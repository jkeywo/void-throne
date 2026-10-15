"""All-seat paper procedure. Decisions are supplied; the facilitator only resolves."""
from dataclasses import asdict
from copy import deepcopy
from pathlib import Path
import json
from .operations import State, resolve
from .presentation import track_descriptions
from .settlement import leverage, ballot
from .charter import evaluate, apply_locks, CHOICES

ROOT=Path(__file__).resolve().parents[2]
ROLES=('GN','GS','JN','JS','A')
ASSETS={'GN':{'wayfarer':['Council','Trade'],'lantern':['Council','Maintain']},
        'GS':{'wayfarer':['Council','Trade'],'lantern':['Council','Maintain']},
        'JN':{'spear':['Council','Raid','Stand down'],'vigil':['Council','Home']},
        'JS':{'spear':['Council','Raid','Stand down'],'vigil':['Council','Home']}}
NAV=['Relief','Military','Shared','Repair','Hold']
SEC=['Campaign','Raid','Guard','Restraint']
ARTICLES={'navigation':['NG','NI','NJ'],'military':['MI','MA','MJ']}
DEFAULTS={'Guild':{'wayfarer':'Trade','lantern':'Maintain'},'Janissariat':{'spear':'Stand down','vigil':'Home'}}

def choice(value,allowed):
    if value not in allowed:raise ValueError('Choose one of: '+', '.join(map(str,allowed)))
    return value

def boolean(value):
    if type(value) is not bool:raise ValueError('An approval must be an explicit yes or no.')
    return value

def notes(payload):
    result=payload.get('notes',{})
    if not isinstance(result,dict) or any(k not in ROLES or not isinstance(v,str) or len(v)>4000 for k,v in result.items()):
        raise ValueError('Notes must be short text, keyed by player role.')
    return result

class Session:
    def __init__(self):
        self.state=asdict(State());self.round=1;self.stage='draft';self.foresight=3
        self.articles={'navigation':'I','military':'I'};self.pledges=[]
        self.history=[];self.actions=[];self.drafts={};self.assignments={};self.reserve='Keep'
        self.vision=None;self.disclosed=False;self.trial=None;self.package=None;self.ballots=0
        self.settlement=None;self.report_notes=''

    def record(self,event,**data):
        self.history.append({'sequence':len(self.history)+1,'round':self.round,'phase':self.stage,'event':event,**deepcopy(data)})

    def apply(self,payload):
        # Validate on a copy. A rejected request cannot spend a token or half-apply orders.
        draft=deepcopy(self);draft._apply(payload);draft.actions.append(deepcopy(payload))
        self.__dict__.update(draft.__dict__)
        return self.public()

    def _apply(self,p):
        if not isinstance(p,dict) or p.get('stage')!=self.stage:raise ValueError('This sheet belongs to a different phase. Refresh before submitting.')
        ns=notes(p)
        if self.stage=='draft' and 'choice' in p:
            # Current paper procedure: choose foresight before hearing faction plans.
            # Legacy records with proposals still follow their original draft step.
            self.stage='vision'
            self._apply(dict(p,stage='vision'))
            return
        if self.stage=='draft':
            proposals=p.get('proposals',{})
            if set(proposals)!=set(ROLES):raise ValueError('Record all five draft positions; disagreements remain visible.')
            for role in ROLES:
                row=proposals[role]
                for asset,options in ASSETS.get(role,{}).items():choice(row.get(asset),options)
                choice(row.get('navigation','Undeclared'),NAV+['Undeclared']);choice(row.get('security','Undeclared'),SEC+['Undeclared'])
                if role=='A':boolean(row.get('warrant',False))
            self.drafts=deepcopy(proposals);self.record('Public draft sheets',sheets=proposals,notes=ns,standing_commitments=self.pledges)
            self.stage='vision'
        elif self.stage=='vision':
            selected=choice(p.get('choice'),['None','Navigation','Security'])
            before=self.foresight
            if selected!='None':
                if self.foresight<1:raise ValueError('No foresight remains.')
                self.foresight-=1
                ident=f'R{self.round}-'+('N' if selected=='Navigation' else 'S')
                self.vision=json.loads((ROOT/'design/private-cards'/f'{ident}.json').read_text(encoding='utf-8'))
            else:self.vision=None
            self.record('Foresight purchase',choice=selected,before=before,after=self.foresight,notes=ns,
                        private_answer=self.vision,leverage=leverage(self.state,self.foresight))
            self.stage='commit'
        elif self.stage=='commit':
            rows=p.get('assignments',{});sign=p.get('signatures') # Legacy transcripts retain their original signature gate.
            self.disclosed=boolean(p.get('disclose',False));result={};issues=[]
            for owner,roles in [('Guild',('GN','GS')),('Janissariat',('JN','JS'))]:
                submitted=[]
                for role in roles:
                    row=rows.get(role,{})
                    if not isinstance(row,dict):raise ValueError('Asset assignments must be a sheet.')
                    # Missing or multiple asset entries use printed asset defaults.
                    submitted.append({a:row.get(a) if row.get(a) in opts else DEFAULTS[owner][a] for a,opts in ASSETS[role].items()})
                    if sign is not None:boolean(sign.get(role,False))
                confirmed=all(sign.get(role) is True for role in roles) if sign is not None else all(role in rows for role in roles)
                if submitted[0]==submitted[1] and confirmed:result[owner]=submitted[0]
                else:result[owner]=deepcopy(DEFAULTS[owner]);issues.append(owner+': no matching confirmed assignments; printed defaults apply.')
            result=apply_locks(result,self.pledges)
            for owner,row in result.items():
                for asset in row:
                    if asset!='vigil' and not self.state[asset]:row[asset]='Absent'
            self.assignments=result;self.reserve=choice(p.get('reserve','Keep'),['Keep','Relief lift','Tender cover'])
            if not self.state['reserve']:self.reserve='Keep'
            self.record('Final faction sheets',submitted=rows,sheets=result,reserve=self.reserve,
                        disclosed=self.disclosed,notes=ns,defaults=issues,standing_commitments=self.pledges)
            self.stage='council'
        elif self.stage=='council':
            decisions={};authorities={};valid={}
            auth={'navigation':{'I':('A',),'NI':('A',),'NG':('GN',),'NJ':('GN','JN')},
                  'military':{'I':('A',),'MI':('A',),'MA':('JS',),'MJ':('GS','JS')}}
            for domain,key,options,default in [('navigation','navigation',NAV,'Hold'),('military','security',SEC,'Restraint')]:
                allowed=('GN','JN','A') if key=='navigation' else ('GS','JS','A')
                rows=p.get(key,{})
                if not isinstance(rows,dict) or any(r not in allowed for r in rows):raise ValueError('Unknown council representative.')
                for val in rows.values():choice(val,options+['No agreement','Unsigned'])
                required=auth[domain][self.articles[domain]];votes=[rows.get(r,'No agreement') for r in required]
                valid[key]=len(set(votes))==1 and votes[0] in options
                decisions[key]=votes[0] if valid[key] else default;authorities[key]=list(required)
            warrant=boolean(p.get('warrant',False));before=deepcopy(self.state)
            inputs=dict(rnd=self.round,w=self.assignments['Guild']['wayfarer'],l=self.assignments['Guild']['lantern'],
                        s=self.assignments['Janissariat']['spear'],v=self.assignments['Janissariat']['vigil'],
                        nav=decisions['navigation'],sec=decisions['security'],na=self.articles['navigation'],ma=self.articles['military'],
                        warrant=warrant,intervention=self.reserve,nav_signed=valid['navigation'],sec_signed=valid['security'])
            result,detail=resolve(State(**self.state),**inputs);self.state=asdict(result)
            self.record('Council order sheets',navigation=p.get('navigation',{}),security=p.get('security',{}),
                        effective=decisions,required_agreement=authorities,valid=valid,warrant=warrant,notes=ns)
            self.record('Operational resolution',before=before,after=self.state,inputs=inputs,detail=detail,
                        effects=effect_ledger(before,self.state,inputs,detail),leverage=leverage(self.state,self.foresight))
            self.pledges=[] # Each active assignment has now completed its one round.
            self.stage='trial-proposal' if self.round==1 else 'free'
        elif self.stage=='trial-proposal':
            articles=p.get('articles',{})
            for d,options in ARTICLES.items():choice(articles.get(d),options)
            pledges=p.get('pledges',[])
            if not isinstance(pledges,list) or len(pledges)>2:raise ValueError('At most one commitment per faction.')
            seen=set()
            for pledge in pledges:
                owner=choice(pledge.get('owner'),['Guild','Janissariat'])
                if owner in seen:raise ValueError('Only one commitment per faction.');
                seen.add(owner)
                assets=['Wayfarer','Lantern'] if owner=='Guild' else ['Spear','Vigil']
                asset=choice(pledge.get('asset'),assets);choice(pledge.get('assignment'),CHOICES[asset])
                choice(pledge.get('article'),list(articles.values()))
                if asset!='Vigil' and not self.state[asset.lower()]:raise ValueError('Unavailable assets cannot be pledged.')
            plan=p.get('plan','')
            if not isinstance(plan,str) or len(plan)>4000:raise ValueError('Keep the public plan to 4,000 characters.')
            self.trial={'id':'trial-1','articles':articles,'commitments':pledges,'plan':plan}
            self.record('Exact provisional proposal',proposal=self.trial,notes=ns);self.stage='trial-vote'
        elif self.stage=='trial-vote':
            rows=p.get('votes',{})
            if set(rows)!=set(ROLES):raise ValueError('Record all five players before closing the trial.')
            votes={}
            for role,row in rows.items():
                votes[role]={'proposal_id':self.trial['id'],'article_approvals':{d:boolean(row.get(d,False)) for d in ARTICLES},
                             'commitment_approvals':{owner:boolean(row.get(owner,False)) for owner in DEFAULTS}}
            gate=evaluate(self.trial,votes,self.state)
            self.articles=gate['articles_after'];self.pledges=gate['activated_commitments']
            self.record('Provisional agreement and result',votes=votes,result=gate,notes=ns)
            self.round=2;self.stage='draft';self.vision=None;self.disclosed=False
        elif self.stage=='free':
            self.record('Final free discussion',notes=ns);self.stage='ceremony-proposal'
        elif self.stage=='ceremony-proposal':
            package=p.get('package',{})
            for d,options in ARTICLES.items():choice(package.get(d),options)
            self.package=deepcopy(package);self.record('Exact settlement package',package=package,weights=leverage(self.state,self.foresight),notes=ns)
            self.stage='ceremony-vote'
        elif self.stage=='ceremony-vote':
            approvals=p.get('approvals',{})
            if set(approvals)!=set(ROLES):raise ValueError('Record a yes or no for every player.')
            for val in approvals.values():boolean(val)
            tally=ballot(self.state,self.foresight,approvals,self.package);self.ballots+=1
            self.record('Settlement ballot',package=self.package,approvals=approvals,result=tally,notes=ns)
            if tally['ratified'] or self.ballots>=2:
                self.articles=self.package if tally['ratified'] else {'navigation':'I','military':'I'}
                self.settlement=dict(tally,package=self.package,approvals=approvals,articles_after=self.articles)
                self.stage='ended'
            else:self.stage='ceremony-proposal'
        elif self.stage=='ended':
            self.record('Debrief',notes=ns)
        else:raise ValueError('Unknown phase.')

    def public(self):
        covers=[json.loads((ROOT/'design/public-covers'/f'R{self.round}-{d}.json').read_text(encoding='utf-8')) for d in ('N','S')]
        return deepcopy(dict(state=self.state,round=self.round,stage=self.stage,foresight=self.foresight,articles=self.articles,
                             pledges=self.pledges,drafts=self.drafts,assignments=self.assignments,reserve=self.reserve,
                             selected_vision=self.vision,disclosed=self.disclosed,covers=covers,track_descriptions=track_descriptions(),trial=self.trial,package=self.package,
                             ballots=self.ballots,settlement=self.settlement,leverage=leverage(self.state,self.foresight),
                             history=self.history,actions=self.actions,mode='all_seats',ruleset='vt:rules:revised-visions-v0.3'))

def effect_ledger(before,after,inputs,detail):
    out=['Monthly consumption: Stability -1.']
    out.append(f'Beacon prepared to {detail["prepared"]}: Maintain +1 or funded Repair +2; preparation capped at 4.')
    if detail['delivered']:out.append('Delivered '+detail['nav']+': Stability '+str({'Relief':2,'Military':0,'Shared':1}[detail['nav']])+'.')
    out.extend(detail['events'])
    out.append(f'Crossing wear: {int(detail["delivered"])+int(detail["trade"] or (before["wayfarer"] and not after["wayfarer"]))}; final Beacon {after["beacon"]}.')
    out.append('Readiness '+('+1 after successful combat.' if detail['combat'] else '-1: no qualifying combat.'))
    out.append('Final Stability '+str(after['communities'])+'; tracks capped 0–4 only after aggregate resolution.')
    return out
