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

function ExampleHousehold({ data, decileData }) {
  const [decile, setDecile] = useState(3);
  const [hasBenefits, setHasBenefits] = useState(true);
  const [hasCar, setHasCar] = useState(true);

  const baselineRow = data?.baseline?.by_decile?.find((d) => d.decile === decile);
  const scenarioRow = decileData.find((d) => d.decile === decile);
  if (!baselineRow || !scenarioRow) return null;

  const energy = scenarioRow.energy;
  const fuel = hasCar ? scenarioRow.fuel : 0;
  const food = scenarioRow.food;
  const uprating = hasBenefits ? scenarioRow.benefit_uprating_lag : 0;
  const total = energy + fuel + food + uprating;
  const pctIncome = (total / baselineRow.mean_net_income) * 100;

  const rows = [
    { label: "Higher energy bills", value: energy },
    { label: "Higher fuel costs", value: fuel },
    { label: "Higher food prices", value: food },
    { label: "Lost real benefit value (uprating lag)", value: uprating },
  ];

  return (
    <>
      <div className="border-t border-slate-200 pt-10">
        <SectionHeading
          title="What would this mean for a household like yours?"
          description="Pick an income decile and household characteristics to see the estimated 2026-27 cost for a typical household in that group under the selected scenario. Figures are decile averages from the microsimulation — an individual household's cost depends on its actual energy use, mileage, and benefit income."
        />
      </div>
      <div className="section-card">
        <div className="flex flex-wrap items-center gap-6">
          <label className="flex items-center gap-2 text-sm text-slate-600">
            Income decile (1 = lowest income)
            <select
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
              value={decile}
              onChange={(e) => setDecile(Number(e.target.value))}
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={hasBenefits}
              onChange={(e) => setHasBenefits(e.target.checked)}
            />
            Receives CPI-linked benefits (UC, child benefit, PIP, etc.)
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={hasCar}
              onChange={(e) => setHasCar(e.target.checked)}
            />
            Runs a car
          </label>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <div>
            <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
              Estimated extra cost in 2026-27
            </div>
            <div className="mt-2 text-4xl font-bold tracking-tight" style={{ color: colors.primary[800] }}>
              {formatCurrency(total)}
            </div>
            <div className="mt-1 text-sm text-slate-500">
              {pctIncome.toFixed(1)}% of this group{"’"}s average net income
              ({formatCurrency(baselineRow.mean_net_income)}/yr); typical baseline energy
              bill {formatCurrency(baselineRow.mean_energy_spend)}/yr
            </div>
          </div>
          <div>
            <table className="data-table">
              <tbody>
                {rows.map((r) => (
                  <tr key={r.label}>
                    <td className="text-slate-600">{r.label}</td>
                    <td className="text-right font-medium">
                      {r.value > 0 ? `+${formatCurrency(r.value)}` : "—"}
                    </td>
                  </tr>
                ))}
                <tr>
                  <td className="font-semibold text-slate-800">Total</td>
                  <td className="text-right font-semibold" style={{ color: colors.primary[800] }}>
                    +{formatCurrency(total)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}

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
          description="Who bears the cost. Each bar shows the average household cost in 2026-27, stacked by transmission channel, for a different slice of the population: income decile (1 = lowest income, 10 = highest), UK region, country, housing tenure, or household type. Higher-income households pay more in cash terms because they consume more energy and fuel — but as a share of income the burden falls hardest on the lowest deciles, who spend roughly three times as much of their budget on energy. Pensioner and benefit-reliant households also carry the uprating-lag loss that working households avoid."
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

  // External-comparison table: each row is a metric that BOTH a published
  // source and our model put a number on, computed live from the pipeline
  // output so it stays in sync when the data regenerates.
  const comparisonRows = useMemo(() => {
    const scen = (key) => data?.scenarios?.[key];
    const low = scen("low_shock");
    const central = scen("central_shock");
    const severe = scen("severe_shock");
    const nHH = data?.baseline?.n_households_m;
    if (!low || !central || !severe || !nHH) return [];
    const fpMillions = (s) => ((s.summary.fp_rate_shocked_pct / 100) * nHH).toFixed(1);
    return [
      {
        metric: "Extra energy bill per household per year",
        external: [
          { label: `Ofgem (observed): +${formatCurrency(221)} (+13.5%, July 2026 cap)`, url: "https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-july-and-30-september-2026" },
          { label: `JRF: +${formatCurrency(288)} predicted`, url: "https://www.jrf.org.uk/cost-of-living/addressing-the-2026-energy-price-crisis" },
          { label: `Resolution Foundation: ~+${formatCurrency(500)} if rises are sustained`, url: "https://www.resolutionfoundation.org/press-releases/poorest-households-are-set-to-see-inflation-nearly-a-third-higher-than-the-richest/" },
        ],
        ours: `${formatCurrency(low.channel_decomposition.energy_shock)} (low) to ${formatCurrency(central.channel_decomposition.energy_shock)} (central)`,
        note: "Our low scenario matches the observed cap rise; the RF sustained case sits between our low and central.",
      },
      {
        metric: "Households in fuel poverty (10%-of-income indicator)",
        external: [
          { label: "End Fuel Poverty Coalition: ~13m UK households >10% after the July rise (income after housing costs)", url: "https://www.endfuelpoverty.org.uk/government-urged-to-prepare-emergency-energy-bill-support/" },
          { label: "NEA: over 10 million after the July cap rise", url: "https://www.nea.org.uk/about-us/energy-crisis/energy-crisis-timeline/" },
        ],
        ours: `${fpMillions(low)}m (low) to ${fpMillions(central)}m (central)`,
        note: "Definitions differ: our indicator uses net income before housing costs, so our counts are lower than the after-housing-costs campaign figures.",
      },
      {
        metric: "Pushed into poverty in 2026-27",
        external: [
          { label: "NIESR: 200,000 additional UK households", url: "https://www.gbnews.com/money/iran-war-british-households-poverty-cost-of-living" },
        ],
        ours: `${formatCount(low.summary.n_pushed_into_poverty)} people (low) to ${formatCount(central.summary.n_pushed_into_poverty)} people (central)`,
        note: "NIESR counts households; we count people, so our low scenario (~386k people ≈ ~170k households) is close to NIESR's estimate.",
      },
      {
        metric: "Conflict impact on CPI inflation",
        external: [
          { label: "OBR: ~+1pp (CPI to 3% by end-2026 vs 2% anticipated)", url: "https://www.investmentweek.co.uk/news/4526778/obr-warns-iran-conflict-force-uk-inflation-end-2026" },
          { label: "NIESR: +1pp to +3pp (central ~4% CPI, pessimistic ~5%)", url: "https://niesr.ac.uk/blog/possible-effects-uk-inflation-2026-us-iran-conflict" },
          { label: "Bank of England: ~3% Q3, ~3¼% Q4 2026", url: "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026" },
        ],
        ours: `+${low.params.cpi_increase_pp}pp (low), +${central.params.cpi_increase_pp}pp (central), +${severe.params.cpi_increase_pp}pp (high)`,
        note: "Our low matches the OBR/BoE view of the shock as it stands; central and high match NIESR's pessimistic range.",
      },
      {
        metric: "Total household cost (all channels)",
        external: [
          { label: "No published aggregate estimate exists for this metric", url: null },
        ],
        ours: `£${low.summary.total_impact_bn}bn (low) to £${severe.summary.total_impact_bn}bn (high) per year`,
        note: "For scale: the 2022-23 Energy Price Guarantee cost ~£23bn, and ministers ruled out repeating ~£40bn universal support.",
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
        description="Choose a conflict path to see its estimated impact on UK households over the 2026-27 tax year. Each scenario applies a different magnitude of energy, fuel, food, and inflation shock, sustained for 12 months."
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
            Additional cost per household in 2026-27 under {scenarioLabel.toLowerCase()}
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
            Percentage point increase in the 10%-of-income fuel poverty indicator in 2026-27
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
            People pushed below 60% of median equivalised income in 2026-27
          </div>
        </div>
      </div>

      {/* ================================================================ */}
      {/* EXAMPLE HOUSEHOLD                                                 */}
      {/* ================================================================ */}
      <ExampleHousehold data={data} decileData={decileData} />

      {/* ================================================================ */}
      {/* CHANNEL DECOMPOSITION                                             */}
      {/* ================================================================ */}
      <div className="border-t border-slate-200 pt-10">
        <SectionHeading
          title="Cost breakdown by transmission channel"
          description="How the average household cost in 2026-27 splits across the four routes the shock reaches households. Energy: higher gas and electricity bills as the Ofgem price cap passes wholesale prices through. Fuel: petrol and diesel at the pump, scaled by how much each income decile typically spends on motoring. Food: energy is a major input to food production and distribution, so grocery prices follow with a lag. Benefit uprating lag: CPI-linked benefits were fixed from September 2025 prices, so their real value erodes during the shock until the April 2027 uprating — a loss that only affects benefit-recipient households. Direct energy bills are usually the largest channel, but the mix varies by scenario severity."
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
              <col style={{ width: "20%" }} />
              <col style={{ width: "32%" }} />
              <col style={{ width: "22%" }} />
              <col style={{ width: "26%" }} />
            </colgroup>
            <thead>
              <tr>
                <th>Metric</th>
                <th>Published estimates</th>
                <th>Our model</th>
                <th>How they compare</th>
              </tr>
            </thead>
            <tbody>
              {comparisonRows.map((row) => (
                <tr key={row.metric}>
                  <td className="font-medium">{row.metric}</td>
                  <td>
                    <ul className="list-disc pl-4 space-y-1">
                      {row.external.map((e) => (
                        <li key={e.label}>
                          {e.url ? (
                            <a href={e.url} target="_blank" rel="noreferrer" className="underline">{e.label}</a>
                          ) : (
                            <span className="text-slate-500">{e.label}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </td>
                  <td className="font-medium" style={{ color: colors.primary[800] }}>{row.ours}</td>
                  <td className="text-slate-500">{row.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
