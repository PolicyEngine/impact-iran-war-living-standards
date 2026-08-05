"use client";

import { useMemo, useState } from "react";
import { colors, policyColors } from "../lib/colors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import SectionHeading from "./SectionHeading";
import { getPolicyComparison, POLICY_KEYS, POLICY_LABELS } from "../lib/dataHelpers";
import { formatCurrency, formatBn } from "../lib/formatters";
import ChartLogo from "./ChartLogo";
import QuintileTargetingChart from "./QuintileTargetingChart";
import { getScenarioNarrative, getScenarioOptions } from "../lib/scenarioContent";

const AXIS_STYLE = {
  fontSize: 12,
  fill: colors.gray[500],
};

const POLICY_DESCRIPTIONS = {
  epg: {
    mechanism: "Caps the domestic energy-bill increase at 10% of each household's pre-shock energy bill — a stylised version of the 2022 Energy Price Guarantee, which froze the unit-price level rather than the percentage increase. Ministers have ruled out repeating universal 2022-scale support, favouring targeted help, so this is modelled as the ruled-out benchmark the targeted options are judged against.",
    model: "The model treats this as a direct reduction in the household energy bill, so it can reduce both residual household impact and fuel poverty.",
  },
  flat_rebate: {
    mechanism: "Pays every household a flat £400 energy rebate.",
    model: "The model treats this as cash support against the selected energy price shock. It lowers residual household impact and improves energy affordability through higher disposable resources.",
  },
  ct_rebate: {
    mechanism: "Pays a £300 council tax rebate to households in bands A-D.",
    model: "The model treats this as targeted cash support. Eligibility is based on the household council tax band in the microsimulation.",
  },
  uc_uplift: {
    mechanism: "Increases Universal Credit by £20 per week for UC-recipient households, matching the 2020-21 covid uplift.",
    model: "The model annualises this to £1,040 for households receiving UC and treats it as income support during the selected shock scenario.",
  },
  fuel_duty_cut: {
    mechanism: "Extends the existing 5p per litre fuel duty cut (currently legislated to expire 31 December 2026) through the shock period.",
    model: "The model applies an average £60 annual transport-fuel saving, scaled by each household's imputed fuel spending so low-mileage and non-driving households receive less.",
  },
  means_tested: {
    mechanism: "Pays £650 to households receiving a means-tested benefit (UC, Pension Credit or income-related legacy benefits), mirroring the 2022 Cost of Living Payment.",
    model: "The model treats this as income support for benefit-recipient households in the selected shock scenario.",
  },
  elec_vat_cut: {
    mechanism: "Extends the electricity VAT cut (5% to 0%) announced in July 2026 — currently legislated for October 2026 to March 2027 — for a full year.",
    model: "The model removes the 5% VAT component from each household's post-shock electricity bill, directly reducing energy costs and fuel poverty.",
  },
  accelerated_uprating: {
    mechanism: "Updates benefit levels immediately for the shock-driven inflation increase instead of waiting for the usual uprating cycle.",
    model: "The model offsets the estimated real loss from benefit-uprating lag for households receiving uprated benefits.",
  },
  social_tariff: {
    mechanism: "Offers a discounted energy tariff to low-income and vulnerable households, halving the energy price shock for those on Universal Credit or with household income below \u00A320,000.",
    model: "The model applies a 50% reduction in the energy price shock for eligible households. This directly reduces both residual household impact and fuel poverty, and is the most progressive policy option modelled.",
  },
  combined: {
    mechanism: "Applies all policies above together (excluding the social tariff).",
    model: "Household benefit is capped at the size of the shock, but the fiscal cost reflects the full unclipped government outlay of every component policy.",
  },
};

function CustomTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-lg">
      {label !== undefined ? (
        <div className="mb-2 font-semibold text-slate-800">{label}</div>
      ) : null}
      {payload.map((entry) => (
        <div className="flex items-center justify-between gap-4" key={entry.name}>
          <span className="flex items-center gap-2 text-slate-600">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            {entry.name}
          </span>
          <span className="font-medium text-slate-800">
            {formatter ? formatter(entry.value, entry.name) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function PolicyTab({ data }) {
  const [scenario, setScenario] = useState("low_shock");
  const [selectedPolicy, setSelectedPolicy] = useState("epg");

  const policies = getPolicyComparison(data, scenario);
  const policy = policies?.[selectedPolicy] || null;
  const policyLabel = POLICY_LABELS[selectedPolicy] || selectedPolicy;
  const policyDescription = POLICY_DESCRIPTIONS[selectedPolicy];
  const scenarioDescription = getScenarioNarrative(scenario);
  const scenarioOptions = getScenarioOptions(data);

  // Decile data for selected policy
  const quintileData = useMemo(() => {
    if (!policy?.by_quintile) return [];
    return policy.by_quintile.map((q) => ({
      ...q,
      label: `Q${q.quintile}`,
    }));
  }, [policy]);

  const winnersLosersData = useMemo(() => {
    if (!policy?.winners_losers) return [];
    return policy.winners_losers.map((d) => ({
      ...d,
      label: `Q${d.quintile}`,
    }));
  }, [policy]);

  // Build summary rows for the policy selector table
  const policyRows = useMemo(() => {
    return POLICY_KEYS.map((key) => {
      const p = policies?.[key];
      if (!p) return null;
      return {
        key,
        label: POLICY_LABELS[key] || key,
        fiscal_cost_bn: p.fiscal_cost_bn,
        avg_household_benefit: p.avg_household_benefit,
        fuel_poverty_reduction_pp: p.fuel_poverty_reduction_pp,
        targeting_bottom40: p.targeting_bottom40,
        color: policyColors[key] || colors.gray[400],
      };
    }).filter(Boolean);
  }, [policies]);

  return (
    <div className="space-y-10">

      {/* ================================================================ */}
      {/* SCENARIO SELECTOR                                                 */}
      {/* ================================================================ */}
      <p className="text-sm leading-7 text-slate-600">
        This tab compares the government support options for the 2027-28 tax year — including
        the decisions on the table for the Autumn Budget on 28 October 2026 (extending the
        electricity VAT cut and the 5p fuel duty cut, a benefits-targeted winter energy
        payment, and the timing of benefit uprating). The baseline for every comparison is
        the selected shock scenario before any policy response; the reform case is the same
        scenario with the selected policy applied. Fiscal cost is the full government outlay
        of the policy in 2027-28; average household benefit is the reduction in annual
        household impact from the energy price shock; fuel poverty reduction compares the
        10%-of-income fuel poverty indicator before and after the policy. Targeting matters
        as much as scale: a policy that spends less but concentrates support on the
        lowest-income households can protect them better per pound than a larger universal
        scheme.
      </p>

      <div className="grid items-stretch gap-6 lg:grid-cols-2">
        <div className="section-card flex h-full flex-col">
          <SectionHeading
            title="Select scenario"
            description="Choose a scenario to evaluate policy responses."
          />
          <div className="mt-4 flex flex-wrap gap-2">
            {scenarioOptions.map((s) => (
              <button
                key={s.id}
                className={`rounded-full px-5 py-2 text-sm font-medium transition-colors ${
                  scenario === s.id
                    ? "text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
                style={
                  scenario === s.id
                    ? { backgroundColor: colors.primary[800] }
                    : undefined
                }
                onClick={() => setScenario(s.id)}
              >
                {s.label}
              </button>
            ))}
          </div>
          {scenarioDescription ? (
            <p className="mt-5 text-sm leading-7 text-slate-600">
              <strong className="text-slate-800">{scenarioDescription.shortLabel}:</strong>{" "}
              {scenarioDescription.description} The policy comparison treats this selected scenario as the baseline before government support.
            </p>
          ) : null}
        </div>

        {/* ================================================================ */}
        {/* POLICY SELECTOR                                                   */}
        {/* ================================================================ */}
        <div className="section-card flex h-full flex-col">
          <SectionHeading
            title="Select a policy"
            description="Choose a policy to compare the selected shock scenario before policy with the same scenario after policy."
          />

          {policyRows.length > 0 ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {policyRows.map((row) => {
                const isActive = selectedPolicy === row.key;
                return (
                  <button
                    key={row.key}
                    onClick={() => setSelectedPolicy(row.key)}
                    className={`rounded-full px-5 py-2 text-sm font-medium transition-colors ${
                      isActive
                        ? "text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                    style={
                      isActive
                        ? { backgroundColor: policyColors[row.key] || colors.primary[800] }
                        : undefined
                    }
                  >
                    {row.label}
                  </button>
                );
              })}
            </div>
          ) : (
            <p className="mt-4 text-sm text-slate-500">Policy data not yet available.</p>
          )}

          {policyDescription ? (
            <p className="mt-5 text-sm leading-7 text-slate-600">
              <strong className="text-slate-800">{policyLabel}:</strong>{" "}
              {policyDescription.mechanism} {policyDescription.model}
            </p>
          ) : null}
        </div>
      </div>

      {/* ================================================================ */}
      {/* SELECTED POLICY DETAIL                                            */}
      {/* ================================================================ */}
      {policy ? (
        <>
          {/* Three metric boxes */}
          <div className="grid gap-4 md:grid-cols-3">
            <div className="metric-card">
              <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
                Fiscal cost
              </div>
              <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                {policy.fiscal_cost_bn != null ? formatBn(policy.fiscal_cost_bn) : "--"}
              </div>
              <div className="mt-2 text-sm leading-6 text-slate-500">
                Estimated government cost of applying {policyLabel.toLowerCase()} in the selected shock scenario over 2027-28.
              </div>
            </div>
            <div className="metric-card">
              <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
                Avg household benefit
              </div>
              <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                {policy.avg_household_benefit != null
                  ? formatCurrency(policy.avg_household_benefit)
                  : "--"}
              </div>
              <div className="mt-2 text-sm leading-6 text-slate-500">
                Average reduction in 2027-28 household impact from the energy price shock after this policy.
              </div>
            </div>
            <div className="metric-card">
              <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
                Fuel poverty reduction vs scenario
              </div>
              <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                {policy.fuel_poverty_reduction_pp != null
                  ? `${policy.fuel_poverty_reduction_pp.toFixed(1)}pp`
                  : "--"}
              </div>
              <div className="mt-2 text-sm leading-6 text-slate-500">
                Percentage point fall in fuel poverty compared with the same shock scenario before policy.
              </div>
            </div>
          </div>

          <div className="grid items-stretch gap-6 xl:grid-cols-2">
            <div className="flex h-full flex-col">
              {quintileData.length > 0 ? (
                <div className="section-card flex h-[560px] flex-col">
                  <div className="min-h-[132px]">
                    <SectionHeading
                      title="Distributional impact by quintile"
                      description={`Average household reduction in the selected shock scenario's residual impact after ${policyLabel.toLowerCase()}, by income quintile (Q1 = lowest income).`}
                    />
                  </div>
                  <div className="min-h-0 flex-1 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={quintileData}>
                        <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
                        <XAxis dataKey="label" tick={AXIS_STYLE} tickLine={false} />
                        <YAxis
                          tick={AXIS_STYLE}
                          tickLine={false}
                          axisLine={false}
                          tickFormatter={(v) => `\u00A3${v}`}
                        />
                        <Tooltip
                          content={<CustomTooltip formatter={(v) => formatCurrency(v)} />}
                        />
                        <Bar
                          dataKey="mean_benefit"
                          name="Avg benefit"
                          fill={colors.primary[800]}
                          radius={[6, 6, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <ChartLogo />
                </div>
              ) : (
                <div className="section-card flex h-[560px] flex-col">
                  <p className="text-sm text-slate-500">Decile data not available for this policy.</p>
                </div>
              )}
            </div>

            <div className="flex h-full flex-col">
              {winnersLosersData.length > 0 ? (
                <div className="section-card flex h-[560px] flex-col">
                  <div className="min-h-[132px]">
                    <SectionHeading
                      title="Winners and losers"
                      description={`Share of households better off, unchanged, or worse off when moving from the selected shock scenario before policy to the same scenario with ${policyLabel.toLowerCase()}. A household counts as better or worse off if its annual residual impact changes by more than £1.`}
                    />
                  </div>
                  <div className="min-h-0 flex-1 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={winnersLosersData}>
                        <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
                        <XAxis dataKey="label" tick={AXIS_STYLE} tickLine={false} />
                        <YAxis
                          domain={[0, 100]}
                          ticks={[0, 25, 50, 75, 100]}
                          tick={AXIS_STYLE}
                          tickLine={false}
                          axisLine={false}
                          tickFormatter={(v) => `${v}%`}
                        />
                        <Tooltip
                          content={
                            <CustomTooltip
                              formatter={(v) => `${v}%`}
                            />
                          }
                        />
                        <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: 13 }} />
                        <Bar
                          dataKey="pct_winners"
                          name="Better off"
                          stackId="shares"
                          fill={colors.primary[800]}
                        />
                        <Bar
                          dataKey="pct_unchanged"
                          name="No change"
                          stackId="shares"
                          fill={colors.gray[300]}
                        />
                        <Bar
                          dataKey="pct_losers"
                          name="Worse off"
                          stackId="shares"
                          fill="#dc2626"
                        />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                  <ChartLogo />
                </div>
              ) : (
                <div className="section-card flex h-[560px] flex-col">
                  <p className="text-sm text-slate-500">Winners/losers data not available.</p>
                </div>
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="section-card">
          <p className="text-sm text-slate-500">Select a policy above to see its details.</p>
        </div>
      )}

      {/* ================================================================ */}
      {/* QUINTILE TARGETING                                                */}
      {/* ================================================================ */}
      <QuintileTargetingChart data={data} scenarioKey={scenario} />
    </div>
  );
}
