"use client";

import { useMemo, useState } from "react";
import { colors, channelColors } from "../lib/colors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import SectionHeading from "./SectionHeading";
import {
  getScenario,
  getDecileBreakdown,
  getFuelPoverty,
  getRegionalBreakdown,
  getCountryBreakdown,
  getChannelDecomposition,
  getHouseholdTypeBreakdown,
} from "../lib/dataHelpers";
import { formatCurrency, formatPct, formatCount } from "../lib/formatters";
import ChartLogo from "./ChartLogo";
import { getScenarioNarrative, getScenarioOptions } from "../lib/scenarioContent";

const AXIS_STYLE = {
  fontSize: 12,
  fill: colors.gray[500],
};

const CHANNEL_LABELS = {
  energy: "Energy",
  fuel: "Fuel",
  food: "Food",
  benefit_uprating_lag: "Benefit uprating lag",
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

function ScenarioSelector({ data, selected, onSelect }) {
  const scenarioOptions = getScenarioOptions(data);
  const active = getScenarioNarrative(selected);
  return (
    <div className="mb-8">
      <div className="flex flex-wrap gap-2">
        {scenarioOptions.map((s) => (
          <button
            key={s.id}
            className={`rounded-full px-5 py-2 text-sm font-medium transition-colors ${
              selected === s.id
                ? "text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
            style={
              selected === s.id
                ? { backgroundColor: colors.primary[800] }
                : undefined
            }
            onClick={() => onSelect(s.id)}
          >
            {s.label}
          </button>
        ))}
      </div>
      {active?.description && (
        <div
          className="mt-4 rounded-2xl border-l-4 bg-slate-50 px-5 py-4 text-[0.9rem] leading-relaxed text-slate-600"
          style={{ borderLeftColor: colors.primary[700] }}
        >
          <span className="font-semibold text-slate-800">{active.selectorLabel}:</span>{" "}
          {active.description}
        </div>
      )}
    </div>
  );
}

const CHANNEL_STACK = [
  { key: "energy", label: "Energy", color: channelColors.energy },
  { key: "fuel", label: "Fuel", color: channelColors.fuel },
  { key: "food", label: "Food", color: channelColors.food },
  { key: "benefit_uprating_lag", label: "Benefit uprating lag", color: channelColors.benefit_uprating_lag },
];

const DIST_VIEWS = [
  { id: "decile", label: "Income decile" },
  { id: "region", label: "Region" },
  { id: "country", label: "Country" },
  { id: "household_type", label: "Household type" },
];

const HH_TYPE_LABELS = {
  COUPLE_NO_CHILDREN: "Couple, no children",
  COUPLE_WITH_CHILDREN: "Couple with children",
  LONE_PARENT: "Lone parent",
  PENSIONER: "Pensioner",
  SINGLE_WORKING_AGE: "Single working age",
};

function DistributionalBreakdown({ decileData, regionalData, countryData, hhTypeData }) {
  const [view, setView] = useState("decile");

  const sortedRegional = useMemo(() => {
    return [...regionalData].sort((a, b) => (b.avg_cost || 0) - (a.avg_cost || 0));
  }, [regionalData]);

  const sortedCountry = useMemo(() => {
    return [...countryData].sort((a, b) => (b.avg_cost || 0) - (a.avg_cost || 0));
  }, [countryData]);

  const sortedHhType = useMemo(() => {
    return [...hhTypeData]
      .map((h) => ({ ...h, label: HH_TYPE_LABELS[h.hh_type] || h.hh_type }))
      .sort((a, b) => (b.avg_cost || 0) - (a.avg_cost || 0));
  }, [hhTypeData]);

  // Decile uses vertical stacked bars; everything else uses horizontal stacked bars
  const isVertical = view === "decile";

  let chartData, labelKey, chartHeight;
  if (view === "decile") {
    chartData = decileData;
    labelKey = "label";
    chartHeight = 380;
  } else if (view === "region") {
    chartData = sortedRegional;
    labelKey = "region";
    chartHeight = 520;
  } else if (view === "country") {
    chartData = sortedCountry;
    labelKey = "country";
    chartHeight = Math.max(300, sortedCountry.length * 80 + 60);
  } else {
    chartData = sortedHhType;
    labelKey = "label";
    chartHeight = Math.max(300, sortedHhType.length * 80 + 60);
  }

  const hasData = chartData.length > 0;

  return (
    <>
      <div className="border-t border-slate-200 pt-10">
        <SectionHeading
          title="Distributional impact"
          description="Average annual household cost decomposed by transmission channel, broken down by income decile, UK region, country, or household type."
        />
      </div>

      {hasData ? (
        <div className="section-card">
          {/* View toggle */}
          <div className="mb-6 flex flex-wrap gap-2">
            {DIST_VIEWS.map((v) => (
              <button
                key={v.id}
                className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                  view === v.id
                    ? "bg-slate-800 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
                onClick={() => setView(v.id)}
              >
                {v.label}
              </button>
            ))}
          </div>

          {isVertical ? (
            <div style={{ height: chartHeight }} className="w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
                  <XAxis
                    dataKey={labelKey}
                    tick={AXIS_STYLE}
                    tickLine={false}
                  />
                  <YAxis
                    tick={AXIS_STYLE}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v) => `\u00A3${v}`}
                  />
                  <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                  <Legend />
                  {CHANNEL_STACK.map((ch) => (
                    <Bar
                      key={ch.key}
                      dataKey={ch.key}
                      name={ch.label}
                      stackId="channels"
                      fill={ch.color}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ height: chartHeight }} className="w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  layout="vertical"
                  margin={{ left: 10, right: 30, top: 10, bottom: 10 }}
                  barSize={24}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} horizontal={false} />
                  <XAxis
                    type="number"
                    tick={AXIS_STYLE}
                    tickLine={false}
                    tickFormatter={(v) => `\u00A3${v}`}
                  />
                  <YAxis
                    type="category"
                    dataKey={labelKey}
                    tick={{ ...AXIS_STYLE, fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                    width={180}
                  />
                  <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                  <Legend />
                  {CHANNEL_STACK.map((ch) => (
                    <Bar
                      key={ch.key}
                      dataKey={ch.key}
                      name={ch.label}
                      stackId="channels"
                      fill={ch.color}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          <ChartLogo />
        </div>
      ) : (
        <div className="section-card">
          <p className="text-sm text-slate-500">Distributional breakdown data not yet available.</p>
        </div>
      )}
    </>
  );
}

export default function ScenariosTab({ data }) {
  const [scenario, setScenario] = useState("low_shock");

  const scenarioData = getScenario(data, scenario);
  const decileData = getDecileBreakdown(data, scenario);
  const fuelPoverty = getFuelPoverty(data, scenario);
  const regionalData = getRegionalBreakdown(data, scenario);
  const countryData = getCountryBreakdown(data, scenario);
  const channels = getChannelDecomposition(data, scenario);
  const hhTypeData = getHouseholdTypeBreakdown(data, scenario);
  const scenarioLabel = getScenarioNarrative(scenario)?.selectorLabel || scenario;
  const activeColor = colors.primary[800];

  // Build channel chart data, sorted by cost descending with gradient colors
  const SORTED_FILLS = [
    colors.primary[900],
    colors.primary[700],
    colors.primary[500],
    colors.gray[500],
    colors.gray[300],
  ];
  const channelChartData = useMemo(() => {
    if (!channels || typeof channels !== "object") return [];
    return Object.entries(channels)
      .map(([key, value]) => ({
        channel: CHANNEL_LABELS[key] || key,
        cost: typeof value === "number" ? value : value?.avg_cost || 0,
      }))
      .sort((a, b) => b.cost - a.cost)
      .map((d, i) => ({ ...d, fill: SORTED_FILLS[i] || colors.gray[400] }));
  }, [channels]);

  return (
    <div className="space-y-10">

      {/* Scenario selector */}
      <SectionHeading
        title="Select scenario"
        description="Choose a scenario to see its estimated impact on UK households."
      />
      <ScenarioSelector data={data} selected={scenario} onSelect={setScenario} />

      {/* ================================================================ */}
      {/* HEADLINE METRICS                                                  */}
      {/* ================================================================ */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="metric-card">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            Avg household cost
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            {scenarioData?.avg_household_cost != null
              ? formatCurrency(scenarioData.avg_household_cost)
              : "--"}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            Annual additional cost per household under {scenarioLabel.toLowerCase()}
          </div>
        </div>
        <div className="metric-card">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            Fuel poverty increase
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight" style={{ color: colors.primary[800] }}>
            {fuelPoverty?.increase_pp != null
              ? `+${formatPct(fuelPoverty.increase_pp, 1)}`
              : "--"}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            Percentage point increase in fuel poverty rate
          </div>
        </div>
        <div className="metric-card">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            Poverty increase
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight" style={{ color: colors.primary[800] }}>
            {scenarioData?.poverty_increase != null
              ? `+${formatCount(scenarioData.poverty_increase)}`
              : "--"}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            Additional households pushed into poverty
          </div>
        </div>
      </div>

      {/* ================================================================ */}
      {/* CHANNEL DECOMPOSITION                                             */}
      {/* ================================================================ */}
      <div className="border-t border-slate-200 pt-10">
        <SectionHeading
          title="Cost breakdown by transmission channel"
          description="How the net household cost decomposes across energy bills, fuel prices, food prices, and benefit uprating lag."
        />
      </div>

      {channelChartData.length > 0 ? (
        <div className="section-card">
          <div className="h-[380px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={channelChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
                <XAxis
                  dataKey="channel"
                  tick={AXIS_STYLE}
                  tickLine={false}
                />
                <YAxis
                  tick={AXIS_STYLE}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `\u00A3${v}`}
                />
                <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                <Bar dataKey="cost" name="Avg household cost" radius={[6, 6, 0, 0]}>
                  {channelChartData.map((entry, idx) => (
                    <rect key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <ChartLogo />
        </div>
      ) : (
        <div className="section-card">
          <p className="text-sm text-slate-500">Channel decomposition data not yet available.</p>
        </div>
      )}

      {/* ================================================================ */}
      {/* DISTRIBUTIONAL IMPACT (decile / region / country / hh type)       */}
      {/* ================================================================ */}
      <DistributionalBreakdown
        decileData={decileData}
        regionalData={regionalData}
        countryData={countryData}
        hhTypeData={hhTypeData}
      />

      {/* ================================================================ */}
      {/* COMPARISON TO OTHER ESTIMATES                                    */}
      {/* ================================================================ */}
      <details className="section-card">
        <summary className="cursor-pointer list-none">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="flex items-center gap-2 text-xl font-semibold tracking-tight text-slate-900">
                <span className="details-triangle text-sm text-slate-500">▶</span>
                <span>Comparison to other estimates</span>
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                How our modelled numbers compare to published estimates from think tanks,
                government bodies, and analysts for comparable UK energy and cost-of-living shocks.
              </p>
            </div>
          </div>
        </summary>

        <div className="mt-6 overflow-x-auto border-t border-slate-200 pt-5">
          <table className="data-table" style={{ tableLayout: "fixed" }}>
            <colgroup>
              <col style={{ width: "18%" }} />
              <col style={{ width: "18%" }} />
              <col style={{ width: "14%" }} />
              <col style={{ width: "50%" }} />
            </colgroup>
            <thead>
              <tr>
                <th>Source</th>
                <th>Energy bill impact</th>
                <th style={{ textAlign: "right" }}>Inflation</th>
                <th>Key findings</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="font-medium">
                  <a href="https://www.cornwall-insight.com/press/cornwall-insight-comments-on-the-impact-of-the-iran-conflict-on-uk-energy-bills/" target="_blank" rel="noreferrer" className="underline">Cornwall Insight</a>
                </td>
                <td>+{formatCurrency(288)}/yr (July cap)</td>
                <td style={{ textAlign: "right" }}>--</td>
                <td className="text-slate-500">
                  Ofgem cap forecast to rise 18% to {formatCurrency(1929)} from July 2026;
                  wholesale gas prices have doubled since the supply disruption began
                </td>
              </tr>
              <tr>
                <td className="font-medium">
                  <a href="https://economy2030.resolutionfoundation.org/reports/tackling-the-cost-of-living-crunch/" target="_blank" rel="noreferrer" className="underline">Resolution Foundation</a>
                </td>
                <td>+{formatCurrency(500)}/yr; cap to {formatCurrency(1929)}{"\u2013"}{formatCurrency(2050)}</td>
                <td style={{ textAlign: "right" }}>+1pp; food to ~10%</td>
                <td className="text-slate-500">
                  Median household {formatCurrency(480)} worse off. Below-average incomes lose 2.4pp of growth.
                  730k households facing mortgage shock (+{formatCurrency(350)}/month).
                  Social tariff best policy for vulnerable households.
                </td>
              </tr>
              <tr>
                <td className="font-medium">
                  <a href="https://www.endfuelpoverty.org.uk/iran-conflict-pushes-gas-prices-higher-but-the-risk-for-bills-lies-ahead/" target="_blank" rel="noreferrer" className="underline">End Fuel Poverty Coalition</a>
                </td>
                <td>13m HH in fuel poverty</td>
                <td style={{ textAlign: "right" }}>--</td>
                <td className="text-slate-500">
                  If bills increase from July, ~13m households could spend {">"}10% of income on energy;
                  ~5m spending {">"}20%; heating oil already up 39% year-on-year
                </td>
              </tr>
              <tr>
                <td className="font-medium">
                  <a href="https://niesr.ac.uk/blog/impact-middle-east-conflict-uk-energy-prices-and-fiscal-policy" target="_blank" rel="noreferrer" className="underline">NIESR</a>
                </td>
                <td>--</td>
                <td style={{ textAlign: "right" }}>+0.7pp</td>
                <td className="text-slate-500">
                  NiGEM model: oil +30%, gas +50% sustained for 1 year; CPI +0.7pp;
                  interest rates +0.8pp; GDP -0.3% in 2027
                </td>
              </tr>
              <tr>
                <td className="font-medium">
                  <a href="https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/may-2026" target="_blank" rel="noreferrer" className="underline">Bank of England</a>
                </td>
                <td>--</td>
                <td style={{ textAlign: "right" }}>3-3.5%</td>
                <td className="text-slate-500">
                  CPI likely 3-3.5% in Q2-Q3 2026 due to higher energy prices;
                  oil up ~20%, gas up ~50% since the supply disruption began; rate cuts now unlikely
                </td>
              </tr>
              <tr>
                <td className="font-medium">
                  <a href="https://obr.uk/efo/economic-and-fiscal-outlook-march-2026/" target="_blank" rel="noreferrer" className="underline">OBR</a>
                </td>
                <td>--</td>
                <td style={{ textAlign: "right" }}>+1pp</td>
                <td className="text-slate-500">
                  Sustained energy spike could add 1pp to UK inflation in 2026;
                  UK economy could face {"\u201c"}very significant{"\u201d"} impact; growth forecast cut to 0.7%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
