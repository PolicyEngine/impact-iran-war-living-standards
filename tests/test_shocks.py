"""The four transmission channels and their composition into a net impact."""

import numpy as np
import pytest

from iran_impact import config
from iran_impact.pipeline import compute_scenario


def test_energy_shock_is_baseline_spend_times_cap_increase(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    pct = config.SCENARIOS["central_shock"]["cap_increase_pct"] / 100
    assert impacts["energy_shock"] == pytest.approx(synthetic_data["energy"] * pct)


def test_fuel_and_food_shocks_scale_imputed_spend(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    params = config.SCENARIOS["central_shock"]
    assert impacts["fuel_shock"] == pytest.approx(
        synthetic_data["fuel_cost"] * params["fuel_pct"] / 100
    )
    assert impacts["food_shock"] == pytest.approx(
        synthetic_data["food_cost"] * params["food_increase_pct"] / 100
    )


def test_uprating_shortfall_applies_only_the_residual_cpi(synthetic_data):
    """April 2027 uprating is set from September 2026 CPI, which already
    carries the part of the shock in prices by then. Only the residual goes
    unindexed, so the shortfall must not be sized on the whole addition."""
    impacts = compute_scenario(synthetic_data, "central_shock")
    cpi = config.SCENARIOS["central_shock"]["cpi_increase_pp"]
    residual = cpi - config.captured_in_sept_2026_cpi_pp()
    assert impacts["benefit_uprating_shortfall"] == pytest.approx(
        synthetic_data["benefit_income"]
        * (round(residual, 2) / 100)
        * config.UPRATING_LAG_FACTOR
    )


def test_a_cpi_addition_already_captured_leaves_no_shortfall(synthetic_data):
    """A scenario whose addition is at or below what September 2026 CPI
    already carries has no shortfall, not a negative one."""
    params = dict(config.SCENARIOS["low_shock"])
    params["cpi_increase_pp"] = config.captured_in_sept_2026_cpi_pp() - 0.5
    impacts = compute_scenario(synthetic_data, "low_shock", params_override=params)
    assert np.all(impacts["benefit_uprating_shortfall"] == 0)


def test_households_without_benefit_income_have_no_shortfall(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    no_benefits = synthetic_data["benefit_income"] == 0
    assert np.all(impacts["benefit_uprating_shortfall"][no_benefits] == 0)


def test_net_impact_is_the_sum_of_the_three_cost_channels(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    assert impacts["net_impact"] == pytest.approx(
        impacts["energy_shock"] + impacts["fuel_shock"] + impacts["food_shock"]
    )


def test_the_uprating_shortfall_is_not_counted_as_a_cost(synthetic_data):
    """Adding it to the price channels counted the same shock twice
    (#13 review C1)."""
    impacts = compute_scenario(synthetic_data, "central_shock")
    assert np.any(impacts["benefit_uprating_shortfall"] > 0)
    assert impacts["net_impact"] == pytest.approx(
        impacts["energy_shock"] + impacts["fuel_shock"] + impacts["food_shock"]
    )


def test_accelerated_uprating_pays_the_shortfall(synthetic_data):
    """The shortfall's role: what an immediate uprating would deliver."""
    from iran_impact.pipeline import compute_policies

    impacts = compute_scenario(synthetic_data, "central_shock")
    policies = compute_policies(synthetic_data, "central_shock", impacts)
    assert policies["accelerated_uprating"] == pytest.approx(
        impacts["benefit_uprating_shortfall"]
    )


@pytest.mark.parametrize(
    "milder,harsher",
    [("low_shock", "central_shock"), ("central_shock", "severe_shock")],
)
def test_scenarios_are_ordered_by_severity(synthetic_data, milder, harsher):
    mild = compute_scenario(synthetic_data, milder)["net_impact"]
    hard = compute_scenario(synthetic_data, harsher)["net_impact"]
    assert np.all(hard >= mild)
    assert hard.sum() > mild.sum()
