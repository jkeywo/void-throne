import json,sys,unittest
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from void_throne.current_session import Session,DEVELOPMENTS,development_effect,from_actions,RULESET
from void_throne.session_v04 import Session as V04Session
from void_throne.session import ROLES
from void_throne.multiplayer import Multiplayer
from void_throne.browser_host import BrowserHost
from void_throne.orders_v04 import resolve
from void_throne.operations import State
def o(order,asset):return {'order':order,'asset':asset}
def open_round(g,card,nav=None,sec=None,articles=None,agree=False,pledges=None):
 g.apply(dict(stage='opening',development=card))
 g.apply(dict(stage='free'))
 g.apply(dict(stage='veto',navigation=nav or {},military=sec or {}))
 g.apply(dict(stage='trial-proposal',articles=articles or {'navigation':'NG','military':'MA'},pledges=pledges or [],plan=''))
 g.apply(dict(stage='trial-vote',votes={r:dict(navigation=agree,military=agree,Guild=agree,Janissariat=agree) for r in ROLES}))
def commit(g,choice='None',w='Council',l='Council',s='Council',v='Council',reserve='Keep'):
 g.apply(dict(stage='draft',choice=choice))
 g.apply(dict(stage='commit',assignments={r:dict(wayfarer=w,lantern=l) if r.startswith('G') else dict(spear=s,vigil=v) for r in ROLES if r!='A'},reserve=reserve))
def council(g,nav=None,sec=None,warrant=False):
 g.apply(dict(stage='council',navigation={'GN':nav or []},security={'JS':sec or []},warrant=warrant))
class OpeningRoundTests(unittest.TestCase):
 def test_complete_sequence_two_openings_two_trials_and_direct_ceremony(self):
  g=Session();self.assertEqual(g.stage,'opening')
  open_round(g,'R1-RELIEF',articles={'navigation':'NJ','military':'MJ'},agree=True)
  self.assertEqual((g.round,g.stage),(1,'draft'))
  commit(g,'Navigation')
  council(g,[o('Relief','Lantern'),o('Military','Wayfarer')],[o('Campaign','Spear'),o('Guard','Vigil')])
  self.assertEqual((g.round,g.stage),(2,'opening'));self.assertIsNone(g.vision);self.assertFalse(g.pledges)
  g.apply(dict(stage='opening',development='R2-TRUCE'));g.apply(dict(stage='free'))
  self.assertEqual(g.public()['veto_authority'],{'navigation':['GN','JN'],'military':['GS','JS']})
  g.apply(dict(stage='veto',navigation={'GN':'Relief','JN':'Repair'},military={'JS':'Campaign'}))
  g.apply(dict(stage='trial-proposal',articles={'navigation':'NG','military':'MA'}))
  g.apply(dict(stage='trial-vote',votes={r:{} for r in ROLES}))
  self.assertEqual(g.articles,{'navigation':'NJ','military':'MJ'}) # rejected amendment retains joint
  self.assertEqual(g.vetoes['navigation'],['Relief','Repair'])
  commit(g);council(g)
  self.assertEqual(g.stage,'ceremony-proposal');self.assertEqual(g.foresight,2)
  for _ in range(2):
   g.apply(dict(stage='ceremony-proposal',package={'navigation':'NG','military':'MA'}))
   g.apply(dict(stage='ceremony-vote',approvals={r:False for r in ROLES}))
  self.assertEqual(g.articles,{'navigation':'I','military':'I'})
  self.assertEqual(from_actions(g.actions).public(),g.public())
 def test_development_choice_is_round_specific_and_irrevocable(self):
  g=Session();before=g.public()
  with self.assertRaises(ValueError):g.apply(dict(stage='opening',development='R2-TRUCE'))
  self.assertEqual(g.public(),before)
  g.apply(dict(stage='opening',development='R1-REPAIR'))
  with self.assertRaises(ValueError):g.apply(dict(stage='opening',development='R1-RELIEF'))
  self.assertEqual(g.development['id'],'R1-REPAIR')
 def test_condition_uses_delivered_not_selected_relief(self):
  g=Session();g.state['beacon']=0;open_round(g,'R1-RELIEF');commit(g)
  council(g,[o('Relief','Lantern')])
  e=g.history[-1]
  self.assertFalse(e['detail']['development_effect']['condition_met'])
  self.assertEqual(g.state['communities'],0) # consumption, failed voyage, development
 def test_development_adjustment_precedes_final_clamp(self):
  g=Session();g.state['communities']=4
  open_round(g,'R1-RELIEF');commit(g)
  council(g,[o('Relief','Lantern')],[o('Guard','Vigil')])
  e=g.history[-1];self.assertEqual(e['detail']['unclamped_tracks']['communities'],6)
  self.assertEqual(g.state['communities'],4)
  # Negative truce effect consumes excess; it must not turn a clamped 4 into 3.
  open_round(g,'R2-TRUCE');g.state.update(beacon=3,communities=4,readiness=3)
  commit(g);council(g,[o('Relief','Lantern'),o('Military','Wayfarer')],[o('Campaign','Spear'),o('Guard','Vigil')])
  self.assertEqual(g.history[-1]['detail']['unclamped_tracks']['communities'],5)
  self.assertEqual(g.state['communities'],4)
 def test_each_development_responds_to_legal_orders_and_failure_cases(self):
  cards={c['id']:c for c in DEVELOPMENTS}
  cases=[
   ('R1-REPAIR',dict(l='Council',nav=[o('Repair','Lantern')]),True),
   ('R1-REPAIR',dict(l='Maintain'),False),
   ('R1-REPAIR',dict(l='Council',nav=[o('Repair','Lantern')],vetoes={'navigation':['Repair']}),False),
   ('R2-ESCORT',dict(nav=[o('Relief','Wayfarer')],sec=[o('Guard','Vigil')]),True),
   ('R2-ESCORT',dict(nav=[o('Relief','Wayfarer')],warrant=True),True),
   ('R2-ESCORT',dict(nav=[o('Relief','Wayfarer')],intervention='Tender cover'),False),
   ('R2-ESCORT',dict(sec=[o('Guard','Vigil')]),False),
   ('R2-TRUCE',dict(sec=[o('Campaign','Spear')]),False), # funded, no delivered transport
   ('R2-TRUCE',dict(s='Raid'),False), # no target but attempted
   ('R2-TRUCE',dict(s='Raid',vetoes={'military':['Raid']}),True),
   ('R2-TRUCE',dict(s='Stand down',sec=[o('Campaign','Spear')]),True), # unfunded
   ('R2-TRUCE',dict(sec=[o('Guard','Vigil')]),True)]
  for ident,args,wanted in cases:
   _,detail=resolve(State(),rnd=cards[ident]['round'],**args)
   self.assertEqual(development_effect(cards[ident],detail)['condition_met'],wanted,(ident,args))
 def test_opening_veto_and_pledge_apply_to_same_round(self):
  g=Session();pledge=dict(owner='Guild',asset='Wayfarer',assignment='Council',article='NI')
  open_round(g,'R1-REPAIR',nav={'A':'Repair'},articles={'navigation':'NI','military':'MA'},agree=True,pledges=[pledge])
  self.assertEqual(g.vetoes['navigation'],['Repair']);self.assertTrue(g.pledges)
  commit(g,w='Trade');self.assertEqual(g.assignments['Guild']['wayfarer'],'Council')
  council(g,[o('Repair','Lantern')])
  self.assertFalse(g.history[-1]['detail']['development_effect']['condition_met'])
  self.assertFalse(g.pledges);self.assertEqual(g.vetoes,{'navigation':[],'military':[]})
 def test_multiplayer_host_selects_card_and_conceals_exact_effects(self):
  m=Multiplayer();m.begin_host()
  for r in ROLES:m.receive(r,dict(type='hello',name=r,role=r));m.approve(r,r)
  self.assertEqual(m.required(),[])
  for r in ROLES:
   self.assertNotIn('development_options',m.view(r))
   self.assertNotIn('table',m.channels(r))
   with self.assertRaises(ValueError):m.validate_sheet(r,{'development':'R1-REPAIR'})
  m.advance(m.epoch,{'development':'R1-RELIEF'})
  self.assertIn('table',m.channels('GN'))
  self.assertEqual(m.view('GN')['development']['id'],'R1-RELIEF')
  self.assertNotIn('success',m.view('GN')['development'])
  m.advance(m.epoch);m.advance(m.epoch,allow_missing=True)
  m.advance(m.epoch,{'articles':{'navigation':'NG','military':'MA'}})
  m.advance(m.epoch,allow_missing=True)
  self.assertEqual(m.game.stage,'draft');self.assertNotIn('table',m.channels('GN'))
  m.advance(m.epoch,allow_missing=True);m.advance(m.epoch,allow_missing=True);m.advance(m.epoch,allow_missing=True)
  for r in ROLES:
   event=next(e for e in m.view(r)['history'] if e['event']=='Operational resolution')
   self.assertNotIn('detail',event);self.assertNotIn('effects',event)
  restored=BrowserHost(m.backup());self.assertEqual(restored.session.game.public(),m.game.public())
 def test_empty_v04_save_keeps_its_original_start(self):
  m=Multiplayer();m.game=V04Session()
  restored=BrowserHost(m.backup());self.assertEqual(restored.session.game.stage,'draft')
  self.assertNotEqual(restored.session.game.public()['ruleset'],RULESET)
 def test_visions_remain_optional_after_opening_negotiation(self):
  for selected in ('None','Navigation','Security'):
   g=Session();open_round(g,'R1-REPAIR')
   commit(g,selected)
   self.assertEqual(g.foresight,3 if selected=='None' else 2)
   council(g,[o('Relief','Lantern')],[o('Guard','Vigil')])
   self.assertTrue(g.state['lantern']) # protection still averts R1-N loss
