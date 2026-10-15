import sys,unittest
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from test_opening_rounds import open_round,commit,council,o
from void_throne.current_session import Session,from_actions
from void_throne.multiplayer import Multiplayer
from void_throne.session import ROLES

def setup():
 g=Session();open_round(g,'R1-RELIEF');g.apply({'stage':'draft','choice':'None'});return g
def placements():return {r:dict(wayfarer='Council',lantern='Maintain') if r.startswith('G') else dict(spear='Council',vigil='Council') for r in ROLES if r!='A'}
def proposal(asset,text='An unusual task'):return dict(order='Other',asset=asset,proposal=text)
def ruling(basis):return dict(basis=basis,reason='Use the same requirements and risks as the comparable task.')
class OtherOrderTests(unittest.TestCase):
 def test_pending_ruling_blocks_phase_atomically(self):
  g=setup();p=placements()
  for r in ['GN','GS']:p[r].update(wayfarer='Other',other={'wayfarer':'Deliver private contract cargo by an unusual route.'})
  before=g.public()
  with self.assertRaises(ValueError):g.apply(dict(stage='commit',assignments=p))
  self.assertEqual(before,g.public())
  g.apply(dict(stage='commit',assignments=p,rulings={'wayfarer':ruling('Trade')}))
  self.assertEqual(g.assignments['Guild']['wayfarer'],'Trade')
  self.assertEqual(from_actions(g.actions).public(),g.public())
 def test_teammates_must_agree_proposal_and_commitments_override(self):
  g=setup();p=placements()
  for r in ['GN','GS']:p[r].update(wayfarer='Other',other={'wayfarer':r+' wants something different'})
  g.apply(dict(stage='commit',assignments=p));self.assertEqual(g.assignments['Guild'],{'wayfarer':'Trade','lantern':'Maintain'})
  g=setup();g.pledges=[dict(owner='Guild',asset='Wayfarer',assignment='Council',article='NI')]
  for r in ['GN','GS']:p[r]['other']['wayfarer']='Keep the ship for ourselves'
  g.apply(dict(stage='commit',assignments=p));self.assertEqual(g.assignments['Guild']['wayfarer'],'Council')
 def test_equivalent_council_order_preserves_development_and_prophecy(self):
  a=setup();b=setup()
  for g in (a,b):g.apply(dict(stage='commit',assignments=placements()))
  council(a,[o('Relief','Wayfarer')],[o('Guard','Vigil')])
  b.apply(dict(stage='council',navigation={'GN':[proposal('Wayfarer','Deliver emergency medical stores')]},security={'JS':[o('Guard','Vigil')]},rulings={'navigation':ruling('Relief')}))
  self.assertEqual(a.state,b.state);self.assertTrue(b.history[-1]['detail']['development_effect']['condition_met'])
  self.assertEqual(from_actions(b.actions).public(),b.public())
 def test_other_cannot_duplicate_order_or_invent_traits(self):
  g=setup();g.apply(dict(stage='commit',assignments={r:dict(wayfarer='Council',lantern='Council') if r.startswith('G') else dict(spear='Council',vigil='Council') for r in ROLES if r!='A'}))
  for rows,basis in [([o('Relief','Wayfarer'),proposal('Lantern')],'Relief'),([proposal('Lantern')],'Military'),([o('Relief','Wayfarer'),proposal('Wayfarer')],'Other')]:
   before=g.public()
   with self.assertRaises(ValueError):g.apply(dict(stage='council',navigation={'GN':rows},rulings={'navigation':ruling(basis)}))
   self.assertEqual(g.public(),before)
 def test_attack_still_requires_transport_and_veto_still_blocks(self):
  for veto in [[],['Campaign'],['Other']]:
   g=setup();g.apply(dict(stage='commit',assignments=placements()));g.vetoes['military']=veto
   g.apply(dict(stage='council',security={'JS':[proposal('Spear','A show of force at the anchorage')]},rulings={'military':ruling('Campaign')}))
   d=g.history[-1]['detail'];self.assertFalse(d['combat']);self.assertEqual(d['offensive_attempt'],not bool(veto))
   if not veto:self.assertTrue(any('lacks delivered military passage' in x for x in d['events']))
 def test_faction_other_cannot_use_council_effects_or_evade_raid_veto(self):
  g=setup();p=placements()
  for r in ['JN','JS']:p[r].update(spear='Other',other={'spear':'Hunt a patrol independently'})
  with self.assertRaises(ValueError):g.apply(dict(stage='commit',assignments=p,rulings={'spear':ruling('Campaign')}))
  g.apply(dict(stage='commit',assignments=p,rulings={'spear':ruling('Raid')}));g.vetoes['military']=['Raid'];council(g)
  self.assertFalse(g.history[-1]['detail']['offensive_attempt'])
 def test_no_effect_occupies_asset_and_consumes_cutter_service(self):
  g=setup();p=placements()
  for r in ['GN','GS']:p[r].update(lantern='Other',other={'lantern':'Survey a distant wreck'})
  g.apply(dict(stage='commit',assignments=p,reserve='Other',reserve_proposal='Carry a diplomatic visitor',rulings={'lantern':ruling('Other'),'reserve':ruling('Other')}))
  council(g,[o('Repair','Lantern')]);self.assertEqual(g.state['beacon'],2);self.assertFalse(g.state['reserve'])
  self.assertEqual(g.history[-1]['detail']['used_assets']['Lantern'],'Other')
  self.assertTrue(g.history[-1]['detail']['rejected'])
 def test_multiplayer_peers_propose_only_facilitator_adjudicates(self):
  m=Multiplayer();m.game=setup()
  for r in ROLES:
   m.receive(r,dict(type='hello',name=r,role=r));m.approve(r,r)
  p=placements()
  for r in ['GN','GS']:p[r].update(wayfarer='Other',other={'wayfarer':'Private contract delivery'},rulings={'wayfarer':ruling('Trade')})
  for r in ROLES:m.receive(r,dict(type='sheet',id='commit-'+r,epoch=m.epoch,sheet=p.get(r,dict(reserve='Keep'))))
  self.assertNotIn('rulings',m.sheets['GN']);self.assertNotIn('GS',m.view('JN')['working_sheets'])
  with self.assertRaises(ValueError):m.advance(m.epoch)
  m.advance(m.epoch,{'rulings':{'wayfarer':ruling('Trade')}})
  for r in ROLES:m.receive(r,dict(type='sheet',id='council-'+r,epoch=m.epoch,sheet={'security':[proposal('Spear')]} if r=='JS' else {}))
  with self.assertRaises(ValueError):m.advance(m.epoch)
  m.advance(m.epoch,{'rulings':{'military':ruling('Campaign')}})
  self.assertEqual(m.game.stage,'opening');self.assertFalse(m.game.history[-1]['detail']['combat'])
if __name__=='__main__':unittest.main()

