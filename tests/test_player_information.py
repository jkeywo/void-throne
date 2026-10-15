"""The host resolves exact rules; players receive declared choices and observed events."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from void_throne.session import Session,ROLES
from void_throne.multiplayer import Multiplayer
from void_throne.operations import State,resolve
from void_throne.presentation import player_vision,track_descriptions,public_resolution,OUTCOMES

class PlayerInformationTests(unittest.TestCase):
    def test_all_public_tracks_describe_every_value(self):
        tracks=track_descriptions()
        for key in ['beacon','communities','readiness']:
            self.assertEqual(set(tracks[key]['values']),set('01234'))
            self.assertEqual(len({v['label'] for v in tracks[key]['values'].values()}),5)
            for value in tracks[key]['values'].values():self.assertGreater(len(value['description']),30)
        self.assertEqual(Session().public()['track_descriptions'],tracks)

    def test_each_purchased_handout_has_no_operational_arithmetic(self):
        for path in (ROOT/'design/private-cards').glob('*.json'):
            private=json.loads(path.read_text(encoding='utf8'));public=player_vision(private)
            self.assertEqual(public['id'],private['id']);self.assertEqual(len(public['branches']),len(private['branches']))
            self.assertNotIn('public_rules',public)
            text=json.dumps(public,ensure_ascii=False)
            self.assertNotRegex(text,r'[+−]\s*\d|Readiness [0-9]|Beacon [0-9]|Stability [0-9]|prepared Beacon')
            for branch in private['branches']:self.assertNotIn(branch['consequence'],text)
        with self.assertRaises(ValueError):player_vision({'id':'unregistered','private_answer':'secret'})

    def test_players_get_qualitative_vision_and_result_even_when_disclosed(self):
        for disclose in [False,True]:
            m=Multiplayer();g=m.game
            g.apply({'stage':'draft','choice':'Navigation'})
            rows={r:({'wayfarer':'Council','lantern':'Council'} if r.startswith('G') else {'spear':'Council','vigil':'Council'}) for r in ROLES if r!='A'}
            g.apply({'stage':'commit','assignments':rows,'reserve':'Keep','disclose':disclose})
            g.apply({'stage':'council','navigation':{'A':'Shared'},'security':{'A':'Campaign'},'warrant':True})
            host=m.envelope()['host']['game'];host_result=next(e for e in host['history'] if e['event']=='Operational resolution')
            self.assertIn('effects',host_result);self.assertIn('prepared',host_result['detail'])
            for role in ROLES:
                v=m.view(role);p=next(e for e in v['history'] if e['event']=='Operational resolution')
                self.assertEqual(p['after'],host_result['after'])
                self.assertTrue(p['outcomes'])
                for key in ['effects','inputs','detail','prepared']:self.assertNotIn(key,p)
                encoded=json.dumps(v,ensure_ascii=False)
                self.assertNotIn('Maintain +1',encoded);self.assertNotIn('Monthly consumption: Stability -1',encoded)
                self.assertNotIn(g.vision['public_rules'],encoded)
                if role=='A' or disclose:
                    self.assertEqual(v['selected_vision'],player_vision(g.vision))
                    purchase=next(e for e in v['history'] if e['event']=='Foresight purchase')
                    self.assertEqual(purchase['private_answer'],player_vision(g.vision))
                else:self.assertIsNone(v['selected_vision'])

    def test_player_projection_never_copies_unknown_calculation_fields(self):
        e={'event':'Operational resolution','before':{},'after':{},'detail':{'events':['Unknown hidden arithmetic: Stability -99']},'secret_threshold':123,'effects':['secret']}
        p=public_resolution(e)
        self.assertNotIn('secret_threshold',p);self.assertNotIn('effects',p);self.assertEqual(p['outcomes'],[])

    def test_public_documents_have_purposes_not_numeric_operation_effects(self):
        docs=json.loads((ROOT/'docs/drive-publication-blocks.json').read_text(encoding='utf8'))
        for key in ['rulebook','briefs','components']:
            text='\n'.join(t for _,t in docs[key]['blocks'])
            self.assertNotRegex(text,r'(?:Stability|Beacon|Readiness) [＋+−-]\d|prepared Beacon [23]|opening Readiness (?:at least|below) \d')
        c='\n'.join(t for _,t in docs['components']['blocks'])
        for track in track_descriptions().values():
            for level,v in track['values'].items():self.assertIn(level+' — '+v['label']+':',c)
        f='\n'.join(t for _,t in docs['facilitator']['blocks'])
        self.assertIn('Prepared Beacon equals opening Beacon, plus 1',f)
        self.assertIn('Final Stability equals opening Stability plus the complete change ledger.',f)
        self.assertIn('At prepared Beacon 2 without protection, disable Wayfarer',f)

    def test_facilitator_worked_example_matches_model(self):
        st,detail=resolve(State(),rnd=1,w='Council',l='Council',s='Council',v='Council',nav='Shared',sec='Campaign',warrant=True,intervention='Keep')
        self.assertEqual((st.beacon,st.communities,st.readiness),(1,3,4))
        self.assertTrue(st.wayfarer and st.lantern and st.spear and st.reserve)
        self.assertEqual(st.contracts,0)
        for event in detail['events']:self.assertTrue(any(event.startswith(prefix) for prefix in OUTCOMES),event)

if __name__=='__main__':unittest.main()
