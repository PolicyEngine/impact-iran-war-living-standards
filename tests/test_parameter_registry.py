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
    # The double-count risk must be stated, not left implicit.
    assert "double-count" in registry["counterfactual"]
    assert "immediate" in registry["counterfactual"]


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
