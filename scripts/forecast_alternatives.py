"""Microsimulation figures for alternatives to the forecast scenario's choices.

The forecast-based scenario makes choices where no published forecast
settles the matter: which energy path to hold, the tax basis, the fuel
pass-through. This runs the same baseline the pipeline runs and evaluates
the scenario with one parameter changed at a time through compute_scenario,
so each figure is a run of its own parameters, never a scaling of another.
It also sweeps the energy rise in half-point steps and reports which survey
records carry the largest step in the poverty count.

Varied: the energy path, the electricity VAT basis, the fuel duty rate and
the refining-margin scaling (on the slope ending July-September 2026). Food
and the earlier-quarter margin scalings are not varied here; the results
file's sensitivity block covers the price ranges.

It writes nothing into the results file and is not part of the pipeline.
Needs the managed dataset, like `iran-impact-build`, and prints one JSON
object:

    python scripts/forecast_alternatives.py > alternatives.json
"""

import json
from pathlib import Path

import numpy as np

from iran_impact import config

RESULTS = (
    Path(__file__).resolve().parents[1]
    / "dashboard"
    / "public"
    / "data"
    / "iran_impact_results.json"
)
VAT_ON_DUTY = 1.2
DUTY_REFERENCE_PENCE = 52.95  # the rate at both ends of the pump-price slopes


def model_duty_2027_28_pence(results_path=RESULTS):
    """The model's own 2027-28 fuel duty rate, as the committed results
    record it from the PolicyEngine UK parameter."""
    results = json.loads(Path(results_path).read_text())
    rate = results["parameters"]["fuel_duty_exchequer_cost"]["duty_rate_gbp_per_litre"]
    return rate * 100


def fuel_rise_with_duty_pct(duty_pence):
    """The fuel parameter with duty at `duty_pence` instead of the reference
    rate: the same composite as config.fuel_rise_pct_at_brent, with the duty
    change and the VAT on it added to each pump price."""
    extra = (duty_pence - DUTY_REFERENCE_PENCE) * VAT_ON_DUTY
    brent = config.forecast_brent_2027_28()
    total = (
        config.PETROL_WEEKLY_SPEND
        + config.DIESEL_WEEKLY_SPEND
        + config.OTHER_MOTOR_OILS_WEEKLY_SPEND
    )
    composite = 0.0
    for spend, pre, slope in (
        (
            config.PETROL_WEEKLY_SPEND + config.OTHER_MOTOR_OILS_WEEKLY_SPEND,
            config.PRE_CONFLICT_PETROL_PENCE,
            config.petrol_slope(),
        ),
        (
            config.DIESEL_WEEKLY_SPEND,
            config.PRE_CONFLICT_DIESEL_PENCE,
            config.diesel_slope(),
        ),
    ):
        price = pre + slope * (brent - config.BRENT_NOV_2025) + extra
        composite += spend / total * (price / pre - 1)
    return round(composite * 100, 1)


def energy_on_supplier_quarters_pct():
    """Energy on the supplier quarters instead of Cornwall's held winter
    quarter: April-June is the mean of the suppliers that forecast it,
    July-September likewise, and that is held for October 2027 to March
    2028."""
    by_period = {}
    for forecast in config.SUPPLIER_CAP_FORECASTS_2027_28:
        by_period.setdefault(forecast["period"], []).append(forecast["total_gbp"])
    q2 = np.mean(by_period["April-June 2027"])
    q3 = np.mean(by_period["July-September 2027"])
    return config.cap_rise_pct((q2 + 3 * q3) / 4)


def alternative_parameters(duty_pence=None):
    """Each alternative's parameters. Needs no dataset, so it is tested."""
    base = dict(config.SCENARIOS["external_forecast"])
    if duty_pence is None:
        duty_pence = model_duty_2027_28_pence()
    return {
        "as_committed": base,
        "fuel_duty_at_model_2027_28_rate": {
            **base,
            "fuel_pct": fuel_rise_with_duty_pct(duty_pence),
        },
        "fuel_at_low_end_of_range": {
            **base,
            "fuel_pct": config.forecast_fuel_range_pct()[0],
        },
        "fuel_eia_scaled_retail": {
            **base,
            "fuel_pct": config.eia_consistent_fuel_rise_pct("retail"),
        },
        "fuel_eia_scaled_wholesale": {
            **base,
            "fuel_pct": config.eia_consistent_fuel_rise_pct("wholesale"),
        },
        "energy_on_supplier_quarters": {
            **base,
            "cap_increase_pct": energy_on_supplier_quarters_pct(),
        },
        "energy_without_vat_restoration": {
            **base,
            "cap_increase_pct": config.cap_rise_pct(
                config.forecast_cap_2027_28_gbp(vat=0)
            ),
        },
    }


def main():
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
    alternatives = alternative_parameters()
    base = alternatives["as_committed"]
    line = _poverty_line(data)
    in_poverty = _baseline_in_poverty(data, line)
    weights = data["weights"]
    person_weights = weights * data["people"]

    def newly_below(params):
        impacts = compute_scenario(data, "external_forecast", params_override=params)
        return impacts["net_impact"], (~in_poverty) & _below_anchored_line(
            data, impacts["net_impact"], line
        )

    out = {"alternatives": {}}
    for name, params in alternatives.items():
        net, newly = newly_below(params)
        out["alternatives"][name] = {
            "params": params,
            "mean_net_impact": round(weighted_mean(net, weights)),
            "total_impact_bn": round(weighted_sum(net, weights) / 1e9, 1),
            "n_newly_below_anchored_line": round(
                weighted_sum(newly.astype(float), person_weights)
            ),
        }

    # The poverty count against the energy rise, in half-point steps, and
    # the records that carry the step between the scenario's energy figure
    # with and without the VAT restoration.
    committed = base["cap_increase_pct"]
    without_vat = alternatives["energy_without_vat_restoration"]["cap_increase_pct"]
    sweep = {}
    for energy in np.arange(30.0, 46.01, 0.5):
        _, newly = newly_below({**base, "cap_increase_pct": float(energy)})
        sweep[round(float(energy), 1)] = round(
            weighted_sum(newly.astype(float), person_weights)
        )
    _, low = newly_below({**base, "cap_increase_pct": without_vat})
    _, high = newly_below(base)
    crossing = high & ~low
    carried = np.sort(person_weights[crossing])[::-1]
    out["energy_sweep"] = {
        "count_by_energy_pct": sweep,
        "step_from_pct": without_vat,
        "step_to_pct": committed,
        "people_crossing": round(float(carried.sum())),
        "records_crossing": int(crossing.sum()),
        "largest_crossing_records_people": [round(float(x)) for x in carried[:10]],
        "records_newly_below_as_committed": int(high.sum()),
        "largest_record_newly_below_as_committed_people": round(
            float(person_weights[high].max())
        ),
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
