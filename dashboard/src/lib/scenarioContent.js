export const SCENARIO_CONTENT = {
  low_shock: {
    shortLabel: "Low",
    selectorLabel: "Low (+15% energy, +20% fuel, +1pp CPI)",
    description:
      "The conflict de-escalates and prices stabilise where they already are: Brent ~$85/bbl, energy bills +15% (the observed July 2026 cap rise plus Cornwall Insight's Q4 forecast), fuel +20% (today's pump prices), food +2%, CPI +1pp — the cost of the conflict as it has already happened, sustained for 12 months.",
  },
  central_shock: {
    shortLabel: "Central",
    selectorLabel: "Central (+45% energy, +45% fuel, +2.5pp CPI)",
    description:
      "The Strait of Hormuz constraint persists, keeping Brent above $100/bbl (Goldman Sachs' extended-closure case): energy cap +45%, fuel +45%, food +4%, CPI +2.5pp, sustained for 12 months. Lower-income households, who spend roughly three times the budget share on energy of the top decile, bear the largest proportional losses.",
  },
  severe_shock: {
    shortLabel: "High",
    selectorLabel: "High (+90% energy, +80% fuel, +4.5pp CPI)",
    description:
      "A prolonged war with extended Strait of Hormuz closure — the tail risk: Brent above $115-120 (Goldman extreme-adverse; Oxford Economics sees a global recession). Energy cap +90% — comparable to the 2022 gas crisis — fuel +80%, food +6.5%, CPI +4.5pp, sustained for 12 months.",
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
