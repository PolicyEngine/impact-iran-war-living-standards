"""Versioned spending inputs, read from committed source tables.

Nothing here is hand-set: the figures come from the ONS Family Spending
workbook via `scripts/extract_ons_a6.py`, and the CSV carries the source URL,
reference period, units, grouping variable and the SHA-256 of the workbook it
was extracted from.
"""

import csv
import hashlib
from pathlib import Path

INPUTS_DIR = Path(__file__).resolve().parent / "inputs"
ONS_A6_PATH = INPUTS_DIR / "ons_family_spending_a6_fye2024.csv"

WEEKS_PER_YEAR = 52

# Commodity keys as written by the extraction script.
TRANSPORT_FUEL = "transport_fuel"
FOOD = "food_and_non_alcoholic_drinks"


def _read_rows(path):
    with path.open() as handle:
        lines = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(lines))


def _read_header(path):
    """The commented provenance header, as a dict of its labelled lines."""
    metadata = {}
    with path.open() as handle:
        for line in handle:
            if not line.startswith("#"):
                break
            body = line.lstrip("#").strip()
            if ": " in body:
                key, _, value = body.partition(": ")
                metadata[key.lower().replace(" ", "_").rstrip(":")] = value
            elif body:
                metadata.setdefault("description", "")
                metadata["description"] += (" " if metadata["description"] else "") + body
    return metadata


class SpendingTable:
    """Annual household spending on one commodity, by gross-income decile.

    ONS Table A6 groups households by **gross household income** decile. The
    model must group them the same way; mapping these figures onto a decile
    built from a different income concept would silently mis-assign them
    (#12).
    """

    def __init__(self, commodity, path=ONS_A6_PATH):
        rows = [row for row in _read_rows(path) if row["commodity"] == commodity]
        if not rows:
            raise LookupError(f"no rows for commodity {commodity!r} in {path}")
        self.commodity = commodity
        self.path = path
        self.a6_code = rows[0]["a6_code"]
        self.description = rows[0]["a6_description"]
        weekly_all = float(rows[0]["all_households_weekly_spend_gbp"])
        self.annual_mean = round(weekly_all * WEEKS_PER_YEAR, 2)
        self.weekly_mean = weekly_all
        self.annual_by_decile = {
            int(row["gross_income_decile"]): round(
                float(row["weekly_spend_gbp"]) * WEEKS_PER_YEAR, 2
            )
            for row in rows
        }
        # Ratio of each decile's spending to the all-household mean, so the
        # model can express spending as mean × factor.
        self.decile_factors = {
            decile: amount / self.annual_mean
            for decile, amount in self.annual_by_decile.items()
        }
        if sorted(self.annual_by_decile) != list(range(1, 11)):
            raise ValueError(
                f"{commodity}: expected deciles 1-10, got "
                f"{sorted(self.annual_by_decile)}"
            )


def source_metadata():
    """Provenance of the committed input table, for the results file."""
    header = _read_header(ONS_A6_PATH)
    return {
        "table": header.get("table", ""),
        "reference_period": "financial year ending 2024",
        "units": header.get("units", ""),
        "grouping_variable": header.get("grouping_variable", ""),
        "bulletin_url": header.get("bulletin", ""),
        "workbook_url": header.get("workbook", ""),
        "workbook_sha256": header.get("workbook_sha-256", ""),
        "csv_sha256": hashlib.sha256(ONS_A6_PATH.read_bytes()).hexdigest(),
    }


TRANSPORT_FUEL_SPEND = SpendingTable(TRANSPORT_FUEL)
FOOD_SPEND = SpendingTable(FOOD)
