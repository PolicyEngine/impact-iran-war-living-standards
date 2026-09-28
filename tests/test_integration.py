"""End-to-end checks against the certified managed dataset.

Skipped wherever the private managed dataset is unavailable, which includes
CI. Run locally with managed-data access before pushing any change to the
calculation:

    pytest tests/test_integration.py

The pinned values are the results for the certified data build named below.
"""

import pytest

from iran_impact import config

CERTIFIED_DATA_BUILD = "policyengine-uk-data-1.56.16"
CERTIFIED_MODEL_VERSION = "2.90.2"

# Baseline figures for the certified build above (policyengine 5.3.0,
# enhanced_frs_2024_25). Tolerances are tight because the same code against
# the same certified build is deterministic; they exist only to absorb the
# rounding applied on output.
#
# The September 2026 audit's reproduced figures (29.6m households, £61,924
# mean net income, £1,331 mean energy spend) belong to the superseded
# populace_uk_2023 build and no longer apply.
EXPECTED_HOUSEHOLDS_M = 31.6
EXPECTED_MEAN_NET_INCOME = 57_103
EXPECTED_MEAN_ENERGY_SPEND = 1_584


def _baseline():
    """Run the baseline, skipping only where the dataset is genuinely absent.

    Availability is not guessed at. Enumerating token environment variables
    or looking for a Hugging Face cache directory both get this wrong:
    policyengine.py accepts several token names, and it only reuses a
    SHA-verified artifact at its own materialization target, so a populated
    hub cache does not mean the run can proceed.

    Instead the materializer decides. Only its own
    DatasetMaterializationError counts as "no data"; every other failure —
    model, schema or calculation — propagates as a test failure, which is the
    point of these tests.
    """
    try:
        from policyengine.provenance.dataset_materialization import (
            DatasetMaterializationError,
        )
    except ImportError:
        pytest.skip("policyengine[uk] is not installed")

    from iran_impact.pipeline import run_baseline

    try:
        return run_baseline(year=config.YEAR)
    except DatasetMaterializationError as exc:
        pytest.skip(f"certified dataset unavailable: {exc}")


@pytest.fixture(scope="module")
def baseline():
    return _baseline()


def test_run_uses_the_certified_data_build(baseline):
    """A different data build invalidates every pinned figure below."""
    bundle = baseline["bundle"]
    assert bundle, "managed simulation exposed no release bundle"
    assert bundle["certified_data_build_id"] == CERTIFIED_DATA_BUILD
    assert bundle["model_version"] == CERTIFIED_MODEL_VERSION


def test_baseline_population_matches_the_audit(baseline):
    from iran_impact.pipeline import weighted_mean

    weights = baseline["weights"]
    assert weights.sum() / 1e6 == pytest.approx(EXPECTED_HOUSEHOLDS_M, abs=0.05)
    assert weighted_mean(baseline["income"], weights) == pytest.approx(
        EXPECTED_MEAN_NET_INCOME, abs=1
    )
    assert weighted_mean(baseline["energy"], weights) == pytest.approx(
        EXPECTED_MEAN_ENERGY_SPEND, abs=1
    )


def test_every_household_array_is_the_same_length(baseline):
    lengths = {
        key: len(value)
        for key, value in baseline.items()
        if key not in ("bundle", "uprating_gains") and hasattr(value, "__len__")
    }
    assert len(set(lengths.values())) == 1, lengths
    # The reform gains are one household array per residual.
    (n,) = set(lengths.values())
    for residual, gain in baseline["uprating_gains"].items():
        assert len(gain) == n, residual


def test_deciles_are_clipped_into_range(baseline):
    """PolicyEngine assigns -1 to negative-income households."""
    decile = baseline["decile"]
    assert decile.min() >= 1
    assert decile.max() <= 10


def test_transport_fuel_spending_is_not_universal(baseline):
    """The A6 mean must not be assigned to households with no vehicle (#12)."""
    from iran_impact.pipeline import weighted_mean

    weights = baseline["weights"]
    fuel_cost = baseline["fuel_cost"]
    assert (fuel_cost == 0).any(), "every household was assigned fuel spending"
    owns = baseline["owns_vehicle"]
    assert not fuel_cost[~owns].any()
    # Concentrating spending on owners must leave the population mean at A6's.
    assert weighted_mean(fuel_cost, weights) == pytest.approx(
        config.BASE_FUEL_SPEND, rel=0.01
    )


def test_food_spending_mean_matches_the_published_table(baseline):
    from iran_impact.pipeline import weighted_mean

    assert weighted_mean(baseline["food_cost"], baseline["weights"]) == pytest.approx(
        config.BASE_FOOD_SPEND, rel=0.01
    )


def test_gross_income_deciles_are_ten_equal_weighted_groups(baseline):
    weights = baseline["weights"]
    shares = [
        weights[baseline["gross_decile"] == d].sum() / weights.sum()
        for d in range(1, 11)
    ]
    assert all(share == pytest.approx(0.1, abs=0.005) for share in shares)


def test_the_fuel_duty_cut_costs_the_cut_times_the_duty_base():
    """Exchequer cost from a real PolicyEngine reform, reconciled against the
    duty base rather than inferred from household spending (#14).

    Skipped where the dataset is unavailable, like the other managed-data
    tests, since it runs two simulations.
    """
    from iran_impact.pipeline import _fuel_duty_exchequer_cost

    if not _managed_data_available_for_reform():
        pytest.skip("certified dataset unavailable")

    result = _fuel_duty_exchequer_cost(year=config.YEAR)
    assert result is not None

    # The cost must equal the rate cut times modelled volume, which is what
    # makes it a reconciliation rather than a second independent estimate.
    implied = (
        config.FUEL_DUTY_CUT_PENCE
        / config.PENCE_PER_POUND
        * result["modelled_litres_bn"]
    )
    assert result["exchequer_cost_bn"] == pytest.approx(implied, abs=0.05)
    # And receipts must fall by exactly that much.
    assert (
        result["baseline_receipts_bn"] - result["reform_receipts_bn"]
    ) == pytest.approx(result["exchequer_cost_bn"], abs=0.01)
    # A cut cannot raise receipts.
    assert result["reform_receipts_bn"] < result["baseline_receipts_bn"]


def _managed_data_available_for_reform():
    try:
        from policyengine.provenance.dataset_materialization import (
            DatasetMaterializationError,
        )
        from policyengine.tax_benefit_models.uk import managed_microsimulation
    except ImportError:
        return False
    try:
        managed_microsimulation()
    except DatasetMaterializationError:
        return False
    return True


def test_the_reform_actually_changes_the_parameter():
    """Guards the bug this implementation had to work around: a bare-date
    reform key moved receipts by only about a twelfth of the expected amount,
    because it did not apply across the year. If the range form ever stops
    applying, the cost collapses and this fails."""
    from iran_impact.pipeline import _fuel_duty_exchequer_cost, _fuel_duty_rate

    if not _managed_data_available_for_reform():
        pytest.skip("certified dataset unavailable")

    result = _fuel_duty_exchequer_cost(year=config.YEAR)
    rate = _fuel_duty_rate(config.YEAR)
    cut_share = (config.FUEL_DUTY_CUT_PENCE / config.PENCE_PER_POUND) / rate
    # Receipts should fall by the proportional rate cut, about 8.4%.
    observed_share = (
        result["exchequer_cost_bn"] / result["baseline_receipts_bn"]
    )
    assert observed_share == pytest.approx(cut_share, rel=0.02)


def _household_gain(sit, residual_pp):
    """Run the pipeline's own reform on one household, the way the population
    run does, and return its change in household benefits."""
    policyengine_uk = pytest.importorskip("policyengine_uk")
    from iran_impact.pipeline import _uprating_gain

    base = policyengine_uk.Simulation(situation=sit)

    def factory(reform):
        return policyengine_uk.Simulation(situation=sit, reform=reform)

    return base, _uprating_gain(base, residual_pp, 2027, simulation_factory=factory)[0]


def _single(age, earnings, rent=0, claims_uc=True, **person):
    household = {"members": ["a"]}
    if rent:
        household.update(
            rent={2027: rent},
            region={2027: "LONDON"},
            tenure_type={2027: "RENT_PRIVATELY"},
        )
    return {
        "people": {
            "a": {"age": {2027: age}, "employment_income": {2027: earnings}, **person}
        },
        "benunits": {"b": {"members": ["a"], "would_claim_uc": {2027: claims_uc}}},
        "households": {"h": household},
    }


def test_uprating_reform_raises_uc_pound_for_pound():
    """#61 second review C2: a working UC renter with a positive award gains
    exactly the uprated standard allowance, which a share-of-award rule
    understated by 74%."""
    base, gain = _household_gain(_single(30, 15_000, rent=12_000), 1.94)
    standard_allowance = base.calculate("uc_standard_allowance", 2027)[0]
    assert gain == pytest.approx(standard_allowance * 0.0194, abs=0.01)


def test_uprating_reform_is_run_at_the_residual_not_scaled_from_one_percent():
    """#61 third review C2: a claimant just above the zero-award boundary
    gains nothing at 1% but something at the central 2.2%, which scaling a
    1% run cannot see."""
    sit = _single(30, 9_600)
    _, at_one = _household_gain(sit, 1.0)
    _, at_central = _household_gain(sit, 2.2)
    assert at_one == pytest.approx(0, abs=0.01)
    assert at_central > 0


def test_uprating_reform_scales_reported_esa():
    """#61 third and fourth reviews: ESA is paid from reported awards the
    model uprates by index. The claimant does not claim UC, so the gain is
    ESA's alone and the test fails if ESA scaling is removed."""
    sit = _single(50, 0, claims_uc=False, esa_income_reported={2027: 5_000})
    _, gain = _household_gain(sit, 2.2)
    assert gain == pytest.approx(5_000 * 0.022, abs=0.01)


def test_uprating_reform_scales_reported_jsa_once():
    """#61 fourth review C2: contribution-based JSA is CPI-uprated and paid
    from its reported award. policyengine-uk lists jsa_contrib twice in
    household_benefits, so the gain must be counted once, not twice."""
    sit = _single(50, 0, claims_uc=False, jsa_contrib_reported={2027: 5_000})
    _, gain = _household_gain(sit, 2.2)
    assert gain == pytest.approx(5_000 * 0.022, abs=0.01)


def test_uprating_every_cpi_tagged_benefit_input_is_classified():
    """#61 fifth review C2: coverage is checked against the model, not by
    inspection. Every input PolicyEngine UK tags for CPI uprating that is a
    benefit — a `_reported` award or a household_benefits component — must be
    scaled by the reform, bounded as partly CPI-linked, or excluded with a
    reason. A new one in the model fails this test until it is classified."""
    policyengine_uk = pytest.importorskip("policyengine_uk")
    from policyengine_uk.variables.household.income.household_benefits import (
        HOUSEHOLD_BENEFIT_VARIABLES,
    )

    from iran_impact import config

    tbs = policyengine_uk.CountryTaxBenefitSystem()
    tagged = {
        name
        for name, var in tbs.variables.items()
        if not var.formulas
        and "consumer_price_index" in str(getattr(var, "uprating", "") or "")
        and (name.endswith("_reported") or name in HOUSEHOLD_BENEFIT_VARIABLES)
    }
    classified = (
        set(config.CPI_UPRATED_REPORTED_INPUTS)
        | set(config.PARTLY_CPI_LINKED_INPUTS)
        | set(config.NOT_SCALED_REPORTED_INPUTS)
    )
    assert tagged - classified == set(), tagged - classified
    assert not (set(config.CPI_UPRATED_REPORTED_INPUTS) & set(config.NOT_SCALED_REPORTED_INPUTS))


def test_uprating_reform_scales_reported_iidb():
    """#61 fifth review C2: IIDB is paid straight from its reported award."""
    sit = _single(50, 0, claims_uc=False, iidb_reported={2027: 5_000})
    _, gain = _household_gain(sit, 2.2)
    assert gain == pytest.approx(5_000 * 0.022, abs=0.01)



def test_uprating_reform_scales_reported_afcs_and_incapacity_benefit():
    for var in ("afcs_reported", "incapacity_benefit_reported"):
        sit = _single(50, 0, claims_uc=False, **{var: {2027: 5_000}})
        _, gain = _household_gain(sit, 2.2)
        assert gain == pytest.approx(5_000 * 0.022, abs=0.01), var


def test_uprating_reform_raises_additional_state_pension():
    """Additional State Pension is CPI-uprated, unlike the triple-locked
    basic and new State Pension; the reform must raise it and nothing else
    for a pensioner outside Pension Credit."""
    sit = {
        "people": {
            "a": {
                "age": {2027: 75},
                "state_pension_type": {2027: "BASIC"},
                "state_pension_reported": {2027: 16_000},
            }
        },
        "benunits": {"b": {"members": ["a"], "would_claim_pc": {2027: False}}},
        "households": {"h": {"members": ["a"]}},
    }
    base, gain = _household_gain(sit, 2.2)
    additional = base.calculate("additional_state_pension", 2027)[0]
    assert additional > 0
    assert gain == pytest.approx(additional * 0.022, abs=0.01)


def _reform_pair(sit, residual_pp):
    policyengine_uk = pytest.importorskip("policyengine_uk")
    from iran_impact.pipeline import _cpi_uprating_reform, _uprating_gain

    base = policyengine_uk.Simulation(situation=sit)

    def factory(reform):
        return policyengine_uk.Simulation(situation=sit, reform=reform)

    reform = factory(_cpi_uprating_reform(base, residual_pp, 2027))
    gain = _uprating_gain(base, residual_pp, 2027, simulation_factory=factory)[0]
    return base, reform, gain


def _scottish_working_parent():
    return {
        "people": {
            "p": {"age": {2027: 35}, "employment_income": {2027: 15_000}},
            "c": {"age": {2027: 5}},
        },
        "benunits": {
            "b": {
                "members": ["p", "c"],
                "would_claim_uc": {2027: True},
                "would_claim_child_benefit": {2027: False},
            }
        },
        "households": {"h": {"members": ["p", "c"], "region": {2027: "SCOTLAND"}}},
    }


def test_uprating_reform_raises_scottish_child_payment_once():
    """#61 sixth review A11: end to end. The gain is the UC change plus the
    Scottish Child Payment change, counted exactly once; it fails if SCP is
    dropped from the reform or from the benefits total, or counted twice."""
    base, reform, gain = _reform_pair(_scottish_working_parent(), 2.2)
    scp = base.calculate("scottish_child_payment", 2027).sum()
    uc_change = (
        reform.calculate("universal_credit", 2027).sum()
        - base.calculate("universal_credit", 2027).sum()
    )
    assert scp > 0
    assert gain - uc_change == pytest.approx(scp * 0.022, abs=0.01)


def test_uprating_reform_raises_the_uc_work_allowance():
    """#61 sixth review C2: work allowances are uprated in the official
    tables and raise UC for working claimants."""
    base, reform, _ = _reform_pair(_scottish_working_parent(), 2.2)
    before = base.calculate("uc_work_allowance", 2027).sum()
    after = reform.calculate("uc_work_allowance", 2027).sum()
    assert after == pytest.approx(before * 1.022, rel=1e-6)


def test_uprating_reform_counts_pension_age_winter_heating_payment():
    """#61 sixth review C2: PAWHP is outside policyengine-uk's
    household_benefits, so its change must be added explicitly."""
    sit = {
        "people": {"a": {"age": {2027: 82}}},
        "benunits": {"b": {"members": ["a"], "would_claim_pc": {2027: True}}},
        "households": {"h": {"members": ["a"], "region": {2027: "SCOTLAND"}}},
    }
    base, _, gain = _reform_pair(sit, 2.2)
    pawhp = base.calculate("pawhp", 2027).sum()
    assert pawhp > 0
    assert gain == pytest.approx(pawhp * 0.022, abs=0.01)


def test_uprating_known_live_paths_have_the_right_disposition():
    """#61 sixth review C2: membership in some list is not enough. The paths
    the official 2026-27 tables uprate must be in the reform, and the
    exclusions must be only those that are genuinely not CPI-uprated."""
    from iran_impact import config

    for path in (
        "gov.dwp.universal_credit.means_test.work_allowance",
        "gov.dwp.universal_credit.elements.childcare.cap",
        "gov.dwp.universal_credit.elements.housing.non_dep_deduction.amount",
        "gov.social_security_scotland.pawhp.amount",
        "gov.social_security_scotland.scottish_child_payment.amount",
    ):
        assert path in config.CPI_UPRATED_BENEFIT_PARAMETERS, path
        assert not any(path.startswith(k) for k in config.CPI_PARAMETER_EXCLUSIONS), path
    assert "pawhp" in config.BENEFITS_OUTSIDE_HOUSEHOLD_BENEFITS
    assert "statutory_paternity_pay" in config.PARTLY_CPI_LINKED_INPUTS
    assert set(config.CPI_PARAMETER_EXCLUSIONS) == {
        "gov.dwp.IIDB.maximum",
        "gov.dwp.housing_benefit.means_test.income_disregard",
        "gov.dwp.pension_credit.guarantee_credit.minimum_guarantee",
        "gov.dwp.pension_credit.savings_credit.threshold",
        "gov.dwp.tax_credits",
        "gov.dwp.universal_credit.elements.disabled.amount",
    }

def test_uprating_every_cpi_tagged_benefit_parameter_is_classified():
    """Every currency parameter under the benefit branches that the model
    tags with either CPI index is in the reform or excluded with a reason, so
    a parameter carrying the OBR CPI tag cannot be missed again."""
    policyengine_uk = pytest.importorskip("policyengine_uk")
    from iran_impact import config

    params = policyengine_uk.CountryTaxBenefitSystem().parameters
    unclassified = []
    for root in ("gov.dwp", "gov.hmrc.child_benefit", "gov.social_security_scotland"):
        node = params
        for part in root.split("."):
            node = getattr(node, part)
        for leaf in node.get_descendants():
            if not hasattr(leaf, "values_list"):
                continue
            meta, parent = leaf.metadata or {}, leaf.parent
            uprating, unit = meta.get("uprating"), meta.get("unit")
            while parent is not None and (uprating is None or unit is None):
                pm = parent.metadata or {}
                uprating = uprating or pm.get("uprating")
                unit = unit or pm.get("unit")
                parent = getattr(parent, "parent", None)
            tagged = any(k in str(uprating or "") for k in ("benefit_uprating_cpi", "consumer_price_index"))
            if not (tagged and str(unit or "").startswith("currency")):
                continue
            known = list(config.CPI_UPRATED_BENEFIT_PARAMETERS) + list(config.CPI_PARAMETER_EXCLUSIONS)
            if not any(leaf.name == k or leaf.name.startswith(k + ".") for k in known):
                unclassified.append(leaf.name)
    assert unclassified == [], unclassified
