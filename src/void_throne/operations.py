"""Desk-check model for the printed 0.2 rules; never needed at the table."""
from dataclasses import dataclass, replace, asdict
from itertools import product
import json
from pathlib import Path

@dataclass(frozen=True)
class State:
    beacon:int=2
    communities:int=3
    readiness:int=3
    wayfarer:bool=True
    lantern:bool=True
    spear:bool=True
    contracts:int=0
    reserve:bool=True

def clamp(n):return max(0,min(4,n))

def resolve(st, rnd=1, w='Council', l='Maintain', s='Council', v='Council',
            nav='Relief', sec='Restraint', na='I', ma='I', warrant=False,
            intervention='Keep', nav_signed=True, sec_signed=True):
    assert rnd in (1,2)
    assert na in ('I','NG','NI','NJ') and ma in ('I','MI','MA','MJ')
    events=[]
    c=-1; wear=0; contracts=st.contracts
    W=st.wayfarer; L=st.lantern; S=st.spear; reserve=st.reserve
    w=w if W else 'Absent'; l=l if L else 'Absent'; s=s if S else 'Absent'
    if not nav_signed: nav='Hold'
    if not sec_signed: sec='Restraint'
    guarded=False
    if warrant and ma in ('I','MI'):
        if st.readiness>=3 and v=='Council':
            guarded=True; c+=1; events.append('Warrant: Vigil used; Stability +1')
        else:
            c-=1; events.append('Unsupported warrant: Stability -1')
    elif warrant:
        events.append('Warrant outside authority: advice only')
    if sec=='Guard':
        if v=='Council' and not guarded:
            guarded=True;c+=1;events.append('Guard: Vigil used; Stability +1')
        else:
            sec='Restraint';c-=1;events.append('Unfunded Guard: Restraint; Stability -1')
    # Establish paid navigation order, including the conditional hired cutter.
    offeredW=w=='Council'; offeredL=l=='Council'
    if nav=='Relief' and not offeredW and intervention=='Relief lift' and reserve:
        offeredW=True; reserve=False; events.append('Grey Petrel provides Relief lift; reserve spent')
    funded={'Relief':offeredW,'Military':w=='Council','Shared':w=='Council' and offeredL,
            'Repair':offeredL,'Hold':True}[nav]
    if not funded:
        nav='Hold';c-=1;events.append('Unfunded Navigation: Hold; Stability -1')
    prepared=clamp(st.beacon+(1 if l=='Maintain' else 0)+(2 if nav=='Repair' else 0))
    voyage=nav in ('Relief','Military','Shared')
    delivered=voyage and prepared>=2
    if voyage and not delivered:
        c-=1;events.append('Unsafe passage: voyage halted; Stability -1')
    if delivered:
        wear+=1
        c+={'Relief':2,'Military':0,'Shared':1}[nav]
    trade=False
    if w=='Trade':
        if prepared>=2 and (prepared>=3 or guarded):
            trade=True;contracts+=1;wear+=1;events.append('Wayfarer commercial contract completed')
        elif prepared>=2:
            W=False;wear+=1;events.append('Wayfarer attacked: no contract; ship disabled')
        else:
            events.append('Commercial voyage halted: no contract; ship intact')
    # Each institution can lose at most one Stability for breach this round.
    guild_breach=(na=='NG' and not (l=='Maintain' or nav=='Repair')) or (na in ('NI','NJ') and w!='Council')
    jan_breach=(ma in ('MI','MJ') and s!='Council') or (ma=='MA' and v!='Home') or (ma=='I' and s=='Raid')
    if guild_breach:c-=1;events.append('Guild duty broken: Stability -1')
    if jan_breach:c-=1;events.append('Janissariat duty broken: Stability -1')
    raid=s=='Raid' or (sec=='Raid' and s=='Council')
    campaign=sec=='Campaign' and s=='Council'
    if sec in ('Raid','Campaign') and s!='Council':
        c-=1;events.append('Unfunded Security order: Restraint; Stability -1')
    combat=False
    if campaign:
        if not (delivered and nav in ('Military','Shared')):
            c-=1;events.append('Campaign lacks delivered military passage: Stability -1')
        else:
            c-=1
            if st.readiness>=2:combat=True;events.append('Campaign fought: Stability -1; conditioning sustained')
            else:S=False;events.append('Campaign overmatched: Spear disabled; Stability -1')
    if raid:
        c-=1
        present=trade if rnd==1 else delivered and nav=='Relief'
        if present:
            if st.readiness>=2:
                combat=True;c-=1;events.append('Raid fought: Stability -2 total; conditioning sustained')
            else:S=False;events.append('Raid overmatched: Spear disabled')
        else:events.append('Raid target absent: Stability -1; no qualifying combat')
    if rnd==1 and delivered and nav=='Shared' and not guarded:
        if intervention=='Tender cover' and reserve:
            reserve=False;events.append('Grey Petrel protects Lantern crew; reserve spent')
        else:
            L=False;events.append('Exposed transfer berth: Lantern navigation team lost')
    if rnd==2:
        if delivered and nav=='Military' and not guarded:
            c-=1;events.append('Unprotected military-only loading: Stability -1')
        if nav=='Repair' and trade:
            c+=1;events.append('Repair and completed commercial voyage: Stability +1')
    new=State(clamp(prepared-wear),clamp(st.communities+c),clamp(st.readiness+(1 if combat else -1)),W,L,S,contracts,reserve)
    return new,dict(events=events,prepared=prepared,nav=nav,sec=sec,guarded=guarded,delivered=delivered,
                    trade=trade,combat=combat,guild_breach=bool(guild_breach),jan_breach=bool(jan_breach))

