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
  getQuintileBreakdown,
  getFuelPoverty,
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
  { id: "quintile", label: "Income quintile" },
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

function NumberInput({ label, hint, value, onChange }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs font-medium uppercase tracking-[0.06em] text-slate-500">
        {label}
      </span>
      <span className="relative block">
        <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-sm text-slate-400">
          {"£"}
        </span>
        <input
          type="number"
          min="0"
          step="100"
          className="w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-7 pr-3 text-sm font-medium text-slate-800 shadow-sm outline-none transition-colors focus:border-teal-700 focus:ring-2 focus:ring-teal-700/15"
          value={value}
          onChange={(e) => onChange(Math.max(0, Number(e.target.value)))}
        />
      </span>
      {hint ? <span className="text-[11px] leading-4 text-slate-400">{hint}</span> : null}
    </label>
  );
}

function ExampleHousehold({ data, scenario }) {
  const [income, setIncome] = useState(35000);
  const [energyBill, setEnergyBill] = useState(1700);
  const [fuelSpend, setFuelSpend] = useState(1300);
  const [foodSpend, setFoodSpend] = useState(5000);
  const [benefitIncome, setBenefitIncome] = useState(0);

  const params = data?.scenarios?.[scenario]?.params;
  if (!params) return null;

  const energy = energyBill * (params.cap_increase_pct / 100);
  const fuel = fuelSpend * (params.fuel_pct / 100);
  const food = foodSpend * (params.food_increase_pct / 100);
  const uprating = benefitIncome * (params.cpi_increase_pp / 100) * 0.5;
  const total = energy + fuel + food + uprating;
  const pctIncome = income > 0 ? (total / income) * 100 : null;

  const rows = [
    { label: "Higher energy bills", value: energy, color: channelColors.energy },
    { label: "Higher fuel costs", value: fuel, color: channelColors.fuel },
    { label: "Higher food prices", value: food, color: channelColors.food },
    { label: "Benefit uprating lag", value: uprating, color: channelColors.benefit_uprating_lag },
  ];
  const maxRow = Math.max(...rows.map((r) => r.value), 1);

  return (
    <>
      <div className="border-t border-slate-200 pt-10">
        <SectionHeading
          title="What would this mean for a household like yours?"
          description="Enter your household's details to see the estimated extra cost under the selected scenario, using the same shock parameters as the full microsimulation. Set a field to zero if it doesn't apply."
        />
      </div>
      <div className="section-card">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <NumberInput label="Net income / yr" value={income} onChange={setIncome} />
          <NumberInput
            label="Energy bill / yr"
            hint={`UK typical ~${formatCurrency(1663)} (Ofgem cap)`}
            value={energyBill}
            onChange={setEnergyBill}
          />
          <NumberInput
            label="Petrol & diesel / yr"
            hint={`UK typical ~${formatCurrency(1300)}; 0 if no car`}
            value={fuelSpend}
            onChange={setFuelSpend}
          />
          <NumberInput
            label="Food spend / yr"
            hint={`UK typical ~${formatCurrency(5000)}`}
            value={foodSpend}
            onChange={setFoodSpend}
          />
          <NumberInput
            label="CPI-linked benefits / yr"
            hint="UC, child benefit, PIP…; 0 if none"
            value={benefitIncome}
            onChange={setBenefitIncome}
          />
        </div>

        <div className="mt-8 grid items-center gap-8 md:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
          <div
            className="rounded-2xl px-6 py-6"
            style={{ backgroundColor: colors.primary[50] }}
          >
            <div className="text-xs font-medium uppercase tracking-[0.08em]" style={{ color: colors.primary[700] }}>
              Estimated extra cost for your household
            </div>
            <div className="mt-2 flex items-baseline gap-3">
              <span className="text-5xl font-bold tracking-tight" style={{ color: colors.primary[900] }}>
                {formatCurrency(total)}
              </span>
              <span className="text-lg font-semibold" style={{ color: colors.primary[700] }}>
                /yr
              </span>
            </div>
            {pctIncome != null ? (
              <div className="mt-2 text-sm" style={{ color: colors.primary[800] }}>
                {pctIncome.toFixed(1)}% of your net income
              </div>
            ) : null}
          </div>

          <div className="space-y-3">
            {rows.map((r) => (
              <div key={r.label} className="grid grid-cols-[170px_1fr_80px] items-center gap-3">
                <span className="flex items-center gap-2 text-sm text-slate-600">
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full"
                    style={{ backgroundColor: r.color }}
                  />
                  {r.label}
                </span>
                <span className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                  <span
                    className="block h-full rounded-full transition-all"
                    style={{
                      width: `${(r.value / maxRow) * 100}%`,
                      backgroundColor: r.color,
                    }}
                  />
                </span>
                <span className="text-right text-sm font-semibold text-slate-800">
                  {r.value > 0 ? `+${formatCurrency(r.value)}` : "—"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function DistributionalBreakdown({ quintileData, countryData, tenureData, hhTypeData }) {
  const [view, setView] = useState("quintile");

  const labelled = (rows, key, labels) =>
    rows
      .map((r) => ({ ...r, label: labels[r[key]] || r[key] }))
      .sort((a, b) => (b.avg_cost || 0) - (a.avg_cost || 0));

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

  // Quintile uses vertical stacked bars; everything else uses horizontal stacked bars
  const isVertical = view === "quintile";

  const labelKey = "label";
  let chartData, chartHeight;
  if (view === "quintile") {
    chartData = quintileData;
    chartHeight = 380;
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
          description="Who bears the cost: average household cost in 2027-28, stacked by channel, split by income quintile (Q1 = lowest income), country, housing tenure, or household type. Higher-income households pay more in cash terms, but as a share of income the burden falls hardest on the lowest quintiles."
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
  const quintileData = getQuintileBreakdown(data, scenario);
  const fuelPoverty = getFuelPoverty(data, scenario);
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
    const meanHHSize = data?.baseline?.mean_household_size;
    if (!low || !central || !severe || !nHH || !meanHHSize) return [];
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
        metric: "Pushed into poverty in 2027-28",
        external: [
          { label: "NIESR: 200,000 additional UK households", url: "https://www.gbnews.com/money/iran-war-british-households-poverty-cost-of-living" },
        ],
        ours: `${formatCount(low.summary.n_pushed_into_poverty)} people (low) to ${formatCount(central.summary.n_pushed_into_poverty)} people (central)`,
        note: `NIESR counts households; we count people, so our low scenario (${formatCount(low.summary.n_pushed_into_poverty)} people \u2248 ${formatCount(Math.round(low.summary.n_pushed_into_poverty / meanHHSize))} households) is close to NIESR's estimate.`,
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
        description="Choose a conflict path to see its estimated impact on UK households over the 2027-28 tax year. Each scenario applies a different magnitude of energy, fuel, food, and inflation shock, sustained for 12 months."
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
            Additional cost per household in 2027-28 under {scenarioLabel.toLowerCase()}
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
            Percentage point increase in the 10%-of-income fuel poverty indicator in 2027-28
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
            People pushed below 60% of median equivalised income in 2027-28
          </div>
        </div>
      </div>

      {/* ================================================================ */}
      {/* EXAMPLE HOUSEHOLD                                                 */}
      {/* ================================================================ */}
      <ExampleHousehold data={data} scenario={scenario} />

      {/* ================================================================ */}
      {/* CHANNEL DECOMPOSITION                                             */}
      {/* ================================================================ */}
      <div className="border-t border-slate-200 pt-10">
        <SectionHeading
          title="Cost breakdown by transmission channel"
          description="How the average household cost in 2027-28 splits across the four routes the shock reaches households: energy bills (via the Ofgem cap), fuel at the pump, food prices (energy is a major input cost), and the real-value loss on CPI-linked benefits until the next uprating — a loss that only affects benefit-recipient households."
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
      {/* DISTRIBUTIONAL IMPACT (decile / country / tenure / hh type)        */}
      {/* ================================================================ */}
      <DistributionalBreakdown
        quintileData={quintileData}
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
