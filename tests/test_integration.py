"""End-to-end checks against the certified managed dataset.

Skipped wherever the private managed dataset is unavailable, which includes
CI. Run locally with managed-data access before pushing any change to the
calculation:

    pytest tests/test_integration.py

The pinned values are the reproduced results recorded in the September 2026
model-validation audit (issue #16).
"""

import pytest

from iran_impact import config

CERTIFIED_DATA_BUILD = "populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z"
CERTIFIED_MODEL_VERSION = "2.89.2"

# Reproduced audit figures. Tolerances are tight because the same code against
# the same certified build is deterministic; they exist only to absorb the
# rounding applied on output.
EXPECTED_HOUSEHOLDS_M = 29.6
EXPECTED_MEAN_NET_INCOME = 61_924
EXPECTED_MEAN_ENERGY_SPEND = 1_331


def _baseline():
    from iran_impact.pipeline import run_baseline

    try:
        return run_baseline(year=config.YEAR)
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"managed dataset unavailable: {type(exc).__name__}: {exc}")


@pytest.fixture(scope="module")
def baseline():
    return _baseline()


def test_run_uses_the_certified_data_build(baseline):
    """A different data build invalidates every pinned figure below."""
    bundle = baseline["bundle"]
    assert bundle, "managed simulation exposed no release bundle"
    assert bundle["certified_data_build_id"] == CERTIFIED_DATA_BUILD
    assert bundle["model_version"] == CERTIFIED_MODEL_VERSION


def test_baseline_population_matches_the_audit(baseline):
    from iran_impact.pipeline import weighted_mean

    weights = baseline["weights"]
    assert weights.sum() / 1e6 == pytest.approx(EXPECTED_HOUSEHOLDS_M, abs=0.05)
    assert weighted_mean(baseline["income"], weights) == pytest.approx(
        EXPECTED_MEAN_NET_INCOME, abs=1
    )
    assert weighted_mean(baseline["energy"], weights) == pytest.approx(
        EXPECTED_MEAN_ENERGY_SPEND, abs=1
    )


def test_every_household_array_is_the_same_length(baseline):
    lengths = {
        key: len(value)
        for key, value in baseline.items()
        if key != "bundle" and hasattr(value, "__len__")
    }
    assert len(set(lengths.values())) == 1, lengths


def test_deciles_are_clipped_into_range(baseline):
    """PolicyEngine assigns -1 to negative-income households."""
    decile = baseline["decile"]
    assert decile.min() >= 1
    assert decile.max() <= 10
