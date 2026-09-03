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
CURRENT_ENERGY_CAP = 1_663

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
#   (Brent >$115-120) and Oxford Economics prolonged-war scenario (world CPI
#   7.7%, global recession).
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
