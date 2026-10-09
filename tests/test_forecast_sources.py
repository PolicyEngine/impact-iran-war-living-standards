"""Every scenario parameter must match the source it cites.

The forecast scenario exists so that a reporter can write "if prices follow
the latest published forecasts" (Telegraph, 9 October 2026). That claim is
only as good as the link between each number and its source, so the link is
tested here rather than left to prose:

- a forecast parameter must equal the derivation from the figures recorded
  for its source, so a source update that is not carried through fails;
- an observed or published-scenario parameter must equal the same
  derivation the stress tests use;
- a derived parameter (CPI) must equal its first-round floor rounded up;
- a judgement must say it is one, so it is never displayed as a forecast.
"""

import pytest

from iran_impact import config

# For each parameter whose value claims to follow from a source, the
# function that recomputes it from what config records about that source.
# A non-judgement entry missing here fails, so a new sourced parameter
# cannot land without a check.
SOURCE_CHECKS = {
    ("low_shock", "fuel_pct"): lambda: round(
        config.fuel_rise_pct_at_brent(config.BRENT_AUG_2026)
    ),
    ("central_shock", "fuel_pct"): lambda: round(config.fuel_rise_pct_at_brent(120)),
    ("severe_shock", "fuel_pct"): lambda: round(config.fuel_rise_pct_at_brent(140)),
    ("external_forecast", "cap_increase_pct"): lambda: config.cap_rise_pct(
        config.forecast_cap_2027_28_gbp()
    ),
    ("external_forecast", "fuel_pct"): lambda: config.fuel_rise_pct_at_brent(
        config.forecast_brent_2027_28()
    ),
    ("external_forecast", "food_increase_pct"): lambda: config.igd_food_revision_pct(),
}


def _entries():
    for scenario, registered in config.PARAMETER_REGISTRY.items():
        for name, entry in registered["parameters"].items():
            yield scenario, name, entry


@pytest.mark.parametrize(
    "scenario,name,entry",
    list(_entries()),
    ids=[f"{s}.{n}" for s, n, _ in _entries()],
)
def test_each_parameter_matches_its_cited_source(scenario, name, entry):
    basis = entry["basis"]
    value = config.SCENARIOS[scenario][name]
    if basis == "judgement":
        assert "judgement" in entry["derivation"].lower(), (
            f"{scenario}.{name} is classed as a judgement but its derivation "
            "does not say so"
        )
        assert (scenario, name) not in SOURCE_CHECKS
    elif basis == "derived":
        # Every CPI adder is its own first-round floor rounded up.
        assert name == "cpi_increase_pp"
        assert value == config.ceil_to_tenth(config.direct_cpi_pp(scenario))
    else:
        assert (scenario, name) in SOURCE_CHECKS, (
            f"{scenario}.{name} claims basis {basis!r} but nothing recomputes "
            "it from its source"
        )
        assert value == SOURCE_CHECKS[(scenario, name)](), (
            f"{scenario}.{name} = {value} no longer matches the derivation "
            "from its recorded source"
        )


def test_only_known_bases_are_used():
    for scenario, name, entry in _entries():
        assert entry["basis"] in config.BASIS_LABELS, f"{scenario}.{name}"
        assert entry["basis_label"] == config.BASIS_LABELS[entry["basis"]]


def test_every_forecast_scenario_price_is_a_forecast():
    """The scenario is labelled forecast-based, so no price in it may be a
    judgement or a stress-test anchor."""
    for name in ("cap_increase_pct", "fuel_pct", "food_increase_pct"):
        entry = config.PARAMETER_REGISTRY["external_forecast"]["parameters"][name]
        assert entry["basis"] == "forecast", name


def test_the_forecast_literals_equal_the_derivation():
    """SCENARIOS holds literals, like the stress tests. They must equal what
    the recorded sources give, all four at once."""
    assert config.SCENARIOS["external_forecast"] == (
        config.forecast_scenario_parameters()
    )


def test_the_forecast_values_are_the_reviewed_ones():
    """Pinned, so a source edit that moves a parameter is a visible change in
    the PR that makes it, not a silent drift."""
    assert config.SCENARIOS["external_forecast"] == {
        "cap_increase_pct": 39.7,
        "cpi_increase_pp": 1.9,
        "fuel_pct": 12.2,
        "food_increase_pct": 2.3,
    }


# ── The recorded source figures themselves ──────────────────────────────


def test_cornwall_components_sum_to_its_published_total():
    f = config.CORNWALL_FORECAST
    # Cornwall rounds each figure to the penny; totals may differ by one.
    assert f["electricity_gbp"] + f["gas_gbp"] == pytest.approx(
        f["total_gbp"], abs=0.01
    )
    assert f["period"] == "January-March 2027"


def test_the_vat_restoration_adds_five_percent_of_electricity_only():
    """The January-March 2027 forecast carries zero VAT on electricity; the
    scenario restores 5% on electricity and leaves gas alone."""
    f = config.CORNWALL_FORECAST
    restored = config.forecast_cap_2027_28_gbp()
    assert restored - f["total_gbp"] == pytest.approx(
        0.05 * f["electricity_gbp"], abs=0.01
    )
    assert config.forecast_cap_2027_28_gbp(vat=0) == pytest.approx(
        f["total_gbp"], abs=0.01
    )


def test_the_eia_path_is_the_published_table():
    b = config.EIA_STEO_BRENT
    assert [b[q] for q in ("2027Q1", "2027Q2", "2027Q3", "2027Q4")] == [
        94.90,
        87.00,
        80.03,
        73.94,
    ]
    # 2027-28 is April 2027 to March 2028; the STEO ends in December 2027.
    assert config.FORECAST_BRENT_QUARTERS_2027_28 == [
        "2027Q2",
        "2027Q3",
        "2027Q4",
        "2027Q4",
    ]
    assert config.forecast_brent_2027_28() == pytest.approx(
        (87.00 + 80.03 + 73.94 + 73.94) / 4, abs=0.005
    )


def test_igd_ranges_are_the_published_one_point_bands():
    for vintage in (
        config.IGD_FOOD_INFLATION_PRE_CONFLICT,
        config.IGD_FOOD_INFLATION_LATEST,
    ):
        for year, band in vintage.items():
            if year == "published":
                continue
            low, high = band
            assert high - low == pytest.approx(1.0), (vintage["published"], year)
    # The pre-conflict vintage must predate the conflict (28 February 2026).
    assert config.IGD_FOOD_INFLATION_PRE_CONFLICT["published"] < "2026-02-28"
    assert config.IGD_FOOD_INFLATION_LATEST["published"] > "2026-02-28"


def test_each_forecast_entry_is_dated_by_its_own_source():
    """An entry citing one source and dated from another sends an auditor to
    the wrong page (#55 review A6)."""
    params = config.PARAMETER_REGISTRY["external_forecast"]["parameters"]
    assert params["cap_increase_pct"]["source_date"] == config.CORNWALL_FORECAST["published"]
    assert params["fuel_pct"]["source_date"] == config.EIA_STEO_BRENT["published"]
    assert params["food_increase_pct"]["source_date"] == (
        config.IGD_FOOD_INFLATION_LATEST["published"]
    )


def test_no_forecast_is_dated_after_the_vintage_it_is_reported_as():
    for name, entry in config.PARAMETER_REGISTRY["external_forecast"][
        "parameters"
    ].items():
        assert entry["source_date"] <= config.FORECAST_AS_OF, name
    for update in config.FORECAST_NEXT_UPDATES:
        assert update["due"] > config.FORECAST_AS_OF[: len(update["due"])]


def test_the_forecast_ranges_come_from_the_sources():
    params = config.PARAMETER_REGISTRY["external_forecast"]["parameters"]
    assert params["cap_increase_pct"]["uncertainty_range"] == (
        config.forecast_energy_range_pct()
    )
    assert params["fuel_pct"]["uncertainty_range"] == config.forecast_fuel_range_pct()
    assert params["food_increase_pct"]["uncertainty_range"] == (
        config.forecast_food_range_pct()
    )
    assert params["cpi_increase_pp"]["uncertainty_range"] == (
        config.forecast_cpi_range_pp()
    )


def test_the_energy_range_spans_the_supplier_forecasts():
    low, high = config.forecast_energy_range_pct()
    totals = [f["total_gbp"] for f in config.SUPPLIER_CAP_FORECASTS_2027_28]
    assert low == config.cap_rise_pct(min(totals))
    assert high == config.cap_rise_pct(max(totals))
    for forecast in config.SUPPLIER_CAP_FORECASTS_2027_28:
        assert "2027" in forecast["period"]
        assert forecast["published"] <= config.FORECAST_AS_OF


# ── Every source is named and every gap stated ──────────────────────────


def test_every_registry_url_has_a_display_name():
    """The dashboard shows who said it, not a bare link."""
    for scenario, name, entry in _entries():
        assert entry["source_name"] == config.SOURCE_NAMES[entry["source_url"]]
        for url in entry.get("supporting_source_urls", []):
            assert url in config.SOURCE_NAMES, f"{scenario}.{name}: {url}"
        assert [s["url"] for s in entry["supporting_sources"]] == list(
            entry.get("supporting_source_urls", [])
        )


def test_the_gaps_are_stated_where_a_reader_will_see_them():
    """Where no forecast covers 2027-28 the scenario rests on an assumption,
    and the output has to say which."""
    gaps = " ".join(config.FORECAST_GAPS)
    assert "Cornwall Insight publishes no price cap forecast" in gaps
    assert "No published forecast of UK pump prices" in gaps
    assert "food" in gaps
    assert "OBR" in gaps
    cap = config.PARAMETER_REGISTRY["external_forecast"]["parameters"][
        "cap_increase_pct"
    ]["derivation"]
    assert "is an assumption, not a forecast" in cap


def test_the_food_parameter_says_it_is_a_revision_not_inflation():
    entry = config.PARAMETER_REGISTRY["external_forecast"]["parameters"][
        "food_increase_pct"
    ]
    assert "Revision" in entry["definition"]
    assert "not the conflict alone" in entry["derivation"]
    assert f"{config.igd_food_revision_pct()}%" in entry["derivation"]


def test_derivations_quote_the_computed_figures():
    """The prose ships publicly, so every figure it quotes must be the one
    the functions compute (#40)."""
    params = config.PARAMETER_REGISTRY["external_forecast"]["parameters"]
    cap = params["cap_increase_pct"]["derivation"]
    assert f"£{config.forecast_cap_2027_28_gbp():,.2f}" in cap
    assert f"+{config.SCENARIOS['external_forecast']['cap_increase_pct']}%" in cap
    fuel = params["fuel_pct"]["derivation"]
    assert f"${config.forecast_brent_2027_28():.2f}" in fuel
    assert f"+{config.SCENARIOS['external_forecast']['fuel_pct']}%" in fuel
