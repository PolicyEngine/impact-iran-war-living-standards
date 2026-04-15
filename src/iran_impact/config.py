"""Configuration constants for energy price shock impact on UK living standards analysis."""

YEAR = 2026
CURRENT_ENERGY_CAP = 1_641  # Ofgem price cap £/year

SCENARIOS = {
    "low_shock": {
        "cap_increase_pct": 30,
        "cpi_increase_pp": 1.5,
        "fuel_pct": 20,
        "food_increase_pct": 2.0,
    },
    "central_shock": {
        "cap_increase_pct": 75,
        "cpi_increase_pp": 3.5,
        "fuel_pct": 50,
        "food_increase_pct": 4.5,
    },
    "severe_shock": {
        "cap_increase_pct": 150,
        "cpi_increase_pp": 6.0,
        "fuel_pct": 100,
        "food_increase_pct": 6.4,
    },
}

BASE_FUEL_SPEND = 1_300
BASE_FOOD_SPEND = 5_000
FUEL_DECILE_FACTORS = {
    1: 0.70,
    2: 0.70,
    3: 0.90,
    4: 0.90,
    5: 1.00,
    6: 1.00,
    7: 1.15,
    8: 1.15,
    9: 1.25,
    10: 1.25,
}
FOOD_DECILE_FACTORS = {
    1: 0.65,
    2: 0.65,
    3: 0.80,
    4: 0.80,
    5: 1.00,
    6: 1.00,
    7: 1.20,
    8: 1.20,
    9: 1.45,
    10: 1.45,
}

UPRATING_LAG_MONTHS = 12
FUEL_POVERTY_THRESHOLD = 0.10

# Structural constants
WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12
PENCE_PER_POUND = 100
POVERTY_LINE_RATIO = 0.6  # 60% of median income (relative poverty)
WINNERS_LOSERS_THRESHOLD = 1  # £1 change threshold for classifying winners/losers

# Policy parameters
EPG_CAP_PCT = 0.10  # Energy Price Guarantee caps increase at 10%
FLAT_REBATE = 400  # £ per household
CT_REBATE = 300    # £ council tax rebate bands A-D
UC_UPLIFT_WEEKLY = 25  # £/week
FUEL_DUTY_CUT_PENCE = 5  # pence per litre
MEAN_ANNUAL_LITRES = 1_200  # avg household fuel consumption litres/year
MEANS_TEST_THRESHOLD = 25_000  # household income threshold for means-tested payment
MEANS_TEST_AMOUNT = 650  # £ payment for eligible households

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
