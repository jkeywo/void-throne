"""Stage only the public player page for static hosting."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "build/pages"
subprocess.run([sys.executable, str(ROOT / "tools/build_multiplayer.py")], check=True)
DEST.mkdir(parents=True, exist_ok=True)
unexpected = [p.name for p in DEST.iterdir() if p.name not in {"index.html", ".nojekyll"}]
if unexpected:
    raise SystemExit("Refusing to publish unexpected files: " + ", ".join(unexpected))
(DEST / "index.html").write_bytes((ROOT / "web/multiplayer-player.html").read_bytes())
(DEST / ".nojekyll").write_text("", encoding="utf-8")
print("Staged public player page in build/pages; no facilitator files or archives.")
