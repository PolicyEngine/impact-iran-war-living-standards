"""Every scenario input must be documented and traceable (#13)."""

import pytest

from iran_impact import config

REQUIRED_FIELDS = [
    "value",
    "definition",
    "unit",
    "geography",
    "applies_to",
    "lag",
    "source_url",
    "source_date",
    "reference_period",
    "derivation",
    "uncertainty_range",
]


def test_registry_covers_exactly_the_configured_scenarios():
    assert set(config.PARAMETER_REGISTRY) == set(config.SCENARIOS)


def test_registry_covers_exactly_the_configured_parameters():
    """No scenario input may go undocumented, and none may be documented but
    unused."""
    for scenario, params in config.SCENARIOS.items():
        registered = config.PARAMETER_REGISTRY[scenario]["parameters"]
        assert set(registered) == set(params)


def test_registry_values_match_the_values_actually_used():
    for scenario, params in config.SCENARIOS.items():
        registered = config.PARAMETER_REGISTRY[scenario]["parameters"]
        for name, value in params.items():
            assert registered[name]["value"] == value


@pytest.mark.parametrize("scenario", list(config.SCENARIOS))
def test_every_entry_carries_the_required_fields(scenario):
    entry = config.PARAMETER_REGISTRY[scenario]
    assert entry["narrative"]
    for name, parameter in entry["parameters"].items():
        for field in REQUIRED_FIELDS:
            assert parameter.get(field) not in (None, "", []), (
                f"{scenario}.{name} is missing {field}"
            )


@pytest.mark.parametrize("scenario", list(config.SCENARIOS))
def test_sources_are_urls_with_dates(scenario):
    for parameter in config.PARAMETER_REGISTRY[scenario]["parameters"].values():
        assert parameter["source_url"].startswith("https://")
        # ISO date, so the vintage of each source is unambiguous.
        assert len(parameter["source_date"]) == 10
        assert parameter["source_date"].count("-") == 2


@pytest.mark.parametrize("scenario", list(config.SCENARIOS))
def test_uncertainty_ranges_bracket_the_value(scenario):
    for name, parameter in config.PARAMETER_REGISTRY[scenario]["parameters"].items():
        low, high = parameter["uncertainty_range"]
        assert low <= parameter["value"] <= high, f"{scenario}.{name}"


def test_units_distinguish_percentages_from_percentage_points():
    """cpi_increase_pp is an addition to CPI, not a percentage increase."""
    for scenario in config.SCENARIOS:
        params = config.PARAMETER_REGISTRY[scenario]["parameters"]
        assert params["cpi_increase_pp"]["unit"] == "percentage points"
        assert params["cap_increase_pct"]["unit"] == "per cent"


def test_severe_cpi_derivation_states_the_published_world_figure():
    """The config previously attributed 7.7% to Oxford Economics; it is 5.8%."""
    derivation = config.PARAMETER_REGISTRY["severe_shock"]["parameters"][
        "cpi_increase_pp"
    ]["derivation"]
    assert "5.8%" in derivation
    assert "7.7%" in derivation and "does not report" in derivation


def test_uprating_lag_registry_states_its_counterfactual():
    registry = config.UPRATING_LAG_REGISTRY
    assert registry["definition"] and registry["derivation"]
    assert registry["source_url"].startswith("https://")
    # The counterfactual must say the amount is not counted as a cost.
    assert "NOT added" in registry["counterfactual"]
    assert "twice" in registry["counterfactual"]
    assert "immediate uprating" in registry["counterfactual"]


def test_scenario_type_is_declared_as_a_stress_test():
    assert config.SCENARIO_TYPE == "annual stress test"


def test_limitations_cover_the_unmodelled_dimensions():
    joined = " ".join(config.METHOD_LIMITATIONS).lower()
    for topic in [
        "standing charge",
        "fixed tariff",
        "quarterly",
        "time path",
        "pass-through",
        "uprating",
        "sampling uncertainty",
    ]:
        assert topic in joined, f"limitations do not mention {topic}"


def test_the_cap_constant_is_not_used_in_any_calculation():
    """CURRENT_ENERGY_CAP is reported as context only (#13)."""
    from pathlib import Path

    pipeline = Path(config.__file__).with_name("pipeline.py").read_text()
    # The constant may be imported and written into the output, but must not
    # appear in any arithmetic.
    allowed = {
        "CURRENT_ENERGY_CAP,",  # the import list
        '"current_energy_cap": CURRENT_ENERGY_CAP,',  # reported as context
    }
    for line in pipeline.splitlines():
        if "CURRENT_ENERGY_CAP" not in line:
            continue
        assert line.strip() in allowed, (
            f"CURRENT_ENERGY_CAP used in a calculation: {line.strip()}"
        )


def test_the_october_cap_is_recorded():
    assert config.OCTOBER_2026_ENERGY_CAP == 1_723
    assert config.FIXED_TARIFF_ACCOUNT_SHARE == pytest.approx(0.40)


# ── Sensitivity: the registry's ranges, evaluated (#13) ──────────────────


def test_compute_scenario_accepts_a_parameter_override():
    """The sensitivity analysis walks the ranges through the real model
    rather than reimplementing the arithmetic."""
    import numpy as np

    from iran_impact.pipeline import compute_scenario

    decile = np.arange(1, 11)
    data = {
        "energy": np.full(10, 1_000.0),
        "fuel_cost": np.full(10, 500.0),
        "food_cost": np.full(10, 2_000.0),
        "benefit_income": np.zeros(10),
    }
    base = compute_scenario(data, "central_shock")
    doubled = dict(config.SCENARIOS["central_shock"])
    doubled["cap_increase_pct"] *= 2
    override = compute_scenario(data, "central_shock", params_override=doubled)
    assert override["energy_shock"].sum() == pytest.approx(
        base["energy_shock"].sum() * 2
    )


def test_the_energy_channel_is_labelled_as_a_sensitivity():
    """#13 offered modelling retail energy properly or relabelling the
    channel. This is the relabel, so the label has to be unambiguous."""
    joined = " ".join(config.METHOD_LIMITATIONS)
    assert "household-energy-expenditure sensitivity" in joined
    assert "rather than a price-cap calculation" in joined
    # And it must say the relabel was the deliberate choice, not an omission.
    assert "this is the relabel" in joined


# ── Pre-conflict baseline (#37) ──────────────────────────────────────────


def test_the_pre_conflict_baseline_is_recorded():
    """The percentages are measured from it, so it has to be a number rather
    than prose or the forcing assumptions cannot be audited."""
    assert config.PRE_CONFLICT_CAP_NEW_BASIS == 1_465
    assert config.PRE_CONFLICT_CAP_OLD_BASIS == 1_641
    # Observed DESNZ November 2025 monthly means, not back-derived (#37).
    # Unrounded DESNZ means: rounding these before dividing gave 19.3%/26.4%
    # where the observed rises are 19.5%/26.5% (#46).
    assert config.PRE_CONFLICT_PETROL_PENCE == pytest.approx(135.04)
    assert config.PRE_CONFLICT_DIESEL_PENCE == pytest.approx(143.82)
    assert config.AUGUST_2026_PETROL_PENCE == pytest.approx(161.42)
    assert config.AUGUST_2026_DIESEL_PENCE == pytest.approx(181.98)
    assert config.observed_petrol_rise_pct() == pytest.approx(19.5, abs=0.05)
    assert config.observed_diesel_rise_pct() == pytest.approx(26.5, abs=0.05)
    # Diesel rose materially more than petrol, so a single uniform uplift
    # cannot describe both — the error the old back-derivation made.
    assert config.observed_diesel_rise_pct() > config.observed_petrol_rise_pct() + 5
    # Pump prices sit on a different reference period from the cap, which the
    # block must state rather than implying one period covers both (#37).
    assert "2025" in config.PRE_CONFLICT_PUMP_PRICE_PERIOD


def test_the_baseline_derivation_reproduces_from_the_stated_figures():
    """£1,663 at +13.5% implies £1,465; and the old-basis cross-check must
    land on PolicyEngine UK's own cap parameter."""
    implied_new = config.CURRENT_ENERGY_CAP / 1.135
    assert implied_new == pytest.approx(config.PRE_CONFLICT_CAP_NEW_BASIS, abs=1)
    # £1,663 new basis is stated as £1,862 old basis in the config comments.
    implied_old = 1_862 / 1.135
    assert implied_old == pytest.approx(config.PRE_CONFLICT_CAP_OLD_BASIS, abs=1)


def test_the_low_scenario_is_not_silently_below_an_announced_outturn():
    """The announced Oct 2026 cap is +17.6% on the pre-conflict baseline. The
    low scenario sits below that, which is defensible only because it is
    labelled as the premium unwinding rather than as de-escalation (#37)."""
    announced_pct = config.announced_oct_2026_vs_pre_conflict_pct()
    assert announced_pct == pytest.approx(17.6, abs=0.1)
    # Derived from the one constant, so the figure cannot drift between the
    # config, the registry and the dashboard.
    assert config.OCTOBER_2026_ENERGY_CAP == 1_723

    low = config.SCENARIOS["low_shock"]["cap_increase_pct"]
    if low < announced_pct:
        derivation = config.PARAMETER_REGISTRY["low_shock"]["parameters"][
            "cap_increase_pct"
        ]["derivation"]
        assert "below" in derivation.lower(), (
            "the low scenario is below the announced October 2026 cap, so its "
            "derivation must say so rather than calling it de-escalation"
        )


def test_the_low_scenario_is_not_described_as_de_escalation():
    """It sits below an announced cap, so calling it de-escalation is wrong.
    The label lives in one place; this guards the config side of it (#37)."""
    low = config.PARAMETER_REGISTRY["low_shock"]
    assert "de-escalat" not in low["narrative"].lower()
    for parameter in low["parameters"].values():
        text = parameter["derivation"].lower()
        # The energy derivation may say "not a de-escalation"; nothing may
        # assert the scenario IS one.
        assert "conflict de-escalates" not in text


def test_emitted_text_quotes_the_computed_announced_cap_percentage():
    """Assert on the emitted text against the function, not on the source.

    An earlier version of this test grepped the source for the current
    computed value. That catches a literal only while it is still correct: if
    the inputs move, a stale literal stops matching what the test searches
    for and the test passes — exactly the drift it claims to prevent (#40).

    Asserting the derivation CONTAINS the computed figure fails the moment the
    inputs move and a stale literal is left behind.
    """
    pct = config.announced_oct_2026_vs_pre_conflict_pct()
    derivation = config.PARAMETER_REGISTRY["low_shock"]["parameters"][
        "cap_increase_pct"
    ]["derivation"]
    assert f"+{pct}%" in derivation


def test_no_new_literals_of_the_computed_percentage_in_source():
    """Belt-and-braces on newly introduced literals, alongside the test above.

    On its own this is not a drift guard, for the reason given there.
    """
    from pathlib import Path

    pct = config.announced_oct_2026_vs_pre_conflict_pct()
    for name in ("config.py", "pipeline.py"):
        source = (Path(config.__file__).with_name(name)).read_text()
        code = "\n".join(
            line for line in source.splitlines() if not line.lstrip().startswith("#")
        )
        assert f"+{pct}%" not in code, (
            f"{name} carries a literal +{pct}% in emitted text; format it from "
            "announced_oct_2026_vs_pre_conflict_pct() instead"
        )


def test_no_cpi_adder_sits_below_its_own_first_round_effect():
    """A scenario's CPI adder must not be below the direct basket effect of
    its own price assumptions unless the derivation says what offsets it.

    Central previously breached this AND its own declared range ceiling: the
    first-round effect was 3.06pp against a range topping out at 3.0pp, so the
    midpoint was not conservative but arithmetically impossible (#37). This is
    checkable in one line by any reader, which is why it matters.
    """
    for key in config.SCENARIOS:
        adder = config.SCENARIOS[key]["cpi_increase_pp"]
        floor = config.direct_cpi_pp(key)
        assert adder >= floor, (
            f"{key}: CPI adder {adder}pp is below the {floor}pp first-round "
            "direct effect of its own energy, fuel and food assumptions"
        )


def test_each_cpi_range_contains_its_own_first_round_effect():
    """The declared uncertainty range must be able to contain the arithmetic."""
    for key in config.SCENARIOS:
        low, high = config.PARAMETER_REGISTRY[key]["parameters"][
            "cpi_increase_pp"
        ]["uncertainty_range"]
        floor = config.direct_cpi_pp(key)
        assert low <= floor <= high, (
            f"{key}: first-round effect {floor}pp falls outside the declared "
            f"range [{low}, {high}]"
        )


def test_the_pump_slopes_derive_from_same_period_monthly_means():
    """Both slopes must come from monthly means at BOTH ends.

    The original defect paired DESNZ monthly pump means with a single-day
    Brent spot, overstating the slope by about 30% (#52 review C2). This
    reproduces the arithmetic independently of the prose.
    """
    petrol = (config.AUGUST_2026_PETROL_PENCE - config.PRE_CONFLICT_PETROL_PENCE) / (
        config.BRENT_AUG_2026 - config.BRENT_NOV_2025
    )
    diesel = (config.AUGUST_2026_DIESEL_PENCE - config.PRE_CONFLICT_DIESEL_PENCE) / (
        config.BRENT_AUG_2026 - config.BRENT_NOV_2025
    )
    assert config.petrol_slope() == pytest.approx(petrol)
    assert config.diesel_slope() == pytest.approx(diesel)
    assert petrol == pytest.approx(0.967, abs=0.005)
    # Diesel cracks widened far more; a petrol-only rate understates the
    # combined ONS category (#55 review C1).
    assert diesel == pytest.approx(1.399, abs=0.005)
    assert diesel > petrol


def test_the_fuel_assumptions_are_the_composite_at_their_cited_brent():
    """Central sits at Goldman's $120 and severe at Oxford's $140, on the
    expenditure-weighted composite rather than a petrol-only rate (#55 C1)."""
    assert config.fuel_rise_pct_at_brent(120) == pytest.approx(45.8, abs=0.3)
    assert config.fuel_rise_pct_at_brent(140) == pytest.approx(62.1, abs=0.3)
    assert config.SCENARIOS["central_shock"]["fuel_pct"] == 46
    assert config.SCENARIOS["severe_shock"]["fuel_pct"] == 62

    # Each scenario must sit at its own cited case, within rounding.
    for key, brent in (("central_shock", 120), ("severe_shock", 140)):
        assert config.SCENARIOS[key]["fuel_pct"] == pytest.approx(
            config.fuel_rise_pct_at_brent(brent), abs=0.5
        ), f"{key} no longer sits at the composite for its cited Brent case"


def test_the_petrol_diesel_split_matches_the_ons_table_it_cites():
    """The shares come from the same ONS release and year as the combined
    mean the model already uses, so they must sum to it."""
    total = (
        config.PETROL_WEEKLY_SPEND
        + config.DIESEL_WEEKLY_SPEND
        + config.OTHER_MOTOR_OILS_WEEKLY_SPEND
    )
    # The sub-lines sum to £19.90 against A6's £19.80: ONS rounds each line
    # to 10p, so the two tables do not reconcile exactly. Only the SHARES are
    # used, and a 10p rounding gap moves them by under half a point.
    assert total == pytest.approx(config.BASE_FUEL_SPEND / 52, abs=0.15), (
        "the A1 sub-lines no longer sum to the A6 combined figure the model uses"
    )
    petrol_share = config.PETROL_WEEKLY_SPEND / total
    assert petrol_share == pytest.approx(0.61, abs=0.01)


def test_the_low_fuel_value_is_the_observed_weighted_composite():
    """Low claims "the observed change" for the combined ONS category, so it
    must be the expenditure-weighted composite of the observed petrol and
    diesel moves, not the petrol figure alone (#55 review A4).

    That was the original defect: 20% was petrol's 19.5% applied to a
    category that is 39% diesel.
    """
    observed = config.fuel_rise_pct_at_brent(config.BRENT_AUG_2026)
    assert config.SCENARIOS["low_shock"]["fuel_pct"] == pytest.approx(
        observed, abs=0.5
    ), (
        "low no longer sits at the observed composite "
        f"({observed}%); it may have reverted to the petrol-only figure"
    )
    # And it must sit between the two products' observed moves.
    assert (
        config.observed_petrol_rise_pct()
        < observed
        < config.observed_diesel_rise_pct()
    )


def test_every_cpi_derivation_quotes_its_own_computed_floor():
    """The registry prose ships publicly, so a floor it quotes must be the
    floor the model computes (#55 review A1)."""
    for key in config.SCENARIOS:
        derivation = config.PARAMETER_REGISTRY[key]["parameters"][
            "cpi_increase_pp"
        ]["derivation"]
        floor = config.direct_cpi_pp(key)
        if "on ONS 2026 basket" in derivation or "ONS 2026 basket" in derivation:
            assert f"{floor}pp" in derivation, (
                f"{key}: the CPI derivation quotes a floor that is no longer "
                f"{floor}pp"
            )


# Each source's own publication date, so an entry cannot cite one source and
# date it from another (#55 review A6).
SOURCE_DATES = {
    "kpler.com": "2026-03-10",
    "oxfordeconomics.com": "2026-03-13",
}


def test_each_entry_is_dated_by_the_source_it_cites():
    """A registry entry that points at one source and carries another's date
    sends an auditor to the wrong page. That happened when a metadata edit
    crossed parameters (#55 review A6)."""
    mismatched = []
    for key, scenario in config.PARAMETER_REGISTRY.items():
        for name, parameter in scenario["parameters"].items():
            for host, published in SOURCE_DATES.items():
                if host in parameter["source_url"]:
                    if parameter["source_date"] != published:
                        mismatched.append(
                            f"{key}.{name} cites {host} but is dated "
                            f"{parameter['source_date']}, not {published}"
                        )
    assert not mismatched, mismatched


def test_the_gas_driven_cap_entries_do_not_cite_an_oil_reference_period():
    """The energy channel is gas-driven — crude enters the cap nowhere (#44).
    A cap entry labelled with a Brent case contradicts its own derivation."""
    for key in ("central_shock", "severe_shock"):
        period = config.PARAMETER_REGISTRY[key]["parameters"][
            "cap_increase_pct"
        ]["reference_period"]
        assert "bbl" not in period and "Brent" not in period, (
            f"{key}: the cap reference_period names an oil case ({period!r}), "
            "but the cap derivation says crude enters it nowhere"
        )


def test_april_june_is_never_tied_to_the_conflict_without_the_announcement():
    """Ofgem announced the April-June 2026 cap on 25 February; the conflict
    began in late February. So the ANNOUNCEMENT precedes the conflict, and
    the period it covers does not.

    I wrote this the wrong way round four times (#37, #54 A1, #55 A8, A10),
    so it is a test. An earlier version tried to match the wrong phrasings
    with regexes; that could not tell whether "before the conflict" attached
    to the period or to the announcement, so it missed real variants and
    flagged a valid reordered one (#55 review A10).

    This asserts the positive instead: wherever April-June 2026 appears near
    the conflict, the announcement must appear too.
    """
    import re
    from pathlib import Path

    sources = [Path(config.__file__).with_name(n) for n in ("config.py", "pipeline.py")]
    sources += sorted((Path(config.__file__).parents[2] / "dashboard" / "src").rglob("*.jsx"))

    period = re.compile(r"April[-–—\s]*(?:June|&ndash;June)\s*2026", re.I)
    offenders = []
    for path in sources:
        text = path.read_text()
        for match in period.finditer(text):
            window = text[max(0, match.start() - 200) : match.end() + 200]
            if not re.search(r"\bconflict\b", window, re.I):
                continue
            if not re.search(r"announc", window, re.I):
                offenders.append(
                    f"{path.name}: ...{window[max(0,match.start()-60-max(0,match.start()-200)):][:150]}..."
                )
    assert not offenders, (
        "these tie April-June 2026 to the conflict without saying the cap was "
        f"ANNOUNCED before it; the period itself is not pre-conflict: {offenders}"
    )
