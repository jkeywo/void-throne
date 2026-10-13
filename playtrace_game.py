"""Game-owned bridge into the existing Playtrace installation."""
from pathlib import Path
import sys,os,json,subprocess,hashlib,argparse
ROOT=Path(__file__).resolve().parent
PT=Path(os.environ.get('PLAYTRACE_ROOT','C:/Coding/playtrace'))
sys.path[:0]=[str(ROOT/'src'),str(PT/'src')]
try:
    import lark,pydantic
except ImportError:
    candidate=PT/'.venv/Scripts/python.exe'
    if candidate.exists() and Path(sys.executable).resolve()!=candidate.resolve():
        raise SystemExit(subprocess.call([str(candidate),str(Path(__file__).resolve()),*sys.argv[1:]],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}))
    raise SystemExit('Use the Playtrace Python environment (Python 3.12+, pydantic and lark).')
from playtrace.tabletop import TabletopProjectAdapter
from playtrace.workspace import FixtureWorkspaceGateway
from playtrace.models import SourceRevision,SourceMedium,Hypothesis,EvidenceRelation
from playtrace.canonical import canonical_digest
from playtrace.simulation import SimulationConfig,InProcessSimulationRunner
from playtrace.simulation_report import write_simulation_report
from playtrace.plugins import registry
from playtrace.storage import PlayTraceStore
from playtrace.evidence import simulation_evidence
from void_throne.plugin import VoidThronePlugin,engine_digest
registry.register(VoidThronePlugin)

def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data.model_dump(mode='json') if hasattr(data,'model_dump') else data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def snapshot():
    captured=TabletopProjectAdapter.from_path(ROOT/'playtrace.toml',FixtureWorkspaceGateway.from_file(ROOT/'tests/fixtures/workspace.json')).snapshot()
    sha=engine_digest()
    revision=SourceRevision(id='vt:engine@'+sha,source_id='vt:engine',medium=SourceMedium.GIT,locator='src/void_throne + design/*-cards',revision=sha,content_digest=sha)
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit='uncommitted-initial-migration'
    try:ptcommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=PT,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:ptcommit='unavailable'
    systemhash=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((PT/'src/playtrace').rglob('*.py')))).hexdigest()
    git=SourceRevision(id='vt:repository@'+commit,source_id='vt:repository',medium=SourceMedium.GIT,locator='.',revision=commit,content_digest=sha)
    system=SourceRevision(id='vt:playtrace@'+systemhash,source_id='vt:playtrace',medium=SourceMedium.GIT,locator=str(PT),revision=ptcommit,content_digest=systemhash)
    return captured.model_copy(update={'id':captured.id+':model:'+sha[:12]+':repo:'+commit[:12],
        'source_revisions':(*captured.source_revisions,revision,git,system),
        'omissions':(*captured.omissions,'Drive data is a verified capture, not a live refresh.','Scripted replay does not generate negotiations or model subjective trust.','Cards and votes execute game-owned Python extensions, not compiled prose.','Shared legacy numeric metrics are zero where not applicable; inspect plugin state and events.')})

def reproduce():
    snap=snapshot();config=SimulationConfig.model_validate_json((ROOT/'design/experiments/replay-config.json').read_text(encoding='utf-8'))
    run=InProcessSimulationRunner().run(registry.for_project('void-throne'),snap,config)
    if run.blockers:raise SystemExit(json.dumps([b.model_dump(mode='json') for b in run.blockers],indent=2))
    expected=json.loads((ROOT/'tests/fixtures/expected-ending.json').read_text(encoding='utf-8'))
    assert run.final_state.data['physical']==expected['physical'],'Replay physical ending differs from original agent record'
    assert run.final_state.data['foresight']==expected['foresight']
    for key in ('weights','supporting_leverage','threshold','ratified','approvals','package'):
        assert run.final_state.data['settlement'][key]==expected['settlement'][key],key
    hypothesis=Hypothesis.model_validate_json((ROOT/'design/experiments/foresight-hypothesis.json').read_text(encoding='utf-8'))
    bundle=simulation_evidence(project_id='void-throne',snapshot=snap,hypothesis=hypothesis,run=run,relation=EvidenceRelation.CONTEXT,
        rationale='Exact replay verifies consequences of preserved six-agent choices; it is not a fresh test of behavioural causation or deliberate saving.',
        assumptions=('Five roles are supplied by an immutable historical script; no new LLM inference.','The two-round prototype is a limited adaptation of the larger setting.'),artifact_path='design/evidence/playtrace-replay.json')
    dump(ROOT/'.playtrace/snapshot.json',snap);dump(ROOT/'design/evidence/playtrace-snapshot.json',snap)
    dump(ROOT/'design/evidence/playtrace-replay.json',run);dump(ROOT/'design/evidence/playtrace-experiment.json',bundle)
    with PlayTraceStore(ROOT/'.playtrace/playtrace.db') as store:
        store.save_snapshot(snap);store.save_simulation(run);store.save_hypothesis(snap.id,hypothesis)
        store.save_experiment_evidence(bundle.evidence);store.save_claim(snap.id,bundle.claim)
    write_simulation_report([run],ROOT/'reports/playtrace-replay.html')
    print(json.dumps({'run':run.id,'events':len(run.events),'ending':run.final_state.data,'evidence_relation':bundle.evidence.hypothesis_link.relation.value,'applicability':bundle.evidence.applicability.value},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['reproduce','snapshot','cli']);parser.add_argument('rest',nargs=argparse.REMAINDER);args=parser.parse_args()
    if args.command=='reproduce':reproduce()
    elif args.command=='snapshot':dump(ROOT/'.playtrace/snapshot.json',snapshot());print('Captured Drive + engine snapshot saved.')
    else:
        # Standard Playtrace CLI after registering the game plugin. The normal simulate
        # command lacks game-owned engine provenance; use reproduce for this strict model.
        from playtrace.cli import main
        sys.argv=['playtrace',*args.rest];main()
