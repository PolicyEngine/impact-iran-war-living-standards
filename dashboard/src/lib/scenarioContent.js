export const SCENARIO_CONTENT = {
  low_shock: {
    // Named by what each assumes, not by likelihood: "Central" read as the
    // estimate of the war's effect (Max, #46 comment 5872474615).
    shortLabel: "Prices so far",
    // The conflict path this scenario represents. Defined once here so a
    // relabel cannot be partial; every tab reads it rather than restating it.
    pathLabel: "premium partially unwinds",
    // Descriptions are built from the generated parameters rather than
    // restating them, so dashboard copy cannot drift from the model the way
    // it did when severe fuel moved 80% -> 65% and the CPI adders were
    // corrected (#37). Only the prose that is NOT a number lives here.
    describe: (p) =>
      `Prices settle near their current elevated levels rather than falling back. Energy spending +${p.cap_increase_pct}%, anchored to the observed +13.5% July 2026 cap rise. This sits slightly below the announced October 2026 cap, so it represents the Q4-2026 premium partially unwinding through 2027-28, not a return to pre-conflict prices. Fuel +${p.fuel_pct}%, food +${p.food_increase_pct}%, CPI +${p.cpi_increase_pp}pp against a no-conflict path (used only to size the benefit uprating gap, not a CPI forecast). Held at those levels for 12 months.`,
  },
  central_shock: {
    shortLabel: "Sustained escalation",
    pathLabel: "sustained disruption",
    describe: (p, observed) =>
      `The Strait of Hormuz constraint persists. The energy channel is gas-driven: NBP/TTF sustained at roughly twice pre-conflict levels as the closure halts Qatari LNG, which on a ~40-45% wholesale share implies energy spending +${p.cap_increase_pct}%. Fuel +${p.fuel_pct}% follows Brent above $100/bbl (Goldman Sachs' extended-closure case); food +${p.food_increase_pct}%, CPI +${p.cpi_increase_pp}pp against a no-conflict path (used only to size the benefit uprating gap, not a CPI forecast), sustained for 12 months. Lower-income households, who spend roughly three times the budget share on energy of the top quintile, bear the largest proportional losses.${observed ? ` For comparison, observed prices so far are energy +${observed.energy}% (July 2026 cap; +${observed.octoberEnergy}% announced for October) and fuel +${observed.fuel}%, close to the prices-so-far scenario: this is a stress test of prices rising well beyond today's, not a forecast.` : ""}`,
  },
  severe_shock: {
    shortLabel: "Severe escalation",
    pathLabel: "prolonged war",
    describe: (p) =>
      `A prolonged war with extended Strait of Hormuz closure, as a tail risk. Gas sustained at roughly triple pre-conflict levels gives energy spending +${p.cap_increase_pct}%, comparable to the 2022 crisis, when the announced October 2022 cap rose 178% year on year. Fuel +${p.fuel_pct}% is the oil-to-pump pass-through at Brent near $140/bbl under the Oxford Economics escalation case, which reports a 5.8% peak in world CPI and a global recession. Food +${p.food_increase_pct}%, CPI +${p.cpi_increase_pp}pp against a no-conflict path (used only to size the benefit uprating gap, not a CPI forecast), sustained for 12 months.`,
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
