/**
 * Data helper functions for the energy price shock impact dashboard.
 *
 * These transform the raw JSON structure (from run_pipeline.py) into the
 * shapes that the React components expect.
 */

export function getBaseline(data) {
  return data?.baseline || {};
}

/**
 * Returns a flat object with headline scenario metrics.
 * Components expect: avg_household_cost, poverty_increase
 */
export function getScenario(data, scenarioKey) {
  const sc = data?.scenarios?.[scenarioKey];
  if (!sc) return null;
  const s = sc.summary || {};
  return {
    ...sc,
    avg_household_cost: s.mean_net_impact,
    poverty_increase: s.n_pushed_into_poverty,
  };
}

/**
 * Quintile breakdown — components use `avg_cost` as the bar dataKey.
 */
export function getQuintileBreakdown(data, scenarioKey) {
  const raw = data?.scenarios?.[scenarioKey]?.by_quintile || [];
  return raw.map((q) => ({
    ...q,
    avg_cost: q.mean_impact,
    label: `Q${q.quintile}`,
  }));
}

/**
 * Channel decomposition — keyed by clean channel name (energy, fuel, food, etc.)
 */
export function getChannelDecomposition(data, scenarioKey) {
  const raw = data?.scenarios?.[scenarioKey]?.channel_decomposition;
  if (!raw) return {};
  return {
    energy: raw.energy_shock,
    fuel: raw.fuel_shock,
    food: raw.food_shock,
    benefit_uprating_shortfall: raw.benefit_uprating_shortfall,
  };
}

/**
 * Regional breakdown — components use `avg_cost`.
 */
export function getRegionalBreakdown(data, scenarioKey) {
  const raw = data?.scenarios?.[scenarioKey]?.by_region || [];
  return raw.map((r) => ({
    ...r,
    avg_cost: r.mean_impact,
  }));
}

/**
 * Country breakdown — components use `avg_cost`.
 */
export function getCountryBreakdown(data, scenarioKey) {
  const raw = data?.scenarios?.[scenarioKey]?.by_country || [];
  return raw.map((c) => ({
    ...c,
    avg_cost: c.mean_impact,
  }));
}

/**
 * Household type breakdown — components use `avg_cost`.
 */
export function getHouseholdTypeBreakdown(data, scenarioKey) {
  const raw = data?.scenarios?.[scenarioKey]?.by_hh_type || [];
  return raw.map((h) => ({
    ...h,
    avg_cost: h.mean_impact,
  }));
}

/**
 * Tenure breakdown — components use `avg_cost`.
 */
export function getTenureBreakdown(data, scenarioKey) {
  const raw = data?.scenarios?.[scenarioKey]?.by_tenure || [];
  return raw.map((t) => ({
    ...t,
    avg_cost: t.mean_impact,
  }));
}

// Single source of truth for policy keys/labels, shared with PolicyTab.
export const POLICY_KEYS = [
  "epg",
  "flat_rebate",
  "ct_rebate",
  "uc_uplift",
  "fuel_duty_cut",
  "means_tested",
  "accelerated_uprating",
  "elec_vat_cut",
  "social_tariff",
  "combined",
];

export const POLICY_LABELS = {
  epg: "Energy Price Guarantee",
  flat_rebate: "Flat rebate",
  ct_rebate: "Council Tax rebate",
  uc_uplift: "UC uplift",
  fuel_duty_cut: "Fuel duty cut extension",
  means_tested: "Means-tested payment",
  accelerated_uprating: "Accelerated uprating",
  elec_vat_cut: "Electricity VAT cut",
  social_tariff: "Social tariff",
  combined: "Combined package",
};

/**
 * Quintile shares — what % of each policy's total spending goes to each
 * quintile. Uses the pipeline's household-weighted `benefit_share_pct` per
 * quintile, so it is consistent with the `targeting_bottom40` statistic.
 */
export function getQuintileShares(data, scenarioKey) {
  const pr = data?.policy_responses?.[scenarioKey];
  if (!pr) return [];
  return POLICY_KEYS.filter((k) => k !== "combined").map(key => {
    const quintiles = pr[key]?.by_quintile || [];
    if (quintiles.length < 5) return null;
    return {
      policy: POLICY_LABELS[key] || key,
      "Q1 (lowest income)": quintiles[0].benefit_share_pct,
      "Q2": quintiles[1].benefit_share_pct,
      "Q3": quintiles[2].benefit_share_pct,
      "Q4": quintiles[3].benefit_share_pct,
      "Q5 (highest income)": quintiles[4].benefit_share_pct,
    };
  }).filter(Boolean);
}

/**
 * Policy comparison — maps the policy_responses structure into per-policy
 * objects with the field names the PolicyTab component expects.
 * Policies are now modelled per scenario.
 */
export function getPolicyComparison(data, scenarioKey) {
  const pr = data?.policy_responses?.[scenarioKey];
  if (!pr) return {};

  const transform = (p) => {
    if (!p) return null;
    return {
      ...p,
      avg_household_benefit: p.avg_benefit_per_hh,
      targeting_bottom40: p.targeting_bottom40,
    };
  };

  const result = {};
  for (const [key, val] of Object.entries(pr)) {
    result[key] = transform(val);
  }

  return result;
}
