"""Build printable fold-over asset cards and trait-based council order cards."""
from pathlib import Path
import sys,html
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from void_throne.assets import ASSET_CARDS,ORDER_TRAITS
from void_throne.orders_v04 import LABELS,NAV
def esc(s):return html.escape(s)
def asset_face(name,c,index):
    extra=''
    if name=='Grey Petrel':extra='One contracted service. Council transport spends the reserve even if halted. An unused offer keeps it. Rescue spends it only if triggered. Remove this card when spent.'
    elif name=='Lantern':extra='The navigation team is irreplaceable. A civilian voyage can expose it to danger. This asset has no Troop Transport trait.'
    elif name=='Spear':extra='Fighting sustains conditioning; a quiet month weakens it. Do not use this card for both an attack and an interception.'
    return '<article class="asset"><div class="owner">'+esc(c['owner'])+' · asset</div><h2>'+esc(name)+'</h2><p class="traits">'+esc(' · '.join(c['traits']))+'</p><h3>Faction Order: '+esc(LABELS[c['home'][index]])+'</h3><p>'+esc(c['home_text'][index])+'</p><h3>At council: offer service</h3><p>Take to <b>'+esc(c['council'])+'</b>. Match these traits to an order. Ignore the Faction Order face while at council. One use this round; unused means no Faction Order.</p><p class="special">'+esc(extra)+'</p><footer>'+('Turn over for the other Faction Order.' if len(c['home'])==2 else 'Same Faction Order on both faces.')+' Return surviving cards after resolution.</footer></article>'
instructions='Print at 100% on A4, single-sided. Cut around each joined pair, fold on the dashed centre line, and glue the backs together. Each pair makes one asset, not two. Cut order cards separately. Keep a reserve token with Grey Petrel.'
style="""
*{box-sizing:border-box}body{margin:24px;background:#e9e5de;color:#202933;font:14px/1.4 Georgia,serif}h1{font-size:24px;margin:0 0 8px}h2{font-size:26px;margin:5px 0}h3{font-size:15px;margin:12px 0 4px}p{margin:6px 0}.page{width:190mm;margin:22px auto;padding:5mm;background:white;box-shadow:0 2px 12px #0002}.pairs{display:grid;gap:5mm}.pair{display:grid;grid-template-columns:1fr 1fr;break-inside:avoid;border:1px solid #546170}.asset{height:122mm;padding:5mm;position:relative;font-size:12px;overflow:visible}.asset+.asset{border-left:1px dashed #777}.owner{text-transform:uppercase;letter-spacing:.08em;font:11px Arial,sans-serif}.traits{font:bold 13px/1.5 Arial,sans-serif;border-block:2px solid #45596b;padding:6px 0}.special{font-size:11px;color:#384b5b}footer{position:absolute;bottom:4mm;left:5mm;right:5mm;font-size:10px;border-top:1px solid #aaa;padding-top:3px}.order-grid{display:grid;grid-template-columns:1fr 1fr;gap:5mm}.order{height:115mm;border:1px solid #546170;padding:5mm;font-size:14px}.order h2{font-size:23px}.paper-line{border-bottom:1px solid #777;margin-top:18px}.screen{max-width:900px;margin:auto}.page>h1{font:14px Arial,sans-serif;margin-bottom:4mm}button{padding:10px 20px;cursor:pointer}@page{size:A4 portrait;margin:10mm}@media print{body{margin:0;background:white}.screen{display:none}.page{width:190mm;margin:0;padding:0;box-shadow:none;break-after:page}.page:last-child{break-after:auto}.asset{height:122mm}a{color:inherit}}
"""
parts=['<!doctype html><html lang="en"><head><meta charset="utf-8"><title>The Void Throne — asset and order cards</title><style>'+style+'</style></head><body><div class="screen"><h1>The Void Throne · asset and order cards</h1><p>'+instructions+'</p><p>Leave cards at home on their chosen face, or take them to their printed council. No faction decision sheet is needed. Traits and Faction Orders are public; exact operational effects stay with the facilitator.</p><button onclick="window.print()">Print cards</button></div>']
items=list(ASSET_CARDS.items())
for start in range(0,len(items),2):
    parts.append('<section class="page"><h1>ASSET CARDS · cut outer line / fold centre line</h1><div class="pairs">')
    for name,c in items[start:start+2]:parts.append('<div class="pair">'+asset_face(name,c,0)+asset_face(name,c,len(c['home'])-1)+'</div>')
    parts.append('</div></section>')
purposes={
 'Relief':'Carry civilian passengers and essential supplies to Sorenne’s Fall. The route must be usable. The voyage can expose its vessel and crew to danger.',
 'Military':'Move the army through the Narrow. The route must be usable. This provides passage for Attack the Anchorage; it does not itself count as combat or civilian relief.',
 'Repair':'Repair navigation and service installations. Other vessels can use the repaired route this round. This does not restore a lost ship or cohort.',
 'Campaign':'Also requires delivered Transport Troops from Navigation. Attack the Sorenne Flag’s anchorage. Combat sustains conditioning but disrupts civilian supplies. A weakened force risks destruction.',
 'Raid':'Seek a Sorenne Flag patrol using local craft. A target may not appear, but the expedition still disrupts traffic. Combat sustains a capable force’s conditioning; a weakened force risks destruction. The same veto bars an independent faction interception.',
 'Guard':'Protect traffic and service installations. Reduce dangers to voyages and support civilian life. This provides neither route repair nor qualifying combat. An effective Warrant uses the defence asset first; do not use it again.'}
items=list(ORDER_TRAITS.items())
for start in range(0,len(items),4):
    parts.append('<section class="page"><h1>COUNCIL ORDER CARDS · cut each card separately</h1><div class="order-grid">')
    for order,trait in items[start:start+4]:
        parts.append('<article class="order"><div class="owner">'+('Navigation and Supply' if order in NAV else 'Security and Government')+'</div><h2>'+esc(LABELS[order])+'</h2><p class="traits">Requires: '+esc(trait)+'</p><p>'+esc(purposes[order])+'</p><p>Place one offered card with this trait beside the order. Use each asset and each order once. A current veto blocks this order.</p><p class="paper-line">Round: ____ &nbsp; Vetoed: □</p><p class="paper-line">Asset used: __________________</p></article>')
    parts.append('</div></section>')
for heading,places in [('OTHER — FACTION ORDER',['Ductus Guild','Janissariat','Ascendant']),('OTHER — COUNCIL ORDER',['Navigation and Supply','Security and Government'])]:
    parts.append('<section class="page"><h1>'+heading+'</h1><div class="order-grid">')
    for place in places:
        parts.append('<article class="order"><div class="owner">'+place+'</div><h2>Other</h2><p>Describe your intended action and outcome. Ask the facilitator to adjudicate it before the phase deadline.</p><p>Other cannot be more efficient than an existing order or bypass necessary cross-faction cooperation. Ownership, traits, single use, vetoes and commitments still apply.</p><p>Place committed assets beside this card. An equivalent printed task still counts towards its once-per-round limit.</p><p class="paper-line">Proposal: ___________________</p><p class="paper-line">Assets: _____________________</p><p class="paper-line">Ruling: _____________________</p></article>')
    parts.append('</div></section>')
parts.append('</body></html>')
(ROOT/'docs/asset-order-cards.html').write_text(''.join(parts),encoding='utf8')
print('Built 5 two-faced assets and 6 trait-based orders and 5 Other cards across 7 print pages.')
