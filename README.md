# Impact of Iran Conflict on UK Living Standards

Microsimulation-based analysis of how energy price increases associated with an Iran conflict would affect UK households in 2026-27 — modelling impacts through energy bills, fuel costs, food inflation, and benefit erosion across ~32 million households using [PolicyEngine UK](https://policyengine.org).

**[Live Dashboard](https://dashboard-policy-engine.vercel.app)**

## Scenarios

| Scenario | Energy cap | Fuel price | Food price | CPI |
|---|---|---|---|---|
| Low | +30% | +20% | +2.0% | +1.5pp |
| Central | +75% | +50% | +4.5% | +3.5pp |
| High | +150% | +100% | +6.4% | +6.0pp |

## How it works

The pipeline applies price increases through four transmission channels and computes household-level impacts for the 2026-27 tax year:

1. **Energy** — Higher domestic bills via energy price cap increase
2. **Fuel** — Petrol/diesel price increase
3. **Food** — Food price inflation from energy input costs
4. **Benefit erosion** — CPI-uprated benefits lag 12 months behind actual inflation

Results are broken down by income decile, region, tenure type, and household composition.

## Policy responses evaluated

- Energy Price Guarantee (cap subsidy)
- Flat energy rebate (£400/household)
- Council tax rebate (bands A–D)
- Universal Credit uplift (£25/week)
- Fuel duty cut (5p/litre)
- Means-tested cost-of-living payment (£650)
- Accelerated benefit uprating
- Social tariff

Each policy is assessed on fiscal cost, targeting efficiency (share reaching bottom quintiles), and fuel poverty reduction.

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
