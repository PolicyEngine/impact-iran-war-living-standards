"use client";

import { useMemo, useState } from "react";
import { colors, channelColors } from "../lib/colors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
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
  getTenureBreakdown,
  getChannelDecomposition,
  getHouseholdTypeBreakdown,
} from "../lib/dataHelpers";
import { formatCurrency, formatCount } from "../lib/formatters";
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

// Channel chart bar fills, darkest for the largest cost
const SORTED_FILLS = [
  colors.primary[900],
  colors.primary[700],
  colors.primary[500],
  colors.gray[500],
  colors.gray[300],
];

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
  { id: "tenure", label: "Tenure" },
  { id: "household_type", label: "Household type" },
];

const HH_TYPE_LABELS = {
  COUPLE_NO_CHILDREN: "Couple, no children",
  COUPLE_WITH_CHILDREN: "Couple with children",
  LONE_PARENT: "Lone parent",
  SINGLE_PENSIONER: "Single pensioner",
  COUPLE_PENSIONER: "Pensioner couple",
  SINGLE_WORKING_AGE: "Single working age",
};

const REGION_LABELS = {
  EAST_MIDLANDS: "East Midlands",
  EAST_OF_ENGLAND: "East of England",
  LONDON: "London",
  NORTH_EAST: "North East",
  NORTH_WEST: "North West",
  SOUTH_EAST: "South East",
  SOUTH_WEST: "South West",
  WEST_MIDLANDS: "West Midlands",
  YORKSHIRE: "Yorkshire and the Humber",
  SCOTLAND: "Scotland",
  WALES: "Wales",
  NORTHERN_IRELAND: "Northern Ireland",
  ENGLAND: "England",
};

const TENURE_LABELS = {
  RENT_FROM_COUNCIL: "Council rent",
  RENT_FROM_HA: "Housing association rent",
  RENT_PRIVATELY: "Private rent",
  OWNED_OUTRIGHT: "Owned outright",
  OWNED_WITH_MORTGAGE: "Owned with mortgage",
};

function DistributionalBreakdown({ decileData, regionalData, countryData, tenureData, hhTypeData }) {
  const [view, setView] = useState("decile");

  const labelled = (rows, key, labels) =>
    rows
      .map((r) => ({ ...r, label: labels[r[key]] || r[key] }))
      .sort((a, b) => (b.avg_cost || 0) - (a.avg_cost || 0));

  const sortedRegional = useMemo(
    () => labelled(regionalData, "region", REGION_LABELS),
    [regionalData]
  );
  const sortedCountry = useMemo(
    () => labelled(countryData, "country", REGION_LABELS),
    [countryData]
  );
  const sortedTenure = useMemo(
    () => labelled(tenureData, "tenure", TENURE_LABELS),
    [tenureData]
  );
  const sortedHhType = useMemo(
    () => labelled(hhTypeData, "hh_type", HH_TYPE_LABELS),
    [hhTypeData]
  );

  // Decile uses vertical stacked bars; everything else uses horizontal stacked bars
  const isVertical = view === "decile";

  const labelKey = "label";
  let chartData, chartHeight;
  if (view === "decile") {
    chartData = decileData;
    chartHeight = 380;
  } else if (view === "region") {
    chartData = sortedRegional;
    chartHeight = 520;
  } else if (view === "country") {
    chartData = sortedCountry;
    chartHeight = Math.max(300, sortedCountry.length * 80 + 60);
  } else if (view === "tenure") {
    chartData = sortedTenure;
    chartHeight = Math.max(300, sortedTenure.length * 80 + 60);
  } else {
    chartData = sortedHhType;
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
  const tenureData = getTenureBreakdown(data, scenario);
  const channels = getChannelDecomposition(data, scenario);
  const hhTypeData = getHouseholdTypeBreakdown(data, scenario);
  const scenarioLabel = getScenarioNarrative(scenario)?.selectorLabel || scenario;

  // "Our model" figures for the external-comparison table, computed from the
  // pipeline output so they stay in sync when the data regenerates.
  const comparisonRows = useMemo(() => {
    const scen = (key) => data?.scenarios?.[key];
    const low = scen("low_shock");
    const central = scen("central_shock");
    const severe = scen("severe_shock");
    const nHH = data?.baseline?.n_households_m;
    if (!low || !central || !severe || !nHH) return [];
    const energyFuelBn = (s) =>
      ((s.channel_decomposition.energy_shock + s.channel_decomposition.fuel_shock) * nHH) / 1000;
    return [
      {
        source: "Ofgem",
        url: "https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-july-and-30-september-2026",
        energy: `+13% to ${formatCurrency(1663)}/yr (Jul–Sep 2026)`,
        inflation: "--",
        ours: `Low: +${low.params.cap_increase_pct}% cap → ${formatCurrency(low.channel_decomposition.energy_shock)}/hh energy`,
        findings:
          "Price cap rose 13% for Jul–Sep 2026 on conflict-driven wholesale gas prices. " +
          `Figure is on Ofgem’s new typical-consumption basis (≈${formatCurrency(1862)} on the pre-July basis).`,
      },
      {
        source: "Cornwall Insight",
        url: "https://www.cornwall-insight.com/predictions-and-insights-into-the-default-tariff-cap/",
        energy: `${formatCurrency(1700)}/yr forecast (Oct–Dec 2026)`,
        inflation: "--",
        ours: `Low assumes +${low.params.cap_increase_pct}% sustained over 2026-27`,
        findings:
          `Q4 2026 cap forecast cut to ~${formatCurrency(1700)} (new basis) after the ` +
          "electricity VAT removal announced in July 2026",
      },
      {
        source: "Resolution Foundation",
        url: "https://www.resolutionfoundation.org/press-releases/poorest-households-are-set-to-see-inflation-nearly-a-third-higher-than-the-richest/",
        energy: "+£11bn energy + fuel spend in 2026",
        inflation: "3.8% vs 2.9%",
        ours: `Low: £${energyFuelBn(low).toFixed(1)}bn/yr energy + fuel (≈£11bn over the ~8-month 2026 shock period)`,
        findings:
          "Bottom-decile inflation of 3.8% vs 2.9% for the top decile by end-2026 — " +
          "the energy shock hits poorer households ~a third harder",
      },
      {
        source: "NIESR",
        url: "https://niesr.ac.uk/blog/impact-middle-east-conflict-uk-energy-prices-and-fiscal-policy",
        energy: `Cap +20% to ~${formatCurrency(1973)}`,
        inflation: "--",
        ours: `Bracketed by low (+${low.params.cap_increase_pct}%) and central (+${central.params.cap_increase_pct}%)`,
        findings:
          `Projects the conflict wiping out roughly half of fiscal headroom and ~£28bn ` +
          "lower output over two years; recommends a variable (rising-block) price cap and " +
          "benefit-targeted support over universal subsidies",
      },
      {
        source: "Bank of England",
        url: "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026",
        energy: "--",
        inflation: "~3–3.25%",
        ours: `Low CPI adder +${low.params.cpi_increase_pp}pp on a ~2% pre-conflict trend → ~3%`,
        findings:
          "June 2026 projection: CPI a little under 3% in Q3 and a little over 3¼% in " +
          "Q4 2026 on conflict-era energy pricing; Bank Rate held at 3.75%",
      },
      {
        source: "Goldman Sachs",
        url: "https://oilprice.com/Latest-Energy-News/World-News/Goldman-Another-Month-of-Hormuz-Closure-Means-Over-100-Brent-Throughout-2026.html",
        energy: "--",
        inflation: "--",
        ours: `Central scenario anchor: +${central.params.cap_increase_pct}% cap, +${central.params.cpi_increase_pp}pp CPI, ${formatCurrency(central.summary.mean_net_impact)}/hh`,
        findings:
          "One more month of Strait of Hormuz closure would keep Brent above $100/bbl " +
          "through 2026 ($120 Q3, $115 Q4); extreme-adverse case above $115–120",
      },
      {
        source: "Oxford Economics",
        url: "https://www.oxfordeconomics.com/resource/iran-war-scenarios-the-oil-price-that-breaks-parts-of-the-economy/",
        energy: "--",
        inflation: "World CPI 7.7% (prolonged war)",
        ours: `High scenario anchor: +${severe.params.cap_increase_pct}% cap, +${severe.params.cpi_increase_pp}pp CPI, ${formatCurrency(severe.summary.mean_net_impact)}/hh`,
        findings:
          "Prolonged-war scenario implies a global recession and a mild UK contraction; " +
          "UK 2026 growth forecast cut from 1.1% to 0.4%",
      },
    ];
  }, [data]);

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
              ? `+${fuelPoverty.increase_pp.toFixed(1)}pp`
              : "--"}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            Percentage point increase in the 10%-of-income fuel poverty indicator
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
            People pushed below 60% of median equivalised income
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
                    <Cell key={idx} fill={entry.fill} />
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
        tenureData={tenureData}
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
              <col style={{ width: "14%" }} />
              <col style={{ width: "18%" }} />
              <col style={{ width: "12%" }} />
              <col style={{ width: "20%" }} />
              <col style={{ width: "36%" }} />
            </colgroup>
            <thead>
              <tr>
                <th>Source</th>
                <th>Energy bill impact</th>
                <th style={{ textAlign: "right" }}>Inflation</th>
                <th>Our model</th>
                <th>Key findings</th>
              </tr>
            </thead>
            <tbody>
              {comparisonRows.map((row) => (
                <tr key={row.source}>
                  <td className="font-medium">
                    <a href={row.url} target="_blank" rel="noreferrer" className="underline">{row.source}</a>
                  </td>
                  <td>{row.energy}</td>
                  <td style={{ textAlign: "right" }}>{row.inflation}</td>
                  <td className="font-medium" style={{ color: colors.primary[800] }}>{row.ours}</td>
                  <td className="text-slate-500">{row.findings}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
