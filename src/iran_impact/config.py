"""Configuration constants for energy price shock impact on UK living standards analysis.

All parameters calibrated to conditions as of August 2026, during the ongoing
Middle East conflict (US/Israel-Iran war from late February 2026, with recurrent
Strait of Hormuz disruption). Sources are cited inline.
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

# The subsequent cap period, published before this analysis was written.
# Source: https://www.ofgem.gov.uk/press-release/energy-price-cap-will-rise-4-october-2026
OCTOBER_2026_ENERGY_CAP = 1_723

# Share of accounts on fixed tariffs for the July 2026 cap period, which the
# cap does not set. Reported as context for the coverage limitation below.
# Source: https://www.ofgem.gov.uk/press-release/energy-price-cap-will-rise-13-july
FIXED_TARIFF_ACCOUNT_SHARE = 0.40

# Scenario calibration (relative to the pre-conflict early-2026 baseline).
# Anchors:
# - "low": conflict de-escalates from the August 2026 position — Brent settles
#   near ~$85/bbl (4 Aug 2026 spot), pump prices ~157p petrol / ~187p diesel
#   (~+20% on Autumn Budget 2025 levels), cap rise in line with the observed
#   +13% July 2026 increase plus Cornwall Insight's Q4 forecast (~£1,700).
# - "central": sustained Strait of Hormuz constraint — Goldman Sachs scenario
#   of Brent averaging >$100/bbl through 2026 ($120 Q3 / $115 Q4 in the
#   extended-closure case). Oil-to-retail pass-through per Commons Library
#   CBP-10601. CPI adder consistent with BoE June 2026 projection moving from
#   ~3% to the 4%+ range.
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
        "cpi_increase_pp": 1.0,
        "fuel_pct": 20,
        "food_increase_pct": 2.0,
    },
    "central_shock": {
        "cap_increase_pct": 45,
        "cpi_increase_pp": 2.5,
        "fuel_pct": 45,
        "food_increase_pct": 4.0,
    },
    "severe_shock": {
        "cap_increase_pct": 90,
        "cpi_increase_pp": 4.5,
        "fuel_pct": 80,
        "food_increase_pct": 6.5,
    },
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
GOLDMAN_HORMUZ = "https://oilprice.com/Latest-Energy-News/World-News/Goldman-Another-Month-of-Hormuz-Closure-Means-Over-100-Brent-Throughout-2026.html"
OXFORD_ECONOMICS = "https://www.oxfordeconomics.com/resource/iran-war-scenarios-the-oil-price-that-breaks-parts-of-the-economy/"
COMMONS_FUEL_PRICES = "https://commonslibrary.parliament.uk/research-briefings/cbp-10601/"
COMMONS_UPRATING = "https://commonslibrary.parliament.uk/research-briefings/cbp-10403/"

_PARAMETER_DEFINITIONS = {
    "cap_increase_pct": {
        "definition": (
            "Percentage increase in household domestic gas and electricity "
            "expenditure relative to the pre-conflict early-2026 baseline"
        ),
        "unit": "per cent",
        "geography": "United Kingdom",
        "applies_to": "each household's own baseline gas + electricity expenditure",
        "lag": "none — applied as a full-year 2027-28 amount",
    },
    "fuel_pct": {
        "definition": (
            "Percentage increase in the pump price of petrol and diesel "
            "relative to the pre-conflict early-2026 baseline"
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
            "Addition to UK CPI inflation, used only to size the real-terms "
            "erosion of CPI-linked benefits before the next April uprating"
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
            "Conflict de-escalates from the August 2026 position: Brent settles "
            "near $85/bbl, pump prices around 157p petrol and 187p diesel"
        ),
        "cap_increase_pct": {
            "source_url": OFGEM_JULY_2026,
            "source_date": "2026-07-01",
            "reference_period": "1 July - 30 September 2026 cap period",
            "derivation": (
                "Set to the observed +13.5% July 2026 cap rise, rounded up to "
                "15% to span Cornwall Insight's ~£1,700 Q4 2026 forecast. "
                "Judgement anchored to the outturn, not a calculation from it"
            ),
            "uncertainty_range": [13, 20],
        },
        "fuel_pct": {
            "source_url": COMMONS_FUEL_PRICES,
            "source_date": "2026-08-04",
            "reference_period": "August 2026 spot prices",
            "derivation": (
                "Observed pump prices are roughly 20% above Autumn Budget 2025 "
                "levels. Set to the observed change"
            ),
            "uncertainty_range": [15, 25],
        },
        "food_increase_pct": {
            "source_url": COMMONS_FUEL_PRICES,
            "source_date": "2026-08-04",
            "reference_period": "2027-28",
            "derivation": (
                "Judgement: food price response to a de-escalating energy "
                "shock, no published scenario for this figure"
            ),
            "uncertainty_range": [1.0, 3.0],
        },
        "cpi_increase_pp": {
            "source_url": "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026",
            "source_date": "2026-06-01",
            "reference_period": "2026-27",
            "derivation": (
                "Bank of England June 2026 projection of CPI near 3% against "
                "about 2% pre-conflict, i.e. roughly +1pp"
            ),
            "uncertainty_range": [0.5, 1.5],
        },
    },
    "central_shock": {
        "narrative": (
            "Sustained Strait of Hormuz constraint: Goldman Sachs scenario of "
            "Brent averaging above $100/bbl through 2026"
        ),
        "cap_increase_pct": {
            "source_url": GOLDMAN_HORMUZ,
            "source_date": "2026-07-01",
            "reference_period": "2026 calendar year",
            "derivation": (
                "Judgement: wholesale gas response to Brent above $100/bbl, "
                "translated to a retail bill increase. The oil-to-retail "
                "pass-through coefficient and lag are not published in the "
                "source and are not derived here"
            ),
            "uncertainty_range": [30, 60],
        },
        "fuel_pct": {
            "source_url": COMMONS_FUEL_PRICES,
            "source_date": "2026-07-01",
            "reference_period": "2026 calendar year",
            "derivation": (
                "Oil-to-pump pass-through per Commons Library CBP-10601 "
                "applied to the Goldman >$100/bbl case, as a judgement"
            ),
            "uncertainty_range": [30, 60],
        },
        "food_increase_pct": {
            "source_url": COMMONS_FUEL_PRICES,
            "source_date": "2026-07-01",
            "reference_period": "2027-28",
            "derivation": (
                "Judgement: food price response to sustained higher energy "
                "input costs, no published scenario for this figure"
            ),
            "uncertainty_range": [2.5, 5.5],
        },
        "cpi_increase_pp": {
            "source_url": "https://niesr.ac.uk/blog/possible-effects-uk-inflation-2026-us-iran-conflict",
            "source_date": "2026-06-01",
            "reference_period": "2026-27",
            "derivation": (
                "NIESR central case of about 4% CPI against about 2% "
                "pre-conflict, taken at the middle of its +1pp to +3pp range"
            ),
            "uncertainty_range": [1.0, 3.0],
        },
    },
    "severe_shock": {
        "narrative": (
            "Extended full closure or prolonged war: Goldman extreme-adverse "
            "case and the Oxford Economics escalation scenario"
        ),
        "cap_increase_pct": {
            "source_url": OXFORD_ECONOMICS,
            "source_date": "2026-06-01",
            "reference_period": "two-month $140/bbl case",
            "derivation": (
                "Judgement: retail bill response under the Oxford Economics "
                "escalation case and Goldman extreme-adverse Brent of "
                "$115-120. Not derived from a published cap projection"
            ),
            "uncertainty_range": [60, 120],
        },
        "fuel_pct": {
            "source_url": OXFORD_ECONOMICS,
            "source_date": "2026-06-01",
            "reference_period": "two-month $140/bbl case",
            "derivation": (
                "Oil-to-pump pass-through applied to Brent of $140/bbl, as a "
                "judgement"
            ),
            "uncertainty_range": [60, 110],
        },
        "food_increase_pct": {
            "source_url": OXFORD_ECONOMICS,
            "source_date": "2026-06-01",
            "reference_period": "2027-28",
            "derivation": (
                "Judgement: food price response under a global recession "
                "scenario, no published figure for UK food prices"
            ),
            "uncertainty_range": [4.0, 9.0],
        },
        "cpi_increase_pp": {
            "source_url": OXFORD_ECONOMICS,
            "source_date": "2026-06-01",
            "reference_period": "two-month $140/bbl case",
            "derivation": (
                "The source reports a 5.8% peak in WORLD CPI, roughly 3pp "
                "above its baseline. Set to 4.5pp for UK CPI as a judgement "
                "reflecting the UK's higher energy import share. The source "
                "does not publish a UK figure, and does not report the 7.7% "
                "this file previously attributed to it"
            ),
            "uncertainty_range": [3.0, 6.0],
        },
    },
}


def _build_parameter_registry():
    registry = {}
    for scenario, sources in _SCENARIO_SOURCES.items():
        entries = {"narrative": sources["narrative"], "parameters": {}}
        for name, definition in _PARAMETER_DEFINITIONS.items():
            entries["parameters"][name] = {
                "value": SCENARIOS[scenario][name],
                **definition,
                **sources[name],
            }
        registry[scenario] = entries
    return registry


PARAMETER_REGISTRY = _build_parameter_registry()

# Uprating lag, registered separately: it is a modelling assumption about the
# counterfactual rather than a price.
UPRATING_LAG_REGISTRY = {
    "definition": (
        "Fraction of a full year's CPI addition applied to CPI-linked benefit "
        "income, representing the average real-terms erosion between a "
        "mid-year shock and the next April uprating"
    ),
    "unit": "fraction of the annual CPI addition",
    "geography": "United Kingdom",
    "source_url": COMMONS_UPRATING,
    "source_date": "2026-01-01",
    "reference_period": "April 2027 uprating (normally set by September 2026 CPI)",
    "derivation": (
        "Expected value across a shock arriving at a uniformly distributed "
        "point in the year, given a maximum 12-month lag: 0.5. Applied "
        "uniformly rather than benefit by benefit"
    ),
    "counterfactual": (
        "Benefits are assumed NOT to be compensated for the shock until the "
        "following April. The channel-4 amount is the real-income loss under "
        "that assumption. It is added to the energy, fuel and food costs, "
        "which double-counts the same price shock unless the comparison is "
        "against immediate and full compensation — a known limitation, see "
        "METHOD_LIMITATIONS"
    ),
    "uncertainty_range": [0.0, 1.0],
}

# Limitations that the implemented model does not address, stated so the
# dashboard and any reader can tell what the numbers do and do not represent.
METHOD_LIMITATIONS = [
    "Scenario type: annual stress test, not a forecast. Every change is "
    "applied as a full-year 2027-28 amount, including where the cited source "
    "describes a 2026 disruption lasting a few months. No time path, quarterly "
    "or monthly profile, or shock duration is modelled.",
    "Energy prices: the model multiplies each household's baseline gas and "
    "electricity expenditure by the scenario percentage. It does not model "
    "unit rates or standing charges, the gas/electricity split, region, "
    "payment method, quarterly cap periods, or fixed-tariff coverage — about "
    "40% of accounts were on fixed tariffs for the July 2026 cap, and the cap "
    "does not set their prices. CURRENT_ENERGY_CAP is reported as context and "
    "does not enter the calculation.",
    "Pass-through: the oil-to-wholesale-to-retail coefficients and lags "
    "implied by the scenario percentages are judgements anchored to the cited "
    "sources, not equations derived from them. See PARAMETER_REGISTRY for the "
    "derivation of each figure.",
    "Benefit uprating: a single expected-lag factor is applied to a broad set "
    "of CPI-linked benefit income, rather than modelling each benefit's own "
    "uprating rule and April 2027 timing against the price path. Adding the "
    "resulting amount to the price shocks double-counts unless the "
    "counterfactual is immediate, full compensation.",
    "Uncertainty: the ranges in PARAMETER_REGISTRY describe the spread of the "
    "price assumptions. They do not include the Living Costs and Food Survey's "
    "sampling uncertainty, which Table A6 does not publish.",
]

SCENARIO_TYPE = "annual stress test"

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

# Benefit uprating lag: CPI-linked benefits are uprated each April using the
# previous September's CPI. For a shock arriving mid-year, the average period
# of un-indexed erosion across the year is roughly half the maximum 12-month
# lag, so we apply an expected-value factor of 0.5 rather than the maximum.
# The April 2026 uprating (+3.8%, Sept 2025 CPI; UC standard allowance +2.3%
# extra under the Universal Credit Act 2025) predates the conflict shock.
# Source: https://commonslibrary.parliament.uk/research-briefings/cbp-10403/
UPRATING_LAG_FACTOR = 0.5

# Fuel poverty indicator: the simple 10%-of-net-income energy-spend ratio.
# NOTE: this is NOT England's official LILEE metric — results are indicative
# and not comparable with official fuel poverty statistics; the dashboard
# labels it accordingly.
FUEL_POVERTY_THRESHOLD = 0.10

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
# this policy models extending it through the shock period rather than a new cut.
# Effective pump saving is ~6p including VAT on duty; we model the 5p duty element.
# Source: https://www.gov.uk/government/publications/amended-fuel-duty-rates-for-2026-to-2027/amended-fuel-duty-rates-2026-to-2027
MEAN_ANNUAL_LITRES = 1_200  # avg household fuel consumption litres/year (scaled by decile fuel spend)
MEANS_TEST_AMOUNT = 650  # £ payment, modelled on the 2022 Cost of Living Payment:
# eligibility keyed to means-tested benefit receipt (UC/Pension Credit/legacy), not an income cliff.

# Electricity VAT cut: enacted July 2026 (VAT on domestic electricity 5% -> 0%
# for 1 Oct 2026-31 Mar 2027, ~£45/household, ~£850m). Modelled here as a
# full-year extension. Saving = 5/105 of the electricity bill.
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
