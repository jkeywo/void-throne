"""v0.5: development, opening free discussion, factions, councils, resolution."""
from copy import deepcopy
from dataclasses import asdict
import json
from .session import Session as LegacySession, ROOT, ROLES, notes, choice, boolean
from .session_v04 import Session as AssetSession, RULESET as V04_RULESET
from .orders_v04 import NAV, SEC, orders, resolve, veto_rights
from .operations import State, clamp
from .charter import evaluate

RULESET='vt:rules:opening-developments-v0.5'
DEVELOPMENTS=json.loads((ROOT/'design/developments.json').read_text(encoding='utf8'))

def development_options(rnd):
    return [deepcopy(d) for d in DEVELOPMENTS if d['round']==rnd]

def development_effect(card, detail):
    trigger=card['trigger']
    delivered=detail['delivered_orders'];active=detail['orders']
    met={'Delivered Relief':'Relief' in delivered,
         'Completed Repair':'Repair' in active,
         'Delivered Relief and protection':'Relief' in delivered and detail['guarded'],
         'No attack or interception attempted':not detail['offensive_attempt']}[trigger]
    return dict(id=card['id'],title=card['title'],condition_met=met,track=card['track'],
                change=card['success'] if met else card['failure'])

class Session(AssetSession):
    def __init__(self):
        super().__init__();self.stage='opening';self.development=None

    def apply(self,payload):
        return LegacySession.apply(self,dict(payload,ruleset=RULESET))

    def _apply(self,p):
        if p.get('stage')!=self.stage:raise ValueError('This decision belongs to a different phase.')
        ns=notes(p)
        if self.stage=='opening':
            ident=choice(p.get('development'),[d['id'] for d in development_options(self.round)])
            self.development=next(d for d in development_options(self.round) if d['id']==ident)
            self.record('Opening development',development={k:self.development[k] for k in ('id','title','announcement')},notes=ns)
            self.stage='free'
        elif self.stage=='free':
            self.record('Opening free discussion',notes=ns);self.stage='veto'
        elif self.stage=='veto':
            decisions={};required={};choices={}
            for domain,options in [('navigation',NAV),('military',SEC)]:
                people=veto_rights(self.articles,self.assignments,self.reserve)[domain];required[domain]=people
                rows=p.get(domain,{})
                if not isinstance(rows,dict) or set(rows)-set(people):raise ValueError('Only the existing authority can set this veto.')
                choices[domain]={r:choice(rows.get(r,'None'),options+['None']) for r in people}
                decisions[domain]=list(dict.fromkeys(v for v in choices[domain].values() if v!='None'))
            self.vetoes=decisions
            self.record('Opening vetoes',vetoes=decisions,authority=self.articles,contributors_from_round=self.round-1,
                        required_agreement=required,choices=choices,expires_after_round=self.round,notes=ns)
            self.stage='trial-proposal'
        elif self.stage=='trial-proposal':
            super()._apply(p)
            self.trial['id']=f'trial-{self.round}'
            self.trial['operational_round']=self.round
            self.history[-1]['proposal']=deepcopy(self.trial)
        elif self.stage=='trial-vote':
            rows=p.get('votes',{})
            if set(rows)!=set(ROLES):raise ValueError('Record all five players before closing the trial.')
            votes={r:dict(proposal_id=self.trial['id'],
                article_approvals={d:boolean(row.get(d,False)) for d in ('navigation','military')},
                commitment_approvals={o:boolean(row.get(o,False)) for o in ('Guild','Janissariat')}) for r,row in rows.items()}
            gate=evaluate(self.trial,votes,self.state)
            # Rejected amendments preserve the existing article, not an automatic reversion.
            for d in ('navigation','military'):
                if gate['issues'][d]:gate['articles_after'][d]=self.articles[d]
            self.articles=gate['articles_after'];self.pledges=gate['activated_commitments']
            self.record('Provisional agreement and result',votes=votes,result=gate,notes=ns)
            self.stage='draft'
        elif self.stage=='council':
            # The inherited resolver records ordinary operations before the conditional event.
            super()._apply(p)
            event=self.history[-1];detail=event['detail'];effect=development_effect(self.development,detail)
            raw=detail['unclamped_tracks'].copy();raw[effect['track']]+=effect['change']
            for track,value in raw.items():self.state[track]=clamp(value)
            detail['development_effect']=effect
            event['after']=deepcopy(self.state);event['leverage']=self.weights()
            event['effects'].append(f"Development {effect['id']}: {effect['track']} {effect['change']:+d}; applied before final track clamps.")
            detail['outcomes'].append(self.development['outcome_met'] if effect['condition_met'] else self.development['outcome_unmet'])
            self.vetoes={'navigation':[],'military':[]}
            if self.round==1:
                self.round=2;self.stage='opening';self.development=None;self.vision=None;self.disclosed=False;self.trial=None;self.drafts={}
            else:self.stage='ceremony-proposal'
        else:super()._apply(p)

    def public(self):
        out=super().public();out['ruleset']=RULESET
        out['development']=({k:self.development[k] for k in ('id','title','announcement')} if self.development else None)
        # Facilitator-only choice list; Multiplayer.view deliberately omits it.
        out['development_options']=development_options(self.round) if self.stage=='opening' else []
        return out

def new_game(ruleset=RULESET):
    if ruleset==RULESET:return Session()
    if ruleset==V04_RULESET:return AssetSession()
    if ruleset=='vt:rules:revised-visions-v0.3':return LegacySession()
    raise ValueError('Unsupported saved ruleset.')

def from_actions(actions):
    game=new_game(actions[0].get('ruleset','vt:rules:revised-visions-v0.3')) if actions else Session()
    for action in actions:game.apply(action)
    return game
