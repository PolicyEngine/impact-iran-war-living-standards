# Impact of the Middle East War on UK Living Standards

Microsimulation-based analysis of how energy price rises from the ongoing Middle East conflict (active since late February 2026, with recurrent Strait of Hormuz disruption) affect UK households in 2027-28 — modelling impacts through energy bills, fuel costs and food inflation across 31.6 million weighted households using [policyengine.py](https://github.com/PolicyEngine/policyengine.py) 5.3.0.

**[Live Dashboard](https://uk-energy-shock-impact.vercel.app)**

## Scenarios

**These are stress tests, not forecasts.** Each scenario applies a set of price assumptions as full-year 2027-28 amounts, including where the cited source describes a 2026 disruption lasting a few months. No time path, quarterly profile or shock duration is modelled, and the pass-through coefficients implied by the percentages are judgements anchored to the cited sources rather than equations derived from them. The results file records the definition, source, reference period, derivation and uncertainty range of every parameter under `parameters.registry`.

Calibrated to conditions as of August 2026 (Brent ~$85/bbl after a ~$109 peak). Anchors: observed path (low), Goldman Sachs extended Hormuz-closure Brent >$100 (central), Goldman extreme-adverse and the Oxford Economics escalation case (high).

| Scenario | Energy bills | Fuel price | Food price | CPI |
|---|---|---|---|---|
| Low | +15% | +20% | +2.0% | +1.0pp |
| Central | +45% | +45% | +4.0% | +2.5pp |
| High | +90% | +80% | +6.5% | +4.5pp |

The Ofgem cap (£1,663 for July–September 2026 on the new typical-consumption basis, £1,723 for October–December) is reported as context and **does not enter the calculation**: the energy percentage is applied to each household's own baseline gas and electricity expenditure in the microdata. The model does not represent unit rates, standing charges, the gas/electricity split, region, payment method, quarterly cap periods or fixed-tariff coverage.

## How it works

The pipeline applies price increases through three transmission channels and computes household-level impacts for the 2027-28 tax year:

1. **Energy** — Each household's own baseline gas and electricity spend, raised by the scenario percentage
2. **Fuel** — Petrol and diesel spending (ONS Family Spending Table A6, allocated to vehicle-owning households only), raised by the scenario percentage
3. **Food** — Food and non-alcoholic drink spending (ONS Family Spending Table A6), raised by the scenario percentage

Plus a separately reported **uprating compensation shortfall** — CPI-linked benefits (state pension excluded: triple lock) are uprated each April from the previous September's CPI, so no offset arrives during the shock year. This is reported as the compensation an immediate uprating would deliver, and is *not* added to the cost channels: the household's loss is the price rise itself, and adding an uprating term on top would count the same shock twice. It is what the accelerated-uprating policy pays.

Poverty is measured as people below 60% of the person-weighted median of equivalised HBAI household net income (BHC); the post-shock figure holds that baseline line fixed and nets modelled costs off income, so it is an anchored, consumption-adjusted measure rather than official HBAI poverty.

No fuel poverty figure is reported. The study previously published an indicative 10%-of-income energy-spend ratio; its level was not comparable with any official statistic (England's LILEE measure adds an energy-efficiency test, and DESNZ's own 10% indicator uses after-housing-costs income and modelled *required* rather than actual energy costs), so it was withdrawn rather than published alongside figures it invited comparison with. See [#22](https://github.com/PolicyEngine/impact-iran-war-living-standards/issues/22).

Results are broken down by income decile, region, country, tenure type, and household composition.

## Headline results

Central scenario, 2027-28, across 31.6 million weighted households. Regenerate with `iran-impact-build --sync-dashboard`; these figures are pinned as a regression test in `tests/test_committed_output.py`.

| | Low | Central | High |
|---|---:|---:|---:|
| Mean cost per household | £517 | **£1,324** | £2,489 |
| As a share of net income | 1.7% | **4.5%** | 8.5% |
| Total cost | £16.3bn | **£41.8bn** | £78.6bn |
| People newly below the anchored poverty line | 359,642 | **1,505,723** | 2,472,590 |

Central-scenario cost by channel, per household: energy £713, fuel £464, food £147. The uprating compensation shortfall is a further £67, reported separately rather than added (see above).

The shock is regressive in relative terms — the poorest fifth of households lose 10.2% of net income against 1.7% for the richest fifth, even though the cash amounts run the other way (£974 against £1,598).

## Policy responses evaluated

Aligned to the live Autumn Budget 2026 decisions where applicable:

- Energy Price Guarantee (cap subsidy)
- Flat energy rebate (£400/household)
- Council tax rebate (bands A–D)
- Universal Credit uplift (£20/week, matching the 2020-21 uplift)
- Fuel duty cut extension (5p/litre on each household's own modelled petrol and diesel volume, so non-drivers receive nothing; the current cut expires 31 Dec 2026)
- Means-tested cost-of-living payment (£650, on the 2022 Cost of Living Payment's qualifying benefits: Universal Credit, income-based JSA, income-related ESA, Income Support, Working Tax Credit, Child Tax Credit and Pension Credit)
- Accelerated benefit uprating
- Electricity VAT cut extension (5% → 0%, enacted Oct 2026–Mar 2027; modelled full-year)
- Social tariff
- Combined package (applied jointly, so the Energy Price Guarantee caps the bill before the electricity VAT relief applies to it)

Every cost is a **gross modelled household transfer, not an Exchequer costing**: it excludes tax and benefit interactions, take-up, behavioural responses, administration, non-household fuel use and financing. Each policy is assessed on gross outlay (unclipped government spending), household protection and residual impact, targeting efficiency (share of spending reaching the bottom two quintiles), and the number of people lifted back above the anchored poverty line.

## Project structure

```
src/iran_impact/        # Python microsimulation pipeline
  config.py             # Scenario parameters, parameter registry, limitations
  pipeline.py           # Core engine (baseline, shocks, policy responses)
  inputs.py             # Loader for the committed spending input tables
  inputs/               # Versioned source data (ONS Family Spending A6 extract)
  cli.py                # CLI entry point
  provenance.py         # Run provenance: revision, versions, bundle, hashes
scripts/
  extract_ons_a6.py     # Regenerates the A6 extract from the ONS workbook
run_pipeline.py         # Runs pipeline, writes JSON output
tests/                  # Unit tests (synthetic) and integration tests (managed data)
requirements.lock       # Fully pinned Python environment
.github/workflows/      # CI: tests, lockfile check, dashboard lint and build
dashboard/              # Next.js interactive dashboard
  src/components/       # React components (scenarios, policy, methodology tabs)
  src/lib/              # Data helpers, formatters, chart utils
  public/data/          # Pipeline JSON output consumed by frontend
```

## Quick start

```bash
# Install the Python package. The `uk` extra pulls policyengine[uk]==5.3.0,
# which brings the UK country package the pipeline needs. Installing plain
# `policyengine` is not enough — the managed-simulation import fails.
pip install -e ".[uk,dev]"

# Or, to pin every dependency exactly (see Reproducibility below). The lock
# holds third-party pins only, so the project itself is installed separately:
#   uv pip sync requirements.lock
#   uv pip install -e . --no-deps

# Authenticate for the managed microdata (see Data access below)
export HF_TOKEN=...            # or: hf auth login

# Run the analysis pipeline and refresh the dashboard's copy of the results
iran-impact-build --sync-dashboard

# Launch dashboard
cd dashboard && bun install && bun run dev
```

Run the unit tests with `pytest`. They use synthetic households and need no
data access. The end-to-end checks in `tests/test_integration.py` require the
managed dataset and skip themselves without it — run them locally before
pushing any change to the calculation.

## Data access

The pipeline runs against policyengine.py's **managed** UK microsimulation, so
the model version and data build are certified by the release bundle rather
than chosen by this repository. The current bundle resolves to:

| | |
|---|---|
| Bundle | `uk-5.3.0` |
| Model | `policyengine-uk` 2.90.2 (certified by the bundle — do not pin separately) |
| Dataset | `enhanced_frs_2024_25` |
| Data build | `policyengine-uk-data-1.56.16` |

The microdata lives in the Hugging Face repository
`policyengine/policyengine-uk-data-private`, which is **gated**: access is
granted per account rather than being public. Running the pipeline requires a
token from an account that has been granted access, supplied either through
`HUGGING_FACE_TOKEN`, `HF_TOKEN` or `HUGGINGFACE_HUB_TOKEN` in the
environment, or by `hf auth login`. Without it the
`managed_microsimulation()` call fails when it tries to fetch the dataset.

A populated Hugging Face hub cache is not sufficient on its own:
policyengine.py reuses only a SHA-verified artifact at its own
materialization target (`./data/enhanced_frs_2024_25.h5` relative to the
working directory), and otherwise downloads it.

Do not pin `policyengine-uk` or the dataset directly. policyengine.py's
release bundle selects both, and pinning them here could contradict it — the
5.3.0 bundle selects `policyengine-uk` 2.90.2, which is not the newest
release of that package.

## Reproducibility

Every generated results file carries a `provenance` block recording the git
revision, the versions of every package that can move a number, the certified
release bundle (model version, dataset, data build ID and artifact hash), and
SHA-256 hashes of the source files that define the calculation.

Two runs of the same revision against the same certified data build produce
identical output apart from the run timestamp and git revision.

`requirements.lock` pins the complete Python environment, including the
`policyengine-uk` version the release bundle certifies. It is a compiled
requirements file, so it contains third-party pins only — installing it takes
two steps, the second of which puts `iran_impact` and the `iran-impact-build`
console script on the path:

```bash
uv pip sync requirements.lock     # exact third-party versions
uv pip install -e . --no-deps     # this project, without touching those pins
```

CI checks that the lock still matches `pyproject.toml`.

CI also compares the source hashes recorded in the committed output against the
working tree. A change to `config.py`, `pipeline.py`, `provenance.py`,
`pyproject.toml` or `requirements.lock` that lands without a regenerated
results file fails the build — a dependency change can move a number without
touching any calculation source. Regenerate with
`iran-impact-build --sync-dashboard`.

## Data sources

- [policyengine.py](https://github.com/PolicyEngine/policyengine.py) 5.3.0 managed UK microsimulation (`enhanced_frs_2024_25`; see Data access) — household incomes, benefits, energy and road-fuel consumption, vehicle ownership
- [ONS Family Spending in the UK, FYE 2024, Table A6](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/april2023tomarch2024) — transport fuel and food spending by gross-income decile, committed as a versioned extract under `src/iran_impact/inputs/`
- [Ofgem price cap announcements](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-july-and-30-september-2026) — reported as context; not used in the calculation
- Scenario anchors: Goldman Sachs Hormuz-closure analysis, [Oxford Economics escalation scenario](https://www.oxfordeconomics.com/resource/iran-war-scenarios-the-oil-price-that-breaks-parts-of-the-economy/), [Commons Library CBP-10601](https://commonslibrary.parliament.uk/research-briefings/cbp-10601/) and [CBP-10403](https://commonslibrary.parliament.uk/research-briefings/cbp-10403/), Bank of England and NIESR inflation projections — see `parameters.registry` in the output for which figure each supports

Built with [PolicyEngine](https://policyengine.org).

## License

[AGPL-3.0](LICENSE), matching the PolicyEngine model packages this project builds on.
