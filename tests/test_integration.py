"""End-to-end checks against the certified managed dataset.

Skipped wherever the private managed dataset is unavailable, which includes
CI. Run locally with managed-data access before pushing any change to the
calculation:

    pytest tests/test_integration.py

The pinned values are the results for the certified data build named below.
"""

import pytest

from iran_impact import config

CERTIFIED_DATA_BUILD = "policyengine-uk-data-1.56.16"
CERTIFIED_MODEL_VERSION = "2.90.2"

# Baseline figures for the certified build above (policyengine 5.3.0,
# enhanced_frs_2024_25). Tolerances are tight because the same code against
# the same certified build is deterministic; they exist only to absorb the
# rounding applied on output.
#
# The September 2026 audit's reproduced figures (29.6m households, £61,924
# mean net income, £1,331 mean energy spend) belong to the superseded
# populace_uk_2023 build and no longer apply.
EXPECTED_HOUSEHOLDS_M = 31.6
EXPECTED_MEAN_NET_INCOME = 57_103
EXPECTED_MEAN_ENERGY_SPEND = 1_584


def _baseline():
    """Run the baseline, skipping only where the dataset is genuinely absent.

    Availability is not guessed at. Enumerating token environment variables
    or looking for a Hugging Face cache directory both get this wrong:
    policyengine.py accepts several token names, and it only reuses a
    SHA-verified artifact at its own materialization target, so a populated
    hub cache does not mean the run can proceed.

    Instead the materializer decides. Only its own
    DatasetMaterializationError counts as "no data"; every other failure —
    model, schema or calculation — propagates as a test failure, which is the
    point of these tests.
    """
    try:
        from policyengine.provenance.dataset_materialization import (
            DatasetMaterializationError,
        )
    except ImportError:
        pytest.skip("policyengine[uk] is not installed")

    from iran_impact.pipeline import run_baseline

    try:
        return run_baseline(year=config.YEAR)
    except DatasetMaterializationError as exc:
        pytest.skip(f"certified dataset unavailable: {exc}")


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


def test_transport_fuel_spending_is_not_universal(baseline):
    """The A6 mean must not be assigned to households with no vehicle (#12)."""
    from iran_impact.pipeline import weighted_mean

    weights = baseline["weights"]
    fuel_cost = baseline["fuel_cost"]
    assert (fuel_cost == 0).any(), "every household was assigned fuel spending"
    owns = baseline["owns_vehicle"]
    assert not fuel_cost[~owns].any()
    # Concentrating spending on owners must leave the population mean at A6's.
    assert weighted_mean(fuel_cost, weights) == pytest.approx(
        config.BASE_FUEL_SPEND, rel=0.01
    )


def test_food_spending_mean_matches_the_published_table(baseline):
    from iran_impact.pipeline import weighted_mean

    assert weighted_mean(baseline["food_cost"], baseline["weights"]) == pytest.approx(
        config.BASE_FOOD_SPEND, rel=0.01
    )


def test_gross_income_deciles_are_ten_equal_weighted_groups(baseline):
    weights = baseline["weights"]
    shares = [
        weights[baseline["gross_decile"] == d].sum() / weights.sum()
        for d in range(1, 11)
    ]
    assert all(share == pytest.approx(0.1, abs=0.005) for share in shares)
