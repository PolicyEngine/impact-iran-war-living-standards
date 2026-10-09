"""Property-based invariants: a higher price never helps a household.

For every price parameter (energy, fuel, food), raising it with the others
held fixed must never lower any household's cost, the total cost, or the
number of people below the anchored poverty line. These hold for every
input, so they are stated as properties over generated populations rather
than checked on one hand-built example. The same holds for each forecast
derivation in the figure it is derived from.

The committed output carries the same properties on the real microsimulation
(tests/test_committed_output.py), and tests/test_integration.py checks them
on the certified data where it is available.
"""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from conftest import LinearGains
from iran_impact import config
from iran_impact.pipeline import (
    _below_anchored_line,
    _baseline_in_poverty,
    _mean_impact_pct,
    _poverty_line,
    compute_scenario,
    weighted_sum,
)

PRICE_PARAMETERS = ["cap_increase_pct", "fuel_pct", "food_increase_pct"]
CHANNEL = {
    "cap_increase_pct": "energy_shock",
    "fuel_pct": "fuel_shock",
    "food_increase_pct": "food_shock",
}

N = 12  # households per generated population
money = st.floats(min_value=0, max_value=20_000, allow_nan=False, allow_infinity=False)
# HBAI income can be zero or negative in the data (self-employment losses).
# Whole pounds, so a subnormal denominator cannot overflow the share-of-income
# arithmetic into infinities that compare equal.
income = st.integers(min_value=-20_000, max_value=200_000).map(float)
pct = st.floats(min_value=0, max_value=200, allow_nan=False, allow_infinity=False)


@st.composite
def populations(draw):
    hbai = draw(arrays(np.float64, N, elements=income))
    # Equivalisation divides by a positive factor, so it keeps the sign.
    factor = draw(
        arrays(np.float64, N, elements=st.floats(min_value=0.67, max_value=2.5))
    )
    return {
        "energy": draw(arrays(np.float64, N, elements=money)),
        "fuel_cost": draw(arrays(np.float64, N, elements=money)),
        "food_cost": draw(arrays(np.float64, N, elements=money)),
        "uprating_gains": LinearGains(np.zeros(N)),
        "income": hbai * 1.05,
        "hbai_income": hbai,
        "equiv_hbai_income": hbai / factor,
        "people": draw(
            arrays(np.float64, N, elements=st.integers(min_value=1, max_value=6))
        ),
        "weights": draw(
            arrays(np.float64, N, elements=st.floats(min_value=1, max_value=5_000))
        ),
    }


@st.composite
def parameters(draw):
    return {
        "cap_increase_pct": draw(pct),
        "fuel_pct": draw(pct),
        "food_increase_pct": draw(pct),
        "cpi_increase_pp": draw(st.floats(min_value=0, max_value=8)),
    }


def _newly_below(data, net):
    line = _poverty_line(data)
    person_weights = data["weights"] * data["people"]
    newly = (~_baseline_in_poverty(data, line)) & _below_anchored_line(data, net, line)
    return weighted_sum(newly.astype(float), person_weights)


@settings(max_examples=300, deadline=None)
@given(
    data=populations(),
    params=parameters(),
    name=st.sampled_from(PRICE_PARAMETERS),
    delta=st.floats(min_value=0, max_value=100, allow_nan=False),
)
def test_raising_a_price_never_lowers_any_cost_or_the_poverty_count(
    data, params, name, delta
):
    before = compute_scenario(data, "central_shock", params_override=params)
    after = compute_scenario(
        data, "central_shock", params_override={**params, name: params[name] + delta}
    )

    # Every household, not just the total.
    assert np.all(after["net_impact"] >= before["net_impact"] - 1e-9)
    # Only the raised channel moves, by exactly spend x delta.
    for other, channel in CHANNEL.items():
        if other == name:
            continue
        np.testing.assert_array_equal(after[channel], before[channel])
    # The aggregates the dashboard reports.
    weights = data["weights"]
    assert weighted_sum(after["net_impact"], weights) >= weighted_sum(
        before["net_impact"], weights
    ) - 1e-6
    assert _newly_below(data, after["net_impact"]) >= _newly_below(
        data, before["net_impact"]
    )
    assert _mean_impact_pct(after["net_impact"], data["income"], weights) >= (
        _mean_impact_pct(before["net_impact"], data["income"], weights) - 1e-9
    )


@settings(max_examples=200, deadline=None)
@given(data=populations(), params=parameters())
def test_the_cpi_parameter_never_moves_the_household_cost(data, params):
    """CPI sizes the uprating shortfall only; it is not a cost channel (#13)."""
    base = compute_scenario(data, "central_shock", params_override=params)
    moved = compute_scenario(
        data,
        "central_shock",
        params_override={**params, "cpi_increase_pp": params["cpi_increase_pp"] + 1},
    )
    np.testing.assert_array_equal(base["net_impact"], moved["net_impact"])


@settings(max_examples=300, deadline=None)
@given(
    data=populations(),
    cost=arrays(np.float64, N, elements=money),
    extra=arrays(np.float64, N, elements=money),
)
def test_more_cost_never_lifts_anyone_above_the_anchored_line(data, cost, extra):
    """The poverty step on its own: anyone below the line at a cost is still
    below it at a higher cost, so the newly-below set only grows."""
    line = _poverty_line(data)
    below = _below_anchored_line(data, cost, line)
    below_more = _below_anchored_line(data, cost + extra, line)
    assert np.all(below_more[below])


# ── The forecast derivations, in their sources ──────────────────────────


@given(a=st.floats(500, 5_000), b=st.floats(500, 5_000))
def test_the_energy_parameter_rises_with_the_forecast_bill(a, b):
    low, high = sorted((a, b))
    assert config.cap_rise_pct(low) <= config.cap_rise_pct(high)


@given(
    electricity=st.floats(100, 3_000),
    gas=st.floats(100, 3_000),
    more=st.floats(0, 500),
    which=st.sampled_from(["electricity_gbp", "gas_gbp"]),
)
def test_the_restored_bill_rises_with_each_forecast_component(
    electricity, gas, more, which
):
    forecast = {"electricity_gbp": electricity, "gas_gbp": gas}
    raised = {**forecast, which: forecast[which] + more}
    assert config.forecast_cap_2027_28_gbp(raised) >= config.forecast_cap_2027_28_gbp(
        forecast
    )


@given(a=st.floats(20, 250), b=st.floats(20, 250))
def test_the_fuel_parameter_rises_with_the_brent_forecast(a, b):
    low, high = sorted((a, b))
    assert config.fuel_rise_pct_at_brent(low) <= config.fuel_rise_pct_at_brent(high)


rate = st.floats(min_value=-2, max_value=15, allow_nan=False)


@st.composite
def igd_vintages(draw):
    def band():
        low = draw(rate)
        return (low, low + 1.0)

    return {"2026": band(), "2027": band()}


@given(
    latest=igd_vintages(),
    pre=igd_vintages(),
    year=st.sampled_from(["2026", "2027"]),
    more=st.floats(0, 5),
)
def test_the_food_revision_rises_with_the_latest_forecast_and_falls_with_the_old(
    latest, pre, year, more
):
    """A higher latest forecast raises the revision; a higher pre-conflict
    forecast lowers it."""
    base = config.igd_food_revision_pct(latest_vintage=latest, pre_conflict_vintage=pre)
    shifted = lambda v: {**v, year: (v[year][0] + more, v[year][1] + more)}  # noqa: E731
    assert (
        config.igd_food_revision_pct(
            latest_vintage=shifted(latest), pre_conflict_vintage=pre
        )
        >= base
    )
    assert (
        config.igd_food_revision_pct(
            latest_vintage=latest, pre_conflict_vintage=shifted(pre)
        )
        <= base
    )


@given(latest=igd_vintages(), pre=igd_vintages())
def test_the_food_range_brackets_the_midpoint_revision(latest, pre):
    """Opposite band ends must contain the midpoint, whatever IGD publishes."""
    mid = config.igd_food_revision_pct(latest_vintage=latest, pre_conflict_vintage=pre)
    low = config.igd_food_revision_pct(
        "low", "high", latest_vintage=latest, pre_conflict_vintage=pre
    )
    high = config.igd_food_revision_pct(
        "high", "low", latest_vintage=latest, pre_conflict_vintage=pre
    )
    assert low <= mid <= high


@given(
    energy=st.floats(0, 200),
    fuel=st.floats(0, 200),
    food=st.floats(0, 50),
    more=st.floats(0, 50),
    which=st.integers(0, 2),
)
def test_the_first_round_cpi_effect_rises_with_each_price(energy, fuel, food, more, which):
    prices = [energy, fuel, food]
    raised = list(prices)
    raised[which] += more
    assert config.first_round_cpi_pp(*raised) >= config.first_round_cpi_pp(*prices)


@given(value=st.floats(min_value=0, max_value=20, allow_nan=False))
def test_rounding_an_adder_up_never_lands_below_its_floor(value):
    rounded = config.ceil_to_tenth(value)
    assert rounded >= round(value, 9)
    assert rounded < value + 0.1 + 1e-9
    assert config.ceil_to_tenth(rounded) == rounded
