"""The committed ONS spending inputs and how they are assigned (#12)."""

import numpy as np
import pytest

from iran_impact import config
from iran_impact.inputs import (
    FOOD_SPEND,
    ONS_A6_PATH,
    TRANSPORT_FUEL_SPEND,
    SpendingTable,
    source_metadata,
)
from iran_impact.pipeline import _allocate_to_vehicle_owners, _weighted_decile

# Published ONS Family Spending FYE 2024, Table A6, £ per week per household.
A6_TRANSPORT_FUEL_MEAN = 19.80
A6_FOOD_MEAN = 70.50
A6_TRANSPORT_FUEL_BY_DECILE = [
    7.40, 8.60, 12.50, 17.80, 19.90, 20.50, 24.10, 26.50, 30.10, 30.90,
]
A6_FOOD_BY_DECILE = [
    38.10, 48.30, 57.00, 62.50, 68.60, 71.30, 76.70, 88.70, 93.20, 100.90,
]


# ── Every value traces to the published table ────────────────────────────


def test_transport_fuel_weekly_values_match_the_published_table():
    assert TRANSPORT_FUEL_SPEND.weekly_mean == pytest.approx(A6_TRANSPORT_FUEL_MEAN)
    weekly = [
        TRANSPORT_FUEL_SPEND.annual_by_decile[d] / config.WEEKS_PER_YEAR
        for d in range(1, 11)
    ]
    assert weekly == pytest.approx(A6_TRANSPORT_FUEL_BY_DECILE)


def test_food_weekly_values_match_the_published_table():
    assert FOOD_SPEND.weekly_mean == pytest.approx(A6_FOOD_MEAN)
    weekly = [
        FOOD_SPEND.annual_by_decile[d] / config.WEEKS_PER_YEAR for d in range(1, 11)
    ]
    assert weekly == pytest.approx(A6_FOOD_BY_DECILE)


def test_annual_means_are_the_weekly_figures_times_fifty_two():
    """The audit's finding: £1,300 and £5,000 were not these numbers (#12)."""
    assert config.BASE_FUEL_SPEND == pytest.approx(A6_TRANSPORT_FUEL_MEAN * 52)
    assert config.BASE_FOOD_SPEND == pytest.approx(A6_FOOD_MEAN * 52)
    assert config.BASE_FUEL_SPEND == pytest.approx(1_029.60)
    assert config.BASE_FOOD_SPEND == pytest.approx(3_666.00)


def test_decile_factors_are_ratios_to_the_published_mean():
    for decile in range(1, 11):
        assert config.FUEL_DECILE_FACTORS[decile] == pytest.approx(
            A6_TRANSPORT_FUEL_BY_DECILE[decile - 1] / A6_TRANSPORT_FUEL_MEAN
        )
        assert config.FOOD_DECILE_FACTORS[decile] == pytest.approx(
            A6_FOOD_BY_DECILE[decile - 1] / A6_FOOD_MEAN
        )


def test_spending_rises_monotonically_with_gross_income():
    for table in (TRANSPORT_FUEL_SPEND, FOOD_SPEND):
        amounts = [table.annual_by_decile[d] for d in range(1, 11)]
        assert amounts == sorted(amounts)


def test_source_metadata_records_units_period_and_hashes():
    metadata = source_metadata()
    assert "A6" in metadata["table"]
    assert metadata["reference_period"] == "financial year ending 2024"
    assert "per week" in metadata["units"]
    assert "gross household income decile" in metadata["grouping_variable"]
    assert metadata["workbook_url"].startswith("https://www.ons.gov.uk/")
    assert len(metadata["workbook_sha256"]) == 64
    assert len(metadata["csv_sha256"]) == 64


def test_a_missing_commodity_is_an_error_not_a_silent_default():
    with pytest.raises(LookupError):
        SpendingTable("cabbages", path=ONS_A6_PATH)


# ── Grouping: gross household income deciles ─────────────────────────────


def test_weighted_decile_splits_the_population_into_ten_equal_groups():
    values = np.arange(1_000.0)
    weights = np.ones(1_000)
    decile = _weighted_decile(values, weights)
    assert set(decile) == set(range(1, 11))
    counts = [int((decile == d).sum()) for d in range(1, 11)]
    assert counts == [100] * 10


def test_weighted_decile_orders_by_value():
    values = np.array([500.0, 100.0, 900.0])
    decile = _weighted_decile(values, np.ones(3))
    assert decile[1] < decile[0] < decile[2]


def test_weighted_decile_respects_weights():
    """Weight, not row count, determines the group boundaries."""
    values = np.array([1.0, 2.0, 3.0])
    heavy_bottom = _weighted_decile(values, np.array([100.0, 1.0, 1.0]))
    assert heavy_bottom[0] <= 5  # the heavy low-income household spans groups
    assert heavy_bottom[2] == 10


# ── Vehicle ownership ─────────────────────────────────────────────────────


def test_non_owners_get_no_transport_fuel_spending():
    spend = np.full(4, 1_000.0)
    decile = np.ones(4, dtype=int)
    owns = np.array([True, True, False, False])
    weights = np.ones(4)
    allocated = _allocate_to_vehicle_owners(spend, decile, owns, weights)
    assert np.all(allocated[~owns] == 0)
    assert np.all(allocated[owns] > 0)


def test_allocation_preserves_the_published_decile_mean():
    """Concentrating spending must not change how much is spent."""
    spend = np.full(4, 1_000.0)
    decile = np.ones(4, dtype=int)
    owns = np.array([True, True, False, False])
    weights = np.ones(4)
    allocated = _allocate_to_vehicle_owners(spend, decile, owns, weights)
    assert allocated.mean() == pytest.approx(spend.mean())
    # Half the households own a vehicle, so owners carry double the mean.
    assert allocated[owns] == pytest.approx(2_000.0)


def test_allocation_is_computed_within_each_decile():
    spend = np.array([100.0, 100.0, 900.0, 900.0])
    decile = np.array([1, 1, 2, 2])
    owns = np.array([True, False, True, True])
    weights = np.ones(4)
    allocated = _allocate_to_vehicle_owners(spend, decile, owns, weights)
    # Decile 1: one owner in two households carries both households' spending.
    assert allocated[0] == pytest.approx(200.0)
    # Decile 2: both own, so nothing is reallocated.
    assert allocated[2] == pytest.approx(900.0)


def test_a_decile_with_no_owners_keeps_its_spending():
    """Rather than discarding that decile's expenditure entirely."""
    spend = np.full(2, 500.0)
    allocated = _allocate_to_vehicle_owners(
        spend, np.ones(2, dtype=int), np.array([False, False]), np.ones(2)
    )
    assert allocated == pytest.approx(spend)
