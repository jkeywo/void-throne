"""Facilitator rulings preserve the ordinary costs and dependencies of equivalent orders."""
from copy import deepcopy
from .session import ASSETS, DEFAULTS, boolean
from .assets import ASSET_CARDS
from .charter import apply_locks
from .orders_v04 import orders, NAV, SEC

def text(value):
    if not isinstance(value,str) or not value.strip() or len(value)>2000:
        raise ValueError('Other needs a proposal and a facilitator ruling, each up to 2000 characters.')
    return value.strip()

def ruling(payload,key,allowed,proposal):
    row=payload.get('rulings',{}).get(key)
    if not isinstance(row,dict) or row.get('basis') not in allowed+['Other']:
        raise ValueError('Facilitator must adjudicate Other for '+key+' before closing the phase.')
    return dict(key=key,proposal=text(proposal),basis=row['basis'],reason=text(row.get('reason')))

def validate_programme(value,domain):
    if not isinstance(value,list):raise ValueError('Choose a list of orders.')
    cleaned=[]
    for row in value:
        if isinstance(row,dict) and row.get('order')=='Other':
            if set(row)!={'order','asset','proposal'}:raise ValueError('Other needs its asset and proposal; rulings belong to the facilitator.')
            text(row['proposal']);cleaned.append({k:row[k] for k in ('order','asset')})
        else:cleaned.append(row)
    orders(cleaned,domain)
    return deepcopy(value)

def council(payload,game):
    p=deepcopy(payload);records=[]
    for field,domain,seat in [('navigation','navigation','GN'),('security','military','JS')]:
        rows=p.get(field,{})
        if not isinstance(rows,dict) or set(rows)-{seat}:raise ValueError('Only the council recorder may allocate its assets.')
        programme=validate_programme(rows.get(seat,[]),domain);resolved=[]
        for row in programme:
            if row['order']!='Other':resolved.append(row);continue
            r=ruling(p,domain,NAV if domain=='navigation' else SEC,row['proposal']);r['asset']=row['asset']
            if 'Other' in game.vetoes.get(domain,[]):r['blocked']='Other is vetoed this round.'
            else:resolved.append(dict(order=r['basis'],asset=row['asset']))
            records.append(r)
        # An equivalent task cannot duplicate a printed order, reuse assets or bypass traits.
        p[field]={seat:orders(resolved,domain)}
    return p,records

def faction(payload,game):
    rows=payload.get('assignments',{});result={};issues=[];records=[]
    if not isinstance(rows,dict):raise ValueError('Card placements must be a mapping.')
    for owner,seats in [('Guild',('GN','GS')),('Janissariat',('JN','JS'))]:
        candidates=[]
        for seat in seats:
            row=rows.get(seat,{})
            if not isinstance(row,dict):raise ValueError('Card placements must be a mapping.')
            candidate={a:row.get(a) if row.get(a) in opts+['Other'] else DEFAULTS[owner][a] for a,opts in ASSETS[seat].items()}
            candidate['other']={a:text(row.get('other',{}).get(a)) for a,v in candidate.items() if v=='Other'}
            candidates.append(candidate)
        confirmed=all(s in rows for s in seats)
        if 'signatures' in payload:confirmed=confirmed and all(boolean(payload['signatures'].get(s,False)) for s in seats)
        if not confirmed or candidates[0]!=candidates[1]:
            result[owner]=deepcopy(DEFAULTS[owner]);issues.append(owner+': no matching card arrangements and Other proposals; printed defaults apply.');continue
        chosen=candidates[0];proposals=chosen.pop('other');result[owner]=chosen
        for asset,proposal in proposals.items():
            if any(x['asset'].lower()==asset for x in game.pledges) or (asset!='vigil' and not game.state[asset]):continue
            name=next(a for a in ASSET_CARDS if a.lower()==asset)
            r=ruling(payload,asset,ASSET_CARDS[name]['home'],proposal);r['asset']=name
            result[owner][asset]=r['basis'];records.append(r)
    result=apply_locks(result,game.pledges)
    for row in result.values():
        for asset in row:
            if asset!='vigil' and not game.state[asset]:row[asset]='Absent'
    reserve=payload.get('reserve','Keep')
    if reserve not in ['Keep','Council','Tender cover','Other']:raise ValueError('Unknown Grey Petrel placement.')
    if not game.state['reserve']:reserve='Keep'
    elif reserve=='Other':
        r=ruling(payload,'reserve',ASSET_CARDS['Grey Petrel']['home'],payload.get('reserve_proposal'));r['asset']='Grey Petrel'
        reserve=r['basis'];records.append(r)
    return result,reserve,issues,records
