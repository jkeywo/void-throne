"""Player information: qualitative choices and events, never resolution arithmetic."""
from copy import deepcopy
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]

def track_descriptions():
    return json.loads((ROOT/'design/track-descriptions.json').read_text(encoding='utf8'))

def player_vision(card):
    if card is None:return None
    ident=card.get('id')
    if ident not in ('R1-N','R1-S','R2-N','R2-S'):
        raise ValueError('No player handout is registered for this vision.')
    folder='design/v04/player-visions' if card.get('ruleset')=='vt:rules:asset-orders-v0.4' else 'design/player-visions'
    return json.loads((ROOT/folder/f'{ident}.json').read_text(encoding='utf8'))

OUTCOMES={
 'Warrant:':'Vigil carried out the imperial Warrant.',
 'Unsupported warrant:':'The imperial Warrant could not be carried out.',
 'Warrant outside authority:':'The Warrant was advice under the current Charter.',
 'Guard:':'Vigil protected traffic and service installations.',
 'Unfunded Guard:':'The council could not carry out Guard.',
 'Grey Petrel provides Relief lift;':'Grey Petrel was called on to provide the Relief voyage.',
 'Unfunded Navigation:':'Navigation could not carry out its order.',
 'Unsafe passage:':'The council voyage did not depart.',
 'Wayfarer commercial contract completed':'Wayfarer completed its commercial voyage.',
 'Wayfarer attacked:':'Wayfarer was disabled in an attack; its contract was not completed.',
 'Commercial voyage halted:':'Wayfarer stayed in port; its contract was not completed.',
 'Guild duty broken:':'The Guild did not fulfil its service duty.',
 'Janissariat duty broken:':'The Janissariat did not fulfil its service duty.',
 'Unfunded Security order:':'Security could not carry out its council order.',
 'Campaign lacks delivered military passage:':'Spear did not receive passage for the Campaign.',
 'Campaign fought:':'The Campaign fought at the Sorenne anchorage.',
 'Campaign overmatched:':'The Campaign overwhelmed the cohort; Spear was disabled.',
 'Raid fought:':'Spear intercepted the Sorenne patrol and fought.',
 'Raid overmatched:':'The patrol overwhelmed the cohort; Spear was disabled.',
 'Raid target absent:':'Spear returned without finding the patrol.',
 'Grey Petrel protects Lantern crew;':'Grey Petrel intervened to save the navigation team.',
 'Exposed transfer berth:':'Lantern’s navigation team was lost during the passage.',
 'Unprotected military-only loading:':'Stores were lost during the military loading operation.',
 'Repair and completed commercial voyage:':'Distribution improved alongside route work and commercial traffic.',
}

def public_resolution(event):
    # Explicit projection, including for old saves: never copy unknown calculation fields.
    out={k:deepcopy(event[k]) for k in ('sequence','round','phase','event','before','after','leverage') if k in event}
    detail=event.get('detail',{});stories=list(detail.get('outcomes',[]))
    if detail.get('delivered'):
        stories.append({'Relief':'Relief supplies reached Sorenne’s Fall.','Military':'Military passage was delivered.','Shared':'Civilian supplies and military passage were delivered together.'}[detail['nav']])
    elif detail.get('nav')=='Repair':stories.append('Lantern carried out the route repair.')
    for raw in detail.get('events',[]):
        story=next((v for k,v in OUTCOMES.items() if raw.startswith(k)),None)
        if story:stories.append(story)
    out['outcomes']=stories
    return out
