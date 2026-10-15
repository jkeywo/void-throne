"""External Playtrace plugin: exact paper-procedure replays, not invented LLM choices."""
from pathlib import Path
import hashlib
from playtrace.canonical import canonical_digest
from playtrace.simulation import (SimulationRun,SimulationProvenance,SimulationMetrics,SimulationEvent,
    SimulationCheckpoint,PluginSimulationState,SimulationBlocker,BlockerKind,SimulationStatus,
    PlayerPolicyKind,snapshot_content_digest)
from playtrace.semantics import SemanticUsage,SemanticOrigin,audit_semantics
from .session import Session, ROOT, ROLES

def engine_digest():
    paths=sorted((ROOT/'src/void_throne').glob('*.py'))+sorted((ROOT/'design/private-cards').glob('*.json'))+sorted((ROOT/'design/public-covers').glob('*.json'))+sorted((ROOT/'design/player-visions').glob('*.json'))+[ROOT/'design/track-descriptions.json']
    h=hashlib.sha256()
    for p in paths:h.update(p.relative_to(ROOT).as_posix().encode());h.update(p.read_bytes())
    return h.hexdigest()

class VoidThronePlugin:
    id='void-throne';version='0.3.0';project_ids=('void-throne',)

    def run(self,snapshot,config,*,runner):
        game=Session();events=[];checkpoints=[];blockers=[]
        initial=PluginSimulationState(plugin_id=self.id,status=SimulationStatus.READY,data={'physical':game.state,'foresight':3,'articles':game.articles})
        snapshot_hash=snapshot_content_digest(snapshot);config_hash=canonical_digest(config,domain='simulation-config')
        model_hash=engine_digest()
        provenance=SimulationProvenance(snapshot_id=snapshot.id,snapshot_digest=snapshot_hash,backend_version='playtrace-game-plugin-v1',
            plugin_id=self.id,plugin_version=self.version,config_digest=config_hash,player_policy=config.player_policy,seeds=(config.seed,),runner=runner)
        usages=tuple(SemanticUsage(id='vt:semantic:'+key,origin=SemanticOrigin.PLUGIN_EXTENSION,description=description,
                     source_revision_ids=tuple(x.id for x in snapshot.source_revisions),provenance=('engine-sha256:'+model_hash,),executed=False)
                     for key,description in [('operations','Exact concrete-asset funding, defaults, hidden consequences, costs and track changes.'),
                     ('foresight','Public drafts, paid conditional answer, one purchase per round, three tokens.'),
                     ('trial','Independent domain assent and exact owner-signed assignment pledges.'),
                     ('settlement','Five explicit approvals, three weighted signatures, threshold and fallback.')])
        try:
            if snapshot.project_id!='void-throne':raise ValueError('Wrong project snapshot.')
            if config.ruleset_id!='vt:rules:revised-visions-v0.3' or config.scenario_id!='vt:scenario:narrow':raise ValueError('Unsupported ruleset or scenario.')
            if tuple(config.character_ids)!=ROLES:raise ValueError('This projection requires GN, GS, JN, JS and A in order.')
            if config.player_policy!=PlayerPolicyKind.PLUGIN_SCRIPTED:raise ValueError('Only explicit game-owned scripted decisions are supported; no fallback player policy.')
            if config.overrides or config.scripted_steps or config.deck_order:raise ValueError('No undeclared override or generic tabletop action is supported.')
            if config.max_turns!=2:raise ValueError('This paper prototype has exactly two operational rounds.')
            source=next((r for r in snapshot.source_revisions if r.source_id=='vt:engine'),None)
            if source is None or source.content_digest!=model_hash:raise ValueError('Snapshot does not capture the current game engine; reproduce the snapshot first.')
            actions=config.plugin_config.get('actions')
            if not isinstance(actions,list) or not actions or len(actions)>100:raise ValueError('Supply the exact bounded list of phase decisions.')
            for index,action in enumerate(actions):
                before=len(game.history);game.apply(action)
                for item in game.history[before:]:
                    category='foresight' if item['event'] in ('Public draft sheets','Foresight purchase') else 'trial' if item['event'] in ('Exact provisional proposal','Provisional signatures and result') else 'settlement' if item['phase'].startswith('ceremony') else 'operations'
                    events.append(SimulationEvent(sequence=len(events)+1,turn=item['round'],event_type=item['event'],
                                  data={**item,'script_step':index+1},semantic_ids=('vt:semantic:'+category,)))
                checkpoints.append(SimulationCheckpoint(sequence=len(events),state=PluginSimulationState(plugin_id=self.id,turn=game.round,
                    status=SimulationStatus.RUNNING,data={'physical':game.state,'foresight':game.foresight,'articles':game.articles,
                    'stage':game.stage,'settlement':game.settlement})))
            if game.stage!='ended':raise ValueError('Script exhausted before the Ceremony ended. No votes or orders were invented.')
        except (ValueError,TypeError,KeyError,AssertionError) as exc:
            blockers.append(SimulationBlocker(id='vt:blocker:script',kind=BlockerKind.INVALID_CONFIGURATION,message=str(exc),required_input='Correct the exact phase script or refresh the captured model.'))
        # MAX_TURNS means the scheduled prototype ended, not that all parties won.
        status=SimulationStatus.BLOCKED if blockers else SimulationStatus.MAX_TURNS
        final=PluginSimulationState(plugin_id=self.id,turn=game.round,status=status,data={'physical':game.state,'foresight':game.foresight,
             'articles':game.articles,'settlement':game.settlement,'complete':game.stage=='ended','interpretation':'Scheduled two-round game; ratification is not unanimous success.'})
        usage=tuple(u.model_copy(update={'executed':any(u.id in e.semantic_ids for e in events),'execution_count':sum(u.id in e.semantic_ids for e in events)}) for u in usages)
        identity=canonical_digest({'snapshot':snapshot_hash,'config':config_hash,'engine':model_hash,'version':self.version},domain='void-throne-run')[:24]
        return SimulationRun(id='vt:run:'+identity,config=config,provenance=provenance,initial_state=initial,final_state=final,
            events=tuple(events),state_trace=tuple(checkpoints),blockers=tuple(blockers),semantic_audit=audit_semantics(usage,strict=config.strict_semantics),
            metrics=SimulationMetrics(turns_completed=sum(e.event_type=='Operational resolution' for e in events),cards_resolved=0,
                escalation_steps=0,improves=0,worsens=0,maximum_tableau_cubes=0,blocker_count=len(blockers),player_actions=len(game.actions)))
