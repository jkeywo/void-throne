import unittest,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from void_throne.multiplayer import Multiplayer
from void_throne.session import ROLES
SCRIPT=json.loads((ROOT/'design/experiments/replay-config.json').read_text(encoding='utf8'))['plugin_config']['actions']

def row_for(action,r):
    stage=action['stage'];row={'note':action.get('notes',{}).get(r,'')}
    if stage=='draft':row.update(action['proposals'][r])
    elif stage=='vision':row['choice']=action['choice']
    elif stage=='commit':
        if r=='A':row.update(reserve=action['reserve'],disclose=action['disclose'])
        else:row.update(action['assignments'][r]);row['sign']=action['signatures'][r]
    elif stage=='council':
        for k in ('navigation','security'):
            if r in action[k]:row[k]=action[k][r]
        if r=='A':row['warrant']=action['warrant']
    elif stage=='trial-vote':
        row.update(action['votes'][r]);row['pledge']=row.get('Guild' if r.startswith('G') else 'Janissariat',False)
    elif stage=='ceremony-vote':row['approve']=action['approvals'][r]
    return row

class MultiplayerTests(unittest.TestCase):
    def setUp(self):
        self.m=Multiplayer();self.m.begin_host();self.tokens={}
        for r in ROLES:
            self.m.receive(r,dict(type='hello',name=r,role=r))
            response=self.m.approve(r,r);self.tokens[r]=response['direct'][r]['token']
    def send(self,r,row):return self.m.receive(r,dict(type='sheet',id=str(self.m.revision),epoch=self.m.epoch,sheet=row))
    def step(self,a):
        # The preserved script contains pre-choice drafts; current play omits that step.
        if a['stage']=='draft':return
        for r in self.m.required():self.send(r,row_for(a,r))
        self.m.advance(self.m.epoch,a)
    def test_five_independent_sheets_reproduce_physical_ending(self):
        for a in SCRIPT:self.step(a)
        expected=json.loads((ROOT/'tests/fixtures/expected-ending.json').read_text())
        self.assertEqual(self.m.game.state,expected['physical']);self.assertEqual(self.m.game.foresight,1)
        self.assertTrue(self.m.game.settlement['ratified'])
        self.assertNotIn('token',json.dumps(self.m.export()['seats']))
        self.assertIn('Human-seat multiplayer record',self.m.report().decode())
    def test_current_players_submit_without_requests_or_signature_fields(self):
        for action in SCRIPT:
            if action['stage']=='draft':continue
            for role in self.m.required():
                row=row_for(action,role)
                if action['stage']=='draft':
                    for key in ('navigation','security','warrant'):row.pop(key,None)
                row.pop('sign',None)
                self.send(role,row)
                self.assertNotIn('sign',self.m.sheets[role])
            self.m.advance(self.m.epoch,action)
        self.assertTrue(self.m.game.settlement['ratified'])
        for action in self.m.game.actions:
            if action['stage']=='commit':self.assertNotIn('signatures',action)

    def test_private_vision_and_choice_never_sent_to_other_seats(self):
        self.step(SCRIPT[0]);self.step(SCRIPT[1]);answer=self.m.game.vision['branches'][0]['consequence']
        self.assertIn(answer,json.dumps(self.m.view('A'),ensure_ascii=False))
        for r in ('GN','GS','JN','JS'):
            v=self.m.view(r);self.assertIsNone(v['selected_vision']);self.assertNotIn(answer,json.dumps(v,ensure_ascii=False))
            purchase=next(e for e in v['history'] if e['event']=='Foresight purchase')
            self.assertNotIn('choice',purchase);self.assertNotIn('notes',purchase);self.assertNotIn('actions',v)
    def test_disclosure_occurs_only_after_commit_bell(self):
        self.step(SCRIPT[0]);self.step(SCRIPT[1]);a=json.loads(json.dumps(SCRIPT[2]));a['disclose']=True
        self.send('A',row_for(a,'A'));self.assertIsNone(self.m.view('GN')['selected_vision'])
        self.step(a);self.assertIsNotNone(self.m.view('GN')['selected_vision'])
    def test_cannot_submit_for_another_role_or_use_their_channel(self):
        self.step(SCRIPT[1])
        row=row_for(SCRIPT[2],'GN');row['role']='A';row['choice']='Security';self.send('GN',row)
        self.assertEqual(set(self.m.sheets),{'GN'});self.assertNotIn('choice',self.m.sheets['GN'])
        with self.assertRaises(ValueError):self.m.receive('GN',dict(type='chat',id='bad',channel='army',text='spy'))
        self.m.add_chat('JN','army','Army only');self.assertNotIn('Army only',json.dumps(self.m.view('GN')))
    def test_phase_gate_rejects_stale_and_requires_explicit_defaults(self):
        old=self.m.epoch
        with self.assertRaises(ValueError):self.m.advance(old)
        self.m.advance(old,allow_missing=True)
        self.assertEqual(self.m.game.stage,'commit')
        with self.assertRaises(ValueError):self.m.receive('GN',dict(type='sheet',epoch=old,id='late',sheet=row_for(SCRIPT[0],'GN')))
        with self.assertRaises(ValueError):self.send('GN',{'choice':'Security'})
        with self.assertRaises(ValueError):self.m.advance(old,allow_missing=True)
    def test_reconnect_displaces_old_transport_and_preserves_sheet(self):
        self.step(SCRIPT[1])
        self.send('GN',row_for(SCRIPT[2],'GN'));self.m.disconnect('GN')
        self.m.receive('new',dict(type='hello',token=self.tokens['GN']))
        self.assertEqual(self.m.live['new'],'GN');self.assertIn('GN',self.m.sheets)
        with self.assertRaises(ValueError):self.m.receive('GN',dict(type='sheet',epoch=self.m.epoch,id='old',sheet=row_for(SCRIPT[0],'GN')))
        with self.assertRaises(ValueError):self.m.receive('bad',dict(type='hello',token='forged'))
    def test_duplicate_message_is_idempotent(self):
        p=dict(type='chat',id='one',channel='guild',text='One message')
        self.m.receive('GN',p);self.m.receive('GN',p);self.assertEqual(len(self.m.chats),1)
    def test_saved_session_restores_private_state_and_seat_tokens(self):
        self.step(SCRIPT[0]);self.step(SCRIPT[1])
        with tempfile.TemporaryDirectory() as folder:
            self.m.path=Path(folder)/'game.json';self.m.save();restored=Multiplayer(self.m.path);restored.begin_host()
            restored.receive('resume',dict(type='hello',token=self.tokens['A']))
            self.assertEqual(restored.live,{'resume':'A'});self.assertEqual(restored.game.vision,self.m.game.vision)
            self.assertIsNone(restored.view('GN')['selected_vision'])
    def test_host_lease_replaced_and_occupied_seat_cannot_be_stolen(self):
        old=self.m.host_key;self.m.begin_host()
        with self.assertRaises(ValueError):self.m.check_host(old)
        self.m.receive('other',dict(type='hello',name='Other',role='GN'))
        with self.assertRaises(ValueError):self.m.approve('other','GN')

if __name__=='__main__':unittest.main()
