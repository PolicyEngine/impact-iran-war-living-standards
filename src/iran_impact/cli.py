"""CLI entry point for iran-impact-build command."""

import argparse
import json
from pathlib import Path

from .config import YEAR, SCENARIOS


def main():
    parser = argparse.ArgumentParser(
        description="Build Iran war impact on UK living standards analysis"
    )
    parser.add_argument("--year", type=int, default=YEAR)
    parser.add_argument(
        "--output", type=str, default="data/iran_impact_results.json"
    )
    parser.add_argument("--sync-dashboard", action="store_true")
    parser.add_argument(
        "--scenarios",
        type=str,
        default="all",
        help="Comma-separated scenario keys or 'all'",
    )
    args = parser.parse_args()

    from .pipeline import run_full_pipeline

    results = run_full_pipeline(year=args.year, scenario_keys=args.scenarios)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"Results written to {output_path}")

    if args.sync_dashboard:
        dash_path = Path("dashboard/public/data/iran_impact_results.json")
        dash_path.parent.mkdir(parents=True, exist_ok=True)
        dash_path.write_text(json.dumps(results, indent=2))
        print(f"Dashboard synced to {dash_path}")


if __name__ == "__main__":
    main()
