"""
Core simulation pipeline for Iran war impact on UK living standards.

Loads the PolicyEngine UK microsimulation, computes multi-channel shocks
(energy, fuel, food, benefit erosion, fiscal drag), and evaluates policy
responses.
"""

import numpy as np
from collections import defaultdict
from microdf import MicroSeries

from .config import (
    YEAR,
    CURRENT_ENERGY_CAP,
    SCENARIOS,
    BASE_FUEL_SPEND,
    BASE_FOOD_SPEND,
    FUEL_DECILE_FACTORS,
    FOOD_DECILE_FACTORS,
    UPRATING_LAG_MONTHS,
    FUEL_POVERTY_THRESHOLD,
    FLAT_REBATE,
    CT_REBATE,
    UC_UPLIFT_WEEKLY,
    FUEL_DUTY_CUT_PENCE,
    MEAN_ANNUAL_LITRES,
    MEANS_TEST_THRESHOLD,
    MEANS_TEST_AMOUNT,
    SOCIAL_TARIFF_INCOME_THRESHOLD,
    SOCIAL_TARIFF_DISCOUNT,
    WEEKS_PER_YEAR,
    MONTHS_PER_YEAR,
    PENCE_PER_POUND,
    POVERTY_LINE_RATIO,
    WINNERS_LOSERS_THRESHOLD,
    EPG_CAP_PCT,
    REGION_TO_COUNTRY,
)


# ── Helpers ──────────────────────────────────────────────────────────────


def _vals(sim, var, year=YEAR, **kw):
    """Extract numpy array from sim.calculate, handling MicroSeries."""
    v = sim.calculate(var, year, **kw)
    return v if isinstance(v, np.ndarray) else v.values


def _ms(values, weights):
    """Create a MicroSeries for weighted calculations."""
    return MicroSeries(values, weights=weights)


def weighted_mean(values, weights, mask=None):
    """Weighted average using MicroSeries, optionally filtered by boolean mask."""
    if mask is not None:
        values = values[mask]
        weights = weights[mask]
    return float(_ms(values, weights).mean())


def weighted_sum(values, weights, mask=None):
    """Weighted sum using MicroSeries, optionally filtered by boolean mask."""
    if mask is not None:
        values = values[mask]
        weights = weights[mask]
    return float(_ms(values, weights).sum())


def _weighted_median(values, weights):
    """Weighted median using MicroSeries."""
    return float(_ms(values, weights).median())


def _safe_div(numerator, denominator):
    """Element-wise safe division returning 0 where denominator <= 0."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denominator > 0, numerator / denominator, 0.0)


def _decile_amount(decile, factors, base_amount):
    """Map income deciles onto absolute annual spending assumptions."""
    return np.array([base_amount * factors.get(int(d), 1.0) for d in decile])


# ── 1. Baseline ──────────────────────────────────────────────────────────


def _build_household_type(sim, year=YEAR):
    """Classify each household into type based on family_type + pensioner status."""
    hh_id_hh = _vals(sim, "household_id", year)
    hh_id_bu = _vals(sim, "household_id", year, map_to="benunit")
    hh_id_person = _vals(sim, "household_id", year, map_to="person")
    ft = _vals(sim, "family_type", year)
    is_sp = _vals(sim, "is_SP_age", year)

    # First benunit's family_type per household
    hh_ft = {}
    for i, hid in enumerate(hh_id_bu):
        if hid not in hh_ft:
            hh_ft[hid] = str(ft[i])

    # Any person at state pension age -> pensioner household
    hh_pensioner = defaultdict(bool)
    for i, hid in enumerate(hh_id_person):
        if is_sp[i]:
            hh_pensioner[hid] = True

    categories = []
    for hid in hh_id_hh:
        ftype = hh_ft.get(hid, "UNKNOWN")
        is_pen = hh_pensioner[hid]
        if ftype == "SINGLE" and is_pen:
            categories.append("SINGLE_PENSIONER")
        elif ftype == "COUPLE_NO_CHILDREN" and is_pen:
            categories.append("COUPLE_PENSIONER")
        elif ftype == "SINGLE":
            categories.append("SINGLE_WORKING_AGE")
        elif ftype == "COUPLE_NO_CHILDREN":
            categories.append("COUPLE_NO_CHILDREN")
        elif ftype == "COUPLE_WITH_CHILDREN":
            categories.append("COUPLE_WITH_CHILDREN")
        elif ftype == "LONE_PARENT":
            categories.append("LONE_PARENT")
        else:
            categories.append("OTHER")

    return np.array(categories)


def _build_uc_recipients(sim, year=YEAR):
    """Boolean array (household-level) indicating UC receipt and amount."""
    hh_id_hh = _vals(sim, "household_id", year)
    hh_id_bu = _vals(sim, "household_id", year, map_to="benunit")
    uc = _vals(sim, "universal_credit", year)

    hh_uc = defaultdict(float)
    for i, hid in enumerate(hh_id_bu):
        hh_uc[hid] += float(uc[i])

    uc_amount = np.array([hh_uc.get(hid, 0.0) for hid in hh_id_hh])
    return uc_amount > 0, uc_amount


def _build_ct_band(sim, year=YEAR):
    """Extract council tax band per household."""
    return _vals(sim, "council_tax_band", year)


def _build_benefit_income(sim, year=YEAR):
    """Aggregate major uprated benefit income per household."""
    hh_id_hh = _vals(sim, "household_id", year)
    hh_id_bu = _vals(sim, "household_id", year, map_to="benunit")
    hh_id_person = _vals(sim, "household_id", year, map_to="person")

    benunit_vars = [
        "universal_credit",
        "child_benefit",
        "housing_benefit",
        "pension_credit",
        "income_support",
    ]
    person_vars = [
        "state_pension",
        "attendance_allowance",
        "carers_allowance",
    ]

    hh_ben = defaultdict(float)
    for var in benunit_vars:
        values = _vals(sim, var, year)
        for i, hid in enumerate(hh_id_bu):
            hh_ben[hid] += float(values[i])

    for var in person_vars:
        values = _vals(sim, var, year)
        for i, hid in enumerate(hh_id_person):
            hh_ben[hid] += float(values[i])

    return np.array([hh_ben.get(hid, 0.0) for hid in hh_id_hh])



def run_baseline(year=YEAR):
    """Run baseline simulation and return dict of household-level arrays."""
    from policyengine_uk import Microsimulation

    sim = Microsimulation()

    energy = _vals(sim, "electricity_consumption", year) + _vals(sim, "gas_consumption", year)

    income = _vals(sim, "household_net_income", year)
    weights = _vals(sim, "household_weight", year, unweighted=True)
    decile = _vals(sim, "household_income_decile", year, unweighted=True)
    region = _vals(sim, "region", year)
    tenure = _vals(sim, "tenure_type", year)

    hh_type = _build_household_type(sim, year)
    is_uc, _ = _build_uc_recipients(sim, year)
    ct_band = _build_ct_band(sim, year)
    benefit_income = _build_benefit_income(sim, year)

    country_arr = np.array(
        [REGION_TO_COUNTRY.get(str(r), "UNKNOWN") for r in region]
    )

    fuel_cost = _decile_amount(decile, FUEL_DECILE_FACTORS, BASE_FUEL_SPEND)
    food_cost = _decile_amount(decile, FOOD_DECILE_FACTORS, BASE_FOOD_SPEND)

    return {
        "energy": energy,
        "income": income,
        "weights": weights,
        "decile": decile,
        "region": region,
        "tenure": tenure,
        "hh_type": hh_type,
        "country": country_arr,
        "is_uc": is_uc,
        "ct_band": ct_band,
        "benefit_income": benefit_income,
        "fuel_cost": fuel_cost,
        "food_cost": food_cost,
    }


# ── 2. Scenario shock computation ───────────────────────────────────────


def compute_scenario(data, scenario_key):
    """Compute multi-channel shock impacts for a given scenario.

    Returns a dict of per-household numpy arrays for each shock channel
    and the net total.
    """
    params = SCENARIOS[scenario_key]
    cap_increase_pct = params["cap_increase_pct"] / 100
    cpi_increase_pp = params["cpi_increase_pp"] / 100
    fuel_pct = params["fuel_pct"] / 100
    food_increase_pct = params["food_increase_pct"] / 100

    energy = data["energy"]
    fuel_cost = data["fuel_cost"]
    food_cost = data["food_cost"]
    benefit_income = data["benefit_income"]

    # Channel 1: Energy price shock
    energy_shock = energy * cap_increase_pct

    # Channel 2: Fuel (petrol/diesel) shock
    fuel_shock = fuel_cost * fuel_pct

    # Channel 3: Food pass-through
    food_shock = food_cost * food_increase_pct

    # Channel 4: Benefit erosion (uprating lag)
    benefit_erosion = benefit_income * cpi_increase_pp * (UPRATING_LAG_MONTHS / MONTHS_PER_YEAR)

    # Net impact (all positive = cost to household)
    net_impact = energy_shock + fuel_shock + food_shock + benefit_erosion

    return {
        "energy_shock": energy_shock,
        "fuel_shock": fuel_shock,
        "food_shock": food_shock,
        "benefit_erosion": benefit_erosion,
        "net_impact": net_impact,
    }


# ── 3. Policy responses ─────────────────────────────────────────────────


def compute_policies(data, scenario_key, scenario_impacts):
    """Compute the household-level savings from each policy response.

    Returns dict mapping policy name to per-household savings array.
    """
    params = SCENARIOS[scenario_key]
    cap_increase_pct = params["cap_increase_pct"] / 100
    energy = data["energy"]
    income = data["income"]
    is_uc = data["is_uc"]
    ct_band = data["ct_band"]
    weights = data["weights"]
    n = len(weights)

    policies = {}

    # Policy A: Energy Price Guarantee – cap energy increase
    capped_energy_cost = energy * EPG_CAP_PCT
    actual_energy_cost = energy * cap_increase_pct
    policies["energy_price_guarantee"] = np.maximum(
        0, actual_energy_cost - capped_energy_cost
    )

    # Policy B: Flat rebate – £400 to all households
    policies["flat_rebate"] = np.full(n, FLAT_REBATE, dtype=float)

    # Policy C: Council tax rebate – £300 to bands A-D
    ct_band_str = np.array([str(b) for b in ct_band])
    eligible_bands = {"A", "B", "C", "D"}
    ct_eligible = np.array([b in eligible_bands for b in ct_band_str])
    policies["ct_rebate"] = np.where(ct_eligible, CT_REBATE, 0.0)

    # Policy D: UC uplift – £25/week to UC recipients
    uc_annual = UC_UPLIFT_WEEKLY * WEEKS_PER_YEAR
    policies["uc_uplift"] = np.where(is_uc, uc_annual, 0.0)

    # Policy E: Fuel duty cut – 5p/litre × avg 1200 litres/year
    fuel_saving = FUEL_DUTY_CUT_PENCE / PENCE_PER_POUND * MEAN_ANNUAL_LITRES
    policies["fuel_duty_cut"] = np.full(n, fuel_saving, dtype=float)

    # Policy F: Means-tested payment – £650 to households < £25k income
    means_eligible = income < MEANS_TEST_THRESHOLD
    policies["means_tested_payment"] = np.where(
        means_eligible, MEANS_TEST_AMOUNT, 0.0
    )

    # Policy G: Accelerated uprating – eliminates benefit erosion
    policies["accelerated_uprating"] = scenario_impacts["benefit_erosion"].copy()

    # Policy H: Social tariff – 50% discount on energy shock for low-income/UC households
    social_tariff_eligible = is_uc | (income < SOCIAL_TARIFF_INCOME_THRESHOLD)
    social_tariff_benefit = scenario_impacts["energy_shock"] * SOCIAL_TARIFF_DISCOUNT
    policies["social_tariff"] = np.where(social_tariff_eligible, social_tariff_benefit, 0.0)

    # Policy I: Combined – all policies together (excluding social tariff)
    combined = np.zeros(n, dtype=float)
    for key in [
        "energy_price_guarantee",
        "flat_rebate",
        "ct_rebate",
        "uc_uplift",
        "fuel_duty_cut",
        "means_tested_payment",
        "accelerated_uprating",
    ]:
        combined = combined + policies[key]
    policies["combined"] = np.clip(combined, 0, scenario_impacts["net_impact"])

    return policies


def compute_policy_effects(data, scenario_key, scenario_impacts):
    """Compute fiscal benefits and fuel-poverty accounting components.

    Domestic energy subsidies reduce the numerator in the fuel-poverty ratio.
    Cash transfers raise the affordability denominator. Fuel-duty cuts reduce
    total living-standard pressure but do not directly affect domestic energy
    affordability.
    """
    policies = compute_policies(data, scenario_key, scenario_impacts)
    zeros = np.zeros_like(scenario_impacts["net_impact"])
    effects = {}
    for key, benefit in policies.items():
        effects[key] = {
            "benefit": benefit,
            "energy_reduction": zeros.copy(),
            "income_addition": zeros.copy(),
        }

    effects["energy_price_guarantee"]["energy_reduction"] = policies[
        "energy_price_guarantee"
    ]
    # Social tariff reduces energy bills directly
    effects["social_tariff"]["energy_reduction"] = policies["social_tariff"]
    for key in [
        "flat_rebate",
        "ct_rebate",
        "uc_uplift",
        "means_tested_payment",
        "accelerated_uprating",
    ]:
        effects[key]["income_addition"] = policies[key]

    combined_keys = [
        "energy_price_guarantee",
        "flat_rebate",
        "ct_rebate",
        "uc_uplift",
        "fuel_duty_cut",
        "means_tested_payment",
        "accelerated_uprating",
    ]
    combined_benefit = np.clip(
        sum((policies[key] for key in combined_keys), zeros.copy()),
        0,
        scenario_impacts["net_impact"],
    )
    effects["combined"] = {
        "benefit": combined_benefit,
        "energy_reduction": effects["energy_price_guarantee"]["energy_reduction"],
        "income_addition": sum(
            (effects[key]["income_addition"] for key in combined_keys),
            zeros.copy(),
        ),
    }
    return effects


# ── 4. Breakdowns ────────────────────────────────────────────────────────


def _impact_pct(net, income):
    return _safe_div(net, income) * 100


def _fuel_poverty_flags(energy, income):
    return _safe_div(energy, income) > FUEL_POVERTY_THRESHOLD


def _shocked_energy(data, impacts):
    """Energy bill after shock, before policy."""
    return np.maximum(
        data["energy"] + impacts["energy_shock"],
        0,
    )


def _by_decile(data, impacts, shocked_fuel_poor):
    weights = data["weights"]
    decile = data["decile"]
    income = data["income"]
    net = impacts["net_impact"]
    net_pct = _impact_pct(net, income)
    rows = []
    for d in range(1, 11):
        mask = decile == d
        rows.append({
            "decile": d,
            "mean_impact": round(weighted_mean(net, weights, mask)),
            "mean_impact_pct": round(weighted_mean(net_pct, weights, mask), 1),
            "energy": round(weighted_mean(impacts["energy_shock"], weights, mask)),
            "fuel": round(weighted_mean(impacts["fuel_shock"], weights, mask)),
            "food": round(weighted_mean(impacts["food_shock"], weights, mask)),
            "benefit_erosion": round(
                weighted_mean(impacts["benefit_erosion"], weights, mask)
            ),
            "fp_rate_pct": round(
                weighted_mean(shocked_fuel_poor.astype(float), weights, mask) * 100,
                1,
            ),
        })
    return rows


def _grouped_impacts(data, impacts, group_key, label_key, shocked_fuel_poor):
    weights = data["weights"]
    income = data["income"]
    net = impacts["net_impact"]
    net_pct = _impact_pct(net, income)
    rows = []
    for group in sorted(np.unique(data[group_key])):
        group_str = str(group)
        if not group_str or group_str in {"None", "UNKNOWN", "OTHER"}:
            continue
        mask = data[group_key] == group
        if weights[mask].sum() == 0:
            continue
        rows.append({
            label_key: group_str,
            "mean_impact": round(weighted_mean(net, weights, mask)),
            "mean_impact_pct": round(weighted_mean(net_pct, weights, mask), 1),
            "energy": round(weighted_mean(impacts["energy_shock"], weights, mask)),
            "fuel": round(weighted_mean(impacts["fuel_shock"], weights, mask)),
            "food": round(weighted_mean(impacts["food_shock"], weights, mask)),
            "benefit_erosion": round(
                weighted_mean(impacts["benefit_erosion"], weights, mask)
            ),
            "fp_rate_pct": round(
                weighted_mean(shocked_fuel_poor.astype(float), weights, mask) * 100,
                1,
            ),
        })
    return rows


def _fp_by_tenure(data, baseline_fuel_poor, shocked_fuel_poor):
    weights = data["weights"]
    rows = []
    for tenure in sorted(np.unique(data["tenure"])):
        tenure_str = str(tenure)
        if not tenure_str or tenure_str == "None":
            continue
        mask = data["tenure"] == tenure
        if weights[mask].sum() == 0:
            continue
        rows.append({
            "tenure": tenure_str,
            "baseline_fp_pct": round(
                weighted_mean(baseline_fuel_poor.astype(float), weights, mask) * 100,
                1,
            ),
            "shocked_fp_pct": round(
                weighted_mean(shocked_fuel_poor.astype(float), weights, mask) * 100,
                1,
            ),
        })
    return rows


def _channel_decomposition(data, impacts):
    weights = data["weights"]
    return {
        "energy_shock": round(weighted_mean(impacts["energy_shock"], weights)),
        "fuel_shock": round(weighted_mean(impacts["fuel_shock"], weights)),
        "food_shock": round(weighted_mean(impacts["food_shock"], weights)),
        "benefit_erosion": round(weighted_mean(impacts["benefit_erosion"], weights)),
        "net_impact": round(weighted_mean(impacts["net_impact"], weights)),
    }


def _eval_policy(data, impacts, policy_name, effect):
    weights = data["weights"]
    income = data["income"]
    decile = data["decile"]
    baseline_energy = data["energy"]
    net = impacts["net_impact"]
    shocked_energy = _shocked_energy(data, impacts)
    benefit = effect["benefit"]
    energy_reduction = effect["energy_reduction"]
    income_addition = effect["income_addition"]
    residual = np.maximum(net - benefit, 0)
    fp_energy = np.maximum(shocked_energy - energy_reduction, baseline_energy)
    fp_income = income + income_addition
    fp_after = _fuel_poverty_flags(fp_energy, fp_income)
    fp_before = _fuel_poverty_flags(shocked_energy, income)

    poverty_line = POVERTY_LINE_RATIO * _weighted_median(income, weights)
    shocked_income = income - net
    post_policy_income = income - residual
    lifted_out = (shocked_income < poverty_line) & (post_policy_income >= poverty_line)

    by_decile = []
    winners_losers = []
    change_vs_no_policy = net - residual
    for d in range(1, 11):
        mask = decile == d
        d_weights = weights[mask]
        d_change = change_vs_no_policy[mask]
        total_w = d_weights.sum()
        pct_winners = (
            float(d_weights[d_change > WINNERS_LOSERS_THRESHOLD].sum() / total_w * 100)
            if total_w > 0 else 0
        )
        pct_losers = (
            float(d_weights[d_change < -WINNERS_LOSERS_THRESHOLD].sum() / total_w * 100)
            if total_w > 0 else 0
        )
        by_decile.append({
            "decile": d,
            "mean_benefit": round(weighted_mean(benefit, weights, mask)),
            "mean_residual_impact": round(weighted_mean(residual, weights, mask)),
            "mean_benefit_pct_income": round(
                weighted_mean(_safe_div(benefit, income) * 100, weights, mask),
                1,
            ),
        })
        winners_losers.append({
            "decile": d,
            "pct_winners": round(pct_winners, 1),
            "pct_unchanged": round(100 - pct_winners - pct_losers, 1),
            "pct_losers": round(pct_losers, 1),
        })

    return {
        "name": policy_name,
        "fiscal_cost_bn": round(weighted_sum(benefit, weights) / 1e9, 2),
        "avg_benefit_per_hh": round(weighted_mean(benefit, weights)),
        "targeting_bottom3": round(
            weighted_sum(benefit, weights, decile <= 3)
            / weighted_sum(benefit, weights)
            * 100,
            1,
        )
        if weighted_sum(benefit, weights) > 0 else 0,
        "fp_rate_before_pct": round(weighted_mean(fp_before.astype(float), weights) * 100, 1),
        "fp_rate_after_pct": round(weighted_mean(fp_after.astype(float), weights) * 100, 1),
        "n_lifted_from_poverty": round(weighted_sum(lifted_out.astype(float), weights)),
        "by_decile": by_decile,
        "winners_losers": winners_losers,
    }


def _policy_responses(data, scenario_key, impacts):
    effects = compute_policy_effects(data, scenario_key, impacts)
    names = {
        "energy_price_guarantee": "Energy Price Guarantee",
        "flat_rebate": "Flat energy rebate",
        "ct_rebate": "Council tax rebate",
        "uc_uplift": "UC uplift",
        "fuel_duty_cut": "Fuel duty cut",
        "means_tested_payment": "Means-tested cost-of-living payment",
        "accelerated_uprating": "Accelerated benefit uprating",
        "social_tariff": "Social tariff",
        "combined": "Combined package",
    }
    output_keys = {
        "energy_price_guarantee": "epg",
        "means_tested_payment": "means_tested",
    }
    return {
        output_keys.get(key, key): _eval_policy(data, impacts, names[key], effect)
        for key, effect in effects.items()
    }


def _scenario_output(data, scenario_key):
    weights = data["weights"]
    income = data["income"]
    impacts = compute_scenario(data, scenario_key)
    net = impacts["net_impact"]
    gross = (
        impacts["energy_shock"]
        + impacts["fuel_shock"]
        + impacts["food_shock"]
        + impacts["benefit_erosion"]
    )
    baseline_energy = data["energy"]
    shocked_energy = _shocked_energy(data, impacts)
    baseline_fuel_poor = _fuel_poverty_flags(baseline_energy, income)
    shocked_fuel_poor = _fuel_poverty_flags(shocked_energy, income)
    poverty_line = POVERTY_LINE_RATIO * _weighted_median(income, weights)
    baseline_in_poverty = income < poverty_line
    shocked_in_poverty = (income - net) < poverty_line
    newly_poor = (~baseline_in_poverty) & shocked_in_poverty

    summary = {
        "mean_gross_impact": round(weighted_mean(gross, weights)),
        "mean_net_impact": round(weighted_mean(net, weights)),
        "mean_net_impact_pct": round(
            weighted_mean(_impact_pct(net, income), weights),
            1,
        ),
        "total_impact_bn": round(weighted_sum(net, weights) / 1e9, 1),
        "fp_rate_baseline_pct": round(
            weighted_mean(baseline_fuel_poor.astype(float), weights) * 100,
            1,
        ),
        "fp_rate_shocked_pct": round(
            weighted_mean(shocked_fuel_poor.astype(float), weights) * 100,
            1,
        ),
        "fp_extra_households": round(
            weighted_sum(shocked_fuel_poor.astype(float), weights)
            - weighted_sum(baseline_fuel_poor.astype(float), weights)
        ),
        "n_pushed_into_poverty": round(weighted_sum(newly_poor.astype(float), weights)),
    }

    return {
        "params": SCENARIOS[scenario_key],
        "summary": summary,
        "by_decile": _by_decile(data, impacts, shocked_fuel_poor),
        "by_region": _grouped_impacts(
            data, impacts, "region", "region", shocked_fuel_poor
        ),
        "by_tenure": _grouped_impacts(
            data, impacts, "tenure", "tenure", shocked_fuel_poor
        ),
        "by_country": _grouped_impacts(
            data, impacts, "country", "country", shocked_fuel_poor
        ),
        "by_hh_type": _grouped_impacts(
            data, impacts, "hh_type", "hh_type", shocked_fuel_poor
        ),
        "fp_by_tenure": _fp_by_tenure(
            data, baseline_fuel_poor, shocked_fuel_poor
        ),
        "channel_decomposition": _channel_decomposition(data, impacts),
    }, _policy_responses(data, scenario_key, impacts)


# ── 5. Full pipeline ────────────────────────────────────────────────────


def run_full_pipeline(year=YEAR, scenario_keys="all"):
    """Run the complete analysis pipeline.

    Parameters
    ----------
    year : int
        Tax year to simulate.
    scenario_keys : str
        Comma-separated scenario keys or "all".

    Returns
    -------
    dict
        Full results structure, JSON-serializable.
    """
    if scenario_keys == "all":
        keys = list(SCENARIOS.keys())
    else:
        keys = [k.strip() for k in scenario_keys.split(",")]

    data = run_baseline(year=year)
    weights = data["weights"]

    energy_share = _safe_div(data["energy"], data["income"])
    baseline_fuel_poor = _fuel_poverty_flags(data["energy"], data["income"])

    results = {
        "year": year,
        "current_energy_cap": CURRENT_ENERGY_CAP,
        "baseline": {
            "n_households_m": round(float(weights.sum()) / 1e6, 1),
            "mean_energy_spend": round(weighted_mean(data["energy"], weights)),
            "mean_net_income": round(weighted_mean(data["income"], weights)),
            "total_energy_spend_bn": round(
                weighted_sum(data["energy"], weights) / 1e9,
                1,
            ),
            "fuel_poverty_rate_pct": round(
                weighted_mean(baseline_fuel_poor.astype(float), weights) * 100,
                1,
            ),
            "fuel_poor_households": round(
                weighted_sum(baseline_fuel_poor.astype(float), weights)
            ),
            "by_decile": [
                {
                    "decile": d,
                    "mean_energy_spend": round(
                        weighted_mean(data["energy"], weights, data["decile"] == d)
                    ),
                    "mean_net_income": round(
                        weighted_mean(data["income"], weights, data["decile"] == d)
                    ),
                    "energy_share_pct": round(
                        weighted_mean(energy_share, weights, data["decile"] == d) * 100,
                        1,
                    ),
                    "fp_rate_pct": round(
                        weighted_mean(
                            baseline_fuel_poor.astype(float),
                            weights,
                            data["decile"] == d,
                        )
                        * 100,
                        1,
                    ),
                }
                for d in range(1, 11)
            ],
        },
        "scenarios": {},
        "policy_responses": {},
        "parameters": {
            "food_price_increase_pct": {
                key: SCENARIOS[key]["food_increase_pct"]
                for key in SCENARIOS
            },
            "base_fuel_spend": BASE_FUEL_SPEND,
            "base_food_spend": BASE_FOOD_SPEND,
            "fuel_poverty_threshold": FUEL_POVERTY_THRESHOLD,
        },
    }

    for key in keys:
        if key not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {key}")

        results["scenarios"][key], results["policy_responses"][key] = _scenario_output(
            data, key
        )

    return results
