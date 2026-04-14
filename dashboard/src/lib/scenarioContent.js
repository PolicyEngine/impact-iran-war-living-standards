export const SCENARIO_CONTENT = {
  limited_strikes: {
    shortLabel: "Low",
    selectorLabel: "Low (+30% energy, +20% fuel, +1.5pp CPI)",
    description:
      "A moderate scenario: +30% energy price cap, +20% fuel costs, +2% food prices, and a 1.5 percentage point CPI increase, sustained for 12 months.",
  },
  prolonged_conflict: {
    shortLabel: "Central",
    selectorLabel: "Central (+75% energy, +50% fuel, +3.5pp CPI)",
    description:
      "A central scenario: +75% energy price cap, +50% fuel costs, +4.5% food prices, and a 3.5 percentage point CPI increase, sustained for 12 months. Benefit erosion from the uprating lag compounds the direct price effects.",
  },
  strait_of_hormuz: {
    shortLabel: "High",
    selectorLabel: "High (+150% energy, +100% fuel, +6pp CPI)",
    description:
      "A severe scenario: +150% energy price cap, +100% fuel costs, +6.4% food prices, and a 6 percentage point CPI increase, sustained for 12 months.",
  },
};

export const SCENARIO_ORDER = [
  "limited_strikes",
  "prolonged_conflict",
  "strait_of_hormuz",
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
