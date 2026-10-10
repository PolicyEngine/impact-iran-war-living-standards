"""Microsimulation figures for alternatives to the forecast scenario's choices.

The forecast-based scenario makes choices where no published forecast
settles the matter: which energy path to hold, the tax basis, the fuel
pass-through. This runs the same baseline the pipeline runs and evaluates
the scenario with one parameter changed at a time through compute_scenario,
so each figure is a run of its own parameters, never a scaling of another.
It also sweeps the energy rise in half-point steps and reports which survey
records carry the largest steps in the poverty count.

It writes nothing into the results file and is not part of the pipeline.
Needs the managed dataset, like `iran-impact-build`:

    python scripts/forecast_alternatives.py > alternatives.json
"""

import json

from iran_impact import config
from iran_impact.pipeline import (
    _baseline_in_poverty,
    _below_anchored_line,
    _poverty_line,
    compute_scenario,
    run_baseline,
    weighted_mean,
    weighted_sum,
)

data = run_baseline(year=config.YEAR)
base = dict(config.SCENARIOS["external_forecast"])

# Fuel with duty at the model's own 2027-28 rate instead of 52.95p.
DUTY_2027_28_PENCE = 59.25  # parameters.fuel_duty_exchequer_cost in the results
DUTY_REFERENCE_PENCE = 52.95
VAT = 1.2
extra = (DUTY_2027_28_PENCE - DUTY_REFERENCE_PENCE) * VAT
brent = config.forecast_brent_2027_28()
total = (
    config.PETROL_WEEKLY_SPEND
    + config.DIESEL_WEEKLY_SPEND
    + config.OTHER_MOTOR_OILS_WEEKLY_SPEND
)
composite = 0.0
for spend, pre, slope in (
    (config.PETROL_WEEKLY_SPEND + config.OTHER_MOTOR_OILS_WEEKLY_SPEND,
     config.PRE_CONFLICT_PETROL_PENCE, config.petrol_slope()),
    (config.DIESEL_WEEKLY_SPEND, config.PRE_CONFLICT_DIESEL_PENCE, config.diesel_slope()),
):
    price = pre + slope * (brent - config.BRENT_NOV_2025) + extra
    composite += spend / total * (price / pre - 1)
fuel_duty_restored = round(composite * 100, 1)

# Energy on the supplier quarters instead of Cornwall's held winter quarter:
# April-June is the mean of the two suppliers, July-September is E.ON Next,
# which is then held for October 2027 to March 2028.
by_period = {}
for f in config.SUPPLIER_CAP_FORECASTS_2027_28:
    by_period.setdefault(f["period"], []).append(f["total_gbp"])
q2 = sum(by_period["April-June 2027"]) / len(by_period["April-June 2027"])
q3 = sum(by_period["July-September 2027"]) / len(by_period["July-September 2027"])
energy_supplier_path = config.cap_rise_pct((q2 + 3 * q3) / 4)

alternatives = {
    "as_committed": base,
    "fuel_duty_at_model_2027_28_rate": {**base, "fuel_pct": fuel_duty_restored},
    "fuel_at_low_end_of_range": {**base, "fuel_pct": config.forecast_fuel_range_pct()[0]},
    "fuel_eia_consistent_retail": {**base, "fuel_pct": config.eia_consistent_fuel_rise_pct("retail")},
    "fuel_eia_consistent_wholesale": {**base, "fuel_pct": config.eia_consistent_fuel_rise_pct("wholesale")},
    "energy_on_supplier_quarters": {**base, "cap_increase_pct": energy_supplier_path},
    "energy_without_vat_restoration": {
        **base,
        "cap_increase_pct": config.cap_rise_pct(config.forecast_cap_2027_28_gbp(vat=0)),
    },
}

line = _poverty_line(data)
in_poverty = _baseline_in_poverty(data, line)
weights = data["weights"]
out = {}
for name, params in alternatives.items():
    impacts = compute_scenario(data, "external_forecast", params_override=params)
    net = impacts["net_impact"]
    newly = (~in_poverty) & _below_anchored_line(data, net, line)
    out[name] = {
        "params": params,
        "mean_net_impact": round(weighted_mean(net, weights)),
        "total_impact_bn": round(weighted_sum(net, weights) / 1e9, 1),
        "n_newly_below_anchored_line": round(
            weighted_sum(newly.astype(float), weights * data["people"])
        ),
    }
print(json.dumps(out, indent=1))


# ── The step the second review saw near the headline poverty count ───────
import numpy as np

person_weights = weights * data["people"]


def newly_below(energy_pct):
    impacts = compute_scenario(
        data, "external_forecast", params_override={**base, "cap_increase_pct": energy_pct}
    )
    return (~in_poverty) & _below_anchored_line(data, impacts["net_impact"], line)


grid = {}
for energy in np.arange(30.0, 46.01, 0.5):
    grid[round(float(energy), 1)] = round(
        weighted_sum(newly_below(float(energy)).astype(float), person_weights)
    )
low, high = newly_below(36.5), newly_below(39.7)
crossing = high & ~low
order = np.argsort(-person_weights[crossing])
top = person_weights[crossing][order][:10]
step = {
    "count_by_energy_pct": grid,
    "people_crossing_between_36.5_and_39.7": round(float(person_weights[crossing].sum())),
    "records_crossing": int(crossing.sum()),
    "largest_crossing_records_people": [round(float(x)) for x in top],
    "share_of_step_from_largest_record": round(float(top[0] / person_weights[crossing].sum()), 3) if crossing.any() else None,
    "records_newly_below_at_39.7": int(high.sum()),
    "largest_record_newly_below_at_39.7_people": round(float(person_weights[high].max())),
    "max_person_weight_in_data": round(float(person_weights.max())),
    "median_person_weight_of_newly_below": round(float(np.median(person_weights[high]))),
}
print("STEP " + json.dumps(step))
