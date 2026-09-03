"""Poverty and fuel-poverty metric definitions (#11)."""

import numpy as np
import pytest

from iran_impact import config
from iran_impact.pipeline import (
    _baseline_in_poverty,
    _below_anchored_line,
    _equiv_after_cost,
    _non_positive_income,
    _mean_impact_pct,
    _poverty_line,
    compute_scenario,
)


# ── The income concept poverty is measured on ────────────────────────────


def test_poverty_line_uses_the_hbai_income_variable(synthetic_data):
    """Measuring on total net income instead would move the line.

    This is the substance of #11: the pipeline described its measure as HBAI
    BHC while computing it from household_net_income.
    """
    line = _poverty_line(synthetic_data)
    data_on_total_income = dict(synthetic_data)
    data_on_total_income["equiv_hbai_income"] = synthetic_data["equiv_income"]
    assert line != pytest.approx(_poverty_line(data_on_total_income))


def test_baseline_poverty_compares_hbai_income_with_the_line(synthetic_data):
    line = _poverty_line(synthetic_data)
    in_poverty = _baseline_in_poverty(synthetic_data, line)
    assert np.array_equal(in_poverty, synthetic_data["equiv_hbai_income"] < line)


# ── Anchored, not contemporaneous ─────────────────────────────────────────


def test_post_shock_measure_uses_the_baseline_line(synthetic_data):
    """The threshold is anchored: it is not recomputed after the shock."""
    line = _poverty_line(synthetic_data)
    impacts = compute_scenario(synthetic_data, "severe_shock")
    shocked = dict(synthetic_data)
    shocked["equiv_hbai_income"] = _equiv_after_cost(
        synthetic_data, impacts["net_impact"]
    )
    # A line recomputed on the shocked distribution would be lower, so fewer
    # households would fall below it. The anchored line must not move.
    assert _poverty_line(shocked) < line


def test_a_cost_can_only_push_households_below_the_anchored_line(synthetic_data):
    line = _poverty_line(synthetic_data)
    impacts = compute_scenario(synthetic_data, "central_shock")
    baseline_below = _baseline_in_poverty(synthetic_data, line)
    shocked_below = _below_anchored_line(synthetic_data, impacts["net_impact"], line)
    assert np.all(shocked_below | ~baseline_below)


def test_equiv_after_cost_scales_by_the_hbai_denominator(synthetic_data):
    cost = np.full(len(synthetic_data["income"]), 900.0)
    result = _equiv_after_cost(synthetic_data, cost)
    expected = synthetic_data["equiv_hbai_income"] * (
        1 - cost / synthetic_data["hbai_income"]
    )
    assert result == pytest.approx(expected)


def test_equiv_after_cost_never_goes_negative(synthetic_data):
    """A cost larger than income floors the measure at zero, not below."""
    huge = synthetic_data["hbai_income"] * 5
    assert np.all(_equiv_after_cost(synthetic_data, huge) >= 0)


def test_equiv_after_cost_leaves_non_positive_income_untouched(synthetic_data):
    """A proportional reduction is undefined without positive income."""
    data = dict(synthetic_data)
    data["hbai_income"] = np.zeros_like(data["hbai_income"])
    cost = np.full(len(data["income"]), 500.0)
    assert _equiv_after_cost(data, cost) == pytest.approx(data["equiv_hbai_income"])


# ── Undefined share-of-income denominators ───────────────────────────────


def test_non_positive_incomes_are_countable():
    """They are excluded from every share-of-income statistic, so the number
    excluded has to be reportable rather than silently folded in (#11)."""
    income = np.array([10_000.0, 0.0, -1.0])
    assert list(_non_positive_income(income)) == [False, True, True]


# ── Shares of income with undefined denominators ─────────────────────────


def test_mean_impact_pct_excludes_non_positive_income():
    net = np.array([1_000.0, 1_000.0])
    income = np.array([10_000.0, 0.0])
    weights = np.array([1.0, 1.0])
    # Entering the second household as 0% would halve the mean to 5%.
    assert _mean_impact_pct(net, income, weights) == pytest.approx(10.0)


def test_mean_impact_pct_returns_zero_when_no_denominator_is_defined():
    net = np.array([1_000.0])
    assert _mean_impact_pct(net, np.array([0.0]), np.array([1.0])) == 0.0


def test_mean_impact_pct_intersects_the_supplied_mask():
    net = np.array([1_000.0, 2_000.0, 3_000.0])
    income = np.array([10_000.0, 0.0, 10_000.0])
    weights = np.ones(3)
    mask = np.array([True, True, False])
    assert _mean_impact_pct(net, income, weights, mask) == pytest.approx(10.0)


def test_energy_share_excludes_undefined_denominators(synthetic_data):
    """Baseline energy shares must use the same positive-income mask as every
    other share-of-income statistic (#11 review A1)."""
    from iran_impact.pipeline import _positive_income, _safe_div, weighted_mean

    data = dict(synthetic_data)
    data["income"] = np.where(data["decile"] == 1, 0.0, data["income"])
    share = _safe_div(data["energy"], data["income"])
    defined = _positive_income(data["income"])
    with_mask = weighted_mean(share, data["weights"], defined)
    without_mask = weighted_mean(share, data["weights"])
    # Including a zero for the undefined household drags the mean down.
    assert with_mask > without_mask
