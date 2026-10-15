import sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from void_throne.assets import ASSET_CARDS,ORDER_TRAITS
from void_throne.orders_v04 import orders
from void_throne.current_session import Session
from void_throne.multiplayer import Multiplayer

class AssetTraitsTests(unittest.TestCase):
 def test_requirements_follow_traits_not_name_whitelists(self):
  # A replacement's capabilities, not its name, make it eligible.
  with patch.dict(ASSET_CARDS,{'Test transport':{'traits':['Civilian Transport']}}):
   self.assertEqual(orders([{'order':'Relief','asset':'Test transport'}],'navigation')[0]['asset'],'Test transport')
   with self.assertRaisesRegex(ValueError,'Troop Transport'):
    orders([{'order':'Military','asset':'Test transport'}],'navigation')
 def test_existing_matrix_and_single_use_are_preserved(self):
  expected={'Relief':{'Wayfarer','Lantern','Grey Petrel'},'Military':{'Wayfarer','Grey Petrel'},'Repair':{'Lantern'},'Campaign':{'Spear'},'Raid':{'Spear'},'Guard':{'Vigil'}}
  for order,eligible in expected.items():
   for asset in ASSET_CARDS:
    domain='navigation' if order in ('Relief','Military','Repair') else 'military'
    if asset in eligible:orders([{'order':order,'asset':asset}],domain)
    else:
     with self.assertRaises(ValueError):orders([{'order':order,'asset':asset}],domain)
  with self.assertRaisesRegex(ValueError,'only once'):
   orders([{'order':'Relief','asset':'Wayfarer'},{'order':'Military','asset':'Wayfarer'}],'navigation')
 def test_both_home_faces_and_public_projection(self):
  self.assertEqual(ASSET_CARDS['Spear']['home'],['Stand down','Raid'])
  self.assertEqual(ASSET_CARDS['Grey Petrel']['home'],['Keep','Tender cover'])
  game=Session();peer=Multiplayer().view('GN')
  self.assertEqual(peer['asset_cards'],game.public()['asset_cards'])
  self.assertEqual(peer['order_traits'],ORDER_TRAITS)
  peer['asset_cards']['Lantern']['traits'].clear()
  self.assertIn('Civilian Transport',ASSET_CARDS['Lantern']['traits'])
