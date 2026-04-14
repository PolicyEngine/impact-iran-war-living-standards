export const SCENARIO_CONTENT = {
  limited_strikes: {
    shortLabel: "Low",
    selectorLabel: "Low (+30% energy, +20% fuel, +1.5pp CPI)",
    description:
      "Targeted strikes on Iranian nuclear or military facilities with no sustained conflict. Oil markets react with a short-term risk premium. We model a 30% increase in the energy price cap, a 20% rise in fuel costs, a 2% food price increase, and a 1.5 percentage point increase in CPI inflation. All price increases are assumed to be sustained for 12 months.",
  },
  prolonged_conflict: {
    shortLabel: "Central",
    selectorLabel: "Central (+75% energy, +50% fuel, +3.5pp CPI)",
    description:
      "A sustained military campaign lasting several months, with retaliatory attacks on regional oil infrastructure. We model a 75% increase in the energy price cap, a 50% rise in fuel costs, a 4.5% food price increase, and a 3.5 percentage point CPI increase. Benefit erosion from uprating lag and fiscal drag compound the direct price effects over 12 months.",
  },
  strait_of_hormuz: {
    shortLabel: "High",
    selectorLabel: "High (+150% energy, +100% fuel, +6pp CPI)",
    description:
      "A blockade of the Strait of Hormuz cuts a large share of global oil supply and triggers a full-scale energy shock. We model a 150% increase in the energy price cap, a doubling of fuel costs, a 6.4% food price increase, and a 6 percentage point CPI increase over 12 months.",
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
