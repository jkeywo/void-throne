# The Void Throne — Scenario: Charter Day (v0.1)

The single-session scenario. Ten factions, the crisis deck seeded, the Charter draft on the table.

```yaml
scenario:
  id: charter_day
  display_name: Charter Day at the Seam
  setting_ref: setting.the_seam

  active_roles:
    include: [game.the_ascendant, game.ductus_guild, game.ecclesiatum, game.house_vethara]
    # + Janissariat, Administratum, Houses Ondrak/Caelifen/Mourne/Aethon at full player count

  starting_state:
    game.crisis_escalation.stage: 0

  objectives:
    - id: charter_settled
      tier: shared
      statement: The primary outcome is whether the Charter of Settlement is validly signed by the Ceremony.
    # each faction also pursues its private Threshold/Ambition/Legacy goals (see factions.gamespec.md)

  briefing_assignments:
    - recipient_ref: game.the_ascendant
      compose: [game.ascendant_brief]
    - recipient_ref: game.house_vethara
      compose: [game.vethara_brief]

  crisis_deck:
    seed: [charter_legitimacy, fraying_conditioning, pre_human_presence, void_integrity]
    reveal: one_per_phase

  scaling:
    by_player_count: [24, 27, 30]
```
