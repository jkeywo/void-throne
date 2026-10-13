import unittest,sys,json
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
try:
    import lark,pydantic
    import playtrace_game as bridge
    HAS_PT=True
except ImportError:HAS_PT=False

@unittest.skipUnless(HAS_PT,'Run in the Playtrace environment for integration checks.')
class PlaytraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot=bridge.snapshot()
        cls.config=bridge.SimulationConfig.model_validate_json((ROOT/'design/experiments/replay-config.json').read_text(encoding='utf-8'))
    def run_game(self,config=None,snapshot=None):
        return bridge.VoidThronePlugin().run(snapshot or self.snapshot,config or self.config,runner='in_process')
    def test_repeatable_replay(self):
        a=self.run_game();b=self.run_game()
        self.assertFalse(a.blockers);self.assertEqual(a.id,b.id);self.assertEqual(a.events,b.events)
        self.assertTrue(a.semantic_audit.passed);self.assertEqual(a.final_state.data['settlement']['supporting_leverage'],8)
    def test_exhausted_script_is_blocked_not_autocompleted(self):
        data=self.config.model_dump(mode='json');data['plugin_config']['actions']=data['plugin_config']['actions'][:2]
        result=self.run_game(bridge.SimulationConfig.model_validate(data))
        self.assertTrue(result.blockers);self.assertFalse(result.final_state.data['complete'])
    def test_stale_engine_snapshot_rejected(self):
        stale=self.snapshot.model_copy(update={'source_revisions':tuple(r for r in self.snapshot.source_revisions if r.source_id!='vt:engine')})
        self.assertTrue(self.run_game(snapshot=stale).blockers)
    def test_unsupported_override_rejected(self):
        data=self.config.model_dump(mode='json');data['overrides']=[{'key':'free_ships','value':10,'rationale':'test'}]
        self.assertTrue(self.run_game(bridge.SimulationConfig.model_validate(data)).blockers)
    def test_capture_contains_actual_drive_revisions(self):
        docs=json.loads((ROOT/'design/drive-files.json').read_text(encoding='utf-8'))['documents']
        for key,doc in docs.items():self.assertTrue(any(r.source_id=='vt:source:'+key and r.revision==doc['revision'] for r in self.snapshot.source_revisions))

if __name__=='__main__':unittest.main()
