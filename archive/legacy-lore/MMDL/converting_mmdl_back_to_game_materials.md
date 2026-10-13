# Converting MMDL Back into Updated Game Materials

Purpose: turn an MMDL design, or an MMDL patch, back into practical game materials: player guides, facilitator guides, reference sheets, role briefs, cards, maps, spreadsheets, and playtest notes.

This document is intended as context for an LLM. Follow it when asked to update game materials from MMDL.

---

## 1. Primary objective

The objective is to convert structured design changes into usable player-facing and facilitator-facing artefacts without losing:

- local terminology
- hidden information boundaries
- role-specific incentives
- facilitator guidance
- physical component requirements
- timing and phase clarity
- source-of-truth consistency

MMDL is the design layer. Game materials are the delivery layer.

Do not copy MMDL fields directly into player materials unless the user explicitly wants technical material.

---

## 2. Core conversion rule

When converting back:

```yaml
conversion_principle:
  core_type: used internally for reasoning
  local_term: used in player-facing rules
  display_name: used in headings, cards, maps and briefs
  fiction_function: used in setting explanation and role motivation
  rules_function: converted into clear procedures and reference text
  control_notes: moved only to facilitator materials
  private_goals: moved only to the relevant role brief
```

Example:

```yaml
MMDL:
  core_type: location
  local_term: shire
  display_name: Wiltshire
```

Player-facing output:

> Wiltshire is a shire. It can be controlled, stewarded, defended, raided, and used to collect income.

Not:

> Wiltshire is a `location` object.

---

## 3. Visibility categories

Before writing materials, classify every MMDL object or field.

```yaml
visibility:
  public_player_rules:
    definition: Safe for all players.
  role_private:
    definition: Only for a named role or role type.
  team_private:
    definition: Only for one team/faction.
  facilitator_only:
    definition: Control procedure, hidden trigger, adjudication guidance, or secret NPC goal.
  production_only:
    definition: Component layout, file naming, printing, spreadsheet, or versioning information.
```

Never expose facilitator-only or private role information in public rules.

---

## 4. Material mapping

Use this mapping when deciding where MMDL content should go.

| MMDL content | Player Guide | Facilitator Guide | Reference Sheet | Role Brief | Card | Map | Spreadsheet |
|---|---:|---:|---:|---:|---:|---:|---:|
| `game` overview | Yes | Yes | No | Maybe | No | No | Maybe |
| `lexicon` | Translated, not shown | Maybe | No | No | No | No | No |
| `turn_loop` | Yes | Yes | Yes | Maybe | No | No | Maybe |
| `phase` permissions | Yes | Yes | Yes | Maybe | No | No | Maybe |
| `action` public procedure | Yes | Yes | Yes | Role-specific if needed | Maybe | No | Yes |
| `action` hidden consequence | No | Yes | No | No, unless private | No | No | Maybe |
| `contest` procedure | Yes | Yes | Yes | Maybe | Cards if tactic-based | No | Maybe |
| `resource` rules | Yes | Yes | Yes | Starting values | Resource cards | No | Yes |
| `state_variable` | Yes if public | Yes | Maybe | Maybe | No | Usually yes | Yes |
| `upkeep_rule` | Summary only | Full | Maybe | No | No | Usually yes | Maybe |
| `opportunity` | Usually no exact effects | Yes | No | Maybe | No | No | Maybe |
| `soft_goal` | No | Maybe | No | Yes | No | No | Yes |
| `control_judgement` | No | Yes | No | No | No | No | Maybe |
| `rules_conflict` | No | Designer notes | No | No | No | No | Maybe |
| `aftermath_metric` | Yes if public | Yes | Maybe | No | No | Usually yes | Maybe |

---

## 5. Conversion workflow

### Step 1: Identify the change set

If converting a whole MMDL file, summarise the current design first.

If converting a patch, list affected objects.

```yaml
conversion_scope:
  mode: full_rebuild | targeted_update | patch_application
  changed_objects:
  unchanged_objects:
  affected_materials:
  private_information_risk:
```

### Step 2: Build an impact matrix

Before drafting, identify where every change must appear.

```yaml
impact_matrix:
  object_id:
    object_type:
    changed_fields:
    player_guide: none | update | new_section
    facilitator_guide: none | update | new_section
    reference_sheet: none | update | new_box
    role_briefs: []
    cards: []
    maps: []
    spreadsheet: []
    playtest_notes: []
```

Do not update only one document if the rule appears in several places.

### Step 3: Restore local terminology

Convert core concepts back to local language.

```yaml
terminology_restore:
  location: shire
  site: settlement
  contest: battle
  contest_subprocedure: clash
  commitment_token: action card
  authority_token: crown
```

Use MMDL core terms only in internal design notes, not in player-facing prose.

### Step 4: Draft player-facing rules

Player-facing rules should be:

- procedural
- concise
- written in the game’s terminology
- explicit about timing, costs, targets, and effects
- free of facilitator-only reasoning
- clear about what players physically do

Use this structure:

```markdown
### <Rule Name>

When: <phase or trigger>
Who: <eligible actors>
Cost: <cost, if any>
Target: <target, if any>
Effect: <mechanical effect>
Notes: <important limits or exceptions>
```

For timed phases:

```markdown
### <Phase Name> (<duration>)

During this phase, you may:

- <permission>
- <permission>
- <permission>

Before the phase ends, you must:

- <mandatory action>
```

### Step 5: Draft facilitator-facing rules

Facilitator-facing rules should include:

- exact procedures
- hidden triggers
- adjudication criteria
- default rulings
- escalation options
- pacing advice
- what not to reveal
- how to handle edge cases

Use this structure:

```markdown
### <Facilitator Procedure>

Purpose: <why this exists>
When to use: <trigger>
Inputs: <state variables, player actions, hidden info>
Procedure:
1. <step>
2. <step>
3. <step>
Default outcome: <baseline ruling>
Adjustments: <how to vary>
Do not reveal: <hidden info>
Control load: <low / medium / high>
Common problems: <table issues>
```

### Step 6: Update role briefs

Role briefs should convert `soft_goal`, `allegiance`, `authority_token`, `starting_resources`, and `useful_actions` into in-character but unambiguous text.

Use this structure:

```markdown
## <Role Name>

Brief: <fictional situation>
Claims / Authorities / Responsibilities: <as appropriate>
Starting resources: <if player-facing>
Goals:
- <goal>
- <goal>
- <goal>
Guidance:
- <practical advice>
- <likely allies and rivals>
- <mechanisms to pay attention to>
```

Do not expose another role’s private goal unless the original brief intentionally does so.

### Step 7: Update reference sheets

Reference sheets should be compressed and procedural.

Include:

- turn order
- phase permissions
- action list
- costs
- target restrictions
- resource gains
- contest tables
- common exceptions

Avoid:

- setting prose
- design intent
- long examples
- facilitator-only notes

### Step 8: Update cards

For cards, convert MMDL to component text.

```yaml
card_update:
  card_id:
  card_type:
  title:
  timing:
  cost:
  target:
  effect_text:
  reminder_text:
  owner_or_faction:
  quantity:
```

Card text should be shorter than guide text. Use consistent wording.

Example structure:

```markdown
**Title**
Timing / Type
Effect.
Reminder or discard rule.
Owner / faction mark.
```

### Step 9: Update maps and boards

Maps usually express MMDL `domain`, `location`, `site`, `state_variable`, `track`, `authority_token`, and `upkeep_rule`.

For map updates, specify:

```yaml
map_update:
  map_name:
  affected_area:
  add:
  remove:
  rename:
  move:
  state_variable_boxes:
  track_changes:
  icon_changes:
  legend_changes:
  end_of_turn_text:
```

Be explicit whether a change is graphical, textual, or mechanical.

### Step 10: Update spreadsheets or data files

If the game uses spreadsheets, produce data rows rather than prose where useful.

```csv
id,type,display_name,local_term,owner,phase,cost,target,effect,visibility
```

Keep IDs stable with the MMDL.

---

## 6. From MMDL patch to material patch

When given a patch, produce a material patch.

```yaml
material_patch:
  change_id:
  source_mmdl_patch:
  summary:
  update_player_guide:
    sections:
    replacement_text:
  update_facilitator_guide:
    sections:
    replacement_text:
  update_reference_sheets:
    sheets:
    replacement_text:
  update_role_briefs:
    roles:
    replacement_text:
  update_cards:
    cards:
    replacement_text:
  update_maps:
    maps:
    instructions:
  unresolved_questions:
```

If exact page numbers or layout positions are unknown, say so and provide section-level replacement text.

---

## 7. Regression checks

After converting back, run consistency checks.

### 7.1 Rules consistency

- [ ] Does every public rule match the MMDL procedure?
- [ ] Are costs identical across guide, reference sheet, cards, and role brief?
- [ ] Are phase names and durations consistent?
- [ ] Are target restrictions consistent?
- [ ] Are resource names consistent?
- [ ] Are thresholds and track bands consistent?
- [ ] Are once-per-turn and once-per-game limits repeated where needed?

### 7.2 Visibility safety

- [ ] No private goals in public rules.
- [ ] No facilitator-only triggers in player guides.
- [ ] No hidden consequences printed on public cards unless intended.
- [ ] No NPC/facilitator motives exposed accidentally.

### 7.3 Component consistency

- [ ] Every referenced card exists.
- [ ] Every map state variable has rules support.
- [ ] Every role starting resource appears on the role sheet or setup list.
- [ ] Every action in the guide appears on the relevant reference sheet.
- [ ] Every icon or local term has a legend or obvious context.

### 7.4 Playability

- [ ] A new player can tell what to do each phase.
- [ ] A facilitator can resolve edge cases.
- [ ] A player can identify useful actions.
- [ ] A player can see why negotiation matters.
- [ ] The rules do not require players to understand MMDL.

---

## 8. Handling contradictions during conversion

If MMDL contains a `rules_conflict`, do not choose a resolution unless asked.

Instead, output:

```markdown
## Rules conflict needing designer decision

Topic: <topic>
Conflict: <summary>
Appears in: <materials>
Options:
1. <resolution option>
2. <resolution option>
Recommendation: <if useful>
Materials affected: <list>
```

If the user asks you to resolve it, choose the option that best supports:

- current design intent
- player clarity
- lowest facilitator load
- fewest material updates
- consistency with the most authoritative source

State the rationale.

---

## 9. Writing style by material type

### Player guide

Use plain procedural language. Explain what players do and why it matters. Keep hidden machinery out.

### Facilitator guide

Be explicit, operational, and judgement-oriented. Include examples, default rulings, and pacing advice.

### Reference sheet

Use compact text, tables, and repeated wording. Optimise for in-game lookup.

### Role brief

Use in-character framing, but make goals and useful mechanisms unambiguous.

### Card text

Use short, consistent templates. Avoid prose unless the card is primarily narrative.

### Map text

Use the shortest possible rule reminders. Full procedures belong elsewhere.

### Playtest notes

Use issue / evidence / possible fix / decision format.

---

## 10. Standard output formats

### 10.1 Section replacement

```markdown
Replace the current section `<Section Name>` with:

<new text>
```

### 10.2 Additive insert

```markdown
Insert after `<Existing Heading>`:

<new text>
```

### 10.3 Component table

| Component | Change | New text / instruction |
|---|---|---|
| Player Guide: Battle Phase | Replace paragraph 2 | ... |
| Saxon Warrior Reference Sheet | Add action | ... |
| Map: Western England | Add marker | ... |

### 10.4 Full material draft

Use only when the user asks for a complete regenerated file or when the existing material is too inconsistent to patch safely.

---

## 11. Final response after conversion

When returning updated materials, summarise:

- what files or sections were updated
- what MMDL objects drove the changes
- what hidden/private material was intentionally excluded
- what unresolved questions remain
- whether any physical components need layout work

If files were created, provide direct download links.

Do not claim that a PDF, card deck, map, or spreadsheet has been updated unless a new artifact has actually been created.
