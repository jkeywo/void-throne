# The Void Throne — Game Contract (v0.1)

A grimdark political megagame for 24–30 players. Ten factions, all goals private, must
decide whether the Charter of Settlement is signed today at the Seam. The setting (the
Settled Dark, Settlement era) is the shared WorldSpec dependency; this package owns the
game — factions, councils, goals, the ceremony, the crisis clock.

```yaml
game:
  id: void_throne
  display_name: The Void Throne
  game_family: megagame
  active_extensions: [briefings, facilitation, factions, automated-opponent]  # first three via the megagame bundle

  player_count: { min: 24, max: 30 }

  premise: |
    Sixty years after the Ascendant broke the Conclave of Thrones, the conquest is complete
    but the peace has not begun. On Charter Day, ten factions gather at the Seam. Everyone
    has brought their agendas. The Charter must be signed today — or not.

  play_experience:
    - private-goal political negotiation under a hard deadline
    - fractured authority: no one faction can simply impose the outcome
    - grimdark stakes — every settlement is paid for

  core_design_goals:
    - id: charter_is_player_enforced
      statement: Whether the Charter is signed, and on whose terms, must be produced by player negotiation, not scripted.
    - id: legacy_meaning
      statement: Each faction should end able to say what its existence meant, not just whether it "won".

  primary_pressure_loops:
    - game.charter_deadline        # the ceremony ends the game whether or not agreement is reached
    - game.crisis_escalation       # unresolved crises worsen the terms everyone must accept

setting_refs:                       # fictional truth from the shared Settled Dark world
  - setting.the_seam
  - setting.the_ascendant
  - setting.conclave_of_thrones
  - setting.throne_eternal
```

## Core loop

Phase One (Team Councils) → Phase Two (Specialty Councils, cross-faction policy) → Phase
Three (Free Discussion — deals, conspiracies, confrontations) → the Ceremony of Settlement.
Control runs the councils and adjudicates the ceremony; a crisis clock escalates through the phases.

```yaml
design_modules: [factions, councils, charter]
```
