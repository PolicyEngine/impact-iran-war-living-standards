"""Weighted aggregation and the helpers that feed every reported statistic."""

import numpy as np
import pytest

from iran_impact import config
from iran_impact.pipeline import (
    _decile_amount,
    _poverty_line,
    _safe_div,
    _weighted_median,
    weighted_mean,
    weighted_sum,
)


def test_weighted_mean_respects_weights():
    values = np.array([0.0, 100.0])
    # Nine parts zero to one part hundred.
    assert weighted_mean(values, np.array([9.0, 1.0])) == pytest.approx(10.0)


def test_weighted_sum_scales_by_weight():
    assert weighted_sum(
        np.array([2.0, 3.0]), np.array([10.0, 100.0])
    ) == pytest.approx(320.0)


def test_mask_filters_before_aggregating():
    values = np.array([1.0, 2.0, 3.0])
    weights = np.array([1.0, 1.0, 1.0])
    mask = np.array([True, False, True])
    assert weighted_mean(values, weights, mask) == pytest.approx(2.0)
    assert weighted_sum(values, weights, mask) == pytest.approx(4.0)


def test_weighted_median_shifts_with_weight_mass():
    values = np.array([1.0, 2.0, 3.0])
    # Nearly all weight on the top value pulls the median up to it.
    assert _weighted_median(values, np.array([1.0, 1.0, 100.0])) == pytest.approx(3.0)


def test_safe_div_returns_zero_on_non_positive_denominator():
    numerator = np.array([10.0, 10.0, 10.0])
    denominator = np.array([2.0, 0.0, -5.0])
    assert list(_safe_div(numerator, denominator)) == [5.0, 0.0, 0.0]


def test_decile_amount_maps_factors_onto_base():
    decile = np.array([1, 10])
    factors = {1: 0.5, 10: 2.0}
    assert list(_decile_amount(decile, factors, 100.0)) == [50.0, 200.0]


def test_poverty_line_is_person_weighted(synthetic_data):
    """The line must weight by people, not households.

    Household weights are equal here and every household holds two people, so
    person-weighting cannot change the median — but it must still be 60% of it.
    """
    line = _poverty_line(synthetic_data)
    expected_median = _weighted_median(
        synthetic_data["equiv_hbai_income"],
        synthetic_data["weights"] * synthetic_data["people"],
    )
    assert line == pytest.approx(config.POVERTY_LINE_RATIO * expected_median)


def test_poverty_line_person_weighting_differs_from_household(synthetic_data):
    """With unequal household sizes, person-weighting moves the median."""
    data = dict(synthetic_data)
    # Put all the people in the top-income households.
    data["people"] = np.where(data["decile"] >= 8, 10.0, 1.0)
    person_weighted = _poverty_line(data)
    household_weighted = config.POVERTY_LINE_RATIO * _weighted_median(
        data["equiv_hbai_income"], data["weights"]
    )
    assert person_weighted > household_weighted
