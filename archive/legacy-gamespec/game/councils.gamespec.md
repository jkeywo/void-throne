# The Void Throne — Councils, Control, and the Crisis Clock (v0.1)

Phases (core), the Control organisation that runs them (facilitation), and the crisis clock
that escalates across them (automated-opponent).

```yaml
# ---- phases (core turn structure) ----
turn_loop:
  id: charter_day
  phase_sequence: [game.team_councils, game.specialty_councils, game.free_discussion, game.ceremony]

phase: { id: team_councils,      display_name: Team Councils,      function: team_planning, design_intent: [internal faction deliberation] }
phase: { id: specialty_councils, display_name: Specialty Councils, function: negotiation,    design_intent: [cross-faction policy set by delegates] }
phase: { id: free_discussion,    display_name: Free Discussion,    function: freeform_action, design_intent: [deals, conspiracies, confrontations] }
phase: { id: ceremony,           display_name: Ceremony of Settlement, function: commitment, design_intent: [the Charter is signed, amended, or refused] }

# specialty councils are invocation contexts delegates attend
invocation_context:
  id: specialty_council
  actor_scope: { role_types: [faction_delegate] }
  timing: { phase_ref: game.specialty_councils }
  target_selection: { target_types: [charter_clause] }

# ---- Control (facilitation) ----
control_role:
  id: council_control
  display_name: Council Control
  responsibilities:
    - run each council to time and record its resolutions
    - adjudicate whether the Charter is validly signed at the Ceremony
  adjudicates: [game.charter_validity]
  workload_profile: { peak_phases: [game.specialty_councils], concurrent_tables: 3 }

adjudicated_input:                 # CORE — Control judges whether the Charter is validly signed
  id: charter_validity
  judge_ref: game.council_control
  question: Given the signatures, vetoes and amendments on the table, is the Charter validly settled?
  guidance_ref: game.charter_guidance
  output_block: settlement_outcome
  visibility: facilitator_only

adjudication_guidance:
  id: charter_guidance
  output_type: SettlementOutcome
  guidance:
    - settled: required signatories have signed and no standing veto blocks it
    - contested: signed but under a veto or disputed clause; consequences carry forward
    - collapsed: the deadline passes with no valid settlement

# ---- crisis clock (automated-opponent) ----
threat_system:
  id: crisis_escalation
  type: doom_clock
  escalation:
    source: end_of_each_phase
    procedure:
      - Reveal the next Crisis (Charter Legitimacy, Fraying Conditioning, Pre-Human Presence, Void Integrity).
      - Apply its standing effect until a faction spends leverage to contain it.
      - Unresolved crises worsen the terms the Ceremony must accept.
  propagation:
    - each active crisis tightens what counts as a "settled" Charter
  defeat_conditions: [ceremony_reached_with_all_crises_unresolved]
  recovery_paths: [contain_crisis_via_faction_leverage]
```
