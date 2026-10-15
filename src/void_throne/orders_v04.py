"""Current paper operations: funded orders, one use per asset, one transport wear."""
from .operations import State, clamp
from .assets import ASSET_CARDS, ORDER_TRAITS, supports

NAV = ['Relief', 'Military', 'Repair']
SEC = ['Campaign', 'Raid', 'Guard']
LABELS = {'Relief':'Deliver Relief', 'Military':'Transport Troops', 'Repair':'Repair the Narrows',
          'Campaign':'Attack the Anchorage', 'Raid':'Intercept a Patrol', 'Guard':'Protect the Passage',
          'Council':'Offer Council Service', 'Trade':'Fulfil Commercial Contract', 'Maintain':'Maintain the Narrows',
          'Stand down':'Stand Down', 'Home':'Defend Army Bases', 'Absent':'Asset Unavailable',
          'Keep':'Retain the Cutter', 'Relief lift':'Carry Emergency Relief', 'Tender cover':'Protect the Navigators'}
AUTH = {'navigation':{'I':('A',),'NI':('A',),'NG':('GN',),'NJ':()},
        'military':{'I':('A',),'MI':('A',),'MA':('JS',),'MJ':()}}

def veto_rights(articles, assignments, reserve):
    contributors=set()
    for owner,row in assignments.items():
        if 'Council' in row.values():contributors.add(owner)
    if reserve=='Council':contributors.add('Ascendant')
    seats={'navigation':{'Guild':'GN','Janissariat':'JN','Ascendant':'A'},
           'military':{'Guild':'GS','Janissariat':'JS','Ascendant':'A'}}
    return {d:([seats[d][o] for o in ('Guild','Janissariat','Ascendant') if o in contributors]
               if article in ('NJ','MJ') else list(AUTH[d][article])) for d,article in articles.items()}

def orders(value, domain):
    """Validate a declared programme, never silently select between competing assets."""
    if not isinstance(value,list):raise ValueError('Choose a list of orders; leave it empty for no operation.')
    allowed=NAV if domain=='navigation' else SEC
    if len(value)>len(allowed):raise ValueError('Each order may be chosen only once.')
    result=[];used=set();seen=set()
    for row in value:
        if not isinstance(row,dict) or set(row)!={'order','asset'}:raise ValueError('Each order must name its asset.')
        order=row['order'];asset=row['asset']
        if order not in allowed or order in seen:raise ValueError('Unknown or repeated order.')
        if not supports(asset,order):raise ValueError(LABELS[order]+' needs an asset with '+ORDER_TRAITS[order]+'.')
        if asset in used:raise ValueError(asset+' can be used only once this round.')
        seen.add(order);used.add(asset);result.append(dict(row))
    return result

def resolve(st, rnd=1, w='Council',l='Maintain',s='Council',v='Council',nav=None,sec=None,
            na='I',ma='I',warrant=False,intervention='Keep',vetoes=None):
    nav=orders(nav or [],'navigation');sec=orders(sec or [],'military');vetoes=vetoes or {}
    events=[];outcomes=[];used={};rejected=[];c=-1;contracts=st.contracts
    W,L,S,reserve=st.wayfarer,st.lantern,st.spear,st.reserve
    w=w if W else 'Absent';l=l if L else 'Absent';s=s if S else 'Absent'
    assigned={'Wayfarer':w,'Lantern':l,'Spear':s,'Vigil':v}
    guarded=False;combat=False;trade=False;trade_wear=0
    def reject(row,reason):
        rejected.append(dict(row,reason=reason));outcomes.append(LABELS[row['order']]+' was not carried out: '+reason+'.')
    # A veto bars the named council order, including its independent faction equivalent.
    for asset,assignment,task in [('Wayfarer',w,'Trade'),('Lantern',l,'Maintain'),('Spear',s,'Raid'),('Vigil',v,'Home')]:
        if assignment==task:used[asset]=LABELS[task]
    independent_raid=s=='Raid' and 'Raid' not in (vetoes.get('military') or [])
    if s=='Raid' and not independent_raid:outcomes.append('The veto prevented Spear from intercepting a patrol; it remained idle.')
    if warrant and ma in ('I','MI'):
        if 'Guard' in (vetoes.get('military') or []):
            outcomes.append('The passage-protection veto also prevented an imperial Warrant.')
        elif st.readiness>=3 and v=='Council':
            guarded=True;c+=1;used['Vigil']='Imperial Warrant';events.append('Warrant: Vigil used; Stability +1')
        else:c-=1;events.append('Unsupported warrant: Stability -1')
    elif warrant:events.append('Warrant outside authority: advice only')
    active={}
    for domain,programme in [('navigation',nav),('military',sec)]:
        for row in programme:
            order,asset=row['order'],row['asset']
            if order in (vetoes.get(domain) or []):reject(row,'vetoed for this round');continue
            if asset in used:reject(row,'asset already assigned to '+used[asset]);continue
            if asset=='Grey Petrel':
                if not reserve or intervention!='Council':reject(row,'the cutter was not offered to Navigation');continue
                reserve=False;outcomes.append('Grey Petrel carried out its contracted transport service.');events.append('Grey Petrel transport service: reserve spent')
            elif assigned[asset]!='Council':reject(row,'asset unavailable or not offered');continue
            active[order]=asset;used[asset]=LABELS[order]
    if 'Guard' in active:guarded=True;c+=1;events.append('Guard: Vigil used; Stability +1')
    prepared=clamp(st.beacon+(1 if l=='Maintain' else 0)+(2 if 'Repair' in active else 0))
    if 'Repair' in active:outcomes.append('Lantern repaired the Narrows.')
    delivered=[]
    for order in ('Relief','Military'):
        if order not in active:continue
        if prepared<2:c-=1;events.append('Unsafe passage: '+LABELS[order]+' halted; Stability -1');continue
        delivered.append(order)
        if order=='Relief':c+=2;outcomes.append('Relief supplies reached Sorenne’s Fall.')
        else:outcomes.append('The military transport reached the far side of the Narrow.')
    # Wear is for scheduling either/both transport orders, even if a funded voyage is halted.
    transport_wear=int(any(o in active for o in ('Relief','Military')))
    if w=='Trade':
        if prepared>=2 and (prepared>=3 or guarded):
            trade=True;contracts+=1;trade_wear=1;events.append('Wayfarer commercial contract completed')
        elif prepared>=2:W=False;trade_wear=1;events.append('Wayfarer attacked: no contract; ship disabled')
        else:events.append('Commercial voyage halted: no contract; ship intact')
    guild_breach=(na=='NG' and not (l=='Maintain' or 'Repair' in active)) or (na in ('NI','NJ') and w!='Council')
    jan_breach=(ma in ('MI','MJ') and s!='Council') or (ma=='MA' and v!='Home') or (ma=='I' and independent_raid)
    if guild_breach:c-=1;events.append('Guild duty broken: Stability -1')
    if jan_breach:c-=1;events.append('Janissariat duty broken: Stability -1')
    if 'Campaign' in active:
        c-=1
        if 'Military' not in delivered:events.append('Campaign lacks delivered military passage: Stability -1')
        elif st.readiness>=2:combat=True;events.append('Campaign fought: Stability -1; conditioning sustained')
        else:S=False;events.append('Campaign overmatched: Spear disabled; Stability -1')
    if independent_raid or 'Raid' in active:
        c-=1;present=trade if rnd==1 else 'Relief' in delivered
        if not present:events.append('Raid target absent: Stability -1; no qualifying combat')
        elif st.readiness>=2:combat=True;c-=1;events.append('Raid fought: Stability -2 total; conditioning sustained')
        else:S=False;events.append('Raid overmatched: Spear disabled')
    if rnd==1 and 'Relief' in delivered and active['Relief']=='Lantern' and not guarded:
        if intervention=='Tender cover' and reserve:reserve=False;events.append('Grey Petrel protects Lantern crew; reserve spent')
        else:L=False;events.append('Exposed transfer berth: Lantern navigation team lost')
    if rnd==2:
        if 'Military' in delivered and not guarded:c-=1;events.append('Unprotected military-only loading: Stability -1')
        if 'Repair' in active and trade:c+=1;events.append('Repair and completed commercial voyage: Stability +1')
    new=State(clamp(prepared-transport_wear-trade_wear),clamp(st.communities+c),clamp(st.readiness+(1 if combat else -1)),W,L,S,contracts,reserve)
    detail=dict(events=events,outcomes=outcomes,prepared=prepared,orders=active,delivered_orders=delivered,
                used_assets=used,rejected=rejected,transport_wear=transport_wear,trade_wear=trade_wear,
                guarded=guarded,trade=trade,combat=combat,guild_breach=bool(guild_breach),jan_breach=bool(jan_breach))
    return new,detail
