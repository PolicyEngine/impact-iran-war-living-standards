export const SCENARIO_CONTENT = {
  external_forecast: {
    // Built from published forecasts rather than chosen by this study, so it
    // can be reported as "if prices follow the latest forecasts". Promised
    // to the Telegraph on 9 October 2026 in place of purely illustrative
    // paths. Every figure in the description is read from the results file.
    type: "forecast",
    shortLabel: "Latest forecasts",
    pathLabel: "prices following the latest published forecasts",
    describe: (p) =>
      `Prices follow the latest published forecasts for 2027-28. Energy +${p.cap_increase_pct}%: Cornwall Insight's January–March 2027 price cap forecast, with electricity VAT back at 5% from April, held for the year because Cornwall publishes no forecast for 2027-28. Fuel +${p.fuel_pct}%: our pass-through of the US EIA's Brent forecast to UK pump prices, with fuel duty held at 52.95p. Food +${p.food_increase_pct}%: how far IGD has raised its forecast 2027 food prices since before the conflict. CPI +${p.cpi_increase_pp}pp, used only to size the benefit uprating gap, not a forecast. Still not a prediction: report it as what 2027-28 would cost if prices follow these forecasts.`,
  },
  low_shock: {
    type: "stress_test",
    // Named by what each assumes, not by likelihood: "Central" read as the
    // estimate of the war's effect (Max, #46 comment 5872474615).
    shortLabel: "Summer 2026 prices",
    // The conflict path this scenario represents. Defined once here so a
    // relabel cannot be partial; every tab reads it rather than restating it.
    pathLabel: "summer 2026 prices held",
    // Descriptions are built from the generated parameters rather than
    // restating them, so dashboard copy cannot drift from the model the way
    // it did when severe fuel moved 80% -> 65% and the CPI adders were
    // corrected (#37). Only the prose that is NOT a number lives here.
    // A constructed path anchored to observed energy and fuel prices, not the
    // observed prices themselves: food is a judgement and all three are held
    // for a future year (#61 fifth review A8).
    describe: (p, observed) =>
      `An assumption: summer 2026 prices hold for all of 2027-28. Energy +${p.cap_increase_pct}%, anchored to the July cap rise (+13.5%; October's is higher). Fuel +${p.fuel_pct}%, the August pump-price rise${observed ? ` (mid-September: +${observed.fuel}%)` : ""}. Food +${p.food_increase_pct}%, a judgement. CPI +${p.cpi_increase_pp}pp, used only to size the benefit uprating gap, not a forecast.`,
  },
  central_shock: {
    type: "stress_test",
    shortLabel: "Sustained escalation",
    pathLabel: "sustained escalation",
    describe: (p, observed) =>
      `Hormuz stays constrained. Gas stays at about twice its pre-conflict price as Qatari LNG is halted, lifting energy spending +${p.cap_increase_pct}%. Fuel +${p.fuel_pct}% follows Brent above $100/bbl (Goldman Sachs' extended-closure case). Food +${p.food_increase_pct}%. CPI +${p.cpi_increase_pp}pp, used only to size the benefit uprating gap, not a forecast. Held for 12 months.${observed ? ` Observed so far: energy +${observed.energy}% (July cap; +${observed.octoberEnergy}% for October), fuel +${observed.fuel}%. This is a stress test of prices rising well beyond that.` : ""}`,
  },
  severe_shock: {
    type: "stress_test",
    shortLabel: "Severe escalation",
    pathLabel: "severe escalation",
    describe: (p) =>
      `A tail risk: prolonged war and extended Hormuz closure. Gas at about triple its pre-conflict price lifts energy spending +${p.cap_increase_pct}% (the October 2022 cap rose 178%). Fuel +${p.fuel_pct}% is our pass-through of Brent near $140/bbl (Oxford Economics' escalation case). Food +${p.food_increase_pct}%. CPI +${p.cpi_increase_pp}pp, used only to size the benefit uprating gap, not a forecast. Held for 12 months.`,
  },
};

// What a reader should be told each scenario is. A stress test is a level
// this study chose; a forecast-based scenario takes its prices from other
// organisations' published forecasts.
export const SCENARIO_TYPE_LABELS = {
  forecast: "Forecast-based",
  stress_test: "Stress test",
};

// The pipeline's own label for each type, so the dashboard reads the type
// from the results file rather than trusting this file alone.
const PIPELINE_TYPES = {
  "annual forecast-based scenario": "forecast",
  "annual stress test": "stress_test",
};

/**
 * The scenario's type, from the results file where it says, else from the
 * content above. A results file that contradicts the content wins: the
 * pipeline is what produced the numbers.
 */
export function getScenarioType(key, data) {
  const fromData = PIPELINE_TYPES[data?.scenarios?.[key]?.scenario_type];
  return fromData || SCENARIO_CONTENT[key]?.type || "stress_test";
}

// Built from the generated parameters so the selector cannot advertise
// figures the model no longer uses.
export function buildSelectorLabel(key, params) {
  const short = SCENARIO_CONTENT[key]?.shortLabel || key;
  if (!params) return short;
  // CPI is left out of the label: it is not a price the household pays and
  // only sizes the benefit uprating gap, so listing it beside energy and fuel
  // read as an inflation forecast.
  return `${short} (+${params.cap_increase_pct}% energy, +${params.fuel_pct}% fuel, +${params.food_increase_pct}% food)`;
}

// The forecast-based scenario leads: it is the one to report.
export const SCENARIO_ORDER = [
  "external_forecast",
  "low_shock",
  "central_shock",
  "severe_shock",
];

/**
 * The scenario a tab opens on: the first in SCENARIO_ORDER that the results
 * file contains, so an older file without the forecast scenario still opens.
 */
export function getDefaultScenario(data) {
  const keys = Object.keys(data?.scenarios || {});
  return SCENARIO_ORDER.find((key) => keys.includes(key)) || keys[0];
}

export function getScenarioOptions(data) {
  const scenarioKeys = Object.keys(data?.scenarios || {});
  const orderedKeys = SCENARIO_ORDER.filter((key) => scenarioKeys.includes(key));
  return orderedKeys.map((key) => {
    const type = getScenarioType(key, data);
    return {
      id: key,
      label: buildSelectorLabel(key, data?.scenarios?.[key]?.params),
      type,
      typeLabel: SCENARIO_TYPE_LABELS[type],
    };
  });
}

/**
 * The selector's options grouped by type, forecast-based first, so the
 * stress tests are visibly labelled as such rather than sitting beside the
 * forecast as equals. Empty groups are dropped.
 */
export function getScenarioGroups(data) {
  const options = getScenarioOptions(data);
  return ["forecast", "stress_test"]
    .map((type) => ({
      type,
      label: type === "forecast" ? "Forecast-based" : "Stress tests",
      options: options.filter((o) => o.type === type),
    }))
    .filter((group) => group.options.length > 0);
}

export function getScenarioNarrative(scenarioKey, data) {
  const content = SCENARIO_CONTENT[scenarioKey];
  if (!content) return null;
  const params = data?.scenarios?.[scenarioKey]?.params;
  const baseline = data?.metadata?.pre_conflict_baseline;
  const observed =
    Number.isFinite(baseline?.observed_energy_rise_by_sept_2026_pct) &&
    Number.isFinite(baseline?.observed_fuel_rise_by_sept_2026_pct) &&
    Number.isFinite(baseline?.announced_oct_2026_vs_pre_conflict_pct)
      ? {
          energy: baseline.observed_energy_rise_by_sept_2026_pct,
          fuel: baseline.observed_fuel_rise_by_sept_2026_pct,
          octoberEnergy: baseline.announced_oct_2026_vs_pre_conflict_pct,
        }
      : null;
  const type = getScenarioType(scenarioKey, data);
  return {
    ...content,
    type,
    typeLabel: SCENARIO_TYPE_LABELS[type],
    selectorLabel: buildSelectorLabel(scenarioKey, params),
    description: params ? content.describe(params, observed) : "",
  };
}

/**
 * The paths, named once, in scenario order. Tabs that list the paths read
 * this rather than restating them, so a relabel cannot be partial. Pass a
 * type to list only the stress tests or only the forecast-based scenario.
 */
export function getScenarioPathLabels(type) {
  return SCENARIO_ORDER.filter(
    (key) => !type || SCENARIO_CONTENT[key]?.type === type,
  )
    .map((key) => SCENARIO_CONTENT[key]?.pathLabel)
    .filter(Boolean);
}
