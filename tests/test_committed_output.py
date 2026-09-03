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
            "fp_rate_baseline_pct",
            "fp_rate_shocked_pct",
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
    assert baseline["fuel_poverty_rate_pct"] == 10.5

    central = results["scenarios"]["central_shock"]["summary"]
    assert central["mean_net_impact"] == 1_324
    assert central["total_impact_bn"] == 41.8
    assert central["n_newly_below_anchored_line"] == 1_505_723

    package = results["policy_responses"]["central_shock"]["combined"]
    assert package["gross_outlay_bn"] == 54.87
    assert package["household_protection_bn"] == 37.03
    assert package["residual_impact_bn"] == 4.77


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
