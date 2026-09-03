"""Policy eligibility, interactions and cost accounting (#14)."""

import numpy as np
import pytest

from iran_impact import config
from iran_impact.pipeline import (
    COMBINED_KEYS,
    MEANS_TESTED_QUALIFYING_BENEFITS,
    _eval_policy,
    compute_combined_package,
    compute_policies,
    compute_policy_effects,
    compute_scenario,
)


@pytest.fixture
def impacts(synthetic_data):
    return compute_scenario(synthetic_data, "central_shock")


@pytest.fixture
def policies(synthetic_data, impacts):
    return compute_policies(synthetic_data, "central_shock", impacts)


# ── £650 payment eligibility ──────────────────────────────────────────────


def test_qualifying_benefits_match_the_2022_scheme():
    """Per the government's factsheet. Housing Benefit alone did not qualify,
    and the two tax credits and income-related ESA/JSA did (#14)."""
    assert set(MEANS_TESTED_QUALIFYING_BENEFITS) == {
        "universal_credit",
        "jsa_income",
        "esa_income",
        "income_support",
        "working_tax_credit",
        "child_tax_credit",
        "pension_credit",
    }


def test_housing_benefit_is_not_a_qualifying_benefit():
    assert "housing_benefit" not in MEANS_TESTED_QUALIFYING_BENEFITS


def test_payment_goes_only_to_qualifying_households(policies, synthetic_data):
    qualifying = synthetic_data["is_means_tested"]
    assert np.all(policies["means_tested_payment"][qualifying] == config.MEANS_TEST_AMOUNT)
    assert np.all(policies["means_tested_payment"][~qualifying] == 0)


# ── Fuel duty on litres, not scaled spending ──────────────────────────────


def test_fuel_duty_saving_is_pence_per_litre_times_litres(policies, synthetic_data):
    expected = (
        config.FUEL_DUTY_CUT_PENCE
        / config.PENCE_PER_POUND
        * synthetic_data["fuel_litres"]
    )
    assert policies["fuel_duty_cut"] == pytest.approx(expected)


def test_households_with_no_vehicle_get_no_fuel_duty_benefit(policies, synthetic_data):
    """Every household used to receive one, including non-drivers (#14)."""
    no_vehicle = ~synthetic_data["owns_vehicle"]
    assert no_vehicle.any()
    assert np.all(policies["fuel_duty_cut"][no_vehicle] == 0)
    assert np.all(policies["fuel_duty_cut"][synthetic_data["owns_vehicle"]] > 0)


# ── Package interactions ──────────────────────────────────────────────────


def test_vat_relief_in_the_package_applies_to_the_capped_bill(
    synthetic_data, impacts, policies
):
    """Independently, the relief was computed on the full shocked bill, so
    adding it to the EPG double-counted the overlap (#14)."""
    joint = compute_combined_package(
        synthetic_data, "central_shock", impacts, policies
    )
    capped = synthetic_data["electricity"] * (1 + config.EPG_CAP_PCT) * (
        config.ELEC_VAT_SAVING_RATE
    )
    assert joint["components"]["elec_vat_cut"] == pytest.approx(capped)
    # And it is strictly smaller than the standalone measure.
    assert np.all(joint["components"]["elec_vat_cut"] < policies["elec_vat_cut"])


def test_package_outlay_is_less_than_the_independent_sum(
    synthetic_data, impacts, policies
):
    joint = compute_combined_package(
        synthetic_data, "central_shock", impacts, policies
    )
    independent = sum(policies[key] for key in COMBINED_KEYS)
    assert joint["gross_outlay"].sum() < independent.sum()


def test_package_covers_every_component(synthetic_data, impacts, policies):
    joint = compute_combined_package(
        synthetic_data, "central_shock", impacts, policies
    )
    assert set(joint["components"]) == set(COMBINED_KEYS)


def test_package_outlay_is_the_sum_of_its_post_interaction_components(
    synthetic_data, impacts, policies
):
    joint = compute_combined_package(
        synthetic_data, "central_shock", impacts, policies
    )
    assert joint["gross_outlay"] == pytest.approx(
        sum(joint["components"].values())
    )


def test_package_routing_accounts_for_its_whole_outlay(synthetic_data, impacts):
    """Every pound of outlay must be routed somewhere.

    Not all of it reaches the fuel-poverty ratio: a fuel-duty saving reduces
    road-fuel costs, which are neither a domestic energy bill nor income, so
    the identity is energy + income + other cost reductions = outlay. It was
    previously energy + income = outlay, which only held because the
    fuel-duty saving was wrongly counted as income (#14 review C2).
    """
    from iran_impact.pipeline import OTHER_COST_REDUCTION_KEYS

    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    policies = compute_policies(synthetic_data, "central_shock", impacts)
    components = policies["_combined_components"]
    combined = effects["combined"]
    other = sum(components[key] for key in OTHER_COST_REDUCTION_KEYS)
    assert combined["energy_reduction"] + combined["income_addition"] + other == (
        pytest.approx(combined["fiscal_outlay"])
    )


# ── Cost accounting ───────────────────────────────────────────────────────


def _all_policies(synthetic_data, impacts):
    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    return [
        (name, _eval_policy(synthetic_data, impacts, name, effect))
        for name, effect in effects.items()
    ]


def test_the_three_cost_concepts_are_reported_separately(synthetic_data, impacts):
    for name, result in _all_policies(synthetic_data, impacts):
        for field in [
            "gross_outlay_bn",
            "household_protection_bn",
            "residual_impact_bn",
        ]:
            assert field in result, name


def test_outlay_is_never_below_protection_for_any_policy(synthetic_data, impacts):
    """Outlay is unclipped, so it cannot be below what it protects (#14)."""
    for name, result in _all_policies(synthetic_data, impacts):
        assert result["gross_outlay_bn"] >= result["household_protection_bn"], name


def test_the_accounting_closes_for_every_policy(synthetic_data, impacts):
    """Protection was uncapped for standalone policies, so protection +
    residual exceeded the shock (#14 review C1)."""
    total_shock_bn = (
        impacts["net_impact"] * synthetic_data["weights"]
    ).sum() / 1e9
    for name, result in _all_policies(synthetic_data, impacts):
        assert (
            result["household_protection_bn"] + result["residual_impact_bn"]
            == pytest.approx(total_shock_bn, abs=0.01)
        ), name


def test_protection_never_exceeds_the_shock_for_any_policy(synthetic_data, impacts):
    total_shock_bn = (
        impacts["net_impact"] * synthetic_data["weights"]
    ).sum() / 1e9
    for name, result in _all_policies(synthetic_data, impacts):
        assert result["household_protection_bn"] <= total_shock_bn + 1e-9, name


def test_over_compensation_shows_up_as_outlay_above_protection(synthetic_data):
    """Where a payment exceeds a household's shock the payment does not
    shrink, so outlay must exceed protection.

    Uses a household whose shock is smaller than the flat rebate.
    """
    small = dict(synthetic_data)
    small["energy"] = np.full_like(small["energy"], 100.0)
    small["fuel_cost"] = np.zeros_like(small["fuel_cost"])
    small["food_cost"] = np.zeros_like(small["food_cost"])
    impacts = compute_scenario(small, "low_shock")
    assert np.all(impacts["net_impact"] < config.FLAT_REBATE)

    effects = compute_policy_effects(small, "low_shock", impacts)
    weights = small["weights"]
    outlay = effects["flat_rebate"]["fiscal_outlay"]
    protection = np.minimum(effects["flat_rebate"]["benefit"], impacts["net_impact"])
    assert (outlay * weights).sum() > (protection * weights).sum()


def test_spending_shares_use_the_spending_numerator(synthetic_data, impacts):
    """Issue #14: distributional shares must share a definition with the
    reported aggregate."""
    for name, result in _all_policies(synthetic_data, impacts):
        shares = [row["benefit_share_pct"] for row in result["by_quintile"]]
        assert sum(shares) == pytest.approx(100, abs=0.5), name


def test_cost_is_labelled_as_a_household_transfer_not_an_exchequer_cost(
    synthetic_data, impacts
):
    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    result = _eval_policy(
        synthetic_data, impacts, "Flat energy rebate", effects["flat_rebate"]
    )
    assert "gross modelled household transfer" in result["cost_basis"]
    for omission in ["take-up", "behavioural", "interactions"]:
        assert omission in result["cost_basis"]


# ── The winners/losers identity ───────────────────────────────────────────


def test_no_losers_category_is_reported(synthetic_data, impacts):
    """Losers are impossible by construction, so reporting a zero share would
    present a model identity as a finding (#14)."""
    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    result = _eval_policy(
        synthetic_data, impacts, "Flat energy rebate", effects["flat_rebate"]
    )
    assert "winners_losers" not in result
    assert "support_shares" in result
    for row in result["support_shares"]:
        assert set(row) == {"quintile", "pct_supported", "pct_unsupported"}
        assert row["pct_supported"] + row["pct_unsupported"] == pytest.approx(100, abs=0.2)


def test_support_is_never_negative(synthetic_data, impacts):
    """The reason a losers category cannot exist."""
    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    for name, effect in effects.items():
        assert np.all(effect["benefit"] >= 0), name


# ── Fuel-poverty routing: energy bills vs income vs neither ───────────────


def test_the_routing_lists_partition_the_package(synthetic_data, impacts):
    """Every combined component must be routed exactly once, so a measure
    cannot be silently treated as both or neither (#14 review C2)."""
    from iran_impact.pipeline import (
        CASH_TRANSFER_KEYS,
        ENERGY_BILL_KEYS,
        OTHER_COST_REDUCTION_KEYS,
    )

    routed = ENERGY_BILL_KEYS + CASH_TRANSFER_KEYS + OTHER_COST_REDUCTION_KEYS
    assert sorted(routed) == sorted(COMBINED_KEYS)
    assert len(routed) == len(set(routed))


def test_fuel_duty_savings_are_not_income_for_any_policy(synthetic_data, impacts):
    """A road-fuel saving is neither a domestic energy bill reduction nor
    income, so it must not raise the fuel-poverty denominator.

    The standalone policy got this right while the combined package routed
    the same saving as income, understating combined-policy fuel poverty
    (#14 review C2).
    """
    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    policies = compute_policies(synthetic_data, "central_shock", impacts)
    fuel_duty = policies["fuel_duty_cut"]
    assert np.any(fuel_duty > 0)

    # Standalone: routed to neither.
    assert np.all(effects["fuel_duty_cut"]["income_addition"] == 0)
    assert np.all(effects["fuel_duty_cut"]["energy_reduction"] == 0)

    # Combined: the package's income must be the cash transfers alone.
    expected = sum(
        policies[key] for key in
        ["flat_rebate", "ct_rebate", "uc_uplift", "means_tested_payment",
         "accelerated_uprating"]
    )
    assert effects["combined"]["income_addition"] == pytest.approx(expected)
    # Explicitly: adding the fuel-duty saving would change it.
    assert not np.allclose(
        effects["combined"]["income_addition"], expected + fuel_duty
    )


def test_combined_routing_matches_the_standalone_routing(synthetic_data, impacts):
    """Guards the class of bug directly: the package and the standalone
    policies must agree on how each measure reaches a household."""
    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    for key in COMBINED_KEYS:
        standalone_is_income = np.any(effects[key]["income_addition"] > 0)
        standalone_is_energy = np.any(effects[key]["energy_reduction"] > 0)
        # A measure routed to neither standalone must not appear in the
        # package's income or energy sums either.
        if not standalone_is_income and not standalone_is_energy:
            from iran_impact.pipeline import (
                CASH_TRANSFER_KEYS,
                ENERGY_BILL_KEYS,
            )

            assert key not in CASH_TRANSFER_KEYS, key
            assert key not in ENERGY_BILL_KEYS, key


def test_package_energy_reduction_is_the_energy_measures_only(
    synthetic_data, impacts
):
    effects = compute_policy_effects(synthetic_data, "central_shock", impacts)
    policies = compute_policies(synthetic_data, "central_shock", impacts)
    components = policies["_combined_components"]
    expected = components["energy_price_guarantee"] + components["elec_vat_cut"]
    assert effects["combined"]["energy_reduction"] == pytest.approx(expected)
