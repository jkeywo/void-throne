"""Information boundaries and remaining decisions under prophecy-first timing."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from void_throne.session import Session,ROLES
from void_throne.multiplayer import Multiplayer
from void_throne.operations import State,resolve

class FactionForesightTests(unittest.TestCase):
    def table(self):
        m=Multiplayer();m.begin_host()
        for r in ROLES:
            m.receive(r,dict(type='hello',name=r,role=r));m.approve(r,r)
        return m
    def choose(self,m,choice):
        m.receive('A',dict(type='sheet',id='first',epoch=m.epoch,sheet={'choice':choice}))
        m.advance(m.epoch)

    def test_choice_precedes_visits_and_needs_no_faction_plans(self):
        m=self.table()
        self.assertEqual(m.required(),['A'])
        m.add_chat('GN','guild','Our private opening plan')
        self.assertNotIn('Our private opening plan',json.dumps(m.view('A')))
        for r,c in [('A','visit-guild'),('GN','visit-guild'),('JN','table'),('GN','navigation')]:
            with self.assertRaises(ValueError):m.add_chat(r,c,'Too soon')
        self.choose(m,'None')
        self.assertEqual(m.game.foresight,3);self.assertEqual(m.game.stage,'commit')
        self.assertEqual(m.game.drafts,{})
        m.add_chat('A','visit-guild','Guild proposal')
        m.add_chat('GS','visit-guild','Guild answer')
        m.add_chat('A','visit-army','Army proposal')
        self.assertIn('Guild proposal',json.dumps(m.view('GN')))
        self.assertNotIn('Guild proposal',json.dumps(m.view('JN')))
        self.assertNotIn('Army proposal',json.dumps(m.view('GN')))
        self.assertNotIn('Our private opening plan',json.dumps(m.view('A')))
        with self.assertRaises(ValueError):m.add_chat('GN','table','Cross-faction offer')
        with self.assertRaises(ValueError):m.add_chat('JN','visit-guild','Visit other faction')
        m.advance(m.epoch,allow_missing=True)
        m.add_chat('GN','table','Council phase is open')
        with self.assertRaises(ValueError):m.add_chat('A','visit-guild','Faction phase is over')

    def test_paid_answer_is_private_and_choice_cannot_be_revised(self):
        m=self.table();self.choose(m,'Navigation')
        self.assertEqual(m.game.foresight,2)
        answer=m.game.vision['branches'][0]['consequence']
        self.assertIn(answer,json.dumps(m.view('A'),ensure_ascii=False))
        self.assertNotIn(answer,json.dumps(m.view('GN'),ensure_ascii=False))
        m.add_chat('A','visit-guild',answer)
        self.assertIn(answer,json.dumps(m.view('GS'),ensure_ascii=False))
        self.assertNotIn(answer,json.dumps(m.view('JS'),ensure_ascii=False))
        before=m.game.foresight
        with self.assertRaises(ValueError):m.game.apply({'stage':'draft','choice':'Security'})
        self.assertEqual(m.game.foresight,before)

    def test_legacy_drafts_do_not_brief_ascendant_or_other_faction(self):
        m=self.table()
        proposals={'GN':{'wayfarer':'Trade','lantern':'Maintain'},'GS':{'wayfarer':'Council','lantern':'Council'},'JN':{'spear':'Raid','vigil':'Home'},'JS':{'spear':'Council','vigil':'Council'},'A':{}}
        m.game.apply({'stage':'draft','proposals':proposals,'notes':{'GN':'Guild secret'}})
        for r in ['A','JN','JS']:
            self.assertNotIn('Guild secret',json.dumps(m.view(r)))
            self.assertNotIn('GN',m.view(r)['drafts'])
        self.assertIn('Guild secret',json.dumps(m.view('GS')))

    def test_covers_reveal_councils_but_not_specific_prophecies(self):
        for p in (ROOT/'design/public-covers').glob('*.json'):
            c=json.loads(p.read_text(encoding='utf8'))
            answer=json.loads((ROOT/'design/private-cards'/p.name).read_text(encoding='utf8'))
            self.assertIn(c['primary_council'],['Navigation and Supply','Security and Government'])
            self.assertEqual(set(c['affected_councils']),{'Navigation and Supply','Security and Government'})
            self.assertNotIn(answer['title'],json.dumps(c,ensure_ascii=False))
            for token in ['Shared','Trade','Raid','Military','Repair','Lantern','Spear','Relief','Guard']:
                self.assertNotIn(token,json.dumps(c))

    def test_each_prophecy_has_a_later_council_choice_with_same_assets(self):
        # These pairs hold faction assignments fixed: they remain alternatives even
        # after an asset is locked to Council by a Standing Commitment.
        st=State()
        a,da=resolve(st,rnd=1,w='Council',l='Council',s='Council',v='Council',nav='Shared',sec='Restraint')
        b,db=resolve(st,rnd=1,w='Council',l='Council',s='Council',v='Council',nav='Shared',sec='Guard')
        self.assertFalse(a.lantern);self.assertTrue(b.lantern) # R1-N
        a,da=resolve(st,rnd=1,w='Trade',l='Maintain',s='Council',v='Home',nav='Hold',sec='Raid')
        b,db=resolve(st,rnd=1,w='Trade',l='Maintain',s='Council',v='Home',nav='Hold',sec='Restraint')
        self.assertTrue(da['combat']);self.assertFalse(db['combat']);self.assertNotEqual(a.readiness,b.readiness) # R1-S
        a,da=resolve(State(beacon=3),rnd=2,w='Trade',l='Council',s='Stand down',v='Home',nav='Repair',sec='Restraint')
        b,db=resolve(State(beacon=3),rnd=2,w='Trade',l='Council',s='Stand down',v='Home',nav='Hold',sec='Restraint')
        self.assertTrue(da['trade'] and db['trade']);self.assertEqual(a.communities,b.communities+1) # R2-N distribution
        a,da=resolve(st,rnd=2,w='Council',l='Maintain',s='Stand down',v='Council',nav='Military',sec='Restraint')
        b,db=resolve(st,rnd=2,w='Council',l='Maintain',s='Stand down',v='Council',nav='Military',sec='Guard')
        self.assertIn('Unprotected military-only loading: Stability -1',da['events'])
        self.assertNotIn('Unprotected military-only loading: Stability -1',db['events']) # R2-N loss
        a,da=resolve(st,rnd=2,w='Council',l='Maintain',s='Council',v='Home',nav='Relief',sec='Raid')
        b,db=resolve(st,rnd=2,w='Council',l='Maintain',s='Council',v='Home',nav='Military',sec='Raid')
        self.assertTrue(da['combat']);self.assertFalse(db['combat']) # R2-S

    def test_first_choice_and_later_assignments_preserve_optional_spending(self):
        for selection in ['None','Navigation','Security']:
            g=Session();g.apply({'stage':'draft','choice':selection})
            self.assertEqual(g.stage,'commit');self.assertEqual(g.foresight,3 if selection=='None' else 2)
            self.assertEqual(g.drafts,{})
            rows={r:({'wayfarer':'Council','lantern':'Council'} if r.startswith('G') else {'spear':'Council','vigil':'Council'}) for r in ROLES if r!='A'}
            g.apply({'stage':'commit','assignments':rows,'reserve':'Tender cover'})
            self.assertEqual(g.assignments['Guild']['lantern'],'Council')
            self.assertEqual(g.reserve,'Tender cover');self.assertEqual(g.stage,'council')

if __name__=='__main__':unittest.main()
