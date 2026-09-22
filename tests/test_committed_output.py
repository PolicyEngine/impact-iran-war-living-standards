"""Checks on the committed results file that need no data access.

These run in CI, where the private managed dataset is unavailable. They catch
the failure mode the September 2026 audit found: source or narrative changes
landing without the results being regenerated.
"""

import json
from pathlib import Path

import pytest

from iran_impact import config, provenance

REPO = Path(__file__).resolve().parents[1]
COMMITTED = REPO / "dashboard" / "public" / "data" / "iran_impact_results.json"


@pytest.fixture(scope="module")
def results():
    return json.loads(COMMITTED.read_text())


def test_committed_output_exists(results):
    assert results["year"] == config.YEAR


def test_committed_output_carries_provenance(results):
    """Without this block a results file cannot be traced to what made it."""
    block = results.get("provenance")
    assert block, "committed results have no provenance block — regenerate them"
    assert block["git_revision"]
    assert block["packages"]["policyengine"]
    assert block["release_bundle"]["certified_data_build_id"]


def test_committed_output_is_not_stale(results):
    """The calculation source must match what produced the committed numbers.

    Fails when config.py or pipeline.py changed without a rerun. Fix by
    running `iran-impact-build --sync-dashboard` with managed-data access.
    """
    recorded = results["provenance"]["source_hashes"]
    current = provenance.source_hashes()
    changed = [name for name in current if recorded.get(name) != current[name]]
    assert not changed, (
        f"{', '.join(changed)} changed since the committed results were "
        "generated — rerun `iran-impact-build --sync-dashboard`"
    )


def test_committed_scenarios_match_the_configured_parameters(results):
    """Guards against config edits landing without a regenerated output."""
    for key, params in config.SCENARIOS.items():
        assert results["scenarios"][key]["params"] == params


def test_every_scenario_reports_the_headline_metrics(results):
    for key in config.SCENARIOS:
        summary = results["scenarios"][key]["summary"]
        for field in [
            "mean_net_impact",
            "total_impact_bn",
            "n_pushed_into_poverty",
            "mean_net_impact_pct",
        ]:
            assert isinstance(summary[field], (int, float))


def test_the_uprating_shortfall_is_reported_but_not_summed(results):
    """The three cost channels must sum to the net impact (#13 review C1)."""
    for key in config.SCENARIOS:
        channels = results["scenarios"][key]["channel_decomposition"]
        assert channels["cost_channels"] == ["energy_shock", "fuel_shock", "food_shock"]
        assert channels["benefit_uprating_shortfall"] > 0
        total = sum(channels[name] for name in channels["cost_channels"])
        # Rounded to whole pounds per channel, so allow a pound of slack.
        assert abs(total - channels["net_impact"]) <= 1


def test_dashboard_narrative_inputs_are_present(results):
    """The dashboard derives its comparison note from these two fields."""
    assert results["baseline"]["mean_household_size"] > 1
    assert results["scenarios"]["low_shock"]["summary"]["n_pushed_into_poverty"] > 0


def test_committed_headlines_match_the_reviewed_values(results):
    """Regression baseline for the pinned certified data build.

    These are the figures reviewed in the pull requests that produced them.
    An accidental regeneration that moves a headline fails here until someone
    updates these values deliberately, in the PR that changes them.

    Data build: policyengine-uk-data-1.56.16 (enhanced_frs_2024_25).
    """
    baseline = results["baseline"]
    assert baseline["n_households_m"] == 31.6
    assert baseline["mean_net_income"] == 57_103
    assert baseline["mean_energy_spend"] == 1_584
    assert baseline["poverty_rate_baseline_pct"] == 18.97
    assert baseline["non_positive_income_households"] == 217_920
    assert baseline["households_with_no_transport_fuel_spend"] == 7_197_973

    central = results["scenarios"]["central_shock"]["summary"]
    assert central["mean_net_impact"] == 1_324
    assert central["total_impact_bn"] == 41.8
    assert central["n_newly_below_anchored_line"] == 1_505_723

    package = results["policy_responses"]["central_shock"]["combined"]
    # Raised from 54.10 in the PR that corrected the CPI adders (#37): the
    # accelerated-uprating leg is sized by cpi_increase_pp, so central's
    # adder moving 2.5pp -> 3.1pp lifts that leg £2.13bn -> £2.64bn. The
    # household cost totals are untouched, since the adder never enters them.
    assert package["gross_outlay_bn"] == 54.62
    assert package["household_protection_bn"] == 37.08
    assert package["residual_impact_bn"] == 4.72


def test_the_policy_accounting_closes_in_the_committed_output(results):
    """Protection plus residual must equal the shock for every policy, in
    every scenario (#14 review C1)."""
    for scenario in config.SCENARIOS:
        shock = results["scenarios"][scenario]["summary"]["total_impact_bn"]
        for name, policy in results["policy_responses"][scenario].items():
            closed = (
                policy["household_protection_bn"] + policy["residual_impact_bn"]
            )
            assert closed == pytest.approx(shock, abs=0.05), f"{scenario}/{name}"
            assert policy["gross_outlay_bn"] >= policy["household_protection_bn"]


def test_no_fuel_poverty_figures_remain(results):
    """The indicator was removed because its level invited comparison with
    official statistics it is not comparable to (#22)."""
    text = json.dumps(results)
    for token in ["fuel_poverty_rate", "fuel_poor_households", "fp_rate", "fp_by_tenure"]:
        assert token not in text, f"{token} still present in the committed output"
    assert "Not reported" in results["metadata"]["fuel_poverty"]


def test_every_scenario_reports_an_evaluated_sensitivity(results):
    """#13 asked for results across the registry's ranges, not just the ranges."""
    for scenario in config.SCENARIOS:
        sensitivity = results["scenarios"][scenario]["sensitivity"]
        summary = results["scenarios"][scenario]["summary"]
        assert sensitivity["central_total_impact_bn"] == summary["total_impact_bn"]
        combined = sensitivity["combined"]
        assert (
            combined["total_impact_bn_low"]
            < sensitivity["central_total_impact_bn"]
            < combined["total_impact_bn_high"]
        )
        assert set(sensitivity["by_parameter"]) == set(config.SCENARIOS[scenario])
        assert "NOT a confidence interval" in sensitivity["basis"]


def test_each_parameter_is_varied_within_its_registered_range(results):
    for scenario in config.SCENARIOS:
        registry = config.PARAMETER_REGISTRY[scenario]["parameters"]
        for name, entry in results["scenarios"][scenario]["sensitivity"][
            "by_parameter"
        ].items():
            assert entry["range"] == list(registry[name]["uncertainty_range"])
            assert entry["total_impact_bn_low"] <= entry["total_impact_bn_high"]


def test_the_cpi_parameter_moves_the_shortfall_not_the_household_cost(results):
    """CPI sizes the uprating shortfall, which #13 removed from the cost
    channels — so varying it leaves the household total unchanged while
    moving the shortfall. Reporting only the total would have made it look
    irrelevant (#13 review A1)."""
    for scenario in config.SCENARIOS:
        entry = results["scenarios"][scenario]["sensitivity"]["by_parameter"][
            "cpi_increase_pp"
        ]
        assert entry["total_impact_bn_low"] == entry["total_impact_bn_high"]
        assert (
            entry["uprating_shortfall_bn_low"]
            < entry["uprating_shortfall_bn_high"]
        )
        assert entry["moves"] == ["uprating_shortfall"]


def test_the_price_parameters_move_the_cost_not_the_shortfall(results):
    for scenario in config.SCENARIOS:
        by_parameter = results["scenarios"][scenario]["sensitivity"][
            "by_parameter"
        ]
        for name in ("cap_increase_pct", "fuel_pct", "food_increase_pct"):
            entry = by_parameter[name]
            assert entry["total_impact_bn_low"] < entry["total_impact_bn_high"]
            assert (
                entry["uprating_shortfall_bn_low"]
                == entry["uprating_shortfall_bn_high"]
            )
            assert entry["moves"] == ["total_impact"]


def test_every_registered_parameter_moves_something(results):
    """A parameter that moves no reported aggregate would be either
    mis-registered or have an unreported effect."""
    for scenario in config.SCENARIOS:
        for name, entry in results["scenarios"][scenario]["sensitivity"][
            "by_parameter"
        ].items():
            assert entry["moves"], f"{scenario}/{name} moves no reported output"


def test_the_fuel_duty_exchequer_cost_is_reported(results):
    """#14 asks that aggregate costs reconcile to a documented tax base."""
    cost = results["parameters"]["fuel_duty_exchequer_cost"]
    assert cost, "no reform-based Exchequer cost in the committed output"
    assert cost["cut_pence_per_litre"] == config.FUEL_DUTY_CUT_PENCE
    assert cost["baseline_receipts_bn"] > cost["reform_receipts_bn"]
    assert cost["exchequer_cost_bn"] == pytest.approx(
        cost["baseline_receipts_bn"] - cost["reform_receipts_bn"], abs=0.02
    )
    # It must say what it does not cover.
    assert "reduced_rate" in cost["not_costed_this_way"]


def test_the_exchequer_and_household_figures_are_both_reported(results):
    """They are near-equal here, which is itself the finding: household
    road-fuel volumes sit close to the national total, so they absorb
    business and freight use."""
    exchequer = results["parameters"]["fuel_duty_exchequer_cost"][
        "exchequer_cost_bn"
    ]
    household = results["policy_responses"]["central_shock"]["fuel_duty_cut"][
        "gross_outlay_bn"
    ]
    assert exchequer == pytest.approx(household, abs=0.1)


def test_the_energy_channel_basis_is_stated(results):
    basis = results["metadata"]["energy_channel_basis"]
    assert "sensitivity" in basis
    assert "not a price-cap calculation" in basis
    for unmodelled in ("standing charges", "fixed-tariff", "quarterly"):
        assert unmodelled in basis


def test_the_low_scenario_note_quotes_the_computed_figures(results):
    """The note is formatted from the same helpers as the registry
    derivation, but the emitted-text guard in test_parameter_registry covers
    only the derivation. A stale literal here would not trip it (#40).

    Asserting on the generated output closes that gap: this fails the moment
    the inputs move and the note is left carrying an old figure.
    """
    note = results["metadata"]["pre_conflict_baseline"]["low_scenario_note"]
    pct = config.announced_oct_2026_vs_pre_conflict_pct()
    low_pct = config.SCENARIOS["low_shock"]["cap_increase_pct"]
    assert f"+{pct}%" in note
    assert f"+{low_pct}%" in note


def test_the_readme_headline_table_matches_the_committed_output(results):
    """The README is the first thing a journalist or NEF reads, and it went
    stale for the whole of the #37 stack: it advertised +80% fuel, £78.6bn and
    2,472,590 after the model had moved to +65%, £73.7bn and 2,386,354 (#46).

    Parsing its tables is crude, but a crude check that runs beats a careful
    one nobody performs.
    """
    from pathlib import Path

    readme = (Path(__file__).parents[1] / "README.md").read_text()

    for key, label in (
        ("low_shock", "Low"),
        ("central_shock", "Central"),
        ("severe_shock", "High"),
    ):
        params = config.SCENARIOS[key]
        summary = results["scenarios"][key]["summary"]

        # The scenario table row: label, energy, fuel, food, CPI.
        row = (
            f"| {label} | +{params['cap_increase_pct']}% | "
            f"+{params['fuel_pct']}% | +{params['food_increase_pct']}% | "
            f"+{params['cpi_increase_pp']}pp |"
        )
        assert row in readme, f"README scenario row is stale for {label}: {row}"

        # Headline figures, wherever they appear in the results table.
        assert f"{summary['total_impact_bn']}bn" in readme, (
            f"README is missing the current total for {label}: "
            f"{summary['total_impact_bn']}bn"
        )
        assert f"{summary['n_newly_below_anchored_line']:,}" in readme, (
            f"README is missing the current newly-below count for {label}"
        )
        assert f"£{summary['mean_net_impact']:,}" in readme, (
            f"README is missing the current mean cost for {label}"
        )
        assert f"{summary['mean_net_impact_pct']}%" in readme, (
            f"README is missing the current mean-of-ratios for {label}"
        )

    # The per-channel sentence, which is quoted as often as the table (#51).
    channels = results["scenarios"]["central_shock"]["channel_decomposition"]
    for field in ("energy_shock", "fuel_shock", "food_shock"):
        assert f"£{channels[field]}" in readme, (
            f"README's central channel breakdown is stale for {field}: "
            f"£{channels[field]}"
        )
    assert f"£{channels['benefit_uprating_shortfall']}" in readme, (
        "README's uprating shortfall is stale"
    )
