# Working with MMDL

Purpose: use an existing MMDL file as a structured design partner for developing, analysing, comparing, revising, or expanding megagames and adjacent RPG/boardgame designs.

This document is intended as context for an LLM. Follow it when asked to reason from, edit, critique, extend, or compare an MMDL design.

---

## 1. What MMDL is for

MMDL is not just a summary of rules.

It is a design reasoning layer that makes explicit:

- actors and their incentives
- local terms and their generic mechanism types
- resources and state variables
- turn structure and action grammar
- contests and adjudication procedures
- facilitator judgement points
- soft goals and pressure loops
- unresolved ambiguities
- design queries for future work

Use MMDL to reason about the design before rewriting player-facing material.

---

## 2. Operating rules for an LLM

When working with MMDL:

1. **Preserve stable IDs.** Do not rename object IDs unless the user asks or the ID is misleading.
2. **Keep core and local vocabulary separate.** Use core types for reasoning and local terms for player-facing language.
3. **Do not silently fix contradictions.** Add or update `rules_conflict` entries.
4. **Separate facts from inferences.** Mark inferred material with confidence.
5. **Prefer patches over full rewrites.** When making changes, describe what is added, updated, removed, or deprecated.
6. **Track consequences.** For every proposed change, identify affected roles, resources, phases, actions, and materials.
7. **Respect hidden information.** Do not expose private goals, hidden rules, or facilitator-only information in player-facing outputs.
8. **Respect the design intent.** Preserve existing pressure loops unless the task is to change them.
9. **Minimise ontology drift.** Do not invent new core concepts when an existing one works.
10. **Make Control load explicit.** Note when a change adds facilitator judgement or time pressure.

---

## 3. Standard working modes

### 3.1 Summarise the design

Use this when the user asks what the game is, how it works, or what mechanisms matter.

Output:

```markdown
## High-level design summary
## Core play loop
## Main actor groups
## Main resources and state variables
## Main pressure loops
## Main facilitator burdens
## Notable ambiguities
```

Do not list every object unless requested. Focus on mechanism relationships.

### 3.2 Diagnose the design

Use this when the user asks for weaknesses, playtest risks, balance issues, or design critique.

Check:

- agency distribution
- negotiation incentives
- runaway leader risk
- kingmaking risk
- dead-player / dead-role risk
- phase timing pressure
- Control load
- hidden information load
- rules opacity
- action redundancy
- resource scarcity
- victory or goal legibility
- whether the fiction supports the mechanics

Use this format:

```yaml
diagnostic:
  issue:
  affected_objects:
  evidence_from_mmdl:
  likely_table_effect:
  severity: low | medium | high
  possible_fixes:
  recommended_fix:
  tradeoffs:
```

### 3.3 Add a new rule or mechanism

Use this when the user wants a new action, resource, role, faction, crisis, phase, track, or contest.

Process:

1. Identify the intended design function.
2. Find existing mechanisms that already do something similar.
3. Choose the smallest compatible core type.
4. Add the new object using existing field patterns.
5. Update affected resources, phases, roles, triggers, and materials.
6. Add design queries or failure modes.

Use this patch structure:

```yaml
mmdl_patch:
  change_id:
  intent:
  additions:
    - object_type:
      id:
      summary:
  updates:
    - object_id:
      field:
      old:
      new:
  deprecations: []
  affected_objects:
  affected_materials:
  expected_play_effect:
  risks:
  follow_up_questions:
```

### 3.4 Modify an existing rule

Use this when the user wants to rebalance or clarify something.

Do not just rewrite the rule. Compare before and after.

```yaml
rule_change:
  target_object:
  current_function:
  problem:
  proposed_change:
  mechanical_effect:
  fiction_effect:
  affected_roles:
  affected_pressure_loops:
  control_load_change:
  backwards_conversion_notes:
```

### 3.5 Compare two games

Use shared core concepts.

Compare `actor`, `resource`, `state_variable`, `turn_loop`, `phase`, `action`, `contest`, `opportunity`, `soft_goal`, and `pressure_loop` rather than local terms.

Example comparison table:

| Core concept | Game A local term | Game B local term | Design difference |
|---|---|---|---|
| `commitment_token` | Action Card | Initiative Token | A commits every player to one action; B grants battle-starting authority. |
| `state_variable.track` | War Progress | Danelaw | A changes during play; B summarises aftermath. |

### 3.6 Generate design options

Use this when brainstorming.

Options should be structured, not just prose.

```yaml
design_option:
  id:
  summary:
  core_types_used:
  local_terms_needed:
  player_experience:
  mechanical_effect:
  required_changes:
  risks:
  best_when:
```

Offer a small number of distinct options. Make tradeoffs clear.

---

## 4. Analysis lenses

Use these lenses when asked to critique or improve a design.

### 4.1 Agency

Ask:

- Can each role act every turn?
- Does each role have meaningful choices in more than one phase?
- Are some roles dependent on permission from other players?
- Are there fallback actions when diplomacy fails?
- Are there useful non-combat / non-crisis actions?

### 4.2 Pressure loops

Ask:

- What keeps players moving rather than waiting?
- What creates scarcity?
- What makes negotiation necessary?
- What makes conflict tempting?
- What makes restraint tempting?
- What prevents one obvious best move?

Represent pressure loops explicitly:

```yaml
pressure_loop:
  id:
  summary:
  input_pressure:
  player_response:
  state_change:
  new_pressure:
  risks:
```

### 4.3 Resource economy

Ask:

- What resources enter the game each turn?
- What resources leave the game?
- What resources can be traded?
- What resources are convertible?
- Which resources are bottlenecks?
- Does hoarding help or hurt the experience?

### 4.4 Phase load

Ask:

- What must be done in each timed phase?
- Are players likely to know where to be?
- Can facilitators resolve everything in time?
- Are there too many interruptions?
- Does negotiation happen before or after meaningful information is revealed?

### 4.5 Control load

Use this scale:

```yaml
control_load_scale:
  low: Rule is mechanical, visible, and repeatable with little judgement.
  medium: Rule needs occasional interpretation or prompts.
  high: Rule depends on facilitator judgement, negotiation, hidden information, or bespoke consequences.
```

When adding high-Control mechanisms, add guidance.

```yaml
control_guidance:
  decision_point:
  inputs_to_consider:
  default_ruling:
  escalation_ruling:
  avoid:
```

### 4.6 Information structure

Ask:

- What is public?
- What is private to a role?
- What is private to a team?
- What is facilitator-only?
- What is discoverable?
- What information needs a physical component?

Use tags:

```yaml
visibility:
  - public
  - role_private
  - team_private
  - facilitator_only
  - discoverable
  - secretly_mutable
```

### 4.7 Fiction-mechanism alignment

Ask:

- Does the local term make the mechanism intuitive?
- Does the mechanism produce behaviour that fits the fiction?
- Does a historical, political, or genre term hide an abstract mechanism?
- Would a player understand why the rule works this way?

---

## 5. Editing MMDL safely

### 5.1 Preserve the object graph

Before editing, identify all connected objects.

For an action, check:

- phase
- actor scope
- costs
- target types
- resources
- state variables
- control judgement
- opportunities
- role goals
- player-facing materials

For a resource, check:

- source
- sink
- holders
- trade rules
- conversion rules
- scarcity assumptions
- role starting values
- card/reference sheet representation

For a state variable, check:

- who can modify it
- thresholds
- triggers
- upkeep rules
- aftermath metrics
- player visibility
- map/reference representation

### 5.2 Use patch notes

Every substantive edit should include:

```yaml
patch_note:
  summary:
  reason:
  changed_objects:
  unchanged_assumptions:
  design_effect:
  material_updates_needed:
```

### 5.3 Deprecate rather than delete

If a concept might still exist in source files or older materials, mark it deprecated.

```yaml
deprecated_object:
  id:
  replaced_by:
  reason:
  source_materials_still_containing_it:
```

### 5.4 Record unresolved questions

Do not bury uncertainty.

```yaml
open_question:
  id:
  question:
  affects:
  urgency:
  possible_answers:
```

---

## 6. Common LLM tasks and expected outputs

### Task: “Find gaps in this design.”

Return:

```markdown
## Critical gaps
## Medium-risk gaps
## Minor clean-up
## Questions for the designer
```

Each gap should cite affected MMDL objects by ID.

### Task: “Make this role more interesting.”

Return:

```markdown
## Current role function
## Current constraints
## Proposed changes
## New or changed MMDL objects
## Material updates needed
## Risks
```

### Task: “Add safe actions for every department.”

Return:

```markdown
## Design standard
## Action list
## MMDL patch
## Balance notes
## Failure modes
```

### Task: “Convert this into player-facing rules.”

Do not proceed directly from raw MMDL if hidden information is present. First identify visibility.

Return:

```markdown
## Player-facing concepts
## Facilitator-only concepts excluded
## Rules text draft
## Reference sheet changes
```

### Task: “Compare this to another game.”

Use the shared core ontology and produce concept-level comparisons.

---

## 7. Quality checklist for working with MMDL

Before returning an answer:

- [ ] Did you use core concepts for reasoning?
- [ ] Did you preserve local terms for flavour and materials?
- [ ] Did you avoid inventing unnecessary core concepts?
- [ ] Did you identify affected objects?
- [ ] Did you separate rules facts from design proposals?
- [ ] Did you mark uncertainty?
- [ ] Did you consider Control load?
- [ ] Did you consider player-facing vs facilitator-facing visibility?
- [ ] Did you provide a patch or conversion path if changes were made?

---

## 8. Recommended response style

For MMDL work, be concrete.

Prefer:

```markdown
This change affects `resource.silver`, `action.recruit_soldiers`, `phase.maintenance_phase`, and the Saxon Warrior reference sheet.
```

Avoid:

```markdown
This changes the economy a bit.
```

Prefer:

```yaml
risk:
  id: action_becomes_mandatory
  reason: The new action is strictly better than existing recruitment.
  mitigation: Add a once-per-turn limit or require support.
```

Avoid vague design commentary that cannot be converted back into rules.
