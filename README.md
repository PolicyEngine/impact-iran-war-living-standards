# Impact of Iran Conflict on UK Living Standards

Microsimulation-based analysis of how an Iran war would affect UK households in 2026-27 — modelling energy price shocks, fuel costs, food inflation, and benefit erosion across ~32 million households using [PolicyEngine UK](https://policyengine.org).

**[Live Dashboard](https://dashboard-policy-engine.vercel.app)**

## Scenarios

| Scenario | Energy cap | Avg cost/household | Fuel poverty |
|---|---|---|---|
| Limited strikes | +30% | ~£814/yr | ~9.5% |
| Prolonged conflict | +75% | ~£1,981/yr | ~14.4% |
| Strait of Hormuz closure | +150% | ~£3,722/yr | ~23.7% |

## How it works

The pipeline applies price shocks through four transmission channels and computes household-level impacts for the 2026-27 tax year:

1. **Energy** — Oil/gas spike → higher domestic bills via energy price cap
2. **Fuel** — Petrol/diesel price increase
3. **Food** — Energy costs pass through to food production and transport
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
