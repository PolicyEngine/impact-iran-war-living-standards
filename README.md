# Impact of Energy Price Shocks on UK Living Standards

Microsimulation-based analysis of how energy price rises from the ongoing Middle East conflict (active since late February 2026, with recurrent Strait of Hormuz disruption) affect UK households in 2026-27 — modelling impacts through energy bills, fuel costs, food inflation, and benefit uprating lag across ~32 million households using [PolicyEngine UK](https://policyengine.org).

**[Live Dashboard](https://uk-energy-shock-impact.vercel.app)**

## Scenarios

Calibrated to conditions as of August 2026 (Ofgem Q3 2026 cap £1,663 on the new typical-consumption basis; Brent ~$85/bbl after a ~$109 peak). Anchors: observed path (low), Goldman Sachs extended Hormuz-closure Brent >$100 (central), Goldman extreme-adverse / Oxford Economics prolonged-war (high).

| Scenario | Energy cap | Fuel price | Food price | CPI |
|---|---|---|---|---|
| Low | +15% | +20% | +2.0% | +1.0pp |
| Central | +45% | +45% | +4.0% | +2.5pp |
| High | +90% | +80% | +6.5% | +4.5pp |

## How it works

The pipeline applies price increases through four transmission channels and computes household-level impacts for the 2026-27 tax year:

1. **Energy** — Higher domestic bills via energy price cap increase
2. **Fuel** — Petrol/diesel price increase
3. **Food** — Food price inflation from energy input costs
4. **Benefit uprating lag** — CPI-linked benefits (state pension excluded: triple lock) erode in real terms until the next April uprating; an expected-lag factor of 0.5 is applied

Poverty is measured as people below 60% of median equivalised household net income (BHC). Fuel poverty uses the indicative 10%-of-income ratio (not the official LILEE metric). Results are broken down by income decile, region, country, tenure type, and household composition.

## Policy responses evaluated

Aligned to the live Autumn Budget 2026 decisions where applicable:

- Energy Price Guarantee (cap subsidy)
- Flat energy rebate (£400/household)
- Council tax rebate (bands A–D)
- Universal Credit uplift (£20/week, matching the 2020-21 uplift)
- Fuel duty cut extension (5p/litre, scaled by household fuel spending; the current cut expires 31 Dec 2026)
- Means-tested cost-of-living payment (£650, keyed to means-tested benefit receipt)
- Accelerated benefit uprating
- Electricity VAT cut extension (5% → 0%, enacted Oct 2026–Mar 2027; modelled full-year)
- Social tariff
- Combined package

Each policy is assessed on fiscal cost (unclipped government outlay), targeting efficiency (share reaching bottom quintiles), and fuel poverty reduction.

## Project structure

```
src/iran_impact/        # Python microsimulation pipeline
  config.py             # Scenario parameters and constants
  pipeline.py           # Core engine (baseline, shocks, policy responses)
  cli.py                # CLI entry point
run_pipeline.py         # Runs pipeline, writes JSON output
dashboard/              # Next.js interactive dashboard
  src/components/       # React components (scenarios, policy, methodology tabs)
  src/lib/              # Data helpers, formatters, chart utils
  public/data/          # Pipeline JSON output consumed by frontend
```

## Quick start

```bash
# Install Python package
pip install -e ".[uk]"

# Run analysis pipeline
python run_pipeline.py

# Launch dashboard
cd dashboard && npm install && npm run dev
```

## Data sources

- [PolicyEngine UK](https://policyengine.org) microsimulation (Enhanced FRS 2023–24)
- ONS Consumer Price Index weights
- Ofgem energy price cap data
- OBR fiscal forecasts

Built with [PolicyEngine](https://policyengine.org).
