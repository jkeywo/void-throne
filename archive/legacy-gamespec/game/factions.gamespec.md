# The Void Throne — Factions and Tiered Goals (v0.1)

Ten factions (factions extension), each a team of players with a private briefing whose
goals come in three tiers: Threshold / Ambition / Legacy. Fictional identity is referenced
from the shared world; the game owns the goals and leverage. (Representative subset authored
in full; the remaining Houses follow the same shape.)

```yaml
# ---- institutions ----
faction:
  id: the_ascendant
  display_name: The Ascendant
  core_type: actor
  actor_subtype: faction
  setting_ref: setting.the_ascendant
  objectives: [game.the_ascendant.objective.seal_the_peace]
  design_intent: [supreme authority who cannot personally be everywhere; must delegate and be seen to]

faction:
  id: ductus_guild
  display_name: The Ductus Guild
  core_type: actor
  actor_subtype: faction
  setting_ref: setting.ductus_guild
  design_intent: [holds the void lanes; irreplaceable leverage, but a petition pending on the changing deep]

faction:
  id: ecclesiatum
  display_name: Ecclesiatum Perpetua
  core_type: actor
  actor_subtype: faction
  setting_ref: setting.ecclesiatum_perpetua
  design_intent: [holds the sanctification veto; fractured internally over whether it has taught honestly]

# ---- a noble House (pattern for all five) ----
faction:
  id: house_vethara
  display_name: House Vethara — The Legitimists
  core_type: actor
  actor_subtype: faction
  philosophy: authority derives from continuity and precedent
  design_intent: [wants the Charter to enshrine legitimate succession above raw power]

# ---- tiered private goals (briefings extension: briefing_goal referencing core objectives) ----
objective:
  id: seal_the_peace
  scope: actor
  owner_ref: game.the_ascendant
  visibility: private
  statement: The Charter is signed today with the Ascendant's authority intact and unshared.

briefing:
  id: ascendant_brief
  recipient_ref: game.the_ascendant
  information:
    knows: [the Charter must be signed today, the Janissariat conditioning may be fraying]
    suspects: [at least one House will withhold signature to extract concessions]
    explicitly_does_not_know: [which faction holds proof of the fraying]
  goals:
    - id: threshold
      visibility: private
      objective_ref: game.seal_the_peace
      statement: Threshold — the Charter is signed at all.
    - id: ambition
      visibility: private
      statement: Ambition — it is signed without ceding the sanctification veto to the Ecclesiatum.
    - id: legacy
      visibility: private
      statement: Legacy — history records the Peace as the Ascendant's mercy, not merely their conquest.

# House Vethara brief (same tiered shape)
briefing:
  id: vethara_brief
  recipient_ref: game.house_vethara
  information:
    knows: [the Charter's draft succession clause is ambiguous]
    suspects: [House Ondrak will argue power over precedent]
  goals:
    - id: threshold
      visibility: private
      statement: Threshold — the Charter recognises Vethara's precedence among the Houses.
    - id: legacy
      visibility: private
      statement: Legacy — Vethara is remembered as the House that kept the rule of law alive through the conquest.
```

> Remaining factions (Janissariat, Administratum, Houses Ondrak/Caelifen/Mourne/Aethon)
> follow this exact structure: a `faction` referencing the shared world, a `briefing` with
> Threshold/Ambition/Legacy goals, and leverage tied to what they uniquely control.
