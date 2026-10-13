# Turning Game Rules into MMDL

Purpose: convert existing megagame, boardgame, RPG, or hybrid game materials into **Megagame Mechanism Description Language (MMDL)** so an LLM can reason about the design consistently.

This document is intended as context for an LLM. Follow it when asked to rewrite game rules, guides, cards, maps, role briefs, facilitator notes, spreadsheets, or other game files into MMDL.

---

## 1. Primary objective

The goal is not to make the game executable.

The goal is to make the game **mechanically explicit, comparable, analysable, and editable** while preserving its fiction and player-facing terminology.

MMDL should help an LLM answer questions such as:

- What are the actual mechanisms in this design?
- Which mechanisms create player agency?
- Which mechanisms create negotiation pressure?
- Which rules depend on facilitator judgement?
- Which local terms are just fictional names for reusable concepts?
- Which systems are under-specified, contradictory, or missing?
- What would change if a rule, role, resource, phase, or objective were altered?

---

## 2. Core principle: generic structure, local vocabulary

Always separate:

1. **Core MMDL concept** — the generic reusable mechanism type.
2. **Local term** — the game-specific word used by the original design.
3. **Display name** — the exact player-facing name.
4. **Fiction function** — why the thing makes sense in the setting.
5. **Rules function** — what it does mechanically.

Do not let game-specific words become core ontology unless they are reusable across many games.

Bad:

```yaml
shire:
  id: wiltshire
```

Good:

```yaml
location:
  id: wiltshire
  core_type: location
  local_term: shire
  display_name: Wiltshire
```

Bad:

```yaml
war_progress:
  id: war_progress
```

Better:

```yaml
state_variable:
  id: war_progress
  core_type: state_variable.track
  local_term: War Progress
  display_name: War Progress
```

---

## 3. Minimum shared core concepts

Use these core terms unless a project-specific MMDL core file says otherwise.

```yaml
core_object_types:
  - game
  - source_manifest
  - lexicon
  - actor
  - role
  - faction
  - team
  - facilitator_actor
  - external_actor
  - allegiance
  - domain
  - location
  - site
  - adjacency
  - resource
  - state_variable
  - commitment_token
  - authority_token
  - turn_loop
  - phase
  - action
  - contest
  - resolution_metric
  - control_judgement
  - trigger
  - upkeep_rule
  - opportunity
  - scripted_event
  - soft_goal
  - pressure_loop
  - failure_mode
  - rules_conflict
  - design_query
```

If a game contains something that does not fit this list, prefer to model it as one of these with a specific `local_term`, `subtype`, or `design_tag` before inventing a new core concept.

Only invent a new core concept when all of the following are true:

- It cannot be cleanly represented by an existing core type.
- It is mechanically important.
- It is likely to recur across multiple megagames or game designs.
- You define it clearly in an `invented_concepts` or `core_extension` section.

---

## 4. Input handling

Game materials may include:

- player guides
- facilitator guides
- role briefs
- cards
- maps
- reference sheets
- spreadsheets
- print-and-play files
- playtest notes
- designer comments
- prior MMDL files

First build a `source_manifest`.

```yaml
source_manifest:
  - id: player_guide
    file_name: Example Player Guide.pdf
    source_type: player_guide
    use_for:
      - public rules
      - turn structure
      - setting overview
      - player-facing terminology
  - id: facilitator_guide
    file_name: Example Facilitator Guide.pdf
    source_type: facilitator_guide
    use_for:
      - hidden rules
      - setup
      - adjudication guidance
      - facilitator actors
  - id: cards
    file_name: Example Cards.pdf
    source_type: card_file
    use_for:
      - action text
      - resource definitions
      - repeated components
```

When information comes from one file but conflicts with another, do not silently merge them. Record a `rules_conflict`.

---

## 5. Output structure

A complete MMDL rewrite should use this order unless instructed otherwise.

```markdown
# <Game Name> — Shared-Core MMDL Rewrite

## 1. Source Manifest
## 2. Conversion Notes
## 3. Game Overview
## 4. Lexicon: Local Terms to Core Concepts
## 5. Core Object Summary
## 6. Actor Model
## 7. Spatial / Domain Model
## 8. Resource and State Model
## 9. Turn Loop and Phase Grammar
## 10. Action Model
## 11. Contest / Conflict Model
## 12. Upkeep, Triggers and Opportunities
## 13. Goals, Incentives and Pressure Loops
## 14. Facilitator / Control Model
## 15. Aftermath / End-State Model
## 16. Invented or Extended Concepts
## 17. Rules Conflicts and Ambiguities
## 18. Design Queries for Future LLM Work
```

Some sections may be empty for simpler games, but do not delete them unless asked. Empty sections make missing design areas visible.

---

## 6. Conversion workflow

### Step 1: Identify the game contract

Summarise the basic contract of play.

```yaml
game:
  id: stable_snake_case_game_id
  display_name: Exact Game Title
  player_count:
    min:
    max:
  duration:
  facilitator_count:
  premise:
  play_experience:
  core_design_goal:
  primary_mechanisms:
```

Capture:

- player count
- duration
- facilitator count
- scenario premise
- intended experience
- main sources of conflict
- main sources of cooperation
- whether there is a clear winner, soft goals, or collective narrative outcome

### Step 2: Build the lexicon

Map local game terms to shared concepts.

```yaml
lexicon:
  local_to_core:
    Action Card: commitment_token
    Map: domain
    Shire: location
    Settlement: site
    Crown: authority_token
    War Support: state_variable.score
    War Progress: state_variable.track
    Battle: contest
    Clash: contest.subprocedure
  core_to_local:
    location:
      - Shire
    commitment_token:
      - Action Card
      - Initiative Token
```

Use local terms in `display_name` and player-facing summaries, but use core terms in structural fields.

### Step 3: Extract actors

Use `actor`, `team`, `faction`, `role`, `facilitator_actor`, and `external_actor`.

```yaml
actor:
  id:
  core_type: actor.team
  local_term:
  display_name:
  player_facing: true
  members:
  shared_goals:
  resources:
  authorities:
  vulnerabilities:
  design_tags:
```

For roles:

```yaml
role:
  id:
  core_type: actor.role
  local_title:
  display_name:
  team:
  faction_affiliations:
  public_brief_summary:
  private_goals:
  starting_resources:
  permissions:
  constraints:
  useful_actions:
  tensions:
  design_tags:
```

Do not over-compress roles. Megagame roles are often where the design lives.

### Step 4: Extract domains, locations, and sites

Use `domain` for large play areas or tables, `location` for controllable/targetable places, and `site` for smaller features inside locations.

```yaml
domain:
  id:
  core_type: domain
  local_term:
  display_name:
  contains_locations:
  state_variables:
  associated_facilitator:
  phase_use:
```

```yaml
location:
  id:
  core_type: location
  local_term:
  display_name:
  domain:
  controller:
  steward_or_manager:
  support:
  sites:
  adjacency:
  rules_function:
  fiction_function:
```

```yaml
site:
  id:
  core_type: site
  local_term:
  display_name:
  location:
  produces:
  can_be_defended:
  can_be_destroyed:
  symbolic_tags:
```

### Step 5: Extract resources, state variables, and tokens

Distinguish resources that players hold from values written on the map.

```yaml
resource:
  id:
  core_type: resource.portable_resource
  local_term:
  display_name:
  holder:
  tradable:
  spendable:
  recoverable:
  effect:
  lifecycle:
```

```yaml
state_variable:
  id:
  core_type: state_variable.score
  local_term:
  display_name:
  domain:
  current_value:
  min:
  max:
  thresholds:
  modified_by:
  affects:
```

```yaml
commitment_token:
  id:
  core_type: commitment_token
  local_term:
  display_name:
  holder:
  phase_used:
  commitment_target:
  recovered_when:
  design_function:
```

```yaml
authority_token:
  id:
  core_type: authority_token
  local_term:
  display_name:
  holder:
  grants:
  contested_by:
  transfer_rule:
```

### Step 6: Extract turn loop and phases

Record what each phase permits and forbids.

```yaml
turn_loop:
  turn_count:
  turn_duration:
  phase_sequence:
    - id: team_phase
      duration:
      function:
      player_permissions:
      facilitator_tasks:
      outputs:
```

For each phase, identify:

- who may talk to whom
- what players physically do
- what tokens/cards are placed or reclaimed
- what resources are gained/spent
- what facilitators announce or adjudicate
- whether negotiation, commitment, action declaration, or resolution occurs

### Step 7: Extract actions

An action is any player-initiated procedure with a cost, requirement, target, and effect.

```yaml
action:
  id:
  core_type: action
  local_name:
  phase:
  actor_scope:
  target_types:
  cost:
  requirements:
  procedure:
  effect:
  counterplay:
  control_load:
  design_intent:
  failure_modes:
```

If players may invent actions freely, model that as a generic action grammar.

```yaml
action:
  id: freeform_action_resolution
  core_type: action.freeform
  local_name: Player Action
  phase: action_phase
  procedure:
    - actor states fictional objective
    - facilitator judges relevance, difficulty and effect
    - actor spends resources or adds allies if allowed
    - resolution metric is calculated
    - effect band determines scale of result
  control_load: high
```

### Step 8: Extract contests and resolution procedures

A `contest` resolves opposed intentions.

```yaml
contest:
  id:
  core_type: contest
  local_term:
  display_name:
  participants:
  trigger:
  procedure:
  resolution_metric:
  tie_rule:
  outputs:
  casualties_or_costs:
  state_changes:
  aftermath_effects:
```

Include subprocedures when needed.

```yaml
contest_subprocedure:
  id: clash
  parent_contest: battle
  local_term: Clash
  participants: two opposing players
  procedure:
    - select tactic
    - add bonuses
    - roll leadership die
    - compare scores
    - resolve casualties
```

### Step 9: Extract triggers, upkeep, and opportunities

Use `trigger` for conditions and `upkeep_rule` for scheduled changes.

```yaml
trigger:
  id:
  condition:
  checked_when:
  fires:
```

```yaml
upkeep_rule:
  id:
  checked_when:
  inputs:
  procedure:
  outputs:
  control_discretion:
```

```yaml
opportunity:
  id:
  trigger:
  offered_to:
  choice_structure:
  player_visibility:
  likely_effects:
  hidden_effects:
  design_intent:
```

If the original rules tell facilitators not to reveal mechanical consequences, record that explicitly.

### Step 10: Extract goals, incentives and pressure loops

Goals in megagames are often soft, contradictory, and narrative. Do not turn them into victory points unless the original game does.

```yaml
soft_goal:
  id:
  holder:
  local_text:
  generic_goal_type:
  public_or_private:
  measurable_signals:
  conflicts_with:
  supports:
```

```yaml
pressure_loop:
  id:
  summary:
  starts_with:
  incentivises:
  creates_pressure_on:
  likely_player_behaviour:
  failure_modes:
```

Examples of generic goal types:

```yaml
generic_goal_types:
  - preserve_faction
  - expand_control
  - maintain_legitimacy
  - gain_independence
  - prevent_independence
  - enrich_actor
  - protect_project
  - undermine_enemy
  - survive_collapse
  - gain_recognition
  - preserve_religion_or_culture
  - keep_options_open
```

### Step 11: Extract facilitator model

Megagame rules often rely on human facilitation. Make that explicit.

```yaml
control_judgement:
  id:
  used_when:
  decision:
  inputs:
  guidance:
  risks:
  consistency_notes:
```

```yaml
facilitator_actor:
  id:
  display_name:
  represented_by:
  active_when:
  goals:
  resources:
  negotiation_style:
  limits:
```

Do not hide control load. If a rule requires judgement, mark it.

```yaml
control_load:
  rating: low | medium | high
  reason:
```

### Step 12: Extract aftermath and end state

Use `aftermath_metric` for scores that summarise the world after play.

```yaml
aftermath_metric:
  id:
  display_name:
  local_term:
  measured_from:
  thresholds:
  interpretation:
  player_visibility:
```

Record both mechanical end-state calculations and narrative interpretation.

---

## 7. Handling uncertainty and contradiction

Never resolve contradictions silently.

Use `rules_conflict`.

```yaml
rules_conflict:
  id:
  topic:
  source_a:
  source_b:
  conflict_summary:
  possible_resolutions:
  recommended_resolution:
  confidence:
  needs_designer_decision: true
```

Use `inference` for reasonable reconstruction not explicitly stated.

```yaml
inference:
  id:
  inferred_from:
  assumption:
  confidence:
  risk_if_wrong:
```

Use `missing_rule` when the design appears to require a procedure that is absent.

```yaml
missing_rule:
  id:
  missing_procedure:
  why_it_matters:
  likely_table_failure:
  suggested_questions:
```

---

## 8. Design tags

Use generic tags to help cross-game reasoning.

```yaml
design_tags:
  agency:
    - freeform_action
    - constrained_action
    - hidden_information
    - negotiated_permission
  pressure:
    - resource_scarcity
    - time_pressure
    - escalation_pressure
    - legitimacy_pressure
    - territorial_pressure
  conflict:
    - direct_military
    - indirect_political
    - economic_sabotage
    - social_diplomacy
  control:
    - low_control_load
    - medium_control_load
    - high_control_load
    - requires_adjudication
  information:
    - public_state
    - private_goal
    - hidden_rule
    - facilitator_secret
```

---

## 9. Quality checklist

Before finishing, check:

- [ ] Every game-specific term is mapped to a generic core concept.
- [ ] Every role has goals, resources, permissions, and constraints where available.
- [ ] Every phase says what players can do and what facilitators do.
- [ ] Every resource has a lifecycle: gained, held, spent, traded, recovered, or lost.
- [ ] Every map/domain has its state variables and upkeep rules.
- [ ] Every contest has a trigger, procedure, resolution metric, outputs, and tie rule if relevant.
- [ ] Every facilitator judgement point is marked.
- [ ] Every contradiction is recorded as a `rules_conflict`.
- [ ] Every invented concept is defined and justified.
- [ ] Player-facing local terms are preserved as aliases, not erased.
- [ ] The output supports future editing, not just summarisation.

---

## 10. Recommended final response after creating MMDL

When returning the MMDL to a user, summarise:

- files used
- major MMDL concepts introduced
- major ambiguities found
- any assumptions or inferred structures
- link to the generated `.md` file if one was created

Do not claim full certainty if source files are incomplete, contradictory, truncated, or visually complex.
