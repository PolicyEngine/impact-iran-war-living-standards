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
    assert config.PRE_CONFLICT_PETROL_PENCE == 131
    assert config.PRE_CONFLICT_DIESEL_PENCE == 156
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
