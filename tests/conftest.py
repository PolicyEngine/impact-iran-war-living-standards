"""Synthetic fixtures for the pure calculation functions.

`run_baseline` is the only part of the pipeline that needs the managed
microsimulation. Everything downstream operates on a dict of household-level
numpy arrays, so it can be exercised on a hand-built population whose
expected results are computable by hand.
"""

import numpy as np
import pytest

from iran_impact import config


@pytest.fixture
def synthetic_data():
    """Ten households, one per income decile, with round numbers.

    Incomes ascend so that decile d has income d * 10,000; energy spend is a
    flat £1,000 so energy-shock arithmetic is checkable by inspection.
    """
    decile = np.arange(1, 11)
    n = len(decile)
    return {
        "bundle": None,
        "energy": np.full(n, 1_000.0),
        "electricity": np.full(n, 400.0),
        "income": decile * 10_000.0,
        "equiv_income": decile * 10_000.0,
        # HBAI income sits slightly below total net income, as it does in the
        # data: poverty is measured on it, affordability on the total.
        "hbai_income": decile * 9_000.0,
        "equiv_hbai_income": decile * 9_000.0,
        "people": np.full(n, 2.0),
        "weights": np.full(n, 1_000.0),
        "decile": decile,
        "quintile": (decile + 1) // 2,
        "region": np.array(["LONDON"] * n),
        "tenure": np.array(["RENT_PRIVATELY"] * n),
        "hh_type": np.array(["SINGLE_WORKING_AGE"] * n),
        "country": np.array(["ENGLAND"] * n),
        # The two lowest deciles receive UC and a means-tested benefit.
        "is_uc": decile <= 2,
        "is_means_tested": decile <= 2,
        "ct_band": np.array(["A", "B", "C", "D", "E", "F", "G", "H", "A", "B"]),
        "benefit_income": np.where(decile <= 2, 8_000.0, 0.0),
        # Only vehicle owners have road-fuel volumes; the top eight deciles
        # own one, so the bottom two have none.
        "owns_vehicle": decile > 2,
        "fuel_litres": np.where(decile > 2, 800.0, 0.0),
        "fuel_cost": np.array(
            [config.BASE_FUEL_SPEND * config.FUEL_DECILE_FACTORS[d] for d in decile]
        ),
        "food_cost": np.array(
            [config.BASE_FOOD_SPEND * config.FOOD_DECILE_FACTORS[d] for d in decile]
        ),
    }
