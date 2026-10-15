import json,sys,unittest
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from void_throne.orders_v04 import resolve,orders,veto_rights
from void_throne.operations import State
from void_throne.session_v04 import Session,RULESET
from void_throne.current_session import from_actions
from void_throne.session import ROLES
from void_throne.multiplayer import Multiplayer
from void_throne.browser_host import BrowserHost
from void_throne.presentation import player_vision

def o(order,asset):return {'order':order,'asset':asset}
def commit(g,reserve='Keep',guild=None,army=None):
 rows={r:(guild or {'wayfarer':'Council','lantern':'Council'}).copy() if r.startswith('G') else (army or {'spear':'Council','vigil':'Council'}).copy() for r in ROLES if r!='A'}
 g.apply(dict(stage='commit',assignments=rows,reserve=reserve))
def council(g,nav=None,sec=None,warrant=False):g.apply(dict(stage='council',navigation={'GN':nav or []},security={'JS':sec or []},warrant=warrant))

class OrdersV04Tests(unittest.TestCase):
 def test_current_settlement_weights_follow_written_rulebook(self):
  g=Session();self.assertEqual(g.weights()['weights'],{'Guild':3,'Janissariat':3,'Ascendant':6})
  self.assertEqual(g.weights()['threshold'],8)
  for beacon in range(5):
   g.state['beacon']=beacon;self.assertEqual(g.weights()['weights']['Guild'],2+beacon//2)
  g.state.update(wayfarer=False,lantern=False,beacon=0);self.assertEqual(g.weights()['weights']['Guild'],0)
 def test_separate_transports_and_guard_plus_campaign(self):
  st,d=resolve(State(),l='Council',nav=[o('Relief','Lantern'),o('Military','Wayfarer')],sec=[o('Campaign','Spear'),o('Guard','Vigil')])
  self.assertEqual((st.beacon,st.communities,st.readiness),(1,4,4));self.assertTrue(st.lantern)
  self.assertEqual(d['transport_wear'],1);self.assertEqual(len(d['used_assets']),4)
  self.assertEqual(st.contracts,0)
 def test_each_asset_and_order_once_and_lantern_civilians_only(self):
  for rows in [[o('Relief','Wayfarer'),o('Military','Wayfarer')],[o('Relief','Lantern'),o('Repair','Lantern')],[o('Relief','Wayfarer'),o('Relief','Lantern')],[o('Military','Lantern')]]:
   with self.assertRaises(ValueError):orders(rows,'navigation')
  with self.assertRaises(ValueError):orders([o('Campaign','Spear'),o('Raid','Spear')],'military')
 def test_grey_petrel_can_supply_either_transport_once(self):
  for task in ['Relief','Military']:
   st,d=resolve(State(),w='Trade',nav=[o(task,'Grey Petrel')],intervention='Council')
   self.assertFalse(st.reserve);self.assertIn(task,d['delivered_orders']);self.assertEqual(st.contracts,1)
  st,d=resolve(State(),nav=[],intervention='Council');self.assertTrue(st.reserve)
  for assignment in ['Keep','Tender cover']:
   st,d=resolve(State(),nav=[o('Military','Grey Petrel')],intervention=assignment)
   self.assertTrue(st.reserve);self.assertNotIn('Military',d['orders'])
 def test_all_three_navigation_orders_require_a_real_sacrifice(self):
  st,d=resolve(State(),l='Council',nav=[o('Relief','Grey Petrel'),o('Military','Wayfarer'),o('Repair','Lantern')],sec=[o('Campaign','Spear'),o('Guard','Vigil')],intervention='Council')
  self.assertEqual((st.beacon,st.communities,st.readiness),(3,4,4));self.assertFalse(st.reserve);self.assertEqual(st.contracts,0)
 def test_transport_scheduling_wear_once_even_when_halted(self):
  for nav in [[o('Relief','Lantern')],[o('Military','Wayfarer')],[o('Relief','Lantern'),o('Military','Wayfarer')]]:
   st,d=resolve(State(beacon=1),l='Council',nav=nav)
   self.assertEqual(d['transport_wear'],1);self.assertEqual(st.beacon,0);self.assertEqual(d['delivered_orders'],[])
  st,d=resolve(State(),l='Council',nav=[o('Relief','Lantern')],vetoes={'navigation':['Relief']})
  self.assertEqual(d['transport_wear'],0);self.assertEqual(st.beacon,2)
 def test_commercial_wear_remains_separate(self):
  st,d=resolve(State(beacon=3),w='Trade',l='Council',nav=[o('Relief','Lantern')],sec=[o('Guard','Vigil')])
  self.assertEqual(st.beacon,1);self.assertEqual((d['transport_wear'],d['trade_wear']),(1,1))
 def test_unfunded_orders_do_not_materialise_or_block_other_orders(self):
  st,d=resolve(State(),w='Trade',l='Council',s='Stand down',nav=[o('Military','Wayfarer'),o('Repair','Lantern')],sec=[o('Campaign','Spear'),o('Guard','Vigil')])
  self.assertEqual(set(d['orders']),{'Repair','Guard'});self.assertEqual(len(d['rejected']),2)
 def test_veto_blocks_faction_raid_and_warrant_equivalents(self):
  st,d=resolve(State(),s='Raid',warrant=True,sec=[o('Guard','Vigil')],vetoes={'military':['Raid','Guard']})
  self.assertFalse(d['combat']);self.assertFalse(d['guarded']);self.assertFalse(d['jan_breach']);self.assertEqual(st.readiness,2)
 def test_warrant_does_not_use_vigil_twice(self):
  st,d=resolve(State(),warrant=True,sec=[o('Guard','Vigil')]);self.assertEqual(st.communities,3)
  self.assertEqual(d['used_assets']['Vigil'],'Imperial Warrant');self.assertEqual(len(d['rejected']),1)
 def test_lantern_prophecy_can_be_averted_after_same_assignments(self):
  base=dict(l='Council',nav=[o('Relief','Lantern')])
  st,d=resolve(State(),**base);self.assertFalse(st.lantern)
  for changes in [dict(sec=[o('Guard','Vigil')]),dict(warrant=True),dict(intervention='Tender cover')]:
   st,d=resolve(State(),**base,**changes);self.assertTrue(st.lantern)
  st,d=resolve(State(),l='Council',nav=[o('Relief','Wayfarer')]);self.assertTrue(st.lantern)
 def test_round_two_supply_conditions_can_now_both_trigger(self):
  st,d=resolve(State(),rnd=2,w='Trade',l='Council',nav=[o('Repair','Lantern'),o('Military','Grey Petrel')],intervention='Council')
  self.assertTrue(d['trade']);self.assertIn('Military',d['delivered_orders'])
  self.assertTrue(any(x.startswith('Repair and') for x in d['events']));self.assertTrue(any(x.startswith('Unprotected') for x in d['events']))
 def test_round_two_patrol_follows_any_relief_vessel(self):
  for asset in ['Wayfarer','Lantern','Grey Petrel']:
   st,d=resolve(State(),rnd=2,l='Council',nav=[o('Relief',asset)],s='Raid',intervention='Council')
   self.assertTrue(d['combat'],asset)
 def test_joint_veto_rights_are_per_contributing_party_in_both_domains(self):
  articles={'navigation':'NJ','military':'MJ'}
  assignments={'Guild':{'wayfarer':'Council','lantern':'Council'},'Janissariat':{'spear':'Council','vigil':'Home'}}
  self.assertEqual(veto_rights(articles,assignments,'Council'),{'navigation':['GN','JN','A'],'military':['GS','JS','A']})
  assignments['Guild']={'wayfarer':'Trade','lantern':'Maintain'}
  self.assertEqual(veto_rights(articles,assignments,'Tender cover'),{'navigation':['JN'],'military':['JS']})
 def test_joint_contributors_can_each_block_different_orders(self):
  g=Session();g.stage='veto';g.articles={'navigation':'NJ','military':'MJ'}
  g.assignments={'Guild':{'wayfarer':'Council'},'Janissariat':{'vigil':'Council'}};g.reserve='Council'
  g.apply(dict(stage='veto',navigation={'GN':'Relief','JN':'Military','A':'Repair'},military={'GS':'Campaign','JS':'Raid','A':'Guard'}))
  self.assertEqual(set(g.vetoes['navigation']),{'Relief','Military','Repair'})
  st,d=resolve(State(),l='Council',nav=[o('Relief','Lantern'),o('Military','Wayfarer')],sec=[o('Campaign','Spear'),o('Guard','Vigil')],vetoes=g.vetoes)
  self.assertEqual(d['orders'],{})
 def test_pending_joint_vetoes_are_private_until_the_bell(self):
  m=Multiplayer();m.game=Session();g=m.game;g.stage='veto';g.articles={'navigation':'NJ','military':'MJ'}
  g.assignments={'Guild':{'wayfarer':'Council'},'Janissariat':{'spear':'Council'}};g.reserve='Council'
  for r in ROLES:m.sheets[r]=m.validate_sheet(r,{'navigation':'Repair','military':'Raid','note':r+' private veto'})
  for r in ROLES:self.assertEqual(set(m.view(r)['working_sheets']),{r})
  m.advance(m.epoch)
  event=next(e for e in g.history if e['event']=='Next-round vetoes')
  self.assertEqual(event['choices']['navigation'],{'GN':'Repair','JN':'Repair','A':'Repair'})
  self.assertEqual(g.vetoes,{'navigation':['Repair'],'military':['Raid']})
 def test_noncontributors_cannot_set_joint_veto_and_duplicate_is_one(self):
  g=Session();g.stage='veto';g.articles={'navigation':'NJ','military':'MJ'}
  g.assignments={'Guild':{'wayfarer':'Council'},'Janissariat':{'spear':'Council'}}
  with self.assertRaises(ValueError):g.apply(dict(stage='veto',navigation={'A':'Repair'}))
  g.apply(dict(stage='veto',navigation={'GN':'Repair','JN':'Repair'},military={}))
  self.assertEqual(g.vetoes['navigation'],['Repair']);self.assertEqual(g.vetoes['military'],[])
 def test_complete_new_game_restore_veto_survives_article_change(self):
  g=Session();g.apply(dict(stage='draft',choice='Navigation'));commit(g)
  council(g,[o('Relief','Lantern'),o('Military','Wayfarer')],[o('Campaign','Spear'),o('Guard','Vigil')])
  self.assertEqual(g.stage,'veto');g.apply(dict(stage='veto',navigation={'A':'Repair'},military={'A':'Raid'}))
  g.apply(dict(stage='trial-proposal',articles={'navigation':'NJ','military':'MJ'},pledges=[],plan='Try joint government'))
  g.apply(dict(stage='trial-vote',votes={r:dict(navigation=True,military=True) for r in ROLES}))
  self.assertEqual(g.vetoes['navigation'],['Repair']);self.assertEqual(g.articles['navigation'],'NJ')
  g.apply(dict(stage='draft',choice='None'));commit(g,guild={'wayfarer':'Council','lantern':'Maintain'})
  council(g,[o('Relief','Wayfarer')],[o('Guard','Vigil')])
  g.apply(dict(stage='free'));g.apply(dict(stage='ceremony-proposal',package={'navigation':'NJ','military':'MJ'}))
  g.apply(dict(stage='ceremony-vote',approvals={r:True for r in ROLES}))
  self.assertTrue(g.settlement['ratified']);self.assertEqual(g.foresight,2)
  restored=from_actions(g.actions);self.assertEqual(restored.public(),g.public())
 def test_current_browser_validation_and_private_projections(self):
  m=Multiplayer();m.game=Session();g=m.game;g.apply(dict(stage='draft',choice='Navigation'));commit(g,'Council')
  self.assertEqual(m.validate_sheet('GN',{'navigation':[o('Relief','Lantern'),o('Military','Grey Petrel')]})['navigation'][1]['asset'],'Grey Petrel')
  self.assertNotIn('navigation',m.validate_sheet('A',{'navigation':[o('Military','Grey Petrel')]}))
  before=g.public()
  with self.assertRaises(ValueError):council(g,[o('Relief','Wayfarer'),o('Military','Wayfarer')])
  self.assertEqual(g.public(),before)
  council(g,[o('Relief','Lantern')],[o('Guard','Vigil')])
  for r in ROLES:
   public=m.view(r);event=next(e for e in public['history'] if e['event']=='Operational resolution')
   self.assertNotIn('effects',event);self.assertNotIn('detail',event)
  self.assertEqual(m.required(),['A'])
  h=BrowserHost(m.backup());self.assertEqual(h.session.game.public(),g.public())
 def test_new_vision_handouts_use_correct_assets_and_hide_arithmetic(self):
  for path in (ROOT/'design/v04/private-cards').glob('*.json'):
   card=json.loads(path.read_text(encoding='utf8'));handout=player_vision(card);text=json.dumps(handout,ensure_ascii=False)
   self.assertNotIn('Shared',text);self.assertNotRegex(text,r'(Beacon|Stability|Readiness) [0-9+−]')
   self.assertEqual(card['ruleset'],RULESET)
  g=Session();g.apply(dict(stage='draft',choice='Navigation'))
  self.assertIn('Lantern',g.vision['branches'][0]['condition']);self.assertEqual(g.foresight,2)

if __name__=='__main__':unittest.main()
