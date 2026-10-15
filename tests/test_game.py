import unittest,json,sys
from pathlib import Path
from copy import deepcopy
from dataclasses import replace,asdict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from void_throne.session import Session
from void_throne.operations import State,resolve
from void_throne.settlement import leverage,ballot
from void_throne.charter import evaluate
SCRIPT=json.loads((ROOT/'design/experiments/replay-config.json').read_text(encoding='utf-8'))['plugin_config']['actions']

class GameTests(unittest.TestCase):
    def replay(self,actions=None):
        g=Session()
        for p in actions or SCRIPT:g.apply(p)
        return g
    def test_recorded_agent_ending(self):
        g=self.replay();expected=json.loads((ROOT/'tests/fixtures/expected-ending.json').read_text())
        self.assertEqual(g.state,expected['physical']);self.assertEqual(g.foresight,1)
        for k,v in expected['settlement'].items():self.assertEqual(g.settlement[k],v)
    def test_spoken_decisions_need_no_incoming_orders_or_signatures(self):
        actions=deepcopy(SCRIPT)
        for action in actions:
            if action['stage']=='draft':
                for row in action['proposals'].values():
                    for key in ('navigation','security','warrant'):row.pop(key,None)
            if action['stage']=='commit':action.pop('signatures')
        game=self.replay(actions)
        self.assertEqual(game.state,self.replay().state)
        self.assertTrue(game.settlement['ratified'])
        for event in game.history:
            if event['event']=='Final faction sheets':self.assertNotIn('signatures',event)

    def test_unconfirmed_or_conflicting_assignments_still_default(self):
        for missing in (True,False):
            game=Session()
            for action in SCRIPT[:2]:game.apply(action)
            action=deepcopy(SCRIPT[2]);action.pop('signatures')
            if missing:action['assignments'].pop('JN')
            else:action['assignments']['JN']['spear']='Stand down'
            game.apply(action)
            self.assertEqual(game.assignments['Janissariat'],{'spear':'Stand down','vigil':'Home'})

    def test_none_preserves_leverage_without_changing_fixed_effects(self):
        actions=deepcopy(SCRIPT)
        for p in actions:
            if p['stage']=='vision':p['choice']='None'
        g=self.replay(actions)
        self.assertEqual(g.foresight,3);self.assertEqual(g.state,self.replay().state)
        self.assertEqual(g.settlement['weights']['Ascendant'],6)
    def test_no_second_purchase_or_out_of_phase_mutation(self):
        g=Session();g.apply(SCRIPT[0]);g.apply(SCRIPT[1]);before=g.public()
        with self.assertRaises(ValueError):g.apply(SCRIPT[1])
        self.assertEqual(g.public(),before)
    def test_purchased_card_only(self):
        g=Session();g.apply(SCRIPT[0]);self.assertIsNone(g.public()['selected_vision'])
        g.apply(SCRIPT[1]);self.assertEqual(g.public()['selected_vision']['id'],'R1-S')
        self.assertNotIn('Exposed transfer berth',json.dumps(g.public()))
    def test_legacy_unsigned_owners_default(self):
        g=Session();g.apply(SCRIPT[0]);g.apply(SCRIPT[1]);p=deepcopy(SCRIPT[2]);p['signatures']['JN']=False;g.apply(p)
        self.assertEqual(g.assignments['Janissariat'],{'spear':'Stand down','vigil':'Home'})
    def test_legacy_pledge_survives_unsigned_later_sheet(self):
        g=Session()
        for p in SCRIPT[:8]:g.apply(p)
        p=deepcopy(SCRIPT[8]);p['signatures']['GN']=False;p['assignments']['GN']['lantern']='Maintain';g.apply(p)
        self.assertEqual(g.assignments['Guild'],{'wayfarer':'Trade','lantern':'Council'})
    def test_failed_ratification_restores_interim_not_assets(self):
        actions=deepcopy(SCRIPT);actions[-1]['approvals']={r:False for r in ('GN','GS','JN','JS','A')}
        g=self.replay(actions);st=deepcopy(g.state)
        g.apply(actions[-2]);g.apply(actions[-1])
        self.assertFalse(g.settlement['ratified']);self.assertEqual(g.articles,{'navigation':'I','military':'I'});self.assertEqual(g.state,st)
    def test_divided_faction_has_no_signature(self):
        st=asdict(State());votes=dict(GN=True,GS=False,JN=False,JS=False,A=True)
        tally=ballot(st,1,votes,dict(navigation='NG',military='MJ'))
        self.assertFalse(tally['party_signatures']['Guild']);self.assertFalse(tally['ratified'])
    def test_withheld_assets_do_not_materialise(self):
        st,d=resolve(State(),w='Trade',l='Maintain',s='Stand down',v='Home',nav='Shared',sec='Campaign',warrant=True)
        self.assertEqual(d['nav'],'Hold');self.assertFalse(d['combat']);self.assertEqual(st.contracts,1)
    def test_vigil_cannot_pay_twice(self):
        st,d=resolve(State(),sec='Guard',warrant=True)
        self.assertEqual(d['sec'],'Restraint');self.assertIn('Unfunded Guard: Restraint; Stability -1',d['events'])
    def test_averted_vision_and_untriggered_reserve(self):
        lost,_=resolve(State(),l='Council',nav='Shared',sec='Campaign')
        safe,_=resolve(State(),l='Council',nav='Shared',sec='Campaign',intervention='Tender cover')
        self.assertFalse(lost.lantern);self.assertTrue(safe.lantern);self.assertFalse(safe.reserve)
        unused,_=resolve(State(),intervention='Tender cover',sec='Guard');self.assertTrue(unused.reserve)
    def test_raid_branches_and_civilian_cost(self):
        yes,d=resolve(State(),w='Trade',l='Maintain',s='Raid',v='Home',nav='Hold',sec='Restraint')
        no,e=resolve(State(),w='Council',l='Maintain',s='Raid',v='Home',nav='Relief',sec='Restraint')
        self.assertTrue(d['combat']);self.assertEqual(yes.communities,0);self.assertFalse(e['combat']);self.assertEqual(no.readiness,2)
    def test_readiness_affects_both_parties(self):
        a=leverage(asdict(State(readiness=4)),1)['weights'];b=leverage(asdict(State(readiness=3)),1)['weights']
        self.assertEqual(a['Ascendant']-b['Ascendant'],1);self.assertEqual(a['Janissariat']-b['Janissariat'],1)
    def test_trial_owner_refusal_blocks_only_attached_domain(self):
        g=Session()
        for p in SCRIPT[:5]:g.apply(p)
        p=deepcopy(SCRIPT[5]);p['votes']['GS']['Guild']=False;g.apply(p)
        self.assertEqual(g.articles,{'navigation':'I','military':'I'});self.assertFalse(g.pledges)
    def test_joint_conflict_defaults_without_invalidity_penalty(self):
        g=Session()
        for p in SCRIPT[:3]:g.apply(p)
        g.articles={'navigation':'NJ','military':'MJ'}
        p=deepcopy(SCRIPT[3]);p['navigation']={'GN':'Relief','JN':'Military'};p['security']={'GS':'Guard','JS':'Raid'};p['warrant']=False
        g.apply(p);rec=next(e for e in g.history if e['event']=='Council order sheets')
        self.assertEqual(rec['effective'],{'navigation':'Hold','security':'Restraint'});self.assertFalse(any(rec['valid'].values()))

if __name__=='__main__':unittest.main()
