import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from void_throne.browser_host import BrowserHost
from void_throne.session import ROLES
from test_multiplayer import row_for

SCRIPT=json.loads((ROOT/'design/experiments/replay-config.json').read_text(encoding='utf8'))['plugin_config']['actions']


class BrowserHostTests(unittest.TestCase):
    def test_browser_bridge_replay_resume_and_private_projection(self):
        host=BrowserHost()
        key=host.request('host',{})['envelope']['host_key']
        tokens={}
        for role in ROLES:
            host.request('message',dict(host_key=key,connection=role,message=dict(type='hello',name=role,role=role)))
            result=host.request('approve',dict(host_key=key,connection=role,role=role))
            tokens[role]=result['envelope']['direct'][role]['token']
        for step,action in enumerate(SCRIPT):
            if action['stage']=='draft':continue  # Historical pre-choice plans are no longer collected.
            for role in host.session.required():
                host.request('message',dict(host_key=key,connection=role,message=dict(type='sheet',id=f'{step}-{role}',epoch=host.session.epoch,sheet=row_for(action,role))))
            result=host.request('advance',dict(host_key=key,epoch=host.session.epoch,proposal=action))
            if step==1:
                restored=BrowserHost(result['backup'])
                key=restored.request('host',{})['envelope']['host_key']
                for role in ROLES:
                    restored.request('message',dict(host_key=key,connection=role,message=dict(type='hello',token=tokens[role])))
                self.assertEqual(restored.session.game.vision,host.session.game.vision)
                self.assertIsNone(restored.session.view('GN')['selected_vision'])
                host=restored
        expected=json.loads((ROOT/'tests/fixtures/expected-ending.json').read_text())
        self.assertEqual(host.session.game.state,expected['physical'])
        self.assertTrue(host.session.game.settlement['ratified'])
        report=host.request('report',dict(host_key=key))['download']
        self.assertIn('Human-seat multiplayer record',report)
        exported=host.request('export',dict(host_key=key))['download']
        self.assertNotIn('seen',exported)
        self.assertTrue(all('token' not in seat for seat in exported['seats'].values()))

    def test_host_operations_require_current_authority(self):
        host=BrowserHost()
        old=host.request('host',{})['envelope']['host_key']
        host.request('host',{})
        for action in ('report','export','new','advance'):
            with self.assertRaises(ValueError):host.request(action,dict(host_key=old))

    def test_new_game_resets_state_and_changes_room(self):
        host=BrowserHost()
        before=host.request('host',{})
        after=host.request('new',dict(host_key=before['envelope']['host_key']))
        self.assertNotEqual(before['backup']['room'],after['backup']['room'])
        self.assertEqual(after['backup']['actions'],[])
        self.assertEqual(after['envelope']['host']['game']['foresight'],3)

    def test_invalid_saved_version_rejected(self):
        with self.assertRaises(ValueError):BrowserHost(dict(version=999,actions=[]))


if __name__=='__main__':unittest.main()
