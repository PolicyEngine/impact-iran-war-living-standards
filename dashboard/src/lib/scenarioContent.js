export const SCENARIO_CONTENT = {
  low_shock: {
    shortLabel: "Low",
    selectorLabel: "Low (+15% energy, +20% fuel, +1pp CPI)",
    description:
      "Conflict de-escalation from the August 2026 position: energy cap +15% (in line with the observed +13% July 2026 rise and Cornwall Insight's Q4 forecast), fuel +20% (roughly today's pump prices vs late 2025), +2% food prices, and a 1 percentage point CPI addition, sustained for 12 months.",
  },
  central_shock: {
    shortLabel: "Central",
    selectorLabel: "Central (+45% energy, +45% fuel, +2.5pp CPI)",
    description:
      "A sustained Strait of Hormuz constraint keeping Brent above $100/bbl through 2026 (Goldman Sachs closure scenario): energy cap +45%, fuel +45%, +4% food prices, and a 2.5 percentage point CPI addition, sustained for 12 months. The benefit uprating lag compounds direct price effects for benefit-reliant households.",
  },
  severe_shock: {
    shortLabel: "High",
    selectorLabel: "High (+90% energy, +80% fuel, +4.5pp CPI)",
    description:
      "An extended full closure / prolonged war (Goldman extreme-adverse Brent >$115-120; Oxford Economics prolonged-war scenario): energy cap +90%, fuel +80%, +6.5% food prices, and a 4.5 percentage point CPI addition, sustained for 12 months.",
  },
};

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
    label: SCENARIO_CONTENT[key]?.selectorLabel || key,
  }));
}

export function getScenarioNarrative(scenarioKey) {
  return SCENARIO_CONTENT[scenarioKey] || null;
}
