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
    w = CPI_BASKET_WEIGHTS_2026
    return round(
        s["cap_increase_pct"] * w["energy"]
        + s["fuel_pct"] * w["fuel"]
        + s["food_increase_pct"] * w["food"],
        2,
    )


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
GOLDMAN_HORMUZ = "https://oilprice.com/Latest-Energy-News/World-News/Goldman-Another-Month-of-Hormuz-Closure-Means-Over-100-Brent-Throughout-2026.html"
# The energy channel transmits through GAS, not oil, so it cites gas sources.
# Ofgem's wholesale allowance is built from NBP gas and UK baseload power
# forwards; crude oil enters the cap nowhere (#37).
KPLER_HORMUZ_LNG = "https://www.kpler.com/blog/hormuz-strait-disruptions-trigger-a-price-spike-in-ttf-and-asian-lng-while-middle-east-exports-come-to-a-halt"
OFGEM_CAP_METHODOLOGY = "https://www.ofgem.gov.uk/information-consumers/energy-advice-households/energy-price-cap"
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
            "Prices settle near their current elevated levels rather than "
            "falling back, from the August 2026 position: Brent settles "
            "near $85/bbl, pump prices around 161p petrol and 182p diesel "
            "(DESNZ August 2026 means)"
        ),
        "cap_increase_pct": {
            "source_url": OFGEM_JULY_2026,
            "source_date": "2026-07-01",
            "reference_period": "1 July - 30 September 2026 cap period",
            "derivation": (
                "Anchored to the observed +13.5% July 2026 cap rise. Not "
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
            "source_date": "2026-08-04",
            "reference_period": "August 2026 spot prices",
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
            "source_date": "2026-08-04",
            "reference_period": "2027-28",
            "derivation": (
                "Judgement: food price response to energy prices settling "
                "near current levels; no published scenario for this figure"
            ),
            "uncertainty_range": [1.0, 3.0],
        },
        "cpi_increase_pp": {
            "source_url": "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026",
            "source_date": "2026-06-01",
            "reference_period": "2026-27",
            "derivation": (
                "Bank of England June 2026 projection of CPI near 3% against "
                "about 2% pre-conflict, i.e. roughly +1pp. Raised to 1.3pp so "
                "the adder is not below the first-round direct effect of this "
                "scenario's own price assumptions, which ONS 2026 basket "
                "weights put at 1.23pp (#37)"
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
            "source_date": "2026-07-01",
            "reference_period": "2026 calendar year",
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
            "source_date": "2026-07-01",
            "reference_period": "2026 calendar year",
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
                "pre-conflict, whose +1pp to +3pp range was previously taken "
                "at the middle. Raised to 3.1pp because the first-round "
                "direct effect of this scenario's own price assumptions is "
                "3.06pp on ONS 2026 basket weights, above the whole of that "
                "range — so the midpoint was not merely conservative but "
                "arithmetically impossible without a demand-destruction "
                "offset the derivation never stated (#37)"
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
            "source_date": "2026-06-01",
            "reference_period": "two-month $140/bbl case",
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
            "source_date": "2026-06-01",
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
                "above its baseline. Set to 5.3pp for UK CPI: the "
                "first-round direct effect of this scenario's own price "
                "assumptions on ONS 2026 basket weights, which exceeds the "
                "~3pp world figure, consistent with the UK's higher energy "
                "import share. The source "
                "does not publish a UK figure, and does not report the 7.7% "
                "this file previously attributed to it"
            ),
            "uncertainty_range": [4.5, 7.0],
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
        "Expected fraction of the year an accelerated uprating would cover, "
        "for a shock arriving at a uniformly distributed point in it: 0.5. "
        "Applied uniformly rather than benefit by benefit"
    ),
    "counterfactual": (
        "The scheduled April uprating is set from the previous September's "
        "CPI, so it does not reflect a shock arriving after that and no "
        "offset reaches households during the stress-test year. The "
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
    "Scenario type: annual stress test, not a forecast. Every change is "
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
    "Benefit uprating: a single expected-coverage factor is applied to a broad "
    "set of CPI-linked benefit income, rather than modelling each benefit's "
    "own uprating rule and April 2027 timing against the price path. The "
    "amount is reported as the compensation an immediate uprating would "
    "deliver and is not counted as a cost, so the household loss is the price "
    "rise alone.",
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

# Benefit uprating: CPI-linked benefits are uprated each April using the
# previous September's CPI, so a shock arriving after that September is not
# reflected in the scheduled uprating and no offset arrives during the year.
#
# The household's loss is therefore the price rise itself, which the three
# cost channels already measure. This factor does NOT add a fourth cost — it
# sizes the compensation that an immediate uprating would deliver, which is
# what the accelerated-uprating policy provides. Applying it as an
# expected-value factor of 0.5 reflects an accelerated uprating covering, on
# average, half of the year.
# The April 2026 uprating (+3.8%, Sept 2025 CPI; UC standard allowance +2.3%
# extra under the Universal Credit Act 2025) predates the conflict shock.
# Source: https://commonslibrary.parliament.uk/research-briefings/cbp-10403/
UPRATING_LAG_FACTOR = 0.5

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
