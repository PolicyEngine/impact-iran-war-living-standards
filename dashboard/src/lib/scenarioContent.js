export const SCENARIO_CONTENT = {
  low_shock: {
    shortLabel: "Low",
    selectorLabel: "Low (+30% energy, +20% fuel, +1.5pp CPI)",
    description:
      "A moderate energy price shock: +30% energy price cap, +20% fuel costs, +2% food prices, and a 1.5 percentage point CPI increase, sustained for 12 months. Calibrated to a short-duration supply disruption.",
  },
  central_shock: {
    shortLabel: "Central",
    selectorLabel: "Central (+75% energy, +50% fuel, +3.5pp CPI)",
    description:
      "A central energy price shock: +75% energy price cap, +50% fuel costs, +4.5% food prices, and a 3.5 percentage point CPI increase, sustained for 12 months. The benefit uprating lag compounds direct price effects for benefit-reliant households.",
  },
  severe_shock: {
    shortLabel: "High",
    selectorLabel: "High (+150% energy, +100% fuel, +6pp CPI)",
    description:
      "A severe energy price shock: +150% energy price cap, +100% fuel costs, +6.4% food prices, and a 6 percentage point CPI increase, sustained for 12 months. Calibrated to a major and sustained disruption to oil and gas supply routes.",
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
