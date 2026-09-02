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


def test_uprating_lag_applies_the_expected_value_factor(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    cpi = config.SCENARIOS["central_shock"]["cpi_increase_pp"] / 100
    assert impacts["benefit_uprating_lag"] == pytest.approx(
        synthetic_data["benefit_income"] * cpi * config.UPRATING_LAG_FACTOR
    )


def test_households_without_benefit_income_have_no_uprating_lag(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    no_benefits = synthetic_data["benefit_income"] == 0
    assert np.all(impacts["benefit_uprating_lag"][no_benefits] == 0)


def test_net_impact_is_the_sum_of_the_four_channels(synthetic_data):
    impacts = compute_scenario(synthetic_data, "central_shock")
    assert impacts["net_impact"] == pytest.approx(
        impacts["energy_shock"]
        + impacts["fuel_shock"]
        + impacts["food_shock"]
        + impacts["benefit_uprating_lag"]
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
