"""Paper experiment: leverage and foresight only. Operations remain v0.2."""
from itertools import combinations
PARTIES=('Guild','Janissariat','Ascendant')
def leverage(state,foresight):
    assert isinstance(foresight,int) and 0<=foresight<=3
    r=state['readiness']
    weights={'Guild':2*int(state['wayfarer'])+int(state['lantern'])+int(state['beacon']>=1),'Janissariat':r,'Ascendant':r+foresight}
    total=sum(weights.values());threshold=(2*total+2)//3
    winning=[]
    for size in (2,3):
        for group in combinations(PARTIES,size):
            if total>0 and sum(weights[p]>0 for p in group)>=2 and sum(weights[p] for p in group)>=threshold:winning.append(list(group))
    return {'weights':weights,'foresight_remaining':foresight,'total':total,'threshold':threshold,'winning_coalitions':winning}
def ballot(state,foresight,approvals,package):
    tally=leverage(state,foresight)
    support={'Guild':approvals.get('GN') is True and approvals.get('GS') is True,'Janissariat':approvals.get('JN') is True and approvals.get('JS') is True,'Ascendant':approvals.get('A') is True}
    yes=sum(tally['weights'][p] for p in PARTIES if support[p]);institutions=sum(support[p] and tally['weights'][p]>0 for p in PARTIES)
    valid=package.get('navigation') in ('NG','NI','NJ') and package.get('military') in ('MI','MA','MJ')
    return dict(tally,party_signatures=support,supporting_leverage=yes,supporting_parties=institutions,ratified=bool(valid and tally['total']>0 and yes>=tally['threshold'] and institutions>=2))
def spend(remaining,choice):
    assert choice in ('Navigation','Security','None')
    assert choice=='None' or remaining>0
    return remaining-(choice!='None')
