# The Void Throne

The game is a paper design. The browser and Playtrace are development tools.
Current scope: five players, one facilitator, two operational rounds, weighted settlement and three starting foresight tokens. Preserve actual choices in archived transcripts.

## Authority
The native Drive rulebook and facilitator guide are the editable design documents. `design/drive-files.json` records their IDs and the captured revision. Local `docs/` files are the initial publication source and offline copies, not an automatic two-way sync. Read current Drive documents before publishing revisions. Update the engine and tests when rules change; never silently make code authoritative over an edited document.
Historical sources in `archive/` are read-only provenance. `lore/` separates source lore, user corrections, scenario inventions and unresolved questions. Do not restore obsolete individual goals, Clarity, a strategic map or unanimous final ratification.

## Implementation
Game code stays in this repository. Playtrace remains a dependency at `C:/Coding/playtrace` (override with PLAYTRACE_ROOT). Register the game plugin; do not put game-specific material in the shared system. `python playtrace_game.py reproduce` creates snapshots, deterministic replay, report and hypothesis-linked evidence. `python launch.py` opens the local all-seat browser test. `python -m unittest discover -s tests -v` checks rules and complete-session behavior.
The browser is a facilitator test bench: one person controls all five seats. It does not simulate human bargaining or run live LLM opponents. Exported browser traces and the preserved six-agent transcript are distinct evidence types. New agent simulations must use scoped information and preserve original authored decisions.
