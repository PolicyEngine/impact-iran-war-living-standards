export const SCENARIO_CONTENT = {
  low_shock: {
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
    shortLabel: "Sustained escalation",
    pathLabel: "sustained escalation",
    describe: (p, observed) =>
      `Hormuz stays constrained. Gas stays at about twice its pre-conflict price as Qatari LNG is halted, lifting energy spending +${p.cap_increase_pct}%. Fuel +${p.fuel_pct}% follows Brent above $100/bbl (Goldman Sachs' extended-closure case). Food +${p.food_increase_pct}%. CPI +${p.cpi_increase_pp}pp, used only to size the benefit uprating gap, not a forecast. Held for 12 months.${observed ? ` Observed so far: energy +${observed.energy}% (July cap; +${observed.octoberEnergy}% for October), fuel +${observed.fuel}%. This is a stress test of prices rising well beyond that.` : ""}`,
  },
  severe_shock: {
    shortLabel: "Severe escalation",
    pathLabel: "severe escalation",
    describe: (p) =>
      `A tail risk: prolonged war and extended Hormuz closure. Gas at about triple its pre-conflict price lifts energy spending +${p.cap_increase_pct}% (the October 2022 cap rose 178%). Fuel +${p.fuel_pct}% is our pass-through of Brent near $140/bbl (Oxford Economics' escalation case). Food +${p.food_increase_pct}%. CPI +${p.cpi_increase_pp}pp, used only to size the benefit uprating gap, not a forecast. Held for 12 months.`,
  },
};

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

export const SCENARIO_ORDER = [
  "low_shock",
  "central_shock",
  "severe_shock",
];

export function getScenarioOptions(data) {
  const scenarioKeys = Object.keys(data?.scenarios || {});
  const orderedKeys = SCENARIO_ORDER.filter((key) => scenarioKeys.includes(key));
  return orderedKeys.map((key) => ({
    id: key,
    label: buildSelectorLabel(key, data?.scenarios?.[key]?.params),
  }));
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
  return {
    ...content,
    selectorLabel: buildSelectorLabel(scenarioKey, params),
    description: params ? content.describe(params, observed) : "",
  };
}

/**
 * The three conflict paths, named once, in scenario order. Tabs that list the
 * paths read this rather than restating them, so a relabel cannot be partial.
 */
export function getScenarioPathLabels() {
  return SCENARIO_ORDER.map((key) => SCENARIO_CONTENT[key]?.pathLabel).filter(
    Boolean,
  );
}
