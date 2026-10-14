# The Void Throne

A five-player paper game about the government that survives its conqueror.
Two factions of two players and the Ascendant negotiate scarce transport,
military service and two constitutional instruments over two rounds.

This repository contains the current revised-visions prototype, its sources,
a browser test bench and a game-owned [Playtrace](C:/Coding/playtrace) plugin.
It requires no technology at the table.

## Open the project

- **Drive:** https://drive.google.com/drive/folders/1XxANDmMg-WPg42pdXdhWETZyNCWnmwSE
- **Browser:** double-click `Start Playtest.cmd`, or run `python launch.py`.
  It opens http://127.0.0.1:8877 and restores the last successful sheet.
- **Local handbook:** `docs/rulebook.html` — the expanded 14 October teaching edition,
  with setting, setup, a worked round, action references and a glossary.
  `docs/rulebook-material-map.json` records rule coverage and verification.
- **Facilitator answers:** `docs/facilitator.html` (spoilers).
- **Lore and source distinctions:** `docs/lore.html` and `lore/source-inventory.json`.
- **Original six-agent report:** `reports/six-agent-playtest.html`.
- **Playtrace mechanical replay:** `reports/playtrace-replay.html`.

## Browser testing

The default and current mode is **control every seat**, as requested. Enter each
player's draft, buy or decline foresight, commit faction assets, sign orders,
propose articles and record each vote. The server applies the printed rules.
Use the role/table tabs for parallel discussions and the reason boxes for an
authored transcript. It is an all-seat test bench, not live AI opposition.

The selected answer is behind an Ascendant private-view disclosure. With one
tester controlling every seat, this is an aid to discipline rather than a
security boundary between players. Unpurchased card answers are not sent by
the game-state endpoint. The facilitator guide is explicitly marked as spoilers.

Download HTML and JSON before starting another test. JSON can be resumed with
**Resume exported test**. The server reconstructs it by applying decisions in
order, not by trusting an imported final state. Automatic local storage is in
`.playtrace/browser-session.json`. Closing the terminal stops the server;
restart it to resume. `python launch.py --port 8879` selects another port.

## Reproduce with Playtrace

Use the existing Playtrace environment (Python 3.12+, pydantic and lark):

```powershell
& C:/Coding/playtrace/.venv/Scripts/python.exe playtrace_game.py reproduce
& C:/Coding/playtrace/.venv/Scripts/python.exe -m unittest discover -s tests -v
```

`playtrace_game.py` reads the registered Drive sources through Playtrace's real
tabletop adapter, using a verified connector capture in
`tests/fixtures/workspace.json`. It adds the game engine, repository revision
and shared Playtrace code fingerprints, selects this game's registered plugin,
then persists a typed snapshot, SimulationRun, hypothesis, experiment evidence
and claim in `.playtrace/playtrace.db`. It writes portable JSON evidence and a
native Playtrace HTML report. `PLAYTRACE_ROOT` overrides the shared checkout.

The plugin is also exposed through the `playtrace.simulation_plugins` package
entry point for installation in another environment. The helper registers it directly so this checkout works without installing the
game into that environment. The expanded rulebook requires the repeated-paragraph
import fix in local Playtrace revision `ae44cc3b7f31d690a6b2b558e9034a9dd0ef63dd`;
this preserves identical costs and contents entries as separate occurrences. The strict game model requires its engine
fingerprint in the snapshot, so use `reproduce` rather than the generic CLI's
uncustomised snapshot-and-simulate shortcut. Other standard CLI operations are
available through `playtrace_game.py cli ...`.

The captured source data is an offline snapshot of real documents, not a live
sync or a fixture invented to imitate Drive. Current native document IDs and
revisions are in `design/drive-files.json`. For future live capture, use the
ordinary Playtrace OAuth workflow described in its `docs/google-sheets.md`,
then preserve a new verified capture. No credentials are stored here.

## What the simulation establishes

The preserved six-agent run has 113 original contributions and six debriefs.
The first foresight purchase changed orders; the second mainly improved
confidence and coordination. Both opportunities were purchased. The last
token was guaranteed by the two-round purchase limit, not deliberately saved.
NG/MJ passed 8/11 over both army players' objections.

The Playtrace run **replays those mechanical decisions**. It does not generate
new dialogue or count as another independent playtest. Its hypothesis relation
is `context`. Unsupported scripts, stale engine snapshots and missing decisions
produce explicit blockers. A scheduled end uses `max_turns`; this is not a claim
that every party won. The game-specific event/state records carry the relevant
metrics; unrelated shared card-game counters remain zero.

## Source authority and layout

| Location | Purpose |
| --- | --- |
| Native Drive documents | Editable current rulebook, guide, lore and playtest write-up |
| `docs/` | Initial publication source and offline copies; not automatic two-way sync |
| `src/void_throne/` | Exact operational model, phase/signature procedure, web server and Playtrace plugin |
| `design/experiments/` | Hypothesis, exact replay script and fresh-agent protocol |
| `design/evidence/` | Original authored decisions, packets, audits and typed Playtrace evidence |
| `reports/` | Phased agent report, current replay and historical linked reports |
| `archive/` | Original output packs and larger-game source material, preserved unchanged |
| `lore/` | Source inventory and provenance |
| `tests/` | Consequence, authority, replay and workflow checks |
| `.playtrace/` | Disposable runtime database and browser autosave; ignored by Git |

Read current Drive documents before changing a rule or publishing new copies.
An edited document can make a captured fixture and engine stale. Update the model,
capture and regression expectations deliberately; do not silently treat old code
as authority. The older folders at `C:/AnalogueGames/TheVoidThrone` and
`C:/AnalogueGames/analogue-projects/GameProjects/void_throne` remain intact.

This is draft v0.3: a migration of the accepted revised-visions experiment,
not a balance revision. No strategic map, Clarity track, conspiracy, secret
individual objectives or unanimous final ballot has been reintroduced.

## Current crisis and historical records

The current scenario concerns Sorenne’s Fall and the Sorenne Flag. Stability measures the system’s supplies and civil services. The internal `communities` field retains its old name for saved-session compatibility. Historical reports and transcripts preserve their original terms; the current names do not imply those runs tested the revised setting. See `lore/scenario-setting.json` for established facts and scenario additions.

Player handouts are in `docs/player-briefs.html` and the native Player Briefs document listed in `design/drive-files.json`. The main rulebook keeps shared rules and council seating; faction objectives and advice are separate.

## Human multiplayer — one online page

Open https://jkeywo.github.io/void-throne/ on every machine. The facilitator chooses **Start a new game**, shares the room code, and admits each player. Players choose **Join the table**. Five players submit their own sheets; the facilitator closes phases. There is no Python installation or local game server required for this mode.

The facilitator must keep the hosting tab open. Games autosave in that browser. After a reload, choose **Resume saved game**; players reconnect to the same code, with a Reconnect button if needed. One tab per browser can host at a time. Starting another room archives the prior browser save. HTML reports, decision records, current host backups and archived backups can be downloaded from the facilitator controls. Clearing site storage removes browser saves. Backups preserve data for recovery, but this version has no backup-file import screen.

The first hosting session downloads the pinned Pyodide 314.0.7 runtime from jsDelivr. The existing Python rules and seat authorization run in a module worker; PeerJS carries player messages. IndexedDB stores host saves and Web Locks prevents two tabs from overwriting them. Players do not start the Python runtime. Both generated HTML filenames contain the same start-or-join page.

The source repository is public, including scenario answers. This is a cooperative playtest tool, not an anti-cheat service. The interface still restricts live sheets, private chats and purchased visions to their authorized seats. Never send the worker's full backup or host envelope to player peers.

`python tools/build_pages.py` rebuilds the game and stages only `index.html` and `.nojekyll` in `build/pages/`. The **Publish online game** workflow tests the rules and browser bridge, then deploys on pushes to `main` (or manual dispatch). Saved games, reports and historical archives are not deployed as website assets. Playtrace integration remains a local check because its dependencies are maintained separately.

The all-seat Python test bench remains available through `Start Playtest.cmd`. `Start Multiplayer.cmd` can still serve the unified HTML locally, but games created there now save in that browser origin; older Python multiplayer save files are not automatically migrated. See `docs/multiplayer-guide.txt` for connection and recovery details.
