# MMDL Shared Core Concepts v0.2

This file defines a shared Megagame Mechanism Description Language (MMDL) vocabulary for rewriting different megagames in a comparable form. It deliberately separates **generic mechanism concepts** from **game-specific terms**.

The core rule is:

```yaml
naming_principle:
  core_type_names: generic
  local_terms: preserved as aliases
  object_ids: game_specific_but_normalised
  player_facing_text: uses the game's own terminology
  analysis_tags: generic and reusable
```

This lets one design use `territory.local_term: shire`, another use `territory.local_term: colony`, and a third use `territory.local_term: star system`, while the LLM can still compare them as territories.

---

## 1. Top-level objects

```yaml
core_object_types:
  game:
    definition: The whole playable design.
  source_manifest:
    definition: The files and artefacts used to reconstruct the design.
  lexicon:
    definition: Mapping between generic MMDL terms and local game terms.
  design_goal:
    definition: What the design is trying to make players do, feel, negotiate over, or worry about.
  rules_conflict:
    definition: A contradiction, ambiguity, or variant rule that should not be silently normalised.
  design_query:
    definition: A reusable analysis question for an LLM or designer.
```

---

## 2. Actors and social structure

```yaml
actor:
  definition: Any entity capable of taking action, holding resources, pursuing goals, making deals, or being represented by Control.
  subtypes:
    player_role: A playable individual brief.
    team: A group of players with a shared identity, table, or broad objective.
    faction: A political, military, corporate, religious, or cultural power bloc.
    facilitator_actor: A Control-played entity with agency in the fiction.
    external_actor: A non-played entity accessed through special actions or facilitator negotiation.

role:
  definition: A playable identity with goals, resources, authority, and constraints.
  common_fields:
    - id
    - display_name
    - team
    - faction_affiliations
    - local_title
    - public_brief
    - private_goals
    - starting_resources
    - authorities
    - constraints
    - useful_actions
    - design_tags

allegiance:
  definition: A formal or informal relationship between actors that modifies permissions, support, legitimacy, obligations, or income.
  examples:
    - liege/vassal
    - corporate loyalty
    - political patronage
    - military alliance
    - covert sympathy
```

---

## 3. Spatial and state model

```yaml
domain:
  definition: A physical or conceptual area of play where actions are placed, resolved, or discussed.
  local_examples:
    Crisis_Mars: map
    Raven_Banner: regional map table or team table

location:
  definition: A place or node within a domain that can be controlled, attacked, developed, damaged, supported, or used as a target.
  local_examples:
    Crisis_Mars: orbital zone, planet, moon, trade route area, station
    Raven_Banner: shire

site:
  definition: A smaller feature inside a location that can produce resources, be defended, raided, destroyed, rebuilt, or carry symbolic meaning.
  local_examples:
    Crisis_Mars: starport, moonbase, terraforming station, asteroid station
    Raven_Banner: farm, town, church, castle, missionary

adjacency:
  definition: A permission structure determining what can affect what.
  common_modes:
    - physical_adjacent
    - route_connected
    - ship_connected
    - support_connected
    - politically_connected

state_variable:
  definition: A persistent mechanical quantity that records world state.
  subtypes:
    score: A numeric value without inherent ordered spaces.
    track: A numeric or banded value with directional spatial meaning.
    marker: A named on/off or categorical state.
    aftermath_metric: A final-state measure used to summarise the world after play.
```

---

## 4. Resources and tokens

```yaml
resource:
  definition: Anything held, spent, loaned, consumed, accumulated, or converted.
  subtypes:
    portable_resource: Held by a player or team and traded/spent directly.
    abstract_resource: A map score or value that can be moved between systems.
    unit_resource: A countable capability such as soldiers, ships, fleets, or agents.
    soft_currency: A pacing/agency resource such as momentum.

commitment_token:
  definition: A once-per-cycle or limited agency marker that commits an actor to a location, action, or conflict.
  local_examples:
    Crisis_Mars: action card
    Raven_Banner: initiative token

authority_token:
  definition: A token, title, claim, or state that grants permission or legitimacy.
  local_examples:
    Crisis_Mars: Senate Control category, UN mandate, shipping control
    Raven_Banner: crown claim, liege relationship, local support
```

---

## 5. Turn, phase, action and resolution model

```yaml
turn_loop:
  definition: The repeated real-time structure of play.
  fields:
    - turn_count
    - turn_duration
    - phase_sequence
    - scripted_events
    - upkeep_points

phase:
  definition: A timed segment with a specific action grammar.
  common_phase_functions:
    - team_planning
    - negotiation
    - commitment
    - conflict_resolution
    - economy_upkeep
    - freeform_action
    - debrief

action:
  definition: A player-initiated attempt to change the state of the game.
  fields:
    - id
    - local_name
    - actor_scope
    - phase
    - target_types
    - cost
    - requirements
    - procedure
    - effect
    - counterplay
    - control_load
    - design_intent

contest:
  definition: A resolution procedure where two or more actors' intentions oppose each other.
  local_examples:
    Crisis_Mars: rare opposed action or war-progress competition via scores
    Raven_Banner: battle / clash

resolution_metric:
  definition: A number, band, die roll, or qualitative judgement used to convert intention into effect.
  local_examples:
    Crisis_Mars: impact and effect band
    Raven_Banner: battle score and casualties

control_judgement:
  definition: A facilitator decision converting fictional intent into difficulty, relevance, cost, consequences, or state change.
```

---

## 6. Triggers, upkeep and opportunity

```yaml
trigger:
  definition: A condition that causes another rule or facilitator prompt to fire.
  examples:
    - threshold crossed
    - end of turn
    - control difference exceeds margin
    - actor lacks support
    - trade route damaged
    - character wounded too many times

upkeep_rule:
  definition: A scheduled rule that updates the world, income, opportunities, penalties, or end-state metrics.

opportunity:
  definition: A Control-presented decision created by a trigger. It often hides exact mechanical consequences from players.

scripted_event:
  definition: A pre-authored event, news item, escalation, or timed intervention.
```

---

## 7. Goals, incentives and analysis

```yaml
soft_goal:
  definition: A role or faction objective not reducible to a single score.

pressure_loop:
  definition: A repeating incentive structure that drives play.
  examples:
    - resource scarcity creates negotiation
    - military success creates legitimacy
    - public conflict creates escalation
    - support unlocks income

failure_mode:
  definition: A way the mechanism can fail at the table.
  examples:
    - player has no agency
    - runaway leader
    - Control overload
    - opaque scoring
    - diplomacy becomes irrelevant
    - local term hides generic mechanism
```

---

## 8. Recommended object template

```yaml
object_template:
  id: stable_snake_case_id
  core_type: generic_mmdl_type
  local_term: game_specific_name_for_this_type
  display_name: player_facing_name
  rules_function: what_it_does_mechanically
  fiction_function: why_it_makes_sense_in_the_setting
  state_fields: []
  interactions: []
  design_tags: []
  control_notes: []
```

---

## 9. Lexicon pattern

Each game should start with a lexicon that maps local concepts onto shared concepts.

```yaml
lexicon_template:
  local_to_core:
    Local Term: core_type
  core_to_local:
    core_type: Local Term
  notes:
    - Terms can be many-to-one.
    - A local term should not become a new core term unless it appears across multiple designs.
    - If a local term carries important fictional meaning, keep it as `local_term`, `display_name`, or `design_tag`.
```
