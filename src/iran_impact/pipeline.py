"""
Core simulation pipeline for energy price shock impact on UK living standards.

Loads the PolicyEngine UK microsimulation, computes multi-channel shocks
(energy, fuel, food, benefit uprating lag), and evaluates policy responses.
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
    UPRATING_LAG_FACTOR,
    FUEL_POVERTY_THRESHOLD,
    FLAT_REBATE,
    CT_REBATE,
    UC_UPLIFT_WEEKLY,
    FUEL_DUTY_CUT_PENCE,
    MEAN_ANNUAL_LITRES,
    MEANS_TEST_AMOUNT,
    ELEC_VAT_SAVING_RATE,
    SOCIAL_TARIFF_INCOME_THRESHOLD,
    SOCIAL_TARIFF_DISCOUNT,
    WEEKS_PER_YEAR,
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
    return np.array([base_amount * factors[int(d)] for d in decile])


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


def _build_means_tested_receipt(sim, year=YEAR):
    """Household receives any means-tested benefit (UC, Pension Credit,
    income-related legacy benefits) — the eligibility basis used for the 2022
    Cost of Living Payments."""
    hh_id_hh = _vals(sim, "household_id", year)
    hh_id_bu = _vals(sim, "household_id", year, map_to="benunit")

    hh_mt = defaultdict(float)
    for var in ["universal_credit", "pension_credit", "income_support", "housing_benefit"]:
        values = _vals(sim, var, year)
        for i, hid in enumerate(hh_id_bu):
            hh_mt[hid] += float(values[i])

    return np.array([hh_mt.get(hid, 0.0) for hid in hh_id_hh]) > 0


def _build_ct_band(sim, year=YEAR):
    """Extract council tax band per household."""
    return _vals(sim, "council_tax_band", year)


def _build_benefit_income(sim, year=YEAR):
    """Aggregate CPI-uprated benefit income per household.

    Deliberately EXCLUDES the state pension: it is uprated by the triple lock
    (April 2026: +4.8% via earnings), so it is not subject to the CPI uprating
    lag modelled in channel 4. Includes the major CPI-linked working-age and
    disability benefits available in PolicyEngine UK.
    """
    hh_id_hh = _vals(sim, "household_id", year)
    hh_id_bu = _vals(sim, "household_id", year, map_to="benunit")
    hh_id_person = _vals(sim, "household_id", year, map_to="person")

    benunit_vars = [
        "universal_credit",
        "child_benefit",
        "housing_benefit",
        "pension_credit",
        "income_support",
        "esa_income",
        "jsa_income",
    ]
    person_vars = [
        "pip",
        "dla",
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
    from policyengine.tax_benefit_models.uk import managed_microsimulation

    sim = managed_microsimulation()

    electricity = _vals(sim, "electricity_consumption", year)
    energy = electricity + _vals(sim, "gas_consumption", year)

    income = _vals(sim, "household_net_income", year)
    equiv_income = _vals(sim, "equiv_household_net_income", year)
    people = _vals(sim, "household_count_people", year)
    weights = _vals(sim, "household_weight", year, unweighted=True)
    # Clip deciles into 1-10: PolicyEngine assigns -1 to negative-income
    # households, which would otherwise be dropped from every decile loop.
    decile = np.clip(_vals(sim, "household_income_decile", year, unweighted=True), 1, 10)
    region = _vals(sim, "region", year)
    tenure = _vals(sim, "tenure_type", year)

    hh_type = _build_household_type(sim, year)
    is_uc, _ = _build_uc_recipients(sim, year)
    is_means_tested = _build_means_tested_receipt(sim, year)
    ct_band = _build_ct_band(sim, year)
    benefit_income = _build_benefit_income(sim, year)

    country_arr = np.array(
        [REGION_TO_COUNTRY.get(str(r), "UNKNOWN") for r in region]
    )

    fuel_cost = _decile_amount(decile, FUEL_DECILE_FACTORS, BASE_FUEL_SPEND)
    food_cost = _decile_amount(decile, FOOD_DECILE_FACTORS, BASE_FOOD_SPEND)

    return {
        "energy": energy,
        "electricity": electricity,
        "income": income,
        "equiv_income": equiv_income,
        "people": people,
        "weights": weights,
        "decile": decile,
        "region": region,
        "tenure": tenure,
        "hh_type": hh_type,
        "country": country_arr,
        "is_uc": is_uc,
        "is_means_tested": is_means_tested,
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

    # Channel 4: Benefit uprating lag — CPI-linked benefits are uprated each
    # April using the previous September's CPI, so their real value erodes
    # between the shock arriving and the next uprating. We apply the shock-period
    # CPI adder to CPI-linked benefit income (state pension excluded — triple
    # lock) scaled by an expected-lag factor of 0.5, representing the average
    # erosion over the year rather than the 12-month maximum.
    benefit_uprating_lag = benefit_income * cpi_increase_pp * UPRATING_LAG_FACTOR

    # Net impact (all positive = cost to household)
    net_impact = energy_shock + fuel_shock + food_shock + benefit_uprating_lag

    return {
        "energy_shock": energy_shock,
        "fuel_shock": fuel_shock,
        "food_shock": food_shock,
        "benefit_uprating_lag": benefit_uprating_lag,
        "net_impact": net_impact,
    }


# ── 3. Policy responses ─────────────────────────────────────────────────

COMBINED_KEYS = [
    "energy_price_guarantee",
    "flat_rebate",
    "ct_rebate",
    "uc_uplift",
    "fuel_duty_cut",
    "means_tested_payment",
    "accelerated_uprating",
    "elec_vat_cut",
]


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

    # Policy D: UC uplift – £20/week to UC recipients (2020-21 covid uplift rate)
    uc_annual = UC_UPLIFT_WEEKLY * WEEKS_PER_YEAR
    policies["uc_uplift"] = np.where(is_uc, uc_annual, 0.0)

    # Policy E: Fuel duty cut extension – 5p/litre × avg 1200 litres/year,
    # scaled by each household's imputed fuel spending so non-driving and
    # low-mileage households do not receive the flat average saving.
    mean_saving = FUEL_DUTY_CUT_PENCE / PENCE_PER_POUND * MEAN_ANNUAL_LITRES
    policies["fuel_duty_cut"] = mean_saving * data["fuel_cost"] / BASE_FUEL_SPEND

    # Policy F: Means-tested payment – £650 to households receiving a
    # means-tested benefit (the 2022 Cost of Living Payment eligibility basis)
    policies["means_tested_payment"] = np.where(
        data["is_means_tested"], MEANS_TEST_AMOUNT, 0.0
    )

    # Policy J: Electricity VAT cut (enacted Oct 2026–Mar 2027; modelled as a
    # full-year extension) – removes the 5% VAT on domestic electricity
    policies["elec_vat_cut"] = data["electricity"] * (1 + cap_increase_pct) * ELEC_VAT_SAVING_RATE

    # Policy G: Accelerated uprating – eliminates benefit uprating lag loss
    policies["accelerated_uprating"] = scenario_impacts["benefit_uprating_lag"].copy()

    # Policy H: Social tariff – 50% discount on energy shock for low-income/UC households
    social_tariff_eligible = is_uc | (income < SOCIAL_TARIFF_INCOME_THRESHOLD)
    social_tariff_benefit = scenario_impacts["energy_shock"] * SOCIAL_TARIFF_DISCOUNT
    policies["social_tariff"] = np.where(social_tariff_eligible, social_tariff_benefit, 0.0)

    # Policy I: Combined – all policies together (excluding social tariff).
    # The household benefit is capped at the size of the shock (a household
    # cannot be made better off than pre-shock for impact accounting), but the
    # UNCLIPPED sum is retained separately: government outlay does not shrink
    # when a household is over-compensated, so fiscal cost must use it.
    combined = np.zeros(n, dtype=float)
    for key in COMBINED_KEYS:
        combined = combined + policies[key]
    policies["combined"] = np.clip(combined, 0, scenario_impacts["net_impact"])
    policies["_combined_outlay"] = combined

    return policies


def compute_policy_effects(data, scenario_key, scenario_impacts):
    """Compute fiscal benefits and fuel-poverty accounting components.

    Domestic energy subsidies reduce the numerator in the fuel-poverty ratio.
    Cash transfers raise the affordability denominator. Fuel-duty cuts reduce
    total living-standard pressure but do not directly affect domestic energy
    affordability.
    """
    policies = compute_policies(data, scenario_key, scenario_impacts)
    combined_outlay = policies.pop("_combined_outlay")
    zeros = np.zeros_like(scenario_impacts["net_impact"])
    effects = {}
    for key, benefit in policies.items():
        effects[key] = {
            "benefit": benefit,
            "fiscal_outlay": benefit,
            "energy_reduction": zeros.copy(),
            "income_addition": zeros.copy(),
        }

    effects["energy_price_guarantee"]["energy_reduction"] = policies[
        "energy_price_guarantee"
    ]
    # Social tariff and the electricity VAT cut reduce energy bills directly
    effects["social_tariff"]["energy_reduction"] = policies["social_tariff"]
    effects["elec_vat_cut"]["energy_reduction"] = policies["elec_vat_cut"]
    for key in [
        "flat_rebate",
        "ct_rebate",
        "uc_uplift",
        "means_tested_payment",
        "accelerated_uprating",
    ]:
        effects[key]["income_addition"] = policies[key]

    effects["combined"]["fiscal_outlay"] = combined_outlay
    effects["combined"]["energy_reduction"] = (
        effects["energy_price_guarantee"]["energy_reduction"]
        + effects["elec_vat_cut"]["energy_reduction"]
    )
    effects["combined"]["income_addition"] = sum(
        (effects[key]["income_addition"] for key in COMBINED_KEYS),
        zeros.copy(),
    )
    return effects


# ── 4. Breakdowns ────────────────────────────────────────────────────────


def _impact_pct(net, income):
    return _safe_div(net, income) * 100


def _fuel_poverty_flags(energy, income):
    return _safe_div(energy, income) > FUEL_POVERTY_THRESHOLD


def _shocked_energy(data, impacts):
    """Energy bill after shock, before policy."""
    return data["energy"] + impacts["energy_shock"]


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
            "benefit_uprating_lag": round(
                weighted_mean(impacts["benefit_uprating_lag"], weights, mask)
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
        if not np.any(mask):
            continue
        rows.append({
            label_key: group_str,
            "mean_impact": round(weighted_mean(net, weights, mask)),
            "mean_impact_pct": round(weighted_mean(net_pct, weights, mask), 1),
            "energy": round(weighted_mean(impacts["energy_shock"], weights, mask)),
            "fuel": round(weighted_mean(impacts["fuel_shock"], weights, mask)),
            "food": round(weighted_mean(impacts["food_shock"], weights, mask)),
            "benefit_uprating_lag": round(
                weighted_mean(impacts["benefit_uprating_lag"], weights, mask)
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
        if not np.any(mask):
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
        "benefit_uprating_lag": round(weighted_mean(impacts["benefit_uprating_lag"], weights)),
        "net_impact": round(weighted_mean(impacts["net_impact"], weights)),
    }


def _poverty_line(data):
    """60% of median equivalised household net income (BHC), person-weighted.

    Uses PolicyEngine's equivalised income; the median is taken over people
    (household weight × household size) to match standard HBAI practice.
    """
    person_weights = data["weights"] * data["people"]
    return POVERTY_LINE_RATIO * _weighted_median(data["equiv_income"], person_weights)


def _equiv_after_cost(data, cost):
    """Approximate equivalised income after an annual consumption cost by
    scaling equivalised income with the household-level proportional loss."""
    scale = 1 - _safe_div(cost, data["income"])
    return data["equiv_income"] * np.clip(scale, 0, None)


def _eval_policy(data, impacts, policy_name, effect):
    weights = data["weights"]
    income = data["income"]
    decile = data["decile"]
    baseline_energy = data["energy"]
    net = impacts["net_impact"]
    shocked_energy = _shocked_energy(data, impacts)
    benefit = effect["benefit"]
    fiscal_outlay = effect["fiscal_outlay"]
    energy_reduction = effect["energy_reduction"]
    income_addition = effect["income_addition"]
    residual = np.maximum(net - benefit, 0)
    fp_energy = np.maximum(shocked_energy - energy_reduction, baseline_energy)
    fp_income = income + income_addition
    fp_after = _fuel_poverty_flags(fp_energy, fp_income)
    fp_before = _fuel_poverty_flags(shocked_energy, income)

    # Poverty: people (not households) below 60% of median equivalised income
    person_weights = weights * data["people"]
    poverty_line = _poverty_line(data)
    shocked_equiv = _equiv_after_cost(data, net)
    post_policy_equiv = _equiv_after_cost(data, residual)
    lifted_out = (shocked_equiv < poverty_line) & (post_policy_equiv >= poverty_line)

    total_benefit = weighted_sum(benefit, weights)
    by_decile = []
    winners_losers = []
    change_vs_no_policy = net - residual
    is_winner = (change_vs_no_policy > WINNERS_LOSERS_THRESHOLD).astype(float)
    is_loser = (change_vs_no_policy < -WINNERS_LOSERS_THRESHOLD).astype(float)
    for d in range(1, 11):
        mask = decile == d
        pct_winners = weighted_mean(is_winner, weights, mask) * 100
        pct_losers = weighted_mean(is_loser, weights, mask) * 100
        by_decile.append({
            "decile": d,
            "mean_benefit": round(weighted_mean(benefit, weights, mask)),
            "mean_residual_impact": round(weighted_mean(residual, weights, mask)),
            "mean_benefit_pct_income": round(
                weighted_mean(_safe_div(benefit, income) * 100, weights, mask),
                1,
            ),
            "benefit_share_pct": round(
                weighted_sum(benefit, weights, mask) / total_benefit * 100, 1
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
        "fiscal_cost_bn": round(weighted_sum(fiscal_outlay, weights) / 1e9, 2),
        "avg_benefit_per_hh": round(weighted_mean(benefit, weights)),
        "targeting_bottom3": round(
            weighted_sum(benefit, weights, decile <= 3) / total_benefit * 100,
            1,
        ),
        "fp_rate_before_pct": round(weighted_mean(fp_before.astype(float), weights) * 100, 1),
        "fp_rate_after_pct": round(weighted_mean(fp_after.astype(float), weights) * 100, 1),
        "n_lifted_from_poverty": round(
            weighted_sum(lifted_out.astype(float), person_weights)
        ),
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
        "fuel_duty_cut": "Fuel duty cut extension",
        "means_tested_payment": "Means-tested cost-of-living payment",
        "accelerated_uprating": "Accelerated benefit uprating",
        "elec_vat_cut": "Electricity VAT cut (extended)",
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
        + impacts["benefit_uprating_lag"]
    )
    baseline_energy = data["energy"]
    shocked_energy = _shocked_energy(data, impacts)
    baseline_fuel_poor = _fuel_poverty_flags(baseline_energy, income)
    shocked_fuel_poor = _fuel_poverty_flags(shocked_energy, income)
    # People (not households) pushed below 60% of median equivalised income
    person_weights = weights * data["people"]
    poverty_line = _poverty_line(data)
    baseline_in_poverty = data["equiv_income"] < poverty_line
    shocked_in_poverty = _equiv_after_cost(data, net) < poverty_line
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
        "n_pushed_into_poverty": round(
            weighted_sum(newly_poor.astype(float), person_weights)
        ),
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
        "metadata": {
            "cap_basis": (
                "Ofgem default tariff cap £1,663/yr, Jul-Sep 2026, new TDCV "
                "basis (≈£1,862 on the pre-July 2026 basis)"
            ),
            "fuel_poverty_definition": (
                "Indicative 10%-of-net-income energy spend ratio — not the "
                "official LILEE metric; not comparable with official statistics"
            ),
            "poverty_definition": (
                "People below 60% of median equivalised household net income "
                "(BHC), person-weighted"
            ),
        },
    }

    for key in keys:
        if key not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {key}")

        results["scenarios"][key], results["policy_responses"][key] = _scenario_output(
            data, key
        )

    return results
