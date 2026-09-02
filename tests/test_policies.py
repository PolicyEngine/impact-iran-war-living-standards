"""Policy eligibility rules and the combined package's accounting."""

import numpy as np
import pytest

from iran_impact import config
from iran_impact.pipeline import (
    COMBINED_KEYS,
    compute_policies,
    compute_policy_effects,
    compute_scenario,
)


@pytest.fixture
def policies(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    return compute_policies(synthetic_data, "central_shock", impacts)


def test_flat_rebate_goes_to_every_household(policies, synthetic_data):
    assert np.all(policies["flat_rebate"] == config.FLAT_REBATE)


def test_council_tax_rebate_covers_bands_a_to_d_only(policies, synthetic_data):
    eligible = np.isin(synthetic_data["ct_band"], ["A", "B", "C", "D"])
    assert np.all(policies["ct_rebate"][eligible] == config.CT_REBATE)
    assert np.all(policies["ct_rebate"][~eligible] == 0)


def test_uc_uplift_is_weekly_rate_annualised_for_recipients(policies, synthetic_data):
    expected = config.UC_UPLIFT_WEEKLY * config.WEEKS_PER_YEAR
    assert np.all(policies["uc_uplift"][synthetic_data["is_uc"]] == expected)
    assert np.all(policies["uc_uplift"][~synthetic_data["is_uc"]] == 0)


def test_means_tested_payment_follows_benefit_receipt(policies, synthetic_data):
    recipients = synthetic_data["is_means_tested"]
    assert np.all(policies["means_tested_payment"][recipients] == config.MEANS_TEST_AMOUNT)
    assert np.all(policies["means_tested_payment"][~recipients] == 0)


def test_accelerated_uprating_exactly_offsets_the_shortfall(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    policies = compute_policies(synthetic_data, "central_shock", impacts)
    assert policies["accelerated_uprating"] == pytest.approx(
        impacts["benefit_uprating_shortfall"]
    )


def test_epg_caps_the_energy_increase(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    policies = compute_policies(synthetic_data, "central_shock", impacts)
    pct = config.SCENARIOS["central_shock"]["cap_increase_pct"] / 100
    # The subsidy is the part of the increase above the capped share.
    expected = synthetic_data["energy"] * (pct - config.EPG_CAP_PCT)
    assert policies["energy_price_guarantee"] == pytest.approx(expected)


def test_epg_pays_nothing_when_the_shock_is_below_the_cap(synthetic_data, monkeypatch):
    """Every configured scenario exceeds the 10% cap, so build one that does not."""
    sub_cap = dict(config.SCENARIOS["low_shock"])
    sub_cap["cap_increase_pct"] = config.EPG_CAP_PCT * 100 / 2  # +5%, below the cap
    monkeypatch.setitem(config.SCENARIOS, "sub_cap_shock", sub_cap)
    impacts = compute_scenario(synthetic_data, "sub_cap_shock")
    policies = compute_policies(synthetic_data, "sub_cap_shock", impacts)
    assert np.all(policies["energy_price_guarantee"] == 0)


def test_combined_household_benefit_is_clipped_to_the_shock(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    policies = compute_policies(synthetic_data, "central_shock", impacts)
    assert np.all(policies["combined"] <= impacts["net_impact"] + 1e-9)


def test_combined_outlay_is_unclipped_and_at_least_the_clipped_benefit(synthetic_data):
    """Fiscal cost must not shrink when a household is over-compensated."""
    impacts = compute_scenario(synthetic_data, "central_shock")
    policies = compute_policies(synthetic_data, "central_shock", impacts)
    outlay = policies["_combined_outlay"]
    assert np.all(outlay >= policies["combined"] - 1e-9)
    assert outlay == pytest.approx(sum(policies[k] for k in COMBINED_KEYS))


def test_policy_effects_route_energy_subsidies_and_cash_separately(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    # An energy subsidy lowers the bill, not the income denominator.
    assert np.all(effects["energy_price_guarantee"]["income_addition"] == 0)
    assert np.any(effects["energy_price_guarantee"]["energy_reduction"] > 0)
    # A cash transfer does the opposite.
    assert np.all(effects["flat_rebate"]["energy_reduction"] == 0)
    assert np.any(effects["flat_rebate"]["income_addition"] > 0)
