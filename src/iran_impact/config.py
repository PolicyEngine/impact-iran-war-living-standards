"""Configuration constants for energy price shock impact on UK living standards analysis.

The stress tests are calibrated to conditions as of August 2026, during the
ongoing Middle East conflict (US/Israel-Iran war from late February 2026, with
recurrent Strait of Hormuz disruption). The forecast-based scenario takes the
forecasts published by FORECAST_AS_OF. Sources are cited inline.
"""

from .inputs import FOOD_SPEND, TRANSPORT_FUEL_SPEND

YEAR = 2027  # 2027-28 tax year — the year the Autumn Budget 2026 decisions apply to

# Ofgem default tariff cap, 1 Jul-30 Sep 2026, typical dual-fuel direct-debit
# household under Ofgem's NEW Typical Domestic Consumption Values (revised
# 1 Jul 2026). Equivalent to ~£1,862 on the pre-July TDCV basis — figures on
# the two bases are not comparable; this study uses the new basis throughout.
# Source: https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-july-and-30-september-2026
#
# DESCRIPTIVE ONLY. This figure is reported as context and does not enter any
# calculation: the model multiplies each household's own baseline gas and
# electricity expenditure by the scenario percentage, and never references a
# cap level (#13). It also does not represent unit rates, standing charges,
# gas/electric splits, region, payment method, fixed-tariff coverage or
# quarterly cap periods — see METHOD_LIMITATIONS.
CURRENT_ENERGY_CAP = 1_663

# ── Pre-conflict baseline ────────────────────────────────────────────────
#
# Every scenario percentage is expressed "relative to the pre-conflict
# early-2026 baseline". That baseline was previously stated only in prose, so
# the forcing assumptions could not be audited (#37). It is recorded here.
#
# The old-basis figure is stated outright by Ofgem, not derived: the July 2026
# press release says "The current price cap ... is £1,641" and "Under our
# existing TDCV, the typical household bill from July is £1,862 (up from
# £1,641)". It also matches PolicyEngine UK's own
# `gov.ofgem.energy_price_cap` parameter for 2026 onward.
#
# Consistency check: £1,862 / 1.135 = £1,640.5, which rounds to the published
# £1,641 — so the stated rise and the two TDCV bases agree.
#
# The new-basis figure is INFERRED, not published: Ofgem never gave Apr-Jun
# 2026 on the new TDCVs. £1,663 / 1.135 = £1,465 assumes the rebasing scales
# both quarters equally.
PRE_CONFLICT_CAP_NEW_BASIS = 1_465  # Apr-Jun 2026, new TDCV basis
PRE_CONFLICT_CAP_OLD_BASIS = 1_641  # same cap, pre-July basis; == PE UK's parameter

# Pre-conflict pump prices, OBSERVED as November 2025 monthly means in the
# DESNZ weekly road fuel price series. Monthly means are used at BOTH ends of
# the comparison below, so the two are on one basis. Source:
# https://www.gov.uk/government/statistics/weekly-road-fuel-prices
#
# These were previously BACK-DERIVED rather than observed: an assumed uniform
# "+20% since Autumn Budget 2025" was divided into stated August 2026 prices
# of ~157p/~187p. Both inputs were wrong, so both outputs were (#37):
#   - August 2026 was in fact ~161p petrol / ~182p diesel (monthly means).
#     The 187p was diesel's April 2026 conflict peak, not an August level;
#     diesel did not reach 187p in any August week.
#   - The rise was not uniform: +19.5% petrol but +26.5% diesel, because
#     middle-distillate cracks widened more than gasoline in this episode.
# The old constants were therefore ~5p LOW on petrol and ~11p HIGH on diesel,
# errors in opposite directions that a single uniform uplift could not catch.
#
# Duty was 52.95p/litre at both endpoints (the Autumn Budget 2025 extension of
# the 5p cut ran to 31 August 2026), so the comparison is duty-clean.
#
# NOTE the reference period differs from the cap figures above. These are
# Autumn Budget 2025 (November 2025), not April-June 2026, because that is the
# comparison the fuel scenario is anchored to.
# Stored unrounded: the derived rises below divide these, so rounding the
# constants first gave 19.3%/26.4% where the observed rises are 19.5%/26.5%.
PRE_CONFLICT_PETROL_PENCE = 135.04  # DESNZ November 2025 mean
PRE_CONFLICT_DIESEL_PENCE = 143.82  # DESNZ November 2025 mean
PRE_CONFLICT_PUMP_PRICE_PERIOD = "Autumn Budget 2025 (November 2025)"

# Observed August 2026 pump prices (DESNZ monthly means), recorded so the
# fuel scenarios can be audited against the move they actually represent
# rather than against a uniform assumption.
AUGUST_2026_PETROL_PENCE = 161.42  # DESNZ August 2026 mean
AUGUST_2026_DIESEL_PENCE = 181.98  # DESNZ August 2026 mean


def observed_petrol_rise_pct():
    """Observed Nov 2025 -> Aug 2026 petrol rise, from the DESNZ series."""
    return round(
        (AUGUST_2026_PETROL_PENCE / PRE_CONFLICT_PETROL_PENCE - 1) * 100, 1
    )


def observed_diesel_rise_pct():
    """Observed Nov 2025 -> Aug 2026 diesel rise, from the DESNZ series.

    Materially larger than petrol's; the model applies one fuel_pct to both,
    which METHOD_LIMITATIONS records.
    """
    return round(
        (AUGUST_2026_DIESEL_PENCE / PRE_CONFLICT_DIESEL_PENCE - 1) * 100, 1
    )


# ONS CPI basket weights for 2026, in parts per thousand, from the MM23
# time series: CJVF (04.5 electricity, gas and other fuels), CJXR (07.2.2
# fuels and lubricants) and CHZR (01 food and non-alcoholic beverages).
# Used to check each scenario's CPI adder against the first-round direct
# effect of its OWN price assumptions, which is checkable in one line by
# anyone reading the methodology (#37).
CPI_BASKET_WEIGHTS_2026 = {
    "energy": 0.03198,  # CJVF, 31.98 ppt
    "fuel": 0.02637,  # CJXR, 26.37 ppt
    "food": 0.10961,  # CHZR, 109.61 ppt
}


def direct_cpi_pp(scenario_key):
    """First-round direct CPI effect of a scenario's own price assumptions.

    Weight times price rise, summed over the three priced channels. This is a
    FLOOR, not a forecast: it excludes second-round effects, which push up,
    and demand destruction, which pushes down. The configured adder may
    legitimately differ, but if it sits below this the derivation has to say
    what offsets it (#37).
    """
    s = SCENARIOS[scenario_key]
    return first_round_cpi_pp(
        s["cap_increase_pct"], s["fuel_pct"], s["food_increase_pct"]
    )


def first_round_cpi_pp(energy_pct, fuel_pct, food_pct):
    """Weight times price rise, summed, for any three channel rises.

    The same arithmetic as direct_cpi_pp, for prices that are not yet a
    configured scenario: the forecast scenario's CPI range is the first-round
    effect at the ends of its price ranges.
    """
    w = CPI_BASKET_WEIGHTS_2026
    return round(
        energy_pct * w["energy"] + fuel_pct * w["fuel"] + food_pct * w["food"],
        2,
    )


def ceil_to_tenth(value):
    """Round up to one decimal place, so an adder never sits below its floor.

    Every CPI adder is its scenario's first-round floor rounded UP: 1.28 ->
    1.3, 3.09 -> 3.1, 5.23 -> 5.3. Rounding to nearest would put 1.84 at 1.8,
    below its own floor. The small epsilon stops binary representation
    (1.3 stored as 1.29999...) from rounding a tenth up to the next one.
    """
    import math

    return math.ceil(round(value * 10, 9)) / 10


def observed_energy_rise_by_sept_2026_pct():
    """The July 2026 cap against the pre-conflict cap, both on the new basis.

    This is what September 2026 CPI carries for household energy: the July-
    September cap is the one in force in that month, and the October cap
    (OCTOBER_2026_ENERGY_CAP) starts after it. Derived, so it cannot drift
    from the two cap constants.
    """
    return round((CURRENT_ENERGY_CAP / PRE_CONFLICT_CAP_NEW_BASIS - 1) * 100, 1)


# DESNZ weekly road fuel prices, 14 September 2026: the observation nearest
# ONS's mid-month index day for September 2026 CPI (#61 review A1).
# Source: https://www.gov.uk/government/statistics/weekly-road-fuel-prices
SEPTEMBER_2026_PETROL_PENCE = 168.14
SEPTEMBER_2026_DIESEL_PENCE = 190.72


def observed_fuel_rise_by_sept_2026_pct():
    """The spend-weighted petrol/diesel rise at the September 2026 index week.

    Same A1 expenditure shares as the fuel channel's composite, applied to the
    observed mid-September prices against November 2025. Other motor oils
    follow petrol, as in fuel_rise_pct_at_brent.
    """
    total = (
        PETROL_WEEKLY_SPEND + DIESEL_WEEKLY_SPEND + OTHER_MOTOR_OILS_WEEKLY_SPEND
    )
    petrol = SEPTEMBER_2026_PETROL_PENCE / PRE_CONFLICT_PETROL_PENCE - 1
    diesel = SEPTEMBER_2026_DIESEL_PENCE / PRE_CONFLICT_DIESEL_PENCE - 1
    rise = (
        (PETROL_WEEKLY_SPEND + OTHER_MOTOR_OILS_WEEKLY_SPEND) * petrol
        + DIESEL_WEEKLY_SPEND * diesel
    ) / total
    return round(rise * 100, 1)


# ONS CPI component indices (MM23, 2015=100), from the release of 16 September
# 2026, the latest before September 2026 CPI (#61 second review C1).
#   D7CH: 04.5 electricity, gas and other fuels
#   D7EC: 07.2.2 fuels and lubricants
# https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7ch/mm23
# https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7ec/mm23
# September 2025 is the annual reference for September 2026 CPI. August 2026
# is the latest published month and stands in for September until the
# September release (21 October 2026). The no-conflict counterfactual holds
# each component at its last pre-conflict level: energy at June 2026 (the
# April-June cap, announced before the conflict, the same baseline the energy
# scenarios use) and fuel at February 2026 (collected mid-February, before
# the conflict began).
ONS_CPI_ENERGY_INDEX = {"2025-09": 171.3, "2026-06": 168.3, "2026-08": 181.8}
ONS_CPI_FUEL_INDEX = {"2025-09": 122.3, "2026-02": 120.7, "2026-08": 150.6}
ONS_CPI_LATEST_MONTH = "2026-08"
CAPTURED_CPI_IS_PROXY = True  # flip when the September 2026 outturn replaces it


def captured_in_sept_2026_cpi_pp():
    """The conflict's contribution to the September 2026 ANNUAL CPI rate.

    April 2027 uprating is set from the September 2026 annual CPI rate, which
    compares September 2026 with September 2025. The conflict began in late
    February 2026, so that rate already carries part of the shock and April
    2027 uprating passes it on. Only the rest goes unindexed during 2027-28.

    Measured as the difference between the actual and the no-conflict
    contributions of each component to the annual rate:
        weight x (index_actual - index_counterfactual) / index_Sep2025
    on ONS component indices, so both legs share the September 2025
    reference (#61 second review C1). An earlier version multiplied a cap
    change and a pump-price change, measured from different months, by the
    basket weights, which is not an annual CPI contribution.

    A PROXY until September 2026 CPI is published: August 2026 stands in for
    September, and food is omitted for want of a counterfactual, so this is a
    lower bound on what is captured and the shortfall an upper bound.
    """
    w = CPI_BASKET_WEIGHTS_2026
    e, f = ONS_CPI_ENERGY_INDEX, ONS_CPI_FUEL_INDEX
    latest = ONS_CPI_LATEST_MONTH
    energy = (e[latest] - e["2026-06"]) / e["2025-09"] * 100
    fuel = (f[latest] - f["2026-02"]) / f["2025-09"] * 100
    return round(energy * w["energy"] + fuel * w["fuel"], 2)


def residual_cpi_pp(scenario_key, cpi_increase_pp=None):
    """The part of a scenario's CPI addition that April 2027 uprating misses.

    Never negative: a scenario whose addition is below what is already
    captured has no shortfall, rather than a negative one.
    """
    if cpi_increase_pp is None:
        cpi_increase_pp = SCENARIOS[scenario_key]["cpi_increase_pp"]
    return round(max(0.0, cpi_increase_pp - captured_in_sept_2026_cpi_pp()), 2)


# Petrol and diesel move differently, and ONS Table A6's fuel category is
# "Petrol, diesel and other motor oils" — one combined figure that the model
# multiplies by one percentage. Applying a petrol-only rate to it understates
# the shock for diesel, whose cracks widened far more in this episode (#55
# review C1).
#
# The split comes from the SAME ONS release and year as the £19.80 combined
# mean the model already uses: Family Spending FYE2024 Workbook 1 Table A1,
# sub-lines 7.2.2.1 and 7.2.2.2. It is an expenditure split, not a proxy.
PETROL_WEEKLY_SPEND = 12.10  # ONS A1 FYE2024, 7.2.2.1
DIESEL_WEEKLY_SPEND = 7.70  # ONS A1 FYE2024, 7.2.2.2
OTHER_MOTOR_OILS_WEEKLY_SPEND = 0.10  # 7.2.2.3, half a percent
# The sub-lines sum to £19.90 against A6's £19.80, because ONS rounds each to
# 10p. Only the shares are used, and the gap moves them by under half a point.

# Observed monthly means, both series on the same months so the periods match.
BRENT_NOV_2025 = 63.80  # EIA RBRTE monthly mean
BRENT_AUG_2026 = 91.08  # EIA RBRTE monthly mean
AUGUST_2026_DIESEL_OBSERVED = 181.98  # DESNZ August 2026 mean


def _pump_slope(pre_pence, aug_pence):
    """Pence per litre per $1/bbl, from monthly means at both ends."""
    return (aug_pence - pre_pence) / (BRENT_AUG_2026 - BRENT_NOV_2025)


def petrol_slope():
    return _pump_slope(PRE_CONFLICT_PETROL_PENCE, AUGUST_2026_PETROL_PENCE)


def diesel_slope():
    return _pump_slope(PRE_CONFLICT_DIESEL_PENCE, AUGUST_2026_DIESEL_PENCE)


def fuel_rise_pct_at_brent(brent_usd):
    """Expenditure-weighted rise in the combined A6 fuel category.

    Fixed-weight: the shares are baseline expenditure shares, so this is the
    percentage change in total category spend at unchanged volumes. No
    substitution and no volume response are modelled.
    """
    total = (
        PETROL_WEEKLY_SPEND
        + DIESEL_WEEKLY_SPEND
        + OTHER_MOTOR_OILS_WEEKLY_SPEND
    )
    moves = (
        (PETROL_WEEKLY_SPEND, PRE_CONFLICT_PETROL_PENCE, petrol_slope()),
        (DIESEL_WEEKLY_SPEND, PRE_CONFLICT_DIESEL_PENCE, diesel_slope()),
        # Other motor oils follow petrol; at 0.5% of the category the choice
        # moves the composite by under a tenth of a point.
        (
            OTHER_MOTOR_OILS_WEEKLY_SPEND,
            PRE_CONFLICT_PETROL_PENCE,
            petrol_slope(),
        ),
    )
    composite = 0.0
    for spend, base, slope in moves:
        rise = (base + slope * (brent_usd - BRENT_NOV_2025)) / base - 1
        composite += (spend / total) * rise
    return round(composite * 100, 1)


# Cornwall Insight's Q4 2026 forecast, superseded by the announced cap but
# still cited in the low-scenario derivation as what it was anchored to.
CORNWALL_Q4_FORECAST = 1_700


def cornwall_q4_vs_pre_conflict_pct():
    """The superseded Cornwall forecast as a percentage of the pre-conflict
    cap. Derived so the figure cannot go stale if the baseline moves (#40)."""
    return round(
        (CORNWALL_Q4_FORECAST / PRE_CONFLICT_CAP_NEW_BASIS - 1) * 100, 1
    )


def announced_oct_2026_vs_pre_conflict_pct():
    """The announced Oct-Dec 2026 cap as a percentage of the pre-conflict cap.

    Derived rather than written into prose in several places, so the figure
    cannot drift between the config, the registry and the dashboard (#37).
    """
    return round(
        (OCTOBER_2026_ENERGY_CAP / PRE_CONFLICT_CAP_NEW_BASIS - 1) * 100, 1
    )

# The announced Oct-Dec 2026 cap bounds the low scenario: it is +17.6% on
# PRE_CONFLICT_CAP_NEW_BASIS, so any case below that figure sits beneath an
# announced outturn. It is OCTOBER_2026_ENERGY_CAP, defined below — not
# duplicated here, so the two cannot drift apart.

# The subsequent cap period, published before this analysis was written.
# Source: https://www.ofgem.gov.uk/press-release/energy-price-cap-will-rise-4-october-2026
OCTOBER_2026_ENERGY_CAP = 1_723

# Share of accounts on fixed tariffs for the July 2026 cap period, which the
# cap does not set. Reported as context for the coverage limitation below.
# Source: https://www.ofgem.gov.uk/press-release/energy-price-cap-will-rise-13-july
FIXED_TARIFF_ACCOUNT_SHARE = 0.40

# ── Latest external forecasts ────────────────────────────────────────────
#
# The three scenarios below are stress tests: price levels this study chose
# and anchored to sources. The fourth, `external_forecast`, takes its prices
# from forecasts other organisations have published, so it can be reported as
# "if prices follow the latest published forecasts" rather than as an
# illustration. Each figure is copied from the source named beside it, with
# that source's publication date; the scenario's parameters are derived from
# them by the functions that follow, and a test recomputes every parameter
# from these figures, so a source update that is not carried through fails.
#
# What was looked for and not found is recorded too, because it decides where
# the scenario still rests on an explicit assumption:
#   - Cornwall Insight publishes no forecast for any cap quarter of 2027-28;
#     its latest covers January-March 2027 only.
#   - No published forecast of UK pump prices for 2027-28 was found. The
#     OBR's latest outlook (3 March 2026) used energy prices averaged to
#     22 January 2026, before the conflict, and its next is due 28 October
#     2026.
#   - No published forecast that isolates the conflict's effect on UK food
#     prices was found.
FORECAST_AS_OF = "2026-10-09"

# The gaps above, as data, so the dashboard states them next to the scenario.
FORECAST_GAPS = [
    "Cornwall Insight publishes no price cap forecast for any quarter of "
    "2027-28; its latest covers January-March 2027, which is held for the "
    "year.",
    "No published forecast of UK pump prices for 2027-28 was found. Fuel "
    "uses the US EIA's Brent forecast through this study's pass-through to "
    "pump prices, which carries the refining margins of 2026. The EIA "
    "forecasts US margins narrowing in 2027, so the fuel figure probably "
    "leans high. Its derivation gives four scalings to the EIA's own US "
    "price forecasts; all are lower, by amounts that differ.",
    "No published forecast that isolates the conflict's effect on UK food "
    "prices was found. Food uses the revision to IGD's forecast since "
    "before the conflict, which includes everything IGD revised for.",
    "The OBR's latest forecast (3 March 2026) used energy prices from before "
    "the conflict, so it is not used.",
]

# What the scenario assumes where the forecasts are silent, stated beside it
# on the dashboard rather than only inside a derivation: a reader comparing
# the cost with the fuel duty option needs the duty assumption in view (#67
# second review).
FORECAST_ASSUMPTIONS = [
    "Fuel duty stays at 52.95p a litre, the rate with the temporary 5p cut, "
    "as in the stress tests. Under current law it rises from January 2027. "
    "That rise is not in this scenario's cost, so the fuel duty option on "
    "the Policy options tab offsets a rise the cost here does not include.",
    "VAT on electricity is back at 5% from April 2027, as current law sets. "
    "Extending the zero rate is one of the policy options.",
    "Each forecast's last period is held where it stops short of March "
    "2028: Cornwall Insight's at January-March 2027, the EIA's at "
    "October-December 2027. IGD's revision for calendar 2027 stands for "
    "2027-28.",
]

# Scheduled publications that will supersede a figure here. The scenario
# should be refreshed when each lands.
FORECAST_NEXT_UPDATES = [
    {
        "source": "OBR Economic and fiscal outlook, with the Autumn Budget",
        "due": "2026-10-28",
        "url": "https://obr.uk/",
    },
    {
        "source": "Ofgem price cap for January-March 2027",
        "due": "2026-11",
        "url": "https://www.ofgem.gov.uk/energy-regulation/domestic-and-non-domestic/energy-pricing-rules/energy-price-cap",
    },
]

# Energy. Cornwall Insight's Default Tariff Cap forecast for January-March
# 2027: typical dual-fuel direct-debit household on Ofgem's new TDCVs
# (2,500 kWh electricity, 9,500 kWh gas), published 30 September 2026. The
# press release carries the figures; Cornwall's predictions page gives the
# pricing date, close of play on 28 September 2026. It is the latest Cornwall
# forecast and the only one beyond the announced October cap.
CORNWALL_FORECAST_URL = "https://www.cornwall-insight.com/press-releases/16-price-cap-rise-forecast-in-january/"
CORNWALL_PREDICTIONS_URL = "https://www.cornwall-insight.com/predictions-and-insights-into-the-default-tariff-cap/"
CORNWALL_FORECAST = {
    "period": "January-March 2027",
    "electricity_gbp": 959.44,
    "gas_gbp": 1_039.84,
    "total_gbp": 1_999.28,
    "published": "2026-09-30",
    "prices_as_of": "2026-09-28",
}

# Tax basis. Every scenario prices each channel at the tax rates of the
# reference point its percentage is measured from, so that a percentage is a
# change in price and not partly a change in tax: 5% VAT on electricity (the
# April-June 2026 cap, announced before the conflict) and 52.95p fuel duty
# (Autumn Budget 2025 pump prices).
#
# January-March 2027 falls inside the temporary zero rate of VAT on domestic
# electricity (1 October 2026 - 31 March 2027). Cornwall's release does not
# state its VAT basis; it is inferred here from Ofgem, whose October cap of
# £1,723 "reflect[s]" the VAT removal (about £45 on the typical bill) and is
# the base Cornwall's +16% is measured on. The forecast scenario restores 5%
# on electricity, the reference rate. That is also the rate current law sets
# from April 2027, and extending the cut is a policy option this study
# evaluates.
#
# Fuel duty is NOT treated the same way by current law: 52.95p is the
# reference rate, but duty is scheduled to rise from January 2027 (see
# FUEL_DUTY_CUT_PENCE), and the model's own 2027-28 rate is higher. Holding
# 52.95p therefore assumes the cut continues. The scheduled rise is outside
# every scenario's cost, the forecast scenario's included, and the fuel duty
# option's relief is measured against it.
ELECTRICITY_VAT_FROM_APRIL_2027 = 0.05

# Supplier forecasting services that reach into 2027-28, on the same TDCVs.
# Each supplier labels these its lowest-confidence forecasts. They set the
# energy parameter's uncertainty range, not its value, which follows the
# independent forecaster named above.
EON_NEXT_FORECAST_URL = "https://www.eonnext.com/electricity-and-gas/price-cap/predictions"
BRITISH_GAS_FORECAST_URL = "https://www.britishgas.co.uk/energy/price-cap.html"
SUPPLIER_CAP_FORECASTS_2027_28 = [
    {"supplier": "E.ON Next", "period": "April-June 2027", "total_gbp": 2_131,
     "published": "2026-10-05", "url": EON_NEXT_FORECAST_URL},
    {"supplier": "E.ON Next", "period": "July-September 2027", "total_gbp": 1_927,
     "published": "2026-10-05", "url": EON_NEXT_FORECAST_URL},
    {"supplier": "British Gas", "period": "April-June 2027", "total_gbp": 1_995,
     "published": "2026-10-01", "url": BRITISH_GAS_FORECAST_URL},
]


# The same services' forecasts for the quarter Cornwall covers, as context:
# both sit above Cornwall's £1,999.
SUPPLIER_CAP_FORECASTS_Q1_2027 = [
    {"supplier": "E.ON Next", "period": "January-March 2027", "total_gbp": 2_088,
     "published": "2026-10-05", "url": EON_NEXT_FORECAST_URL},
    {"supplier": "British Gas", "period": "January-March 2027", "total_gbp": 2_080,
     "published": "2026-10-01", "url": BRITISH_GAS_FORECAST_URL},
]


def cap_rise_pct(cap_gbp):
    """A typical annual bill as a rise on the pre-conflict cap, new basis."""
    return round((cap_gbp / PRE_CONFLICT_CAP_NEW_BASIS - 1) * 100, 1)


def forecast_cap_2027_28_gbp(forecast=None, vat=ELECTRICITY_VAT_FROM_APRIL_2027):
    """Cornwall's latest quarter, with electricity VAT at its 2027-28 rate.

    Held for all four 2027-28 cap quarters, because no Cornwall forecast
    covers any of them. That holding is the assumption, and the scenario's
    derivation says so.
    """
    f = forecast or CORNWALL_FORECAST
    return round(f["electricity_gbp"] * (1 + vat) + f["gas_gbp"], 2)


def forecast_energy_range_pct():
    """The lowest and highest supplier forecast for any 2027-28 quarter, each
    held for the year."""
    totals = [f["total_gbp"] for f in SUPPLIER_CAP_FORECASTS_2027_28]
    return [cap_rise_pct(min(totals)), cap_rise_pct(max(totals))]


# Road fuel. The US EIA's Short-Term Energy Outlook, October 2026 (released
# 6 October 2026, inputs finalised 1 October 2026), Table 2: Brent spot,
# quarterly averages in dollars a barrel. The STEO ends in December 2027.
EIA_STEO_URL = "https://www.eia.gov/outlooks/steo/archives/oct26.pdf"
EIA_STEO_BRENT = {
    "2027Q1": 94.90,
    "2027Q2": 87.00,
    "2027Q3": 80.03,
    "2027Q4": 73.94,
    "published": "2026-10-06",
    "inputs_finalised": "2026-10-01",
}
# 2027-28 runs April 2027 to March 2028. January-March 2028 lies beyond the
# STEO, so it holds the last forecast quarter.
FORECAST_BRENT_QUARTERS_2027_28 = ["2027Q2", "2027Q3", "2027Q4", "2027Q4"]

# The same table's US wholesale gasoline and diesel prices, dollars a gallon,
# with Brent for the quarters around the period the pump-price slopes were
# fitted on (November 2025 to August 2026). They are NOT used in
# the fuel parameter. They are recorded because they show what its
# pass-through leaves out: the slopes carry the widening of refining margins
# during 2026, and the EIA forecasts those margins narrowing in 2027. US
# wholesale margins are only a proxy for the UK's, which is why the figure is
# disclosed rather than applied.
EIA_STEO_BRENT_HISTORY = {"2025Q4": 63.63, "2026Q2": 102.93, "2026Q3": 95.95}
EIA_STEO_WHOLESALE = {
    "gasoline": {"2025Q4": 2.00, "2026Q2": 3.38, "2026Q3": 3.49, "2027Q2": 2.77, "2027Q3": 2.57, "2027Q4": 2.24},
    "diesel": {"2025Q4": 2.33, "2026Q2": 3.81, "2026Q3": 4.39, "2027Q2": 3.12, "2027Q3": 2.92, "2027Q4": 2.82},
}
# Retail prices including taxes, same table: regular gasoline and on-highway
# diesel. The pump price is a retail price, so the retail series is the
# nearer proxy; it narrows less than wholesale.
EIA_STEO_RETAIL = {
    "gasoline": {"2025Q4": 3.00, "2026Q2": 4.21, "2026Q3": 4.11, "2027Q2": 3.76, "2027Q3": 3.56, "2027Q4": 3.24},
    "diesel": {"2025Q4": 3.70, "2026Q2": 5.37, "2026Q3": 5.57, "2027Q2": 4.57, "2027Q3": 4.30, "2027Q4": 4.18},
}
GALLONS_PER_BARREL = 42


def eia_wholesale_margin(product, quarter=None):
    """US wholesale price less Brent, $/gallon, on the EIA table.

    With no quarter, the mean over 2027-28 on the same four quarters as the
    Brent path. Decimal arithmetic, rounded half up: in binary floats
    2.33 - 63.63/42 is 0.81499..., which prints as $0.81 for a margin that
    is exactly $0.815.
    """
    from decimal import ROUND_HALF_UP, Decimal

    brent = {**EIA_STEO_BRENT_HISTORY, **EIA_STEO_BRENT}
    prices = EIA_STEO_WHOLESALE[product]
    quarters = [quarter] if quarter else FORECAST_BRENT_QUARTERS_2027_28
    margins = [
        Decimal(str(prices[q])) - Decimal(str(brent[q])) / GALLONS_PER_BARREL
        for q in quarters
    ]
    mean = sum(margins) / len(margins)
    return float(mean.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _product_rises_at_brent(brent_usd):
    """Petrol and diesel pump-price rises at a Brent level, as fractions, on
    this study's slopes: the two terms fuel_rise_pct_at_brent combines."""
    change = brent_usd - BRENT_NOV_2025
    return {
        "gasoline": petrol_slope() * change / PRE_CONFLICT_PETROL_PENCE,
        "diesel": diesel_slope() * change / PRE_CONFLICT_DIESEL_PENCE,
    }


def eia_consistent_fuel_rise_pct(prices="retail", slope_end="2026Q3"):
    """What the fuel parameter would be if UK pump prices fell short of the
    2026 slope by as much as the EIA forecasts US prices to.

    Sizes the "leans high" disclosure; it is NOT the parameter. For each
    product, fit a two-point slope against Brent on the EIA's US series, the
    way this study's UK slopes are fitted (October-December 2025 to
    `slope_end`), see how much of the rise that slope predicts at the
    2027-28 Brent mean the EIA itself forecasts, and scale this study's UK
    rise by that share. Only the ratio crosses the Atlantic, so exchange
    rates and fixed US taxes drop out, but US refining and retail margins
    still stand in for the UK's.

    A two-point proxy, and it moves with the end point: July-September 2026
    is the quarter nearest the UK slopes' August end, and fitting to
    April-June instead gives a much smaller shortfall. So it shows the
    direction, not a size, and is not a second estimate. The direction holds
    for the composite; a single product can sit above its own slope
    (wholesale diesel does when the slope ends in April-June).
    """
    table = {"retail": EIA_STEO_RETAIL, "wholesale": EIA_STEO_WHOLESALE}[prices]
    brent = forecast_brent_2027_28()
    b0, b1 = EIA_STEO_BRENT_HISTORY["2025Q4"], EIA_STEO_BRENT_HISTORY[slope_end]
    uk = _product_rises_at_brent(brent)
    scaled = {}
    for product, series in table.items():
        slope = (series[slope_end] - series["2025Q4"]) / (b1 - b0)
        predicted = slope * (brent - b0)
        forecast = (
            sum(series[q] for q in FORECAST_BRENT_QUARTERS_2027_28)
            / len(FORECAST_BRENT_QUARTERS_2027_28)
            - series["2025Q4"]
        )
        scaled[product] = uk[product] * forecast / predicted
    total = (
        PETROL_WEEKLY_SPEND + DIESEL_WEEKLY_SPEND + OTHER_MOTOR_OILS_WEEKLY_SPEND
    )
    composite = (
        (PETROL_WEEKLY_SPEND + OTHER_MOTOR_OILS_WEEKLY_SPEND) * scaled["gasoline"]
        + DIESEL_WEEKLY_SPEND * scaled["diesel"]
    ) / total
    return round(composite * 100, 1)


def forecast_brent_2027_28():
    """Mean of the four quarters of 2027-28 on the EIA path, $/bbl."""
    path = [EIA_STEO_BRENT[q] for q in FORECAST_BRENT_QUARTERS_2027_28]
    return round(sum(path) / len(path), 2)


def forecast_fuel_range_pct():
    """The composite at the lowest and highest EIA quarter in 2027-28: the
    spread of the forecast's own path over the year, not a forecast error."""
    quarters = [EIA_STEO_BRENT[q] for q in set(FORECAST_BRENT_QUARTERS_2027_28)]
    return [
        fuel_rise_pct_at_brent(min(quarters)),
        fuel_rise_pct_at_brent(max(quarters)),
    ]


# Food. IGD's forecasts of UK retail food and drink inflation, calendar-year
# averages, low and high ends of each published range (midpoint is the mean).
# The last forecast before the conflict that reaches 2027 is IGD's 22 January
# 2026 outlook, which restates its November 2025 baseline for 2026; the
# latest is its 17 September 2026 forecast.
IGD_PRE_CONFLICT_URL = "https://www.igd.com/social-impact/economics/articles/food-inflation-2025-vs-2026-outlook/72283"
IGD_LATEST_URL = "https://www.igd.com/about-us/press-centre/articles/food-inflation-to-strengthen-in-2027-as-cost-pressures-build-igd-forecasts/74093"
IGD_FOOD_INFLATION_PRE_CONFLICT = {
    "published": "2026-01-22",
    "2026": (3.3, 4.3),
    "2027": (2.8, 3.8),
}
IGD_FOOD_INFLATION_LATEST = {
    "published": "2026-09-17",
    "2026": (2.9, 3.9),
    "2027": (5.6, 6.6),
    "2028": (5.3, 6.3),
}


def _igd_level_2027(vintage, end):
    """IGD's forecast 2027 food price level, relative to 2025, at the `end`
    ("low", "mid" or "high") of each year's published range."""
    level = 1.0
    for year in ("2026", "2027"):
        low, high = vintage[year]
        rate = {"low": low, "mid": (low + high) / 2, "high": high}[end]
        level *= 1 + rate / 100
    return level


def igd_food_revision_pct(
    latest="mid",
    pre_conflict="mid",
    latest_vintage=None,
    pre_conflict_vintage=None,
):
    """The revision to IGD's forecast 2027 food price level since its last
    pre-conflict forecast, in per cent.

    The model's food parameter is a price rise relative to a no-conflict
    path, not food inflation: normal inflation over the period would
    otherwise count as a shock. IGD published both paths, so the rise is
    their ratio. Calendar 2027 is the latest year both vintages cover. The
    vintages default to the recorded ones; tests pass others.
    """
    return round(
        (
            _igd_level_2027(latest_vintage or IGD_FOOD_INFLATION_LATEST, latest)
            / _igd_level_2027(
                pre_conflict_vintage or IGD_FOOD_INFLATION_PRE_CONFLICT,
                pre_conflict,
            )
            - 1
        )
        * 100,
        1,
    )


def forecast_food_range_pct():
    """Opposite ends of the two published ranges: the narrowest and widest
    revision IGD's own bands allow."""
    return [
        igd_food_revision_pct(latest="low", pre_conflict="high"),
        igd_food_revision_pct(latest="high", pre_conflict="low"),
    ]


def forecast_cpi_range_pp():
    """The first-round CPI effect at the low and high ends of the forecast
    scenario's three price ranges."""
    ends = list(
        zip(
            forecast_energy_range_pct(),
            forecast_fuel_range_pct(),
            forecast_food_range_pct(),
        )
    )
    # Rounded up, like every adder: rounding to nearest would put the high
    # end below its own first-round floor.
    return [ceil_to_tenth(first_round_cpi_pp(*end)) for end in ends]


def forecast_scenario_parameters():
    """Every forecast-scenario parameter, derived from the figures above.

    SCENARIOS records the same values as literals, like the stress tests, and
    a test holds the two equal: a source update must change both.
    """
    energy = cap_rise_pct(forecast_cap_2027_28_gbp())
    fuel = fuel_rise_pct_at_brent(forecast_brent_2027_28())
    food = igd_food_revision_pct()
    return {
        "cap_increase_pct": energy,
        "cpi_increase_pp": ceil_to_tenth(first_round_cpi_pp(energy, fuel, food)),
        "fuel_pct": fuel,
        "food_increase_pct": food,
    }


# Scenario calibration (relative to the pre-conflict early-2026 baseline).
# Anchors:
# - "low": the conflict's effect on prices as it stands, held for the year.
#   NOT a de-escalation below current levels: the announced Oct-Dec 2026 cap
#   of £1,723 is +17.6% on the pre-conflict £1,465, so +15% is slightly BELOW
#   the level already announced. It is best read as "the Q4-2026 premium
#   partially unwinds through 2027-28", not as prices falling back (#37).
#   Brent settles
#   near ~$85/bbl (4 Aug 2026 spot), pump prices ~161p petrol / ~182p diesel
#   (DESNZ August 2026 means; the ~187p previously quoted here was diesel's
#   April 2026 peak, not an August level)
#   (+19.5% petrol, +26.5% diesel on Autumn Budget 2025 levels), cap rise in line with the observed
#   +13.5% July 2026 increase. (An earlier Cornwall Insight Q4 forecast of
#   ~£1,700 also informed this figure, but has since been superseded by the
#   announced £1,723 — see the registry derivation.)
# - "central": sustained Strait of Hormuz constraint — Goldman Sachs scenario
#   of Brent averaging >$100/bbl through 2026 ($120 Q3 / $115 Q4 in the
#   extended-closure case), which sets the FUEL channel. The ENERGY channel is
#   anchored to gas, not oil: NBP/TTF roughly doubling, transmitted via halted
#   Qatari LNG. Oil-to-pump pass-through per Commons Library CBP-10601 applies
#   to pump prices only. CPI adder consistent with BoE June 2026 projection
#   moving from ~3% to the 4%+ range.
# - "severe": extended full closure / prolonged war — Goldman extreme-adverse
#   (Brent >$115-120) and the Oxford Economics escalation scenario, which
#   reports a 5.8% peak in world CPI under its two-month $140/bbl case. An
#   earlier version of this file described that scenario as raising world CPI
#   to 7.7%, which the source does not say (#13).
# Sources:
#   https://oilprice.com/Latest-Energy-News/World-News/Goldman-Another-Month-of-Hormuz-Closure-Means-Over-100-Brent-Throughout-2026.html
#   https://www.oxfordeconomics.com/resource/iran-war-scenarios-the-oil-price-that-breaks-parts-of-the-economy/
#   https://commonslibrary.parliament.uk/research-briefings/cbp-10601/
SCENARIOS = {
    "low_shock": {
        "cap_increase_pct": 15,
        "cpi_increase_pp": 1.3,
        "fuel_pct": 22,
        "food_increase_pct": 2.0,
    },
    "central_shock": {
        "cap_increase_pct": 45,
        "cpi_increase_pp": 3.1,
        "fuel_pct": 46,
        "food_increase_pct": 4.0,
    },
    "severe_shock": {
        "cap_increase_pct": 90,
        "cpi_increase_pp": 5.3,
        "fuel_pct": 62,
        "food_increase_pct": 6.5,
    },
    # Not a stress test: every price is built from a published forecast, as
    # derived by forecast_scenario_parameters() from the figures recorded
    # above. Literals, like the stress tests, so a changed source has to be
    # carried here deliberately; a test holds the two equal.
    "external_forecast": {
        "cap_increase_pct": 39.7,
        "cpi_increase_pp": 1.9,
        "fuel_pct": 12.2,
        "food_increase_pct": 2.3,
    },
}

# What each scenario is. The stress tests hold prices this study chose at a
# stated level for the year; the forecast scenario holds prices other
# organisations forecast. Both are annual: neither models a time path.
STRESS_TEST = "annual stress test"
FORECAST_BASED = "annual forecast-based scenario"
SCENARIO_TYPES = {
    "low_shock": STRESS_TEST,
    "central_shock": STRESS_TEST,
    "severe_shock": STRESS_TEST,
    "external_forecast": FORECAST_BASED,
}

# ── Parameter registry ───────────────────────────────────────────────────
#
# One entry per scenario input, recording what the number means, where it
# comes from and how it was derived. The scenario dictionaries above set these
# values directly; nothing in the repository previously showed the equations,
# pass-through coefficients, lags or durations linking the cited sources to
# them (#13).
#
# `derivation` states honestly how each figure was arrived at. Where it is a
# judgement anchored to a source rather than a calculation from it, it says
# so — these are stress-test assumptions, not estimates with standard errors.
#
# `lag` records the pass-through delay assumed. All of them are "none": the
# model applies every change as a full-year 2027-28 amount, which is a
# simplification of sources describing 2026 disruptions lasting months. See
# METHOD_LIMITATIONS.

OFGEM_JULY_2026 = "https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-july-and-30-september-2026"
OFGEM_OCTOBER_2026 = "https://www.ofgem.gov.uk/press-release/energy-price-cap-will-rise-4-october-2026"
DESNZ_ROAD_FUEL = "https://www.gov.uk/government/statistics/weekly-road-fuel-prices"
EIA_BRENT_MONTHLY = "https://www.eia.gov/dnav/pet/hist/RBRTEm.htm"
ONS_FAMILY_SPENDING_W1 = "https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/datasets/familyspendingworkbook1detailedexpenditureandtrends"
# Goldman's 8-9 April 2026 client note is not public; this is the report of
# it. No goldmansachs.com page carries the $120 Q3 / $115 Q4 figures.
GOLDMAN_HORMUZ = "https://oilprice.com/Latest-Energy-News/World-News/Goldman-Another-Month-of-Hormuz-Closure-Means-Over-100-Brent-Throughout-2026.html"
# The energy channel transmits through GAS, not oil, so it cites gas sources.
# Ofgem's wholesale allowance is built from NBP gas and UK baseload power
# forwards; crude oil enters the cap nowhere (#37).
KPLER_HORMUZ_LNG = "https://www.kpler.com/blog/hormuz-strait-disruptions-trigger-a-price-spike-in-ttf-and-asian-lng-while-middle-east-exports-come-to-a-halt"
OFGEM_CAP_METHODOLOGY = "https://www.ofgem.gov.uk/information-consumers/energy-advice-households/energy-price-cap"
OXFORD_ECONOMICS = "https://www.oxfordeconomics.com/resource/iran-war-scenarios-the-oil-price-that-breaks-parts-of-the-economy/"
COMMONS_FUEL_PRICES = "https://commonslibrary.parliament.uk/research-briefings/cbp-10601/"
COMMONS_UPRATING = "https://commonslibrary.parliament.uk/research-briefings/cbp-10403/"
BOE_JUNE_2026 = "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026"
NIESR_CONFLICT_CPI = "https://niesr.ac.uk/blog/possible-effects-uk-inflation-2026-us-iran-conflict"
# The 2026 basket weights direct_cpi_pp uses, from the MM23 release of
# 16 September 2026.
ONS_CPI_WEIGHT_ENERGY = "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/cjvf/mm23"
ONS_CPI_WEIGHT_FUEL = "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/cjxr/mm23"
ONS_CPI_WEIGHT_FOOD = "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/chzr/mm23"

# The name the dashboard shows for each source, so a reader sees who said it
# rather than a bare link. A test fails on any registry URL missing here.
SOURCE_NAMES = {
    OFGEM_JULY_2026: "Ofgem, price cap for July-September 2026",
    OFGEM_OCTOBER_2026: "Ofgem, price cap for October-December 2026",
    DESNZ_ROAD_FUEL: "DESNZ, weekly road fuel prices",
    EIA_BRENT_MONTHLY: "US EIA, Brent spot price (monthly)",
    ONS_FAMILY_SPENDING_W1: "ONS Family Spending, workbook 1",
    GOLDMAN_HORMUZ: "Goldman Sachs Hormuz-closure note, as reported by OilPrice.com",
    KPLER_HORMUZ_LNG: "Kpler, Hormuz LNG disruption",
    OXFORD_ECONOMICS: "Oxford Economics, Iran war scenarios",
    COMMONS_FUEL_PRICES: "House of Commons Library, CBP-10601",
    COMMONS_UPRATING: "House of Commons Library, CBP-10403",
    BOE_JUNE_2026: "Bank of England, Monetary Policy Summary, June 2026",
    NIESR_CONFLICT_CPI: "NIESR, effects of the US-Iran conflict on UK inflation",
    ONS_CPI_WEIGHT_ENERGY: "ONS, CPI weight: electricity, gas and other fuels",
    ONS_CPI_WEIGHT_FUEL: "ONS, CPI weight: fuels and lubricants",
    ONS_CPI_WEIGHT_FOOD: "ONS, CPI weight: food and non-alcoholic beverages",
    CORNWALL_FORECAST_URL: "Cornwall Insight, price cap forecast",
    CORNWALL_PREDICTIONS_URL: "Cornwall Insight, price cap predictions page",
    EON_NEXT_FORECAST_URL: "E.ON Next, price cap predictions",
    BRITISH_GAS_FORECAST_URL: "British Gas, price cap predictions",
    EIA_STEO_URL: "US EIA, Short-Term Energy Outlook, October 2026",
    IGD_LATEST_URL: "IGD, food inflation forecast, September 2026",
    IGD_PRE_CONFLICT_URL: "IGD, food inflation outlook, January 2026",
}

# How each parameter value was arrived at, so the dashboard can say which
# figures are someone's forecast and which are this study's choice.
BASIS_LABELS = {
    "forecast": "published forecast",
    # The forecast is of an input (Brent); the pump-price figure is this
    # study's, and must not be quoted as the forecaster's.
    "forecast_pass_through": "published Brent forecast, our pass-through",
    "observed": "observed prices",
    # As above for the stress tests: Goldman and Oxford Economics published
    # Brent cases, and the pump-price figures are this study's.
    "published_scenario_pass_through": "published Brent scenario, our pass-through",
    "judgement": "judgement",
    "derived": "derived from this scenario's prices",
}

_PARAMETER_DEFINITIONS = {
    "cap_increase_pct": {
        "definition": (
            "Percentage increase in household domestic gas and electricity "
            "expenditure, measured from its April-June 2026 level - the "
            "cap Ofgem announced on 25 February 2026, immediately before the "
            "conflict began. The period itself is not pre-conflict; the "
            "announcement is. The fuel channel uses a different baseline, "
            "the Autumn "
            "Budget 2025 pump prices; each parameter's reference_period "
            "states its own"
        ),
        "unit": "per cent",
        "geography": "United Kingdom",
        "applies_to": "each household's own baseline gas + electricity expenditure",
        "lag": "none — applied as a full-year 2027-28 amount",
    },
    "fuel_pct": {
        "definition": (
            "Percentage increase in household spending on the combined ONS "
            "category (petrol, diesel and other motor oils), measured from "
            "the Autumn Budget 2025 pump prices this file records. The "
            "energy channel uses a different baseline, April-June 2026; "
            "each parameter's reference_period states its own"
        ),
        "unit": "per cent",
        "geography": "United Kingdom",
        "applies_to": "modelled household transport-fuel expenditure (ONS Table A6)",
        "lag": "none — applied as a full-year 2027-28 amount",
    },
    "food_increase_pct": {
        "definition": (
            "Percentage increase in food and non-alcoholic drink prices from "
            "higher energy input costs"
        ),
        "unit": "per cent",
        "geography": "United Kingdom",
        "applies_to": "modelled household food expenditure (ONS Table A6)",
        "lag": "none — applied as a full-year 2027-28 amount",
    },
    "cpi_increase_pp": {
        "definition": (
            "Addition to UK CPI inflation against a no-conflict path, measured "
            "from pre-conflict prices. Not a forecast of the headline rate: it "
            "is set from the scenario's own price assumptions (see "
            "first_round_floor_pp). Used only to size the real-terms erosion "
            "of CPI-linked benefits, and so the accelerated-uprating policy. "
            "Part of it is already in September 2026 CPI, which sets April "
            "2027 uprating; only the residual goes unindexed"
        ),
        "unit": "percentage points",
        "geography": "United Kingdom",
        "applies_to": "CPI-linked benefit income, excluding the state pension",
        "lag": "none — applied as a full-year 2027-28 amount",
    },
}

_SCENARIO_SOURCES = {
    "low_shock": {
        "narrative": (
            "Prices settle near their current elevated levels rather than "
            "falling back, from the August 2026 position: Brent settles "
            "near $85/bbl, pump prices around 161p petrol and 182p diesel "
            "(DESNZ August 2026 means)"
        ),
        "cap_increase_pct": {
            "source_url": OFGEM_JULY_2026,
            "basis": "judgement",
            "source_date": "2026-07-01",
            "reference_period": "1 July - 30 September 2026 cap period",
            "derivation": (
                "Judgement, anchored to the observed +13.5% July 2026 cap "
                "rise. Not "
                "a de-escalation: on the pre-conflict "
                f"£{PRE_CONFLICT_CAP_NEW_BASIS:,} baseline this "
                f"sits below the announced Oct-Dec 2026 cap of "
                f"£{OCTOBER_2026_ENERGY_CAP:,} "
                f"(+{announced_oct_2026_vs_pre_conflict_pct()}%), so it "
                "represents the Q4-2026 premium partially "
                "unwinding through 2027-28 rather than prices returning to "
                "pre-conflict levels. Cornwall Insight's earlier "
                f"~£{CORNWALL_Q4_FORECAST:,} Q4 "
                f"forecast (+{cornwall_q4_vs_pre_conflict_pct()}% on this "
                "baseline) has been superseded by "
                "that announcement (#37)"
            ),
            "uncertainty_range": [13, 20],
        },
        "fuel_pct": {
            "source_url": COMMONS_FUEL_PRICES,
            "basis": "observed",
            "source_date": "2026-08-04",
            "reference_period": (
                "November 2025 to August 2026 monthly means"
            ),
            "derivation": (
                "Observed change in the combined ONS fuel category between "
                "Autumn Budget 2025 and August 2026, on DESNZ monthly means: "
                "petrol rose 19.5% and diesel 26.5%, which on the FYE2024 "
                "Table A1 expenditure shares of 61% petrol and 39% diesel is "
                "a 22% composite. Set to that. An earlier version used the "
                "petrol figure alone, which understates a category that is "
                "39% diesel (#55 review C1)"
            ),
            "supporting_source_urls": [
                DESNZ_ROAD_FUEL,
                ONS_FAMILY_SPENDING_W1,
            ],
            "uncertainty_range": [15, 25],
        },
        "food_increase_pct": {
            "source_url": COMMONS_FUEL_PRICES,
            "basis": "judgement",
            "source_date": "2026-08-04",
            "reference_period": "2027-28",
            "derivation": (
                "Judgement: food price response to energy prices settling "
                "near current levels; no published scenario for this figure"
            ),
            "uncertainty_range": [1.0, 3.0],
        },
        "cpi_increase_pp": {
            "source_url": BOE_JUNE_2026,
            "basis": "derived",
            "source_date": "2026-06-01",
            "reference_period": "2027-28 level against a no-conflict path (source figure is 2026-27)",
            "derivation": (
                "Bank of England June 2026 projection of CPI near 3% against "
                "about 2% pre-conflict, i.e. roughly +1pp. Raised to 1.3pp so "
                "the adder is not below the first-round direct effect of this "
                "scenario's own price assumptions, which ONS 2026 basket "
                f"weights put at {direct_cpi_pp('low_shock')}pp (#37)"
            ),
            "uncertainty_range": [1.0, 1.8],
        },
    },
    "central_shock": {
        "narrative": (
            "Sustained Strait of Hormuz constraint: Goldman Sachs scenario of "
            "Brent averaging above $100/bbl through 2026"
        ),
        "cap_increase_pct": {
            "source_url": KPLER_HORMUZ_LNG,
            "basis": "judgement",
            "source_date": "2026-03-10",  # Kpler LNG page
            "reference_period": "NBP/TTF sustained at ~2x pre-conflict",
            "derivation": (
                "Judgement: NBP/TTF gas sustained at roughly twice "
                "pre-conflict levels across the 2027-28 cap assessment "
                "windows, as the Hormuz closure halts Qatari LNG (~19% of "
                "global LNG exports). Wholesale is ~40-45% of the cap, so a "
                "doubling of wholesale implies ~+45% on the retail bill. "
                "Anchored to gas rather than to Brent because Ofgem's "
                "wholesale allowance is built from NBP gas and UK baseload "
                "power forwards and crude oil enters it nowhere; in this "
                "episode oil flows recovered to about two-thirds of pre-war "
                "levels while LNG stayed halted, so an oil anchor would if "
                "anything understate the gas shock. The pass-through "
                "coefficient and hedging lag remain judgements"
            ),
            "uncertainty_range": [30, 60],
        },
        "fuel_pct": {
            "source_url": COMMONS_FUEL_PRICES,
            "basis": "published_scenario_pass_through",
            "source_date": "2026-07-01",
            "reference_period": "Goldman Q3 2026 Brent of $120/bbl",
            "derivation": (
                "Expenditure-weighted pump response to the Goldman "
                "extended-closure case, on the same basis as the severe "
                "scenario so one registry gives one basis for this channel. "
                "Petrol and diesel are derived separately and combined by "
                "their shares of ONS Family Spending FYE2024 Table A1 lines "
                "7.2.2.1 and 7.2.2.2 (£12.10 petrol, £7.70 diesel of the "
                "£19.80 category this model already uses), because A6 gives "
                "one combined figure and the two products moved very "
                "differently. DESNZ monthly mean pump prices moved 135.04p "
                "to 161.42p for petrol and 143.82p to 181.98p for diesel "
                "between November 2025 and August 2026, while EIA monthly "
                "mean Brent moved $63.80 to $91.08 over the same months: "
                "slopes of ~0.97 and ~1.40p/litre per $1/bbl. At Goldman's "
                "$120 Q3 figure that gives +40% petrol, +55% diesel and a "
                "+46% composite. Both series are monthly means, so the "
                "periods match; earlier versions paired monthly pump means "
                "with a single-day Brent spot, and then applied a "
                "petrol-only slope to the combined category (#52 review C2, "
                "#55 review C1). Commons Library CBP-10601 informed the "
                "pass-through framing; the coefficients are this study's"
            ),
            "supporting_source_urls": [
                DESNZ_ROAD_FUEL,
                EIA_BRENT_MONTHLY,
                ONS_FAMILY_SPENDING_W1,
                GOLDMAN_HORMUZ,
            ],
            "uncertainty_range": [30, 60],
        },
        "food_increase_pct": {
            "source_url": COMMONS_FUEL_PRICES,
            "basis": "judgement",
            "source_date": "2026-07-01",
            "reference_period": "2027-28",
            "derivation": (
                "Judgement: food price response to sustained higher energy "
                "input costs, no published scenario for this figure"
            ),
            "uncertainty_range": [2.5, 5.5],
        },
        "cpi_increase_pp": {
            "source_url": NIESR_CONFLICT_CPI,
            "basis": "derived",
            "source_date": "2026-03-23",
            "reference_period": "2027-28 level against a no-conflict path (NIESR's figures are CPI rates reached from July 2026)",
            "derivation": (
                "Set at the first-round price-level effect of this "
                "scenario's own energy, fuel and food rises on ONS 2026 "
                f"basket weights, {direct_cpi_pp('central_shock')}pp, "
                "rounded. For context, NIESR's scenarios have CPI reaching "
                "about 3% (optimistic), 4% (central) or 5% (pessimistic) "
                "from July 2026; those are total rates that include NIESR's "
                "own assumption of 3-4% inflation from other sources, so "
                "they do not convert into a conflict addition by "
                "subtracting a 2% baseline. Not a floor on annual inflation, "
                "which also depends on timing, second-round effects and "
                "demand (#37, #56)"
            ),
            "uncertainty_range": [2.5, 4.1],
        },
    },
    "severe_shock": {
        "narrative": (
            "Extended full closure or prolonged war: Goldman extreme-adverse "
            "case and the Oxford Economics escalation scenario"
        ),
        "cap_increase_pct": {
            "source_url": KPLER_HORMUZ_LNG,
            "basis": "judgement",
            "source_date": "2026-03-10",  # Kpler LNG page
            "reference_period": "NBP/TTF sustained at ~3x pre-conflict",
            "derivation": (
                "Judgement: NBP/TTF gas sustained at roughly triple "
                "pre-conflict levels across the 2027-28 assessment windows "
                "(~+200% wholesale on a ~40-45% share), under the Oxford "
                "Economics escalation case. Not derived from a published cap "
                "projection. For precedent, the announced October 2022 cap of "
                "£3,549 was +178% year-on-year on October 2021's £1,277 under "
                "a comparable gas-supply shock, so a tripling of wholesale is "
                "within recent experience. Anchored to gas rather than Brent, "
                "for the reason given on the central scenario"
            ),
            "uncertainty_range": [60, 120],
        },
        "fuel_pct": {
            "source_url": OXFORD_ECONOMICS,
            "basis": "published_scenario_pass_through",
            "source_date": "2026-03-13",  # Oxford page datePublished
            "reference_period": "two-month $140/bbl case",
            "derivation": (
                "Expenditure-weighted pump response at Brent of $140/bbl. "
                "The source publishes no pump-price figure, so the "
                "pass-through is this study's. Petrol and diesel are derived "
                "separately from DESNZ monthly means against EIA monthly "
                "mean Brent (slopes ~0.97 and ~1.40p/litre per $1/bbl) and "
                "combined by their ONS Family Spending FYE2024 Table A1 "
                "expenditure shares, 61% petrol and 39% diesel. At $140 that "
                "gives +55% petrol, +74% diesel and a +62% composite, which "
                "is where this is set. Diesel cracks widened far more than "
                "gasoline in this episode, which is why a petrol-only rate "
                "understated the combined category (#55 review C1). The "
                "slopes embed that widening as well as crude cost, which is "
                "why they exceed the ~0.56p/litre that $1/bbl contributes "
                "through crude and VAT alone; fuel duty is a fixed "
                "52.95p/litre and damps the percentage rise"
            ),
            "supporting_source_urls": [
                DESNZ_ROAD_FUEL,
                EIA_BRENT_MONTHLY,
                ONS_FAMILY_SPENDING_W1,
                GOLDMAN_HORMUZ,
            ],
            "uncertainty_range": [50, 80],
        },
        "food_increase_pct": {
            "source_url": OXFORD_ECONOMICS,
            "basis": "judgement",
            "source_date": "2026-03-13",  # Oxford page datePublished
            "reference_period": "2027-28",
            "derivation": (
                "Judgement: food price response under a global recession "
                "scenario, no published figure for UK food prices"
            ),
            "uncertainty_range": [4.0, 9.0],
        },
        "cpi_increase_pp": {
            "source_url": OXFORD_ECONOMICS,
            "basis": "derived",
            "source_date": "2026-03-13",  # Oxford page datePublished
            "reference_period": "two-month $140/bbl case",
            "derivation": (
                "The source reports a 5.8% peak in WORLD CPI, roughly 3pp "
                "above its baseline. Set to 5.3pp for UK CPI, at the "
                "first-round direct effect of this scenario's own price "
                f"assumptions, which ONS 2026 basket weights put at "
                f"{direct_cpi_pp('severe_shock')}pp and which exceeds the "
                "~3pp world figure, consistent with the UK's higher energy "
                "import share. The source "
                "does not publish a UK figure, and does not report the 7.7% "
                "this file previously attributed to it"
            ),
            "uncertainty_range": [4.5, 7.0],
        },
    },
    "external_forecast": {
        "narrative": (
            "Prices follow the latest published forecasts as of "
            f"{FORECAST_AS_OF}: Cornwall Insight for the energy price cap, "
            "the US EIA for Brent crude and IGD for food. Where a forecast "
            "stops short of 2027-28 its last period is held, as each "
            "parameter's derivation states"
        ),
        "cap_increase_pct": {
            "source_url": CORNWALL_FORECAST_URL,
            "basis": "forecast",
            "source_date": CORNWALL_FORECAST["published"],
            "source_figure": (
                f"£{CORNWALL_FORECAST['total_gbp']:,.2f} a year for "
                f"{CORNWALL_FORECAST['period']} (electricity "
                f"£{CORNWALL_FORECAST['electricity_gbp']:,.2f}, gas "
                f"£{CORNWALL_FORECAST['gas_gbp']:,.2f}). Cornwall's predictions "
                "page dates the prices to close of play on 28 September 2026"
            ),
            "reference_period": (
                f"{CORNWALL_FORECAST['period']} forecast, held for the four "
                "2027-28 cap quarters"
            ),
            "derivation": (
                "Cornwall Insight's latest forecast, for "
                f"{CORNWALL_FORECAST['period']}, is "
                f"£{CORNWALL_FORECAST['total_gbp']:,.2f}. That quarter falls "
                "inside the zero rate of VAT on domestic electricity, which "
                "ends on 31 March 2027. Cornwall does not state its VAT "
                "basis; it is inferred from Ofgem, whose October cap "
                "reflects the VAT removal and is the base Cornwall's rise is "
                "measured on. Electricity is restored to "
                f"{ELECTRICITY_VAT_FROM_APRIL_2027:.0%} VAT, the rate in the "
                "April-June 2026 cap this is measured from: "
                f"£{forecast_cap_2027_28_gbp():,.2f}, "
                f"+{cap_rise_pct(forecast_cap_2027_28_gbp())}% on that cap's "
                f"£{PRE_CONFLICT_CAP_NEW_BASIS:,}. Cornwall "
                "publishes no forecast for any 2027-28 quarter, so this one "
                "is held for all four. That holding is an assumption, not a "
                "forecast, and it carries no change in network or policy "
                "costs after that quarter. A winter quarter is being held "
                "through a summer: supplier forecasting services that do "
                "reach April-September 2027, each at its lowest confidence, "
                "run from "
                f"£{min(f['total_gbp'] for f in SUPPLIER_CAP_FORECASTS_2027_28):,} "
                f"to £{max(f['total_gbp'] for f in SUPPLIER_CAP_FORECASTS_2027_28):,}"
                ". Each of those single quarters, held for the year, sets "
                "one end of the range. For January-March 2027 itself the "
                "same services forecast "
                f"£{min(f['total_gbp'] for f in SUPPLIER_CAP_FORECASTS_Q1_2027):,} "
                f"and £{max(f['total_gbp'] for f in SUPPLIER_CAP_FORECASTS_Q1_2027):,}"
                ", above Cornwall"
            ),
            "supporting_source_urls": [
                CORNWALL_PREDICTIONS_URL,
                OFGEM_OCTOBER_2026,
                EON_NEXT_FORECAST_URL,
                BRITISH_GAS_FORECAST_URL,
            ],
            "uncertainty_range": forecast_energy_range_pct(),
        },
        "fuel_pct": {
            "source_url": EIA_STEO_URL,
            "basis": "forecast_pass_through",
            "source_date": EIA_STEO_BRENT["published"],
            "source_figure": (
                f"Brent ${EIA_STEO_BRENT['2027Q2']:.2f}/bbl in April-June "
                f"2027, ${EIA_STEO_BRENT['2027Q3']:.2f} in July-September and "
                f"${EIA_STEO_BRENT['2027Q4']:.2f} in October-December (Table "
                "2), from inputs finalised on 1 October 2026. The EIA "
                "forecasts crude, not UK pump prices"
            ),
            "reference_period": (
                "April 2027 - March 2028; January-March 2028 holds the last "
                "EIA quarter"
            ),
            "derivation": (
                "The US EIA's October 2026 Short-Term Energy Outlook "
                f"forecasts Brent at ${EIA_STEO_BRENT['2027Q2']:.2f}, "
                f"${EIA_STEO_BRENT['2027Q3']:.2f} and "
                f"${EIA_STEO_BRENT['2027Q4']:.2f}/bbl over April-December "
                "2027. It does not reach 2028, so January-March 2028 holds "
                "the last quarter. The 2027-28 mean, "
                f"${forecast_brent_2027_28():.2f}, goes through this study's "
                "pump-price pass-through, the same DESNZ-against-EIA slopes "
                "and ONS petrol and diesel shares the stress tests use, to "
                f"+{fuel_rise_pct_at_brent(forecast_brent_2027_28())}% on "
                "Autumn Budget 2025 pump prices. The +"
                f"{fuel_rise_pct_at_brent(forecast_brent_2027_28())}% is this "
                "study's figure, not the EIA's: no published forecast of UK "
                "pump prices for 2027-28 was found, and the OBR's latest "
                "outlook (3 March 2026) used energy prices from before the "
                "conflict. Two things it leaves out, pulling opposite ways. "
                "First, it probably leans high: the slopes were fitted on "
                "November 2025 to August 2026, when refining margins widened, "
                "and the same EIA table has US wholesale margins over Brent "
                "narrowing again (diesel "
                f"${eia_wholesale_margin('diesel', '2025Q4'):.2f} a gallon in "
                "October-December 2025, "
                f"${eia_wholesale_margin('diesel', '2026Q3'):.2f} in "
                "July-September 2026, "
                f"${eia_wholesale_margin('diesel'):.2f} over 2027-28; petrol "
                f"${eia_wholesale_margin('gasoline', '2025Q4'):.2f}, "
                f"${eia_wholesale_margin('gasoline', '2026Q3'):.2f} and "
                f"${eia_wholesale_margin('gasoline'):.2f}). Scaling this "
                "study's rise by the EIA's own US price forecasts, relative "
                "to a slope fitted the same way, gives about +"
                f"{eia_consistent_fuel_rise_pct('retail')}% on US retail "
                "prices and +"
                f"{eia_consistent_fuel_rise_pct('wholesale')}% on US "
                "wholesale when the slope ends in July-September 2026, the "
                "quarter nearest this study's August end point, and +"
                f"{eia_consistent_fuel_rise_pct('retail', '2026Q2')}% and +"
                f"{eia_consistent_fuel_rise_pct('wholesale', '2026Q2')}% when "
                "it ends a quarter earlier. All four sit below this "
                "figure, so the direction is clear; the size depends on the "
                "end point and is not. US prices are only a proxy for the "
                "UK's, so this is disclosed rather than applied. Second, "
                "duty is held at 52.95p, the rate at "
                "both ends of the slopes, as in the stress tests. That "
                "assumes the 5p cut continues: the scheduled duty rises are "
                "outside this scenario's cost, and the fuel duty option's "
                "relief is measured against them. The range is the "
                "composite at the lowest and highest EIA quarter in the "
                "year, each held for the year: the spread of the forecast "
                "path, not a forecast error"
            ),
            "supporting_source_urls": [
                DESNZ_ROAD_FUEL,
                EIA_BRENT_MONTHLY,
                ONS_FAMILY_SPENDING_W1,
            ],
            "uncertainty_range": forecast_fuel_range_pct(),
        },
        "food_increase_pct": {
            "source_url": IGD_LATEST_URL,
            "basis": "forecast",
            "source_date": IGD_FOOD_INFLATION_LATEST["published"],
            # Overrides the shared definition: this is a forecast revision,
            # not the energy-cost share of a price rise.
            "definition": (
                "Revision to the forecast 2027 level of food and "
                "non-alcoholic drink prices since the forecaster's last "
                "pre-conflict forecast, whatever its cause"
            ),
            "source_figure": (
                "Retail food and drink inflation of "
                f"{IGD_FOOD_INFLATION_LATEST['2026'][0]}-"
                f"{IGD_FOOD_INFLATION_LATEST['2026'][1]}% in 2026, "
                f"{IGD_FOOD_INFLATION_LATEST['2027'][0]}-"
                f"{IGD_FOOD_INFLATION_LATEST['2027'][1]}% in 2027 and "
                f"{IGD_FOOD_INFLATION_LATEST['2028'][0]}-"
                f"{IGD_FOOD_INFLATION_LATEST['2028'][1]}% in 2028, against "
                f"{IGD_FOOD_INFLATION_PRE_CONFLICT['2026'][0]}-"
                f"{IGD_FOOD_INFLATION_PRE_CONFLICT['2026'][1]}% and "
                f"{IGD_FOOD_INFLATION_PRE_CONFLICT['2027'][0]}-"
                f"{IGD_FOOD_INFLATION_PRE_CONFLICT['2027'][1]}% for 2026 and "
                "2027 in its January 2026 outlook"
            ),
            "reference_period": "calendar 2027, the latest year both forecasts cover",
            "derivation": (
                "IGD's forecasts of UK retail food and drink inflation, at "
                "the midpoints of its published ranges, compounded over 2026 "
                "and 2027: the latest (17 September 2026) puts the 2027 food "
                f"price level {igd_food_revision_pct()}% above its last "
                "pre-conflict forecast (22 January 2026). That revision is "
                "the rise used, rather than food inflation itself, because "
                "the model needs a rise against a no-conflict path and "
                "normal inflation would otherwise count as a shock. It "
                "includes everything IGD revised for: IGD cites Middle East "
                "disruption, energy and input costs, El Niño weather and "
                "policy measures, so it is not the conflict alone. IGD's "
                "latest has inflation at "
                f"{IGD_FOOD_INFLATION_LATEST['2028'][0]}-"
                f"{IGD_FOOD_INFLATION_LATEST['2028'][1]}% in 2028, so "
                "extending to the 2027-28 fiscal year would probably raise "
                "the figure, but the pre-conflict forecast stops at 2027 and "
                "the extension would need an assumption. The range takes "
                "opposite ends of the two published ranges"
            ),
            "supporting_source_urls": [IGD_PRE_CONFLICT_URL],
            "uncertainty_range": forecast_food_range_pct(),
        },
        "cpi_increase_pp": {
            "source_url": ONS_CPI_WEIGHT_ENERGY,
            "basis": "derived",
            "source_date": "2026-09-16",  # MM23 release the weights are read from
            "reference_period": "2027-28 level against a no-conflict path",
            "derivation": (
                "Not an inflation forecast: the first-round effect of this "
                "scenario's own energy, fuel and food rises on ONS 2026 "
                f"basket weights, {direct_cpi_pp('external_forecast')}pp, "
                "rounded up, as for the stress tests. Published CPI "
                "forecasts are total rates, which do not convert into a "
                "conflict addition by subtracting a baseline (#56). The "
                "range is the same arithmetic at the ends of the three "
                "price ranges"
            ),
            "supporting_source_urls": [ONS_CPI_WEIGHT_FUEL, ONS_CPI_WEIGHT_FOOD],
            "uncertainty_range": forecast_cpi_range_pp(),
        },
    },
}


def _named(url):
    return {"name": SOURCE_NAMES[url], "url": url}


def _build_parameter_registry():
    registry = {}
    for scenario, sources in _SCENARIO_SOURCES.items():
        entries = {
            "narrative": sources["narrative"],
            "scenario_type": SCENARIO_TYPES[scenario],
            "parameters": {},
        }
        for name, definition in _PARAMETER_DEFINITIONS.items():
            entry = {
                "value": SCENARIOS[scenario][name],
                **definition,
                **sources[name],
            }
            # Names for the dashboard, resolved here so every scenario's
            # sources are shown the same way.
            entry["source_name"] = SOURCE_NAMES[entry["source_url"]]
            entry["basis_label"] = BASIS_LABELS[entry["basis"]]
            entry["supporting_sources"] = [
                _named(url) for url in entry.get("supporting_source_urls", [])
            ]
            entries["parameters"][name] = entry
        registry[scenario] = entries
    return registry


PARAMETER_REGISTRY = _build_parameter_registry()

# Uprating lag, registered separately: it is a modelling assumption about the
# counterfactual rather than a price.
UPRATING_LAG_REGISTRY = {
    "definition": (
        "Fraction of a year for which the residual CPI addition (the part "
        "not already in September 2026 CPI) goes unindexed, applied to "
        "CPI-linked benefit income"
    ),
    "unit": "fraction of the residual CPI addition",
    "geography": "United Kingdom",
    "source_url": COMMONS_UPRATING,
    "source_date": "2025-12-01",  # CBP-10403 published 1 Dec 2025, updated 24 Mar 2026
    "reference_period": "April 2027 uprating (normally set by September 2026 CPI)",
    "derivation": (
        "1.0. The conflict began in late February 2026, so the September "
        "2026 annual CPI rate already carries part of each scenario's "
        f"addition ({captured_in_sept_2026_cpi_pp()}pp: the conflict's "
        "contribution on ONS component indices against a September 2025 "
        "reference, a proxy on August 2026 data with food omitted), and April "
        "2027 uprating passes that on. The residual is a level held for the "
        "whole 2027-28 stress-test year and is not indexed until April 2028, "
        "so it goes unindexed for the full year. The earlier 0.5, for a shock "
        "arriving at a uniformly distributed point in the year, does not fit "
        "a shock whose timing is known and which began before the September "
        "reference month. Applied uniformly rather than benefit by benefit"
    ),
    "captured_pp": captured_in_sept_2026_cpi_pp(),
    "captured_basis": (
        "Proxy and lower bound on what the September 2026 annual CPI rate "
        "captures: ONS energy (D7CH) and fuel (D7EC) indices at August 2026 "
        "against pre-conflict counterfactuals (June 2026 energy, February "
        "2026 fuel), on a September 2025 reference; food omitted. "
        "Replace with the outturn once September 2026 CPI is published "
        "(about 21 October 2026)"
    ),
    "counterfactual": (
        "The scheduled April 2027 uprating is set from September 2026 CPI, "
        "which reflects the part of the shock already in prices by then. The "
        "residual addition is not reflected, and no offset for it reaches "
        "households during the stress-test year. The "
        "household's loss is the price rise itself, which the energy, fuel "
        "and food channels already measure in full. This amount is therefore "
        "NOT added to them — doing so counted the same price shock twice. It "
        "measures the compensation an immediate uprating would deliver, and "
        "is what the accelerated-uprating policy pays"
    ),
    "uncertainty_range": [0.0, 1.0],
}

# Limitations that the implemented model does not address, stated so the
# dashboard and any reader can tell what the numbers do and do not represent.
METHOD_LIMITATIONS = [
    "Scenario type: three scenarios are annual stress tests, not forecasts. "
    "The fourth, external_forecast, takes its prices from published "
    "forecasts, but where a forecast stops short of 2027-28 its last period "
    "is held, and its fuel figure goes through this study's pump-price "
    "pass-through, as its registry derivations state. Every change is "
    "applied as a full-year 2027-28 amount, including where the cited source "
    "describes a 2026 disruption lasting a few months. No time path, quarterly "
    "or monthly profile, or shock duration is modelled.",
    "Energy channel: this is a household-energy-expenditure sensitivity "
    "rather than a price-cap calculation — the scenario percentage is applied "
    "to each household's own modelled energy spending, and no cap level, unit "
    "rate or tariff type enters it. Issue #13 offered modelling retail energy "
    "properly or relabelling the channel; this is the relabel.",
    "Energy prices: the model multiplies each household's baseline gas and "
    "electricity expenditure by the scenario percentage. It does not model "
    "unit rates or standing charges, the gas/electricity split, region, "
    "payment method, quarterly cap periods, or fixed-tariff coverage — about "
    "40% of accounts were on fixed tariffs for the July 2026 cap, and the cap "
    "does not set their prices. CURRENT_ENERGY_CAP is reported as context and "
    "does not enter the calculation.",
    "Pass-through: the coefficients and lags implied by the scenario "
    "percentages are judgements anchored to the cited sources, not equations "
    "derived from them. The energy channel is gas-to-retail (Ofgem's wholesale "
    "allowance is built from NBP gas and UK baseload power forwards, and crude "
    "oil enters it nowhere); the fuel channel is oil-to-pump. In this episode "
    "oil and gas flows diverged — oil recovered to roughly two-thirds of "
    "pre-war levels while LNG stayed halted — so an oil-anchored energy "
    "calibration would if anything understate the gas shock. See "
    "PARAMETER_REGISTRY for the derivation of each figure.",
    "Fuel product mix: ONS Table A6 gives one combined figure for petrol, "
    "diesel and other motor oils, and the model multiplies it by one "
    "percentage. That percentage is an expenditure-weighted composite of "
    "separately derived petrol and diesel responses, using the FYE2024 Table "
    "A1 shares (61% petrol, 39% diesel). It is a fixed-weight calculation: no "
    "substitution between fuels and no volume response is modelled, and a "
    "household's own mix is not represented, so a diesel-only household's "
    "shock is understated and a petrol-only household's overstated. The "
    "shares are two years older than the modelled year and the diesel car "
    "fleet share has been falling, which biases the composite very slightly "
    "high.",
    "Share-of-income statistics: the MEAN share is not robust in the bottom "
    "quintile, because a small number of households with a defined but very "
    "small income denominator pull it up sharply. Each quintile row therefore "
    "reports three bases - mean_impact_pct, trimmed_mean_impact_pct "
    "(excluding the bottom 1% of all incomes) and median_impact_pct - and "
    "they differ substantially at the bottom. The GRADIENT between the bottom "
    "and top quintiles holds on every basis; the LEVEL does not, so a single "
    "quoted figure should be the gradient, and the ratio of mean cost to mean "
    "income is the steadiest basis for it. Excluding households with zero "
    "modelled energy spend barely moves any of the three, so the sensitivity "
    "is to the income tail rather than the energy tail; those households are "
    "over-represented in the bottom two quintiles, which hold about three "
    "fifths of them (#46).",
    "Benefit uprating: the gain from an accelerated uprating is modelled by "
    "running a PolicyEngine UK reform at each scenario's residual CPI "
    "addition, raising every CPI-uprated benefit rate, with tapers, award "
    "floors and the benefit cap applied, the reported ESA, contribution-based "
    "JSA, IIDB, incapacity benefit and AFCS awards scaled, and the "
    "CPI-uprated additional State Pension raised, including UC work "
    "allowances, the childcare cap, the non-dependant deduction (which lowers "
    "awards) and Pension Age Winter Heating Payment. Not covered, each with a "
    "published "
    "upper bound on the omission under metadata.uprating_not_covered: the "
    "Pension Credit savings credit maximum, which is not a model parameter, "
    "and the partly CPI-linked maternity allowance and statutory maternity, "
    "paternity and sick pay; the captured "
    "September 2026 CPI is a proxy on August data with food omitted. The "
    "amount is reported as the compensation an immediate uprating would "
    "deliver and is not counted as a cost, so the household loss is the price "
    "rise alone.",
    "Poverty count granularity: the count of people newly below the "
    "anchored line is a sum over survey records whose weights vary by orders "
    "of magnitude, so a single record can carry a large share of it and the "
    "count moves in steps as a price rises: a small change in an assumption "
    "can move it sharply or not at all. Each scenario's summary reports how "
    "many records the count rests on and the share the largest carry "
    "(n_records_newly_below_anchored_line and the two *_share_of_newly_below_pct "
    "fields), and its sensitivity block reports the count at each end of "
    "every price range. Quote the count rounded and with that range, not to "
    "the last person. Each policy's count of people kept above the line is a "
    "sum over a subset of the same records, and can be smaller than the "
    "single largest of them, so it ranks policies only roughly. The cost "
    "figures are sums over every household and are not affected in the same "
    "way.",
    "Means-tested payment timing: the 2022 scheme paid two separate awards of "
    "£326 and £324, each conditional on entitlement in its own qualifying "
    "window, so a household entitled in only one window received that "
    "instalment alone. The annual microdata cannot observe entitlement within "
    "a window, so each instalment is paid at an assumed per-window "
    "entitlement rate (MEANS_TEST_WINDOW_ENTITLEMENT_RATE), which gives the "
    "expected value across all four qualifying states without modelling their "
    "joint distribution. That rate is a stated assumption, not a sourced "
    "figure, and the modelled cost is proportional to it. Take-up among "
    "qualifying households is treated as complete, since the 2022 payments "
    "were automatic.",
    "Uncertainty: the ranges in PARAMETER_REGISTRY describe the spread of the "
    "price assumptions and are now evaluated through the model — see "
    "scenarios[*].sensitivity. They are judgements, not sampling "
    "distributions, so the resulting spread is not a confidence interval. "
    "Survey sampling uncertainty on the spending inputs is reported separately "
    "under parameters.spending_inputs.sampling_uncertainty and is not "
    "propagated, because ONS publishes no decile-level standard errors.",
]


# Household spending inputs, read from the committed ONS Family Spending
# Table A6 extract rather than hand-set here. See `inputs.py` and
# `scripts/extract_ons_a6.py`; the CSV records the workbook URL, reference
# period, units, grouping variable and workbook hash.
#
# A6 reports UK means of £19.80/week on petrol, diesel and other motor oils
# (£1,029.60/year) and £70.50/week on food and non-alcoholic drinks
# (£3,666/year). Earlier versions of this file attributed £1,300 and £5,000 to
# the same table (#12).
#
# A6 groups households by GROSS household income decile, so the model groups
# them the same way — see `household_gross_income_decile` in the pipeline. It
# does not reuse the equivalised HBAI net-income decile that the
# distributional breakdowns are reported on; the two are not interchangeable.
BASE_FUEL_SPEND = TRANSPORT_FUEL_SPEND.annual_mean
BASE_FOOD_SPEND = FOOD_SPEND.annual_mean
FUEL_DECILE_FACTORS = TRANSPORT_FUEL_SPEND.decile_factors
FOOD_DECILE_FACTORS = FOOD_SPEND.decile_factors

# Transport fuel goes only to households that own a vehicle. Constant spending
# within a decile previously gave every household positive fuel expenditure,
# including households with no vehicle, which in turn gave every household a
# modelled fuel-duty benefit (#12, #14). Each decile's spending is instead
# spread across that decile's vehicle-owning households only, so the decile
# mean still matches A6 while non-owners spend nothing.
ALLOCATE_FUEL_TO_VEHICLE_OWNERS = True

# Benefit uprating: CPI-linked benefits are uprated each April using the
# previous September's CPI. The conflict began in late February 2026, so
# September 2026 CPI already carries part of the shock and April 2027 uprating
# passes it on. Only the residual — the scenario's CPI addition less
# captured_in_sept_2026_cpi_pp() — goes unindexed during 2027-28. An earlier
# version applied the whole addition, on the premise that the shock arrived
# after September, which it did not.
#
# The household's loss is therefore the price rise itself, which the three
# cost channels already measure. This factor does NOT add a fourth cost — it
# sizes the compensation that an immediate uprating would deliver, which is
# what the accelerated-uprating policy provides. The factor is 1.0: the
# residual is a level held for the whole stress-test year and is not indexed
# until April 2028. The previous 0.5 assumed a shock arriving at a random
# point in the year, which does not fit a shock that began before the
# September reference month.
# The April 2026 uprating (+3.8%, Sept 2025 CPI; UC standard allowance +2.3%
# extra under the Universal Credit Act 2025) predates the conflict shock.
# Source: https://commonslibrary.parliament.uk/research-briefings/cbp-10403/
UPRATING_LAG_FACTOR = 1.0

# The benefit amounts an accelerated CPI uprating would raise (#61 second
# review C2). Each is a PolicyEngine UK parameter tagged
# `uprating: gov.benefit_uprating_cpi`, less the legal exceptions:
#   - Pension Credit minimum guarantee: uprated at least in line with earnings
#   - UC LCWRA (elements.disabled): frozen by the Universal Credit Act 2025
#   - UC childcare cap, UC non-dependant deduction, UC work allowance, HB
#     income disregards, savings credit threshold: caps, deductions and
#     thresholds, not benefit rates in the annual CPI review
#   - tax credits: abolished April 2025
#   - non-benefit parameters PolicyEngine happens to tag with the same index
# The gain is measured by running the reform through the model, so earnings
# tapers, the benefit cap and every other interaction apply, rather than by
# scaling awards by a share.
CPI_UPRATED_BENEFIT_PARAMETERS = [
    "gov.dwp.JSA.income.amount_18_24",
    "gov.dwp.JSA.income.amount_over_25",
    "gov.dwp.JSA.income.couple",
    "gov.dwp.attendance_allowance.higher",
    "gov.dwp.attendance_allowance.lower",
    "gov.dwp.carer_premium.couple",
    "gov.dwp.carer_premium.single",
    "gov.dwp.carers_allowance.rate",
    "gov.dwp.constant_attendance_allowance.exceptional_rate",
    "gov.dwp.constant_attendance_allowance.full_day_rate",
    "gov.dwp.constant_attendance_allowance.intermediate_rate",
    "gov.dwp.constant_attendance_allowance.part_day_rate",
    "gov.dwp.disability_premia.disability_couple",
    "gov.dwp.disability_premia.disability_single",
    "gov.dwp.disability_premia.enhanced_couple",
    "gov.dwp.disability_premia.enhanced_single",
    "gov.dwp.disability_premia.severe_couple",
    "gov.dwp.disability_premia.severe_single",
    "gov.dwp.dla.mobility.higher",
    "gov.dwp.dla.mobility.lower",
    "gov.dwp.dla.self_care.higher",
    "gov.dwp.dla.self_care.lower",
    "gov.dwp.dla.self_care.middle",
    "gov.dwp.housing_benefit.allowances",
    "gov.dwp.income_support.amounts",
    "gov.dwp.pension_credit.guarantee_credit.carer.addition",
    "gov.dwp.pension_credit.guarantee_credit.child.addition",
    "gov.dwp.pension_credit.guarantee_credit.child.disability.addition",
    "gov.dwp.pension_credit.guarantee_credit.child.disability.severe.addition",
    "gov.dwp.pension_credit.guarantee_credit.child.first.addition",
    "gov.dwp.pension_credit.guarantee_credit.severe_disability.addition",
    "gov.dwp.pip.daily_living.enhanced",
    "gov.dwp.pip.daily_living.standard",
    "gov.dwp.pip.mobility.enhanced",
    "gov.dwp.pip.mobility.standard",
    "gov.dwp.sda.maximum",
    "gov.dwp.universal_credit.elements.carer.amount",
    "gov.dwp.universal_credit.elements.child.amount",
    "gov.dwp.universal_credit.elements.child.disabled.amount",
    "gov.dwp.universal_credit.elements.child.first.higher_amount",
    "gov.dwp.universal_credit.elements.child.severely_disabled.amount",
    "gov.dwp.universal_credit.standard_allowance.amount",
    "gov.hmrc.child_benefit.amount.additional",
    "gov.hmrc.child_benefit.amount.eldest",
    "gov.social_security_scotland.carer_support_payment.rate",
    "gov.social_security_scotland.scottish_child_payment.amount",
    # Uprated in the official 2026-27 tables and live in the UC formula; each
    # passes through the benefit rules with its own sign (#61 sixth review
    # C2). Higher work allowances and childcare cap raise UC; a higher
    # non-dependant deduction lowers the housing element.
    "gov.dwp.universal_credit.means_test.work_allowance",
    "gov.dwp.universal_credit.elements.childcare.cap",
    "gov.dwp.universal_credit.elements.housing.non_dep_deduction.amount",
    "gov.social_security_scotland.pawhp.amount",
]

# Benefits the model computes that policyengine-uk 2.90.2 leaves out of
# household_benefits. Their change is added to the gain explicitly, or an
# uprating of their parameters would register as zero (#61 sixth review C2).
BENEFITS_OUTSIDE_HOUSEHOLD_BENEFITS = ["pawhp"]

# Every other currency parameter under the benefit branches that PolicyEngine
# UK tags with a CPI index, and why the reform leaves it alone. A test sweeps
# the model's parameters and fails on any tagged one in neither list: Scottish
# Child Payment was missed because it carries the OBR CPI tag rather than
# gov.benefit_uprating_cpi.
CPI_PARAMETER_EXCLUSIONS = {
    "gov.dwp.IIDB.maximum": "not used by the model; IIDB is paid from the reported award, which the reform scales",
    "gov.dwp.housing_benefit.means_test.income_disregard": "earnings disregards are frozen in cash terms, not uprated",
    "gov.dwp.pension_credit.guarantee_credit.minimum_guarantee": "uprated at least in line with earnings, not CPI",
    "gov.dwp.pension_credit.savings_credit.threshold": "set by ministerial discretion, not CPI (+7.8% in 2026-27); the savings credit maximum is bounded separately",
    "gov.dwp.tax_credits": "tax credits were abolished in April 2025",
    "gov.dwp.universal_credit.elements.disabled.amount": "the LCWRA element, frozen by the Universal Credit Act 2025",
}

# ESA and contribution-based JSA are paid from survey-reported awards that
# PolicyEngine uprates by the CPI index rather than from rate parameters, so
# the reform scales these inputs directly (#61 third and fourth reviews C2).
CPI_UPRATED_REPORTED_INPUTS = [
    "esa_income_reported",
    "esa_contrib_reported",
    "jsa_contrib_reported",
    "iidb_reported",
    "incapacity_benefit_reported",
    "afcs_reported",
]

# Amounts the model computes rather than reads, which are CPI-uprated in law
# but driven by no rate parameter. Additional State Pension (SERPS/S2P, and
# the protected payment under the new State Pension) is CPI-uprated, unlike
# the triple-locked basic and new State Pension; the model derives it from
# the reported pension above the flat rate. The reform overrides it scaled.
CPI_UPRATED_COMPUTED_AMOUNTS = ["additional_state_pension"]

# Every other input PolicyEngine UK tags for CPI uprating that is a benefit
# (a `_reported` award or a household_benefits component), with the reason it
# is not scaled. A test fails if the model gains one that is in neither list,
# so coverage is checked against the model rather than by inspection (#61
# fifth review C2).
#
# Partly CPI-linked: each pays the lower of a flat CPI-uprated rate and a
# share of earnings, and is paid by employers or at earnings-related rates the
# model does not separate. Not raised; r% of their total is published as an
# upper bound on the omission.
PARTLY_CPI_LINKED_INPUTS = [
    "maternity_allowance_reported",
    "statutory_maternity_pay",
    "statutory_paternity_pay",
    "statutory_sick_pay",
]
NOT_SCALED_REPORTED_INPUTS = {
    "jsa_income_reported": "income-based JSA is inactive in the model from 2027 (gov.dwp.JSA.income.active), so it pays nothing to scale",
    "bsp_reported": "Bereavement Support Payment rates are not uprated",
    "winter_fuel_allowance_reported": "Winter Fuel Payment is a fixed sum, not CPI-uprated",
    "carers_allowance_reported": "receipt flag only; the amount is a reformed rate parameter",
    "sda_reported": "receipt flag only; the amount is a reformed rate parameter",
    "child_benefit_reported": "the model pays the entitlement from reformed rate parameters",
    "housing_benefit_reported": "the model pays the entitlement from reformed rate parameters",
    "income_support_reported": "the model pays the entitlement from reformed rate parameters",
    "pension_credit_reported": "the model pays the entitlement from its parameters",
    "universal_credit_reported": "the model pays the entitlement from reformed rate parameters",
    "child_tax_credit_reported": "tax credits were abolished in April 2025",
    "working_tax_credit_reported": "tax credits were abolished in April 2025",
}


def uprating_residuals_needed():
    """Every residual the pipeline evaluates: each scenario's point value and
    both ends of its CPI uncertainty range, which the sensitivity analysis
    walks. The reform is run at each, not scaled from one run, because award
    floors and the benefit cap make the gain non-linear (#61 third review
    C2)."""
    needed = set()
    for key, params in SCENARIOS.items():
        low, high = PARAMETER_REGISTRY[key]["parameters"]["cpi_increase_pp"][
            "uncertainty_range"
        ]
        for cpi in (params["cpi_increase_pp"], low, high):
            residual = residual_cpi_pp(key, cpi)
            if residual > 0:
                needed.add(residual)
    return sorted(needed)

# Structural constants
WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12
PENCE_PER_POUND = 100
POVERTY_LINE_RATIO = 0.6  # 60% of median equivalised income (relative poverty, BHC)
WINNERS_LOSERS_THRESHOLD = 1  # £1 change threshold for classifying winners/losers

# Policy parameters
EPG_CAP_PCT = 0.10  # Energy Price Guarantee: caps the bill increase at 10% (stylised)
FLAT_REBATE = 400  # £/household, modelled on the 2022 Energy Bills Support Scheme
CT_REBATE = 300    # £ council tax rebate bands A-D (2022 scheme was England-only £150; stylised UK-wide)
UC_UPLIFT_WEEKLY = 20  # £/week, matching the 2020-21 covid UC uplift
FUEL_DUTY_CUT_PENCE = 5  # pence/litre; the existing 5p cut runs to 31 Dec 2026 —
# this policy models EXTENDING it through the shock period rather than a new
# cut. The extension is not government policy: it is a live decision for the
# Autumn Budget on 28 October 2026, which is why it is modelled as an option.
#
# In force now at 52.95p/litre. Absent action the rate returns to the Budget
# 2025 baseline in two steps rather than a single cliff: 55.95p on 1 Jan 2027
# and 57.95p on 1 Mar 2027. The model applies a full-year 2027-28 extension,
# so it does not represent that taper — one more consequence of the annual
# basis recorded in METHOD_LIMITATIONS.
#
# Effective pump saving is ~6p including VAT on duty; we model the 5p duty element.
# Source: https://www.gov.uk/government/publications/amended-fuel-duty-rates-for-2026-to-2027/amended-fuel-duty-rates-2026-to-2027
# The 2022 scheme paid in two instalments, each a separate award conditional
# on its own qualifying period: £326 and £324. A household entitled in only
# one window received that instalment alone — first-only and second-only are
# real states, not just "both or neither".
# Sources:
#   Social Security (Additional Payments) Act 2022, ss.1-2
#     https://www.legislation.gov.uk/ukpga/2022/38
#   DWP ADM Memo 17/22
#     https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1097764/adm17-22.pdf
# Fuel duty is one of the two measures in this study that is an actual
# PolicyEngine parameter, so its Exchequer cost can be computed by running the
# cut as a real reform rather than inferred from household spending. That is
# what #14 asks for where the model supports it.
FUEL_DUTY_PARAMETER = "gov.hmrc.fuel_duty.petrol_and_diesel"

# Electricity VAT is deliberately NOT costed this way. The only relevant
# parameter, gov.hmrc.vat.reduced_rate, applies to all reduced-rate
# consumption rather than domestic electricity alone, so zeroing it would cost
# a much broader reform than the one modelled.

MEANS_TEST_INSTALMENT_AMOUNTS = (326, 324)

# Probability that a household observed on a qualifying benefit in the annual
# microdata was entitled in each instalment's window, applied per instalment.
#
# This is deliberately a PER-WINDOW entitlement rate, not a share entitled in
# both. Multiplying the full award by a "both windows" share would imply that
# every household not entitled twice received nothing, which omits the
# first-only and second-only states the scheme allows. Applying the rate to
# each instalment separately gives the expected value across all four states
# without needing to model their joint distribution — which the annual data
# cannot identify anyway.
#
# DWP's 2022 evaluation is not granular enough to pin the rate, so it is a
# stated assumption, not a sourced figure — see METHOD_LIMITATIONS. Setting it
# to 1.0 reproduces paying every recipient both instalments in full.
MEANS_TEST_WINDOW_ENTITLEMENT_RATE = 0.85

# Take-up. The 2022 payments were made automatically to households already
# receiving a qualifying benefit, so take-up among those households was
# effectively complete; the losses were in benefit take-up upstream, which the
# microdata already reflects. Kept explicit so the assumption is visible.
MEANS_TEST_TAKE_UP = 1.0

# Total award, the sum of the two statutory instalments.
MEANS_TEST_AMOUNT = sum(MEANS_TEST_INSTALMENT_AMOUNTS)  # £650
# Eligibility is keyed to qualifying-benefit receipt, not an income cliff.

# Electricity VAT cut: announced 21 July 2026 (VAT on qualifying domestic
# electricity 5% -> 0% for 1 Oct 2026-31 Mar 2027, ~£45/household, ~£850m,
# electricity only and not gas). Modelled here as a full-year EXTENSION beyond
# 31 March 2027, which is not government policy: the government's stated
# position is that an extension "will be considered at the Autumn Budget",
# so like the fuel duty extension it is a live decision for 28 October 2026
# and is modelled as an option rather than as baseline.
# Saving = 5/105 of the electricity bill.
# Source: https://www.gov.uk/government/news/new-pm-cuts-tax-on-household-electricity-bills-to-give-breathing-space-on-cost-of-living
ELEC_VAT_SAVING_RATE = 5 / 105

# Social tariff parameters
SOCIAL_TARIFF_INCOME_THRESHOLD = 20_000  # household income threshold
SOCIAL_TARIFF_DISCOUNT = 0.50  # 50% discount on energy price shock for eligible households

# Country / nation mapping from region codes
ENGLISH_REGIONS = {
    "EAST_MIDLANDS", "EAST_OF_ENGLAND", "LONDON", "NORTH_EAST",
    "NORTH_WEST", "SOUTH_EAST", "SOUTH_WEST", "WEST_MIDLANDS", "YORKSHIRE",
}

REGION_TO_COUNTRY = {r: "ENGLAND" for r in ENGLISH_REGIONS}
REGION_TO_COUNTRY["SCOTLAND"] = "SCOTLAND"
REGION_TO_COUNTRY["WALES"] = "WALES"
REGION_TO_COUNTRY["NORTHERN_IRELAND"] = "NORTHERN_IRELAND"
