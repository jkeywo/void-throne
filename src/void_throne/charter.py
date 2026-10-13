"""Adjudicate an exact proposed trial row. Physical operations still use the v0.2 resolver."""
from copy import deepcopy

OWNERS={'Wayfarer':'Guild','Lantern':'Guild','Spear':'Janissariat','Vigil':'Janissariat'}
SIGNERS={'Guild':('GN','GS'),'Janissariat':('JN','JS')}
AVAILABLE={'Wayfarer':'wayfarer','Lantern':'lantern','Spear':'spear'}
CHOICES={'Wayfarer':('Council',),'Lantern':('Council','Maintain'),'Spear':('Council',),'Vigil':('Council','Home')}
DOMAINS={'navigation':('NG','NI','NJ'),'military':('MI','MA','MJ')}
COUNCILS={'navigation':('GN','JN'),'military':('GS','JS')}

def code(value):return str(value).replace('-','').upper()

def evaluate(proposal,votes,state,threshold='unanimous'):
 assert threshold in ('unanimous','crown_plus_one')
 articles={d:code(proposal.get('articles',{}).get(d,'')) for d in DOMAINS}
 pledges=proposal.get('commitments',[])
 issues={d:[] for d in DOMAINS}; active=[];result={d:'I' for d in DOMAINS}
 validvotes={role:v for role,v in votes.items() if v.get('proposal_id')==proposal['id']}
 for d,options in DOMAINS.items():
  if articles[d] not in options:issues[d].append('No valid article on this row')
  crown=validvotes.get('A',{}).get('article_approvals',{}).get(d) is True
  delegates=[validvotes.get(r,{}).get('article_approvals',{}).get(d) is True for r in COUNCILS[d]]
  assent=crown and (all(delegates) if threshold=='unanimous' else any(delegates))
  if not assent:issues[d].append('Required article assent absent')
  for pledge in pledges:
   attached=code(pledge.get('article',''))
   if attached not in DOMAINS[d]:continue
   owner=pledge.get('owner');asset=pledge.get('asset');assignment=pledge.get('assignment')
   if attached!=articles[d]:issues[d].append('Attached commitment names a different article')
   if OWNERS.get(asset)!=owner:issues[d].append('Invalid asset owner')
   if assignment not in CHOICES.get(asset,()):issues[d].append('Invalid service assignment')
   if asset in AVAILABLE and not state.get(AVAILABLE[asset],False):issues[d].append('Asset unavailable')
   if sum(p.get('owner')==owner for p in pledges)>1:issues[d].append('More than one commitment from this faction')
   if not all(validvotes.get(r,{}).get('commitment_approvals',{}).get(owner) is True for r in SIGNERS.get(owner,())) or owner not in SIGNERS:
    issues[d].append('Both owner signatures required')
  if not issues[d]:
   result[d]=articles[d]
   for pledge in pledges:
    if code(pledge.get('article',''))==articles[d]:active.append(dict(pledge,owner_signatures=list(SIGNERS[pledge['owner']])))
 return {'articles_after':result,'activated_commitments':active,'issues':issues}

def apply_locks(assignments,pledges):
 result=deepcopy(assignments)
 for p in pledges:result[p['owner']][p['asset'].lower()]=p['assignment']
 return result

