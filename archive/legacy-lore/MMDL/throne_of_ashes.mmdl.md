# Throne of Ashes - Shared-Core MMDL Rewrite

Version: draft 0.1  
Generated from workspace Markdown sources on 2026-06-21.

## 1. Source Manifest

```yaml
source_manifest:
  - id: home
    file_name: Home.md
    source_type: game_overview
    use_for: [premise, navigation, public scope]
  - id: rules_reference
    file_name: Rules.md
    source_type: rules_reference
    use_for: [round_structure, currencies, map_control, order_menu, combat, prescience, pillar_aggregation]
  - id: core_mechanics
    file_name: Game/Core Mechanics.md
    source_type: mechanics_summary
    use_for: [round_structure, currencies, influence_income, clarity, readiness, councils, units]
  - id: five_pillars
    file_name: Game/The Five Pillars.md
    source_type: public_rules
    use_for: [pillar_tracks, pillar_feeds, crisis_thresholds]
  - id: charter
    file_name: Game/The Charter of Settlement.md
    source_type: scenario_document
    use_for: [charter_clauses, disputes, ceremony stakes]
  - id: fringe_campaigns
    file_name: Game/Fringe Campaigns.md
    source_type: scenario_document
    use_for: [campaigns, readiness pressure, public political tensions, hidden campaign information]
  - id: crisis_events
    file_name: Game/Crisis Events.md
    source_type: event_file
    use_for: [pillar_crisis_events]
  - id: factions_overview
    file_name: Factions Overview.md
    source_type: faction_index
    use_for: [faction_count, team size, goal tiers, council structure]
  - id: faction_files
    file_name: Factions/*.md
    source_type: faction_briefs
    use_for: [public faction positions, roles, private goals, hidden information]
  - id: setting
    file_name: Setting.md
    source_type: setting_guide
    use_for: [world premise, history, public fiction]
  - id: throne_eternal
    file_name: The Throne Eternal.md
    source_type: setting_guide
    use_for: [public religion, hidden cosmology]
  - id: ascendant
    file_name: The Ascendant.md
    source_type: solo_role_brief
    use_for: [solo role, prescience, clarity, public pressure]
  - id: systems_overview
    file_name: Systems Overview.md
    source_type: map_index
    use_for: [arms, system statistics]
  - id: system_files
    file_name: Systems/*.md
    source_type: location_briefs
    use_for: [system fiction, map tags, hidden location hooks]
  - id: lore_threads
    file_name: Lore/*.md
    source_type: facilitator_only_threads
    use_for: [hidden pattern tracking, Control connection map]
```

## 2. Conversion Notes

```yaml
conversion_notes:
  scope: full_rebuild_from_markdown_sources
  source_quality:
    - rules are compact and playable at menu level
    - setup, component counts, exact starting resources, map adjacency and timing durations are not specified
    - many role goals and hidden threads are facilitator-only or role-private
  visibility_policy:
    - public_player_rules: round structure, currencies, councils, map control, orders, combat summary, Pillars, Charter stakes
    - role_private: individual character goals, conspiracy membership, hidden knowledge
    - facilitator_only: lore thread synthesis, crisis hidden causes, Control-only procedures, some Ascendant transformation details
  inference_policy:
    - inferred structures are marked as inference
    - contradictions and missing procedures are recorded under sections 17 and 18
```

## 3. Game Overview

```yaml
game:
  id: throne_of_ashes
  display_name: Throne of Ashes
  subtitle: A Megagame of Conquest, Conspiracy and Inevitable Ruin
  player_count:
    min: 24
    max: 30
  duration: unspecified
  facilitator_count: unspecified
  premise: >
    The Ascendant has conquered the Settled Dark. At the Seam, ten factions must negotiate,
    amend and sign the Charter of Settlement before the conquest becomes civil war, collapse,
    or something stranger.
  play_experience:
    - asymmetric faction negotiation
    - simultaneous order resolution
    - political and military crisis management
    - hidden role knowledge and conspiracy play
    - soft legacy outcomes rather than a single victory score
  core_design_goal: >
    Force powerful factions to trade immediate advantage against the long-term viability and
    legitimacy of the new empire.
  primary_mechanisms:
    - team_council_order_submission
    - specialty_council_cross_faction_orders
    - map_income_and_control
    - public_pillar_tracks
    - hidden_information_threads
    - charter_amendment_and_final_ceremony
```

## 4. Lexicon: Local Terms to Core Concepts

```yaml
lexicon:
  local_to_core:
    faction: actor.team
    character: actor.player_role
    council: domain.negotiation_body
    Team Council: phase.team_planning
    Specialty Council: phase.cross_faction_policy
    Free Discussion: phase.negotiation
    Ceremony: end_state_procedure
    system: location
    arm: domain.map_region
    void lane: adjacency.route
    Ductus escort: adjacency_permission_override
    Materiel: resource.portable_resource
    Marks: resource.portable_resource
    Influence: resource.portable_resource
    Garrison: state_variable.location_statistic
    Loyalty: state_variable.location_statistic
    Faith: state_variable.location_statistic
    Output: state_variable.location_statistic
    Order: state_variable.location_statistic
    Pillar: state_variable.public_track
    Readiness: state_variable.faction_track
    Clarity: state_variable.private_role_track
    Order Sheet: commitment_record
    Conditional Order: trigger_bound_action
    Charter: authority_token.constitutional_document
    sanctification: authority_token.veto
    Crisis Event: scripted_event.threshold_trigger
    Stability Dividend: scripted_event.positive_threshold
  core_to_local:
    actor.team: faction
    actor.player_role: character
    location: system
    domain.map_region: arm
    adjacency.route: void lane
    resource.portable_resource: [Materiel, Marks, Influence]
    state_variable.public_track: Pillar
    action: order
    contest: combat_or_suppression
```

## 5. Core Object Summary

```yaml
core_object_summary:
  teams: 10
  playable_roles:
    specified: 30
    notes: Ascendant is solo; faction overview permits 24-30 players, implying some roles may be omitted or combined.
  map_regions: 6
  named_systems: 43
  public_pillars: 5
  currencies: 3
  main_order_types:
    team_council: [move, suppress, raid, repair, stabilise, redeploy_garrison]
    specialty_council: [tax, embargo, legislate]
    any_council: [freeform_order]
  hidden_threads:
    - pre_human_presence
    - void_integrity
    - fraying_conditioning
    - charter_legitimacy
```

## 6. Actor Model

```yaml
team:
  - id: ascendant
    core_type: actor.player_role_solo
    display_name: The Ascendant
    player_count: 1
    public_function: supreme authority attempting to turn conquest into legitimate rule
    resources: { influence_income: 8 }
    authorities: [supreme_executive_military_judicial_authority, conditional_orders, diplomacy_council_seat]
    private_tracks: [clarity]
    public_goal_summary: sign the Charter with sanctification and stable Pillars
    visibility: mixed_public_and_role_private

  - id: janissariat_high_command
    core_type: actor.team
    display_name: Janissariat High Command
    player_count: 4
    local_role: conditioned military institution
    resources: { influence_income: 2, readiness_start: 5 }
    public_goal_summary: maintain Readiness and secure constitutional status
    roles: [j1_marshal_commander, j2_strategic_commander, j3_campaign_commander, j4_diplomatic_marshal]
    design_tags: [military_power, readiness_pressure, internal_division]

  - id: ecclesiatum_perpetua
    core_type: actor.team
    display_name: Ecclesiatum Perpetua
    player_count: 4
    local_role: spiritual authority with sanctification veto
    resources: { influence_income: 6 }
    authorities: [charter_sanctification_veto, faith_council_presence]
    public_goal_summary: amend and sanctify the Charter while preserving unity
    roles: [e1_high_prelate, e2_reformist_prelate, e3_diplomatic_legate, e4_inquiry_prelate]
    design_tags: [legitimacy_pressure, veto_power, faction_fracture]

  - id: administratum
    core_type: actor.team
    display_name: Administratum
    player_count: 3
    local_role: record-keeping and administrative continuity
    resources: { influence_income: 4 }
    authorities: [record_certification, classification_authority, charter_drafting_authority]
    public_goal_summary: preserve document authority and the Succession Clause
    roles: [a1_senior_archivist, a2_chief_registrar, a3_court_attache]
    design_tags: [information_control, legal_authority, continuity]

  - id: ductus_guild
    core_type: actor.team
    display_name: Ductus Guild
    player_count: 3
    local_role: exclusive navigation authority
    resources: { influence_income: 2, marks_income_source: open_void_lanes }
    authorities: [open_void_lanes, close_void_lanes, escort_through_closed_lanes]
    public_goal_summary: secure formal response to navigation rights petition before the Ceremony
    roles: [d1_first_navigator, d2_cartographer, d3_trade_liaison]
    design_tags: [infrastructure_monopoly, information_asymmetry, void_pressure]

  - id: house_vethara
    core_type: actor.team
    display_name: House Vethara
    player_count: 3
    philosophy: Authority from continuity and precedent
    resources: { influence_income: 3 }
    public_goal_summary: restore ancestral property rights and perform ceremonial authorities
    roles: [v1_house_speaker, v2_ceremonial_warden, v3_claims_advocate]
    design_tags: [legalism, property_claims, hidden_forgery]

  - id: house_ondrak
    core_type: actor.team
    display_name: House Ondrak
    player_count: 3
    philosophy: Power is the only unfakeable currency
    resources: { influence_income: 3 }
    public_goal_summary: protect property and military interests
    roles: [o1_strategic_liaison, o2_trade_envoy, o3_court_broker]
    design_tags: [military_leverage, transactional_alliance, intelligence]

  - id: house_caelifen
    core_type: actor.team
    display_name: House Caelifen
    player_count: 3
    philosophy: Value is relational and networked
    resources: { influence_income: 3 }
    public_goal_summary: secure trade infrastructure and commercial leverage
    roles: [c1_trade_cartographer, c2_financial_architect, c3_void_trader]
    design_tags: [trade_networks, debt_leverage, anomalous_goods]

  - id: house_mourne
    core_type: actor.team
    display_name: House Mourne
    player_count: 3
    philosophy: The account is always kept
    resources: { influence_income: 3 }
    public_goal_summary: understand collapse timelines and position for the reckoning
    roles: [m1_war_analyst, m2_faith_scholar, m3_void_analyst]
    design_tags: [prediction, observation, crisis_positioning]

  - id: house_aethon
    core_type: actor.team
    display_name: House Aethon
    player_count: 3
    philosophy: The self is a draft, not a declaration
    resources: { influence_income: 3 }
    public_goal_summary: protect augmentation rights and understand the Ascendant's transformation
    roles: [ae1_court_delegate, ae2_research_director, ae3_void_scholar]
    design_tags: [augmentation, research, transformation]
```

```yaml
role_goal_model:
  goal_tiers:
    threshold: achievable by competent play
    ambition: requires skill, leverage or sacrifice
    legacy: qualitative end-state meaning
  visibility:
    faction_goals: team_private
    individual_character_goals: role_private
    conspiracy_goals: role_private_or_cell_private
    public_faction_position: public_player_rules
```

## 7. Spatial / Domain Model

```yaml
domain:
  - id: core
    display_name: The Core
    locations: [the_seam, pale_meridian, meridian_gate, dusk_relay, pallid_registry, covenant_station, vigil_prime, sonders_approach]
  - id: vethis_cluster
    display_name: Vethis Cluster
    locations: [vethis_secundus, vethis_prime, the_narrow, pale_coast, outer_tongue, embrek, cinder_rest, outfall]
  - id: ecclesiatum_vethara_arm
    display_name: Ecclesiatum and Vethara Arm
    locations: [tessavar, tessavar_minor, orreval, vethara_seat, the_cartouche, the_scar, keths_anchorage]
  - id: caelifen_ondrak_arm
    display_name: Caelifen and Ondrak Arm
    locations: [caelifen, ondraks_reach, vorth_station, the_intermediary, meridion, the_lumen, orvath, pale_hook]
  - id: southern_houses_arm
    display_name: Southern Houses Arm
    locations: [aethons_forge, mournes_watch, new_sorenne, callux_prime, sorennes_fall, mournes_deep, the_proving, sorennes_edge]
  - id: outer_meridian_arm
    display_name: Outer Meridian Arm
    locations: [valdric_station, irongate, guild_anchorage, ashen_reach, blind_shore, the_turning, wreck_shoal, the_severance]
```

```yaml
location_statistic_model:
  always_present: Garrison
  optional_statistics: [Loyalty, Output, Faith, Order]
  major_system_marker: "starred systems have three statistics plus Garrison in Systems Overview"
  public_rules_function:
    Garrison: feeds Martial Authority and defends against combat or suppression
    Loyalty: feeds Spiritual Cohesion
    Faith: feeds Spiritual Cohesion
    Output: feeds Economic Flow and income
    Order: feeds Administrative Order
```

```yaml
adjacency:
  id: void_lane_network
  core_type: adjacency.route_network
  local_term: void lane
  controller: ductus_guild
  rules_function:
    - units move along void lanes
    - move cost is 1 Materiel per lane, maximum 3 lanes
    - closed lanes cannot be traversed except by Ductus military ships or escorted units
    - closed lanes reduce economic output for systems whose only connection runs through them
  missing_detail: exact lane graph is not present in source Markdown
```

## 8. Resource and State Model

```yaml
resource:
  - id: materiel
    core_type: resource.portable_resource
    display_name: Materiel
    source: industrial worlds and active trade routes
    primary_use: military orders
    tradable: inferred_true
    lifecycle: generated_from_map_holdings_and_open_lanes, held_by_players, spent_on_submission

  - id: marks
    core_type: resource.portable_resource
    display_name: Marks
    source: trade worlds and open void lanes
    primary_use: maintenance, repair, specialty orders
    tradable: inferred_true
    lifecycle: generated_from_map_holdings_and_open_lanes, held_by_players, spent_on_submission

  - id: influence
    core_type: resource.portable_resource
    display_name: Influence
    source: fixed income per faction per round
    primary_use: political and legislative orders
    fixed_income:
      ascendant: 8
      ecclesiatum_perpetua: 6
      administratum: 4
      house_vethara: 3
      house_ondrak: 3
      house_caelifen: 3
      house_mourne: 3
      house_aethon: 3
      janissariat_high_command: 2
      ductus_guild: 2
```

```yaml
state_variable:
  - id: martial_authority
    core_type: state_variable.public_track
    display_name: Martial Authority
    range: 1-6
    starts_at: 4
    feeds_from: [Garrison]
    primary_stewards: [janissariat_high_command, ascendant]
    threshold_1_event: the_long_return
    threshold_6_event: stability_dividend

  - id: spiritual_cohesion
    core_type: state_variable.public_track
    display_name: Spiritual Cohesion
    range: 1-6
    starts_at: 4
    feeds_from: [Loyalty, Faith]
    primary_stewards: [ecclesiatum_perpetua]
    threshold_1_event: the_withdrawal
    threshold_6_event: stability_dividend

  - id: economic_flow
    core_type: state_variable.public_track
    display_name: Economic Flow
    range: 1-6
    starts_at: 4
    feeds_from: [Output, open_void_lane_count]
    primary_stewards: [noble_houses, ductus_guild]
    threshold_1_event: the_stillness
    threshold_6_event: stability_dividend

  - id: administrative_order
    core_type: state_variable.public_track
    display_name: Administrative Order
    range: 1-6
    starts_at: 4
    feeds_from: [Order]
    primary_stewards: [administratum]
    threshold_1_event: the_corruption
    threshold_6_event: stability_dividend

  - id: void_integrity
    core_type: state_variable.public_track
    display_name: Void Integrity
    range: 1-6
    starts_at: 4
    feeds_from: [open_void_lane_count]
    primary_stewards: [ductus_guild]
    threshold_1_event: the_silence
    threshold_6_event: stability_dividend

  - id: readiness
    core_type: state_variable.faction_track
    display_name: Readiness
    range: 0-6
    starts_at: 5
    holder: janissariat_high_command
    public: true
    effects:
      5-6: no faction can oppose the Janissariat; Ascendant authority is absolute
      3-4: formidable; noble forces become relevant; dissent becomes thinkable
      1-2: political leverage collapses; commanders look for purpose elsewhere
      0: Janissariat ceases to exist as coherent force
    modifies: janissariat_unit_strength
    upkeep: degrades each round unless maintained through external deployment or internal trials

  - id: clarity
    core_type: state_variable.private_role_track
    display_name: Clarity
    range: 0-4
    starts_at: 4
    holder: ascendant
    public: false
    effects: role-private and facilitator-only
    upkeep: degrades with Communion; recovers partly through delegation, rest, ceremonial functions
```

## 9. Turn Loop and Phase Grammar

```yaml
turn_loop:
  id: standard_round
  turn_count: unspecified
  turn_duration: unspecified
  phase_sequence:
    - phase_one_team_councils
    - phase_two_specialty_councils
    - phase_three_free_discussion
    - end_of_round_aggregation
  final_phase: ceremony
```

```yaml
phase:
  - id: phase_one_team_councils
    display_name: Phase One - Team Councils
    function: internal faction planning and order submission
    player_permissions:
      - meet with own faction
      - discuss and decide faction orders
      - submit orders to Control on faction Order Sheet
      - pay costs on submission
    facilitator_tasks:
      - receive payment and order sheets
      - conduct Ascendant Tarot Session
      - hold submitted currencies from filing moment
    outputs: [team_council_orders, conditional_orders]

  - id: phase_two_specialty_councils
    display_name: Phase Two - Specialty Councils
    function: cross-faction policy and delayed resolution
    player_permissions:
      - attend assigned Specialty Councils
      - negotiate and submit Specialty Council orders
    facilitator_tasks:
      - resolve all Phase One orders simultaneously
      - keep resolution invisible until announced
      - collect Specialty Order Sheets
    outputs: [specialty_council_orders, resolved_phase_one_orders]

  - id: phase_three_free_discussion
    display_name: Phase Three - Free Discussion
    function: open negotiation, deals, confrontations and income collection
    player_permissions:
      - move freely
      - negotiate deals
      - collect Materiel, Marks and Influence from Control
      - pursue freeform council actions where permitted
    facilitator_tasks:
      - announce Specialty Council results from previous round
      - make income available
      - answer Control-facing action queries
    outputs: [deals, income_collected, public_announcements]

  - id: end_of_round_aggregation
    display_name: End of Round - Pillar Aggregation
    function: update public stability tracks
    player_permissions: []
    facilitator_tasks:
      - aggregate system statistics upward into Pillars
      - update Pillar board publicly
      - trigger Crisis Event or Stability Dividend if threshold reached

  - id: ceremony
    display_name: The Ceremony
    function: final Charter resolution
    player_permissions:
      - sign, amend, sanctify or withhold assent from the Charter according to authority
    facilitator_tasks:
      - adjudicate final Charter text
      - determine whether sanctification occurs
      - resolve faction legacy outcomes
```

```yaml
specialty_council:
  - id: war_council
    display_name: War Council
    members: [j1, j2, j3, a1, o1, m1]
  - id: commerce_council
    display_name: Commerce Council
    members: [e4, a2, d3, o2, c1, c2]
  - id: diplomacy_council
    display_name: Diplomacy Council
    members: [ascendant, j4, e3, a3, v1, o3, ae1]
  - id: faith_council
    display_name: Faith Council
    members: [e1, e2, v2, v3, m2, ae2]
  - id: void_council
    display_name: Void Council
    members: [d1, d2, c3, m3, ae3]
```

## 10. Action Model

```yaml
action:
  - id: move
    local_name: MOVE
    phase: phase_one_team_councils
    actor_scope: faction_unit_controller
    target_types: [unit, void_lane_route, destination_system]
    cost: 1 Materiel per void lane traversed, maximum 3 Materiel
    requirements:
      - route must use void lanes
      - closed lane requires Ductus military ship escort unless moving Ductus military ships
    effect: relocate unit
    control_load: low

  - id: suppress
    local_name: SUPPRESS
    phase: phase_one_team_councils
    actor_scope: military_units_only
    target_types: [system_statistic]
    cost: 3 Materiel
    procedure: compare acting unit Strength against target system Garrison plus defending military units
    effect: reduce named statistic at target system
    control_load: medium

  - id: raid
    local_name: RAID
    phase: phase_one_team_councils
    actor_scope: military_units_only
    target_types: [system_statistic]
    cost: 3 Materiel
    effect: reduce targeted statistic and pay its value to raiding faction as currency
    control_load: medium
    missing_detail: exact currency type generated from each statistic is not specified

  - id: repair
    local_name: REPAIR
    phase: phase_one_team_councils
    actor_scope: any_unit
    target_types: [damaged_unit]
    cost: 3 Marks
    requirement: unit must be at same system as order-issuing faction
    effect: remove damage from unit
    control_load: low
    missing_detail: number of damage boxes repaired is not specified

  - id: stabilise
    local_name: STABILISE
    phase: phase_one_team_councils
    actor_scope: non_military_units_only
    target_types: [current_system_statistic]
    cost: 3 Marks
    effect: prevent natural decay for one round or recover a small amount
    control_load: medium
    missing_detail: recover amount and decay rule are unspecified

  - id: redeploy_garrison
    local_name: REDEPLOY GARRISON
    phase: phase_one_team_councils
    actor_scope: faction_with_garrison
    target_types: [garrison_unit, adjacent_system]
    cost: 3 Materiel + 3 Marks
    effect: move Garrison to adjacent system; origin Garrison slot is vacated and Martial Authority feed drops until replaced
    control_load: low
    missing_detail: adjacency map not specified

  - id: tax
    local_name: TAX
    phase: phase_two_specialty_councils
    actor_scope: commerce_council_primary
    target_types: [system_output, recipient_faction]
    cost: 3 Influence
    effect: redirect Output income to designated recipient for one round without reducing Output statistic
    control_load: low

  - id: embargo
    local_name: EMBARGO
    phase: phase_two_specialty_councils
    actor_scope: specialty_council
    target_types: [system]
    cost: 4 Influence
    effect: target system Output generates no income for one round
    duration: one_round
    renewal: must be renewed each round
    control_load: low

  - id: legislate
    local_name: LEGISLATE
    phase: phase_two_specialty_councils
    actor_scope: specialty_council_with_relevant_domain
    target_types: [law, pillar_condition, governance_structure, charter_language]
    cost: 4 Influence
    effect: permanent change until reversed by another Legislate order
    control_load: high

  - id: freeform_order
    local_name: Freeform Order
    phase: any_council
    actor_scope: any_council
    target_types: [fictional_objective]
    cost: Control discretion, generally higher than equivalent menu options
    effect: Control-adjudicated and not guaranteed to succeed
    control_load: high

  - id: conditional_order
    local_name: Conditional Order
    phase: phase_one_team_councils
    actor_scope: ascendant_only
    target_types: [trigger_condition, legal_action]
    cost: action_cost_held_by_Control
    limit: maximum 3 held simultaneously
    effect: if trigger fires, order resolves alongside normal order sequence; if not, cost is refunded
    visibility: role_private
    control_load: high
```

## 11. Contest / Conflict Model

```yaml
contest:
  id: combat_or_suppression_resolution
  core_type: contest
  local_term: combat and suppression
  participants:
    attacker: acting military unit
    defender: target system Garrison plus defending military units
  trigger:
    - suppress order against defended statistic
    - raid order against defended statistic
    - unresolved hostile unit presence
  resolution_metric:
    attacker_score: acting unit Strength
    defender_score: Garrison Strength 2 by default plus defending military unit Strength
    janissariat_strength: current Readiness
    ductus_military_ship_strength: 3
  outputs:
    - statistic reduction
    - damage to units
    - unit destruction at full damage track
    - system contested if hostile units remain
  damage_tracks:
    military_unit: 4 boxes
    non_military_unit: 3 boxes
    garrison: inferred_4_boxes_from_units_summary
  tie_rule: unspecified
  casualty_assignment: unspecified
  control_load: medium
```

## 12. Upkeep, Triggers and Opportunities

```yaml
upkeep_rule:
  - id: income_collection
    checked_when: phase_three_free_discussion
    inputs: [map_holdings, open_void_lanes, influence_income_table]
    procedure:
      - Control makes Materiel, Marks and Influence available
      - factions retrieve income at their own initiative
    outputs: [currency_to_factions]
    missing_detail: exact Materiel and Marks values per system/statistic are not specified

  - id: pillar_aggregation
    checked_when: end_of_round
    inputs: [Garrison, Loyalty, Faith, Output, Order, open_void_lane_count]
    procedure:
      - aggregate all system statistics upward to relevant Pillars
      - update public board
    outputs: [pillar_values, crisis_or_stability_triggers]
    control_discretion: medium

  - id: readiness_degradation
    checked_when: end_of_round
    inputs: [external_deployments, internal_trials]
    procedure: Readiness degrades unless maintained
    outputs: [readiness_value]
    missing_detail: exact degradation amount and maintenance order are unspecified

  - id: closed_lane_output_loss
    checked_when: each_round_lane_remains_closed
    inputs: [closed_void_lanes, systems_with_only_connection_through_closed_lane]
    procedure: affected systems begin losing economic output
    outputs: [reduced_output, lower_economic_flow]
    missing_detail: exact rate of output loss is unspecified
```

```yaml
trigger:
  - id: crisis_event_trigger
    condition: any Pillar drops to 1
    checked_when: end_of_round_aggregation
    fires: associated Crisis Event
    player_visibility: public

  - id: stability_dividend_trigger
    condition: any Pillar reaches 6
    checked_when: end_of_round_aggregation
    fires: positive event benefiting whoever stewarded it there
    player_visibility: public
    missing_detail: exact dividend for each Pillar is unspecified

  - id: charter_sanctification
    condition: Ecclesiatum performs sanctification at Ceremony
    checked_when: ceremony
    fires: Charter takes effect if other signatory conditions are satisfied
    failure: if sanctification is withheld, Charter does not take effect
```

```yaml
scripted_event:
  - id: the_long_return
    pillar: martial_authority
    public_summary: Janissariat forces report anomalous campaign behaviour and unsanctioned movement.
  - id: the_withdrawal
    pillar: spiritual_cohesion
    public_summary: Ecclesiatum issues Interdict of Inquiry and calls Charter legitimacy into question.
  - id: the_stillness
    pillar: economic_flow
    public_summary: eighteen void-trade routes stop moving despite navigability.
  - id: the_corruption
    pillar: administrative_order
    public_summary: central archive has been accessed without authorisation from within.
  - id: the_silence
    pillar: void_integrity
    public_summary: the immaterial deep goes quiet and navigation loses its familiar signal.
```

## 13. Goals, Incentives and Pressure Loops

```yaml
soft_goal:
  - id: sign_charter
    holder: all_factions
    generic_goal_type: preserve_or_shape_legitimacy
    local_text: The Charter must be signed today.
    public_or_private: public
    conflicts_with: [faction_specific_amendments, sanctification_veto, succession_clause_dispute]

  - id: preserve_pillars
    holder: all_factions
    generic_goal_type: prevent_system_collapse
    local_text: Keep the empire's Pillars above crisis threshold.
    public_or_private: public

  - id: faction_threshold_ambition_legacy
    holder: each_faction
    generic_goal_type: asymmetric_soft_goal
    public_or_private: team_private
    measurable_signals: [Charter clauses, Pillar states, faction relationships, exposed secrets, final Ceremony outcome]

  - id: binding_surface_goal
    holder: conspiracy_cells
    generic_goal_type: constrain_supreme_authority
    public_or_private: cell_private
    local_text: The Ascendant must be Bound.
```

```yaml
pressure_loop:
  - id: charter_legitimacy_loop
    summary: Every faction needs the Charter, but each needs it amended differently.
    starts_with: disputed Charter draft
    incentivises: negotiation, brinkmanship, veto threats
    creates_pressure_on: Ascendant, Ecclesiatum, Administratum, Noble Houses, Ductus Guild
    failure_modes: deadlock, sanctification failure, overpowered faction settlement

  - id: pillar_decay_crisis_loop
    summary: Local systems and lanes feed public imperial stability; neglect creates severe shared crises.
    starts_with: Pillars at 4
    incentivises: stabilisation, resource spending, council cooperation
    creates_pressure_on: primary stewards of each Pillar
    failure_modes: crisis cascade, players ignore non-private threats

  - id: resource_control_loop
    summary: Map control produces Materiel and Marks, which fund orders that change map control.
    starts_with: factions holding systems and routes
    incentivises: raids, embargoes, movement, Ductus negotiation
    creates_pressure_on: trade factions and military factions
    failure_modes: runaway economic leader, lane closure bottleneck

  - id: readiness_authority_loop
    summary: Janissariat strength supports Ascendant authority, but maintaining Readiness requires morally and politically costly campaigns.
    starts_with: Readiness at 5
    incentivises: campaign resourcing, constitutional negotiation, cover-ups
    creates_pressure_on: Janissariat, Ascendant, Ecclesiatum
    failure_modes: military collapse, sacred order dominance, unresolved campaign scandals

  - id: hidden_thread_discovery_loop
    summary: Secrets are distributed across roles so cooperation can reveal patterns no one can see alone.
    starts_with: private briefs and facilitator-only threads
    incentivises: cross-faction trust, information trading, risky disclosure
    creates_pressure_on: all intelligence-bearing roles
    failure_modes: secrets never surface, secrets surface too late, player confusion without Control prompts
```

## 14. Facilitator / Control Model

```yaml
control_judgement:
  - id: freeform_order_pricing
    used_when: players submit non-menu orders
    decision: price, feasibility, success, impact and consequences
    inputs: [fictional objective, closest menu equivalent, council domain, resources offered, opposition]
    guidance: price higher than equivalent menu options; do not guarantee success
    control_load: high

  - id: legislate_scope
    used_when: Specialty Council uses LEGISLATE
    decision: whether proposed change is within council domain and what permanent effect it has
    inputs: [council membership, Charter text, Pillar condition, faction authorities]
    control_load: high

  - id: simultaneous_resolution
    used_when: Phase One orders resolve during Phase Two
    decision: order interactions, conflicts, contested targets and hidden announcements
    inputs: [all order sheets, paid resources, map state, conditional orders]
    control_load: high

  - id: hidden_thread_connection
    used_when: player actions approach multiple hidden clues
    decision: what information to reveal and to whom
    inputs: [role knowledge, locations investigated, council actions, Control-only thread map]
    guidance: no single player brief has the full pattern; reward cross-faction synthesis
    control_load: high

facilitator_actor:
  - id: control
    display_name: Control
    represented_by: facilitators
    active_when: all phases
    goals:
      - receive and adjudicate orders
      - hold and refund payments
      - manage hidden information boundaries
      - update map, income and Pillars
      - stage crises and Ceremony outcomes
```

## 15. Aftermath / End-State Model

```yaml
end_state:
  id: ceremony_outcome
  display_name: The Ceremony
  measured_from:
    - final Charter text
    - Ecclesiatum sanctification decision
    - signatory assent
    - Pillar values
    - unresolved Crisis Events
    - faction threshold, ambition and legacy goals
  possible_outcomes:
    - Charter signed substantially as drafted
    - Charter signed with amendments
    - Charter signed but legitimacy compromised
    - Charter fails through sanctification veto or signatory breakdown
    - Charter process overtaken by crisis or hidden-thread revelation
  player_visibility: public summary plus private debriefs
```

## 16. Invented or Extended Concepts

```yaml
core_extension:
  - id: negotiation_body_domain
    base_type: domain
    reason: Specialty Councils function as temporary domains where authority, action permissions and cross-faction bargaining are constrained.
    reusable: true

  - id: trigger_bound_action
    base_type: action
    reason: Conditional Orders are paid, hidden, standing actions that fire when a declared trigger occurs.
    reusable: true

  - id: constitutional_document_authority_token
    base_type: authority_token
    reason: The Charter is both scenario object and rules permission structure.
    reusable: true
```

## 17. Rules Conflicts and Ambiguities

```yaml
missing_rule:
  - id: map_adjacency_missing
    missing_procedure: exact void lane network and adjacency between systems
    why_it_matters: MOVE and REDEPLOY GARRISON require lane or adjacent-system legality
    likely_table_failure: Control must improvise movement permissions

  - id: starting_resources_missing
    missing_procedure: starting Materiel, Marks, units, garrisons and map control values
    why_it_matters: players cannot begin without economic and military setup
    likely_table_failure: first-round orders cannot be costed consistently

  - id: materiel_marks_income_formula_missing
    missing_procedure: exact income values from Output, industrial worlds, trade worlds and open void lanes
    why_it_matters: economy is central to orders and map incentives
    likely_table_failure: Control must invent income and may distort balance

  - id: combat_margin_missing
    missing_procedure: how Strength comparison converts into damage, statistic reduction or failed action
    why_it_matters: combat and suppression are core military procedures
    likely_table_failure: inconsistent battle outcomes

  - id: turn_count_duration_missing
    missing_procedure: number of rounds, real-time phase durations and game-hour definition
    why_it_matters: Clarity references game-hour decisions and player pacing depends on round timing
    likely_table_failure: uneven pressure and unclear endgame timing

  - id: stability_dividend_missing
    missing_procedure: exact benefit when a Pillar reaches 6
    why_it_matters: players need incentives to improve rather than merely protect Pillars
    likely_table_failure: stability gains feel cosmetic

  - id: specialty_order_timing_conflict
    missing_procedure: Rules.md says Specialty Council orders are submitted in Phase Two and Phase Three announces previous round results; Core Mechanics says Specialty Council orders resolve at the start of the next Phase One.
    why_it_matters: timing affects counterplay, announcement and order planning
    recommended_resolution: treat Specialty orders as submitted in Phase Two, locked until next round, and announced in Phase Three after resolution unless Control needs a hidden result.
    needs_designer_decision: true
```

## 18. Design Queries for Future LLM Work

```yaml
design_query:
  - id: define_setup_pack
    question: What are the starting units, garrisons, map control, void lane states and currency totals for each faction?
    urgency: high

  - id: formalise_income
    question: How exactly do Output, industrial worlds, trade worlds and open lanes convert into Materiel and Marks?
    urgency: high

  - id: formalise_combat
    question: What does each margin of Strength comparison do, and who assigns damage?
    urgency: high

  - id: calibrate_control_load
    question: Which freeform and legislative requests should Control usually accept, price upward, delay or reject?
    urgency: medium

  - id: player_guide_visibility
    question: Should the public player guide mention that conspiracy play exists, or should that remain entirely role-private?
    urgency: medium

  - id: pillar_dividends
    question: What positive event or concrete benefit should each Pillar grant at 6?
    urgency: medium

  - id: ceremony_procedure
    question: What exact authorities are required for Charter execution, amendment, signature and sanctification?
    urgency: high
```

