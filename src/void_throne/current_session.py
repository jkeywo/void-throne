"""v0.4 paper procedure; v0.3 remains available for archived replays."""
from copy import deepcopy
from dataclasses import asdict
import json
from .session import Session as LegacySession, ROOT, notes, choice, boolean
from .operations import State
from .orders_v04 import NAV, SEC, AUTH, LABELS, orders, resolve, veto_rights
from .settlement import leverage, ballot

RULESET='vt:rules:asset-orders-v0.4'

class Session(LegacySession):
    def __init__(self):
        super().__init__();self.vetoes={'navigation':[],'military':[]}

    def weights(self):return leverage(self.state,self.foresight,current=True)

    def count_ballot(self,approvals):return ballot(self.state,self.foresight,approvals,self.package,current=True)

    def apply(self,payload):
        return super().apply(dict(payload,ruleset=RULESET))

    def _apply(self,p):
        if p.get('stage')!=self.stage:raise ValueError('This sheet belongs to a different phase.')
        ns=notes(p)
        if self.stage=='council':
            # The owner allocates their own offered assets; authority supplies no approval gate.
            navrows=p.get('navigation',{});secrows=p.get('security',{})
            if not isinstance(navrows,dict) or set(navrows)-{'GN'}:raise ValueError('GN records the Navigation asset allocations.')
            if not isinstance(secrows,dict) or set(secrows)-{'JS'}:raise ValueError('Security allocations come from JS.')
            # GN records the programme, including Grey Petrel if offered to the council.
            nav=orders(navrows.get('GN',[]),'navigation')
            sec=orders(secrows.get('JS',[]),'military')
            before=deepcopy(self.state)
            inputs=dict(rnd=self.round,w=self.assignments['Guild']['wayfarer'],l=self.assignments['Guild']['lantern'],
                        s=self.assignments['Janissariat']['spear'],v=self.assignments['Janissariat']['vigil'],
                        nav=nav,sec=sec,na=self.articles['navigation'],ma=self.articles['military'],
                        warrant=boolean(p.get('warrant',False)),intervention=self.reserve,vetoes=self.vetoes)
            result,detail=resolve(State(**self.state),**inputs);self.state=asdict(result)
            self.record('Council order sheets',navigation=nav,security=sec,vetoes=self.vetoes,
                        warrant=inputs['warrant'],notes=ns)
            self.record('Operational resolution',before=before,after=self.state,inputs=inputs,detail=detail,
                        effects=['Monthly consumption: Stability -1.',*detail['events'],
                                 f"Prepared Beacon {detail['prepared']}; transport wear {detail['transport_wear']}; private trade wear {detail['trade_wear']}.",
                                 'Readiness +1 for qualifying combat, otherwise -1; final tracks clamped 0–4.'],
                        leverage=self.weights())
            self.pledges=[]
            self.stage='veto' if self.round==1 else 'free'
            if self.round==2:self.vetoes={'navigation':[],'military':[]}
        elif self.stage=='veto':
            decisions={};required={}
            for domain,options in [('navigation',NAV),('military',SEC)]:
                people=veto_rights(self.articles,self.assignments,self.reserve)[domain];required[domain]=list(people)
                rows=p.get(domain,{})
                if not isinstance(rows,dict) or set(rows)-set(people):raise ValueError('Only the existing authority can set this veto.')
                selected=[choice(rows.get(r,'None'),options+['None']) for r in people]
                decisions[domain]=list(dict.fromkeys(x for x in selected if x!='None'))
            self.vetoes=decisions
            self.record('Next-round vetoes',vetoes=decisions,authority=deepcopy(self.articles),required_agreement=required,choices={d:{r:p.get(d,{}).get(r,'None') for r in people} for d,people in required.items()},expires_after_round=2,notes=ns)
            self.stage='trial-proposal'
        else:
            stage=self.stage
            if stage=='commit':
                choice(p.get('reserve','Keep'),['Keep','Council','Tender cover'])
                # Reuse unchanged faction/pledge validation, then restore the new cutter assignment.
                reserve=p.get('reserve','Keep');p=dict(p,reserve='Keep' if reserve=='Council' else reserve)
                super()._apply(p)
                self.reserve=reserve if self.state['reserve'] else 'Keep'
                self.history[-1]['reserve']=self.reserve
            else:super()._apply(p)
            if self.stage=='commit' and stage in ('draft','vision') and self.vision:
                ident=self.vision['id'];self.vision=json.loads((ROOT/'design/v04/private-cards'/f'{ident}.json').read_text(encoding='utf8'))
                self.history[-1]['private_answer']=deepcopy(self.vision)

    def public(self):
        out=super().public();out.update(ruleset=RULESET,vetoes=deepcopy(self.vetoes),order_labels=LABELS,
            veto_authority=veto_rights(self.articles,self.assignments,self.reserve))
        return out

def from_actions(actions):
    game=Session() if not actions or actions[0].get('ruleset')==RULESET else LegacySession()
    for action in actions:game.apply(action)
    return game
