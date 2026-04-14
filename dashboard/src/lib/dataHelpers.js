/**
 * Data helper functions for the Iran war impact dashboard.
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
 * Decile breakdown — components use `avg_cost` as the bar dataKey.
 */
export function getDecileBreakdown(data, scenarioKey) {
  const raw = data?.scenarios?.[scenarioKey]?.by_decile || [];
  return raw.map((d) => ({
    ...d,
    avg_cost: d.mean_impact,
    label: `${d.decile}`,
  }));
}

/**
 * Fuel poverty — components expect baseline_rate, shocked_rate, increase_pp.
 */
export function getFuelPoverty(data, scenarioKey) {
  const sc = data?.scenarios?.[scenarioKey];
  if (!sc) return null;
  const s = sc.summary || {};
  return {
    baseline_rate: s.fp_rate_baseline_pct,
    shocked_rate: s.fp_rate_shocked_pct,
    increase_pp: (s.fp_rate_shocked_pct || 0) - (s.fp_rate_baseline_pct || 0),
    extra_households: s.fp_extra_households,
  };
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
    benefit_erosion: raw.benefit_erosion,
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
 * Quintile shares — what % of each policy's total spending goes to each quintile.
 */
export function getQuintileShares(data, scenarioKey) {
  const pr = data?.policy_responses?.[scenarioKey];
  if (!pr) return [];
  const POLICY_KEYS = ["epg","flat_rebate","ct_rebate","uc_uplift","fuel_duty_cut","means_tested","accelerated_uprating","social_tariff"];
  const POLICY_LABELS = {
    epg: "Energy Price Guarantee",
    flat_rebate: "Flat rebate",
    ct_rebate: "Council Tax rebate",
    uc_uplift: "UC uplift",
    fuel_duty_cut: "Fuel duty cut",
    means_tested: "Means-tested payment",
    accelerated_uprating: "Accelerated uprating",
    social_tariff: "Social tariff",
  };
  return POLICY_KEYS.map(key => {
    const deciles = pr[key]?.by_decile || [];
    if (deciles.length < 10) return null;
    const total = deciles.reduce((s, d) => s + (d.mean_benefit || 0), 0);
    if (total === 0) return null;
    return {
      policy: POLICY_LABELS[key] || key,
      "Q1 (poorest)": +((( deciles[0]?.mean_benefit || 0) + (deciles[1]?.mean_benefit || 0)) / total * 100).toFixed(1),
      "Q2": +(((deciles[2]?.mean_benefit || 0) + (deciles[3]?.mean_benefit || 0)) / total * 100).toFixed(1),
      "Q3": +(((deciles[4]?.mean_benefit || 0) + (deciles[5]?.mean_benefit || 0)) / total * 100).toFixed(1),
      "Q4": +(((deciles[6]?.mean_benefit || 0) + (deciles[7]?.mean_benefit || 0)) / total * 100).toFixed(1),
      "Q5 (richest)": +(((deciles[8]?.mean_benefit || 0) + (deciles[9]?.mean_benefit || 0)) / total * 100).toFixed(1),
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
    const fpBefore = p.fp_rate_before_pct || 0;
    const fpAfter = p.fp_rate_after_pct || 0;

    return {
      ...p,
      avg_household_benefit: p.avg_benefit_per_hh,
      fuel_poverty_reduction_pp: fpBefore - fpAfter,
      targeting_bottom3: p.targeting_bottom3,
    };
  };

  const result = {};
  for (const [key, val] of Object.entries(pr)) {
    result[key] = transform(val);
  }

  return result;
}
