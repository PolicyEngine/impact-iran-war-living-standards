export const SCENARIO_CONTENT = {
  low_shock: {
    shortLabel: "Low",
    selectorLabel: "Low (+15% energy, +20% fuel, +1pp CPI)",
    description:
      "The conflict de-escalates from the August 2026 position and prices stabilise near where they already are: negotiations hold, Strait of Hormuz traffic normalises, and Brent settles around its early-August level of ~$85/bbl after the ~$109 wartime peak. Energy bills rise 15% relative to pre-conflict levels — in line with the observed +13% Ofgem cap increase in July 2026 plus Cornwall Insight's ~£1,700 forecast for Q4. Fuel costs stay 20% up, matching today's pump prices (~157p petrol) against late-2025 levels, food prices add 2%, and CPI runs 1 percentage point above its pre-conflict trend, consistent with the Bank of England's June projection of ~3% inflation. This scenario is effectively the cost of the conflict as it has already happened, sustained for 12 months. Even here, benefit-reliant households lose real income until the April 2027 uprating catches up with September 2026 CPI.",
  },
  central_shock: {
    shortLabel: "Central",
    selectorLabel: "Central (+45% energy, +45% fuel, +2.5pp CPI)",
    description:
      "The Strait of Hormuz constraint persists: tit-for-tat strikes continue and shipping remains restricted, keeping Brent above $100/bbl through 2026 — Goldman Sachs' extended-closure case ($120 in Q3, $115 in Q4). Wholesale gas follows oil upward, pushing the energy cap 45% above pre-conflict levels over the year, with fuel up 45%, food up 4%, and CPI 2.5 percentage points above trend — in the range the Bank of England has flagged as the risk case. The benefit uprating lag bites harder here: CPI-linked benefits were set from September 2025 prices, so their real value erodes through the whole shock year. Lower-income households, who spend roughly three times the share of their budgets on energy compared with the top decile, bear the largest proportional losses.",
  },
  severe_shock: {
    shortLabel: "High",
    selectorLabel: "High (+90% energy, +80% fuel, +4.5pp CPI)",
    description:
      "A prolonged war with an extended full closure of the Strait of Hormuz — the tail-risk case: Goldman Sachs' extreme-adverse scenario puts Brent above $115-120/bbl, and Oxford Economics' prolonged-war scenario implies world inflation reaching 7.7%, a global recession, and a mild UK contraction (UK growth already cut from 1.1% to 0.4% for 2026). Energy bills rise 90% above pre-conflict levels — comparable in scale to the 2022 gas crisis before the Energy Price Guarantee — with fuel up 80%, food up 6.5%, and CPI 4.5 percentage points above trend. At this severity the fuel poverty rate more than doubles and support on the scale of 2022 (which ministers have so far ruled out) would return to the agenda; the Policy Responses tab shows what each option would cost and who it would reach.",
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
