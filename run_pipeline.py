"""Run the Iran conflict living-standards pipeline and write dashboard JSON."""

from __future__ import annotations

import json
from pathlib import Path

from iran_impact.pipeline import run_full_pipeline


def main() -> int:
    results = run_full_pipeline()
    for path in [
        Path("data/iran_impact_results.json"),
        Path("dashboard/public/data/iran_impact_results.json"),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(results, indent=2, default=str) + "\n")
        print(f"Written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
