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


HF_CACHE_DATASET = "datasets--policyengine--populace-uk-private"


def _managed_data_available():
    """Whether this environment can reach the private managed dataset.

    Checked before running, rather than by catching every exception from the
    run: a genuine model, schema or calculation regression in an authorized
    environment must fail, not report itself as skipped.
    """
    try:
        import policyengine  # noqa: F401
        from policyengine.tax_benefit_models.uk import (  # noqa: F401
            managed_microsimulation,
        )
    except ImportError:
        return False, "policyengine[uk] is not installed"

    import os
    from pathlib import Path

    if os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"):
        return True, ""
    try:
        from huggingface_hub import get_token

        if get_token():
            return True, ""
    except ImportError:
        pass
    # No token, but an already-downloaded snapshot works offline.
    cache = Path.home() / ".cache" / "huggingface" / "hub" / HF_CACHE_DATASET
    if cache.exists():
        return True, ""
    return False, (
        "no Hugging Face token and no cached populace-uk-private snapshot"
    )


def _baseline():
    """Run the baseline, skipping only where the data is genuinely absent."""
    available, reason = _managed_data_available()
    if not available:
        pytest.skip(f"managed dataset unavailable: {reason}")

    from iran_impact.pipeline import run_baseline

    # Deliberately not wrapped: any failure from here is a real regression.
    return run_baseline(year=config.YEAR)


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
