"""Public asset cards and capability requirements; no concealed resolution math."""
ASSET_CARDS = {'Wayfarer': {'owner': 'Guild',
              'council': 'Navigation and Supply',
              'traits': ['Civilian Transport', 'Troop Transport'],
              'home': ['Trade'],
              'home_text': ['Fulfil the Guild’s commercial contract. A missed contract is lost for '
                            'this month; the surviving ship returns. An unsafe or exposed passage '
                            'can halt the voyage or cost you the ship.']},
 'Lantern': {'owner': 'Guild',
             'council': 'Navigation and Supply',
             'traits': ['Civilian Transport', 'Route Engineering'],
             'home': ['Maintain'],
             'home_text': ['Carry out routine upkeep of the Narrow. This helps the route, but is '
                           'less thorough than the council repair operation. It does not restore a '
                           'lost asset.']},
 'Spear': {'owner': 'Janissariat',
           'council': 'Security and Government',
           'traits': ['Assault', 'Patrol Craft'],
           'home': ['Stand down', 'Raid'],
           'home_text': ['Keep the cohort out of operations. Standing down does not sustain its '
                         'conditioning or restore a lost cohort.',
                         'Seek a Sorenne Flag patrol independently. No other party’s permission is '
                         'needed, but a veto still bars the operation and Charter duties still '
                         'apply. The enemy may not appear; the expedition disrupts civilian '
                         'traffic. A weakened cohort risks destruction.']},
 'Vigil': {'owner': 'Janissariat',
           'council': 'Security and Government',
           'traits': ['Passage Defence'],
           'home': ['Home'],
           'home_text': ['Defend the army’s institutional bases. This meets the duty under '
                         'Military autonomy. It provides neither passage protection nor qualifying '
                         'combat.']},
 'Grey Petrel': {'owner': 'Ascendant',
                 'council': 'Navigation and Supply',
                 'traits': ['Civilian Transport', 'Troop Transport'],
                 'home': ['Keep', 'Tender cover'],
                 'home_text': ['Retain the contracted service for later. The reserve token adds no '
                               'settlement weight.',
                               'Prepare to rescue Lantern’s navigators from the specific '
                               'first-month civilian passage threat. Spend the reserve only if '
                               'this rescue triggers. This is not general passage protection and '
                               'has no second-month trigger.']}}

ORDER_TRAITS = {'Relief': 'Civilian Transport',
 'Military': 'Troop Transport',
 'Repair': 'Route Engineering',
 'Campaign': 'Assault',
 'Raid': 'Patrol Craft',
 'Guard': 'Passage Defence'}


def supports(asset, order):
    return ORDER_TRAITS.get(order) in ASSET_CARDS.get(asset, {}).get("traits", [])
