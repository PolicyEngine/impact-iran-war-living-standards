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
  getCountryBreakdown,
  getTenureBreakdown,
  getChannelDecomposition,
  getHouseholdTypeBreakdown,
  getUpratingInputs,
} from "../lib/dataHelpers";
import { formatCurrency, formatCount } from "../lib/formatters";
import ChartLogo from "./ChartLogo";
import { getScenarioNarrative, getScenarioOptions } from "../lib/scenarioContent";

const AXIS_STYLE = {
  fontSize: 12,
  fill: colors.gray[500],
};

const CHANNEL_LABELS = {
  energy: "Energy spending",
  fuel: "Fuel",
  food: "Food",
  benefit_uprating_shortfall: "Uprating compensation shortfall",
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
  const active = getScenarioNarrative(selected, data);
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
  { key: "energy", label: "Energy spending", color: channelColors.energy },
  { key: "fuel", label: "Fuel", color: channelColors.fuel },
  { key: "food", label: "Food", color: channelColors.food },

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
  const [fuelSpend, setFuelSpend] = useState(1030);
  const [foodSpend, setFoodSpend] = useState(3666);
  const [benefitIncome, setBenefitIncome] = useState(0);

  const scenarioData = data?.scenarios?.[scenario];
  const params = scenarioData?.params;
  if (!params) return null;

  const energy = energyBill * (params.cap_increase_pct / 100);
  const fuel = fuelSpend * (params.fuel_pct / 100);
  const food = foodSpend * (params.food_increase_pct / 100);
  // The uprating shortfall is what an immediate uprating would pay, not a
  // fourth cost — adding it would count the same price shock twice. It is
  // sized on the residual CPI addition that September 2026 CPI misses, read
  // from the results file so it cannot drift from the pipeline.
  const upr = getUpratingInputs(scenarioData);
  const upratingShortfall = upr
    ? benefitIncome * (upr.residual / 100) * upr.factor
    : null;
  const total = energy + fuel + food;
  const pctIncome = income > 0 ? (total / income) * 100 : null;

  const rows = [
    { label: "Higher energy spending", value: energy, color: channelColors.energy },
    { label: "Higher fuel costs", value: fuel, color: channelColors.fuel },
    { label: "Higher food prices", value: food, color: channelColors.food },
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
            hint={`UK typical ~${formatCurrency(1030)}; 0 if no car`}
            value={fuelSpend}
            onChange={setFuelSpend}
          />
          <NumberInput
            label="Food spend / yr"
            hint={`UK typical ~${formatCurrency(3666)}`}
            value={foodSpend}
            onChange={setFoodSpend}
          />
          <NumberInput
            label="CPI-linked benefit rates / yr"
            hint="Your maximum rates before earnings or housing adjustments: UC standard allowance, child and carer elements, child benefit, PIP, DLA, carer's allowance. Not your UC payment; 0 if none"
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
            {benefitIncome > 0 && !upr ? (
              <div className="mt-4 border-t pt-3 text-xs leading-5" style={{ borderColor: colors.primary[200], color: colors.primary[800] }}>
                The benefit uprating figures are unavailable in this results file.
              </div>
            ) : null}
            {upr && upratingShortfall > 0 ? (
              <div className="mt-4 border-t pt-3 text-xs leading-5" style={{ borderColor: colors.primary[200], color: colors.primary[800] }}>
                Uprating your CPI-linked rates immediately would raise them by up to
                about <strong>{formatCurrency(upratingShortfall)}</strong> a year. April
                2027 uprating is set from September 2026 CPI, which already carries
                about {upr.captured}pp of the shock; the
                remaining {upr.residual}pp is not indexed
                until April 2028. That is why the cost above is the full price rise,
                rather than the price rise plus a separate uprating loss. This is a
                maximum-rate illustration: your actual award can change by less once
                earnings, housing costs and the benefit cap apply, or by more if the
                uprating brings you into entitlement. The population figures run the
                full benefit rules at each scenario&apos;s residual.
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
  // Cash or share of income. The share is each channel over the group's mean
  // net income — a ratio of means, which unlike the mean-of-ratios can be
  // decomposed by channel and so can be stacked.
  const [measure, setMeasure] = useState("cash");
  const asShare = measure === "share";

  // A row is convertible only with a finite positive denominator. Returning
  // the row unchanged, as an earlier version did, left pound values to be
  // formatted as percentages: energy £100 rendered as "100.00%", and a
  // denominator of -1 as "-10000.00%" (#57 review A1).
  const canShare = (r) =>
    typeof r.mean_net_income === "number" &&
    Number.isFinite(r.mean_net_income) &&
    r.mean_net_income > 0;

  const shareable = (rows) => rows.every(canShare);

  const toShare = (rows) =>
    rows.map((r) => ({
      ...r,
      energy: (r.energy / r.mean_net_income) * 100,
      fuel: (r.fuel / r.mean_net_income) * 100,
      food: (r.food / r.mean_net_income) * 100,
    }));

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

  // If any row lacks a usable denominator, stay in cash rather than publish
  // pounds labelled as percentages.
  const shareAvailable = chartData.length > 0 && shareable(chartData);
  const showingShare = asShare && shareAvailable;
  if (showingShare) chartData = toShare(chartData);

  const hasData = chartData.length > 0;

  return (
    <>
      <div className="border-t border-slate-200 pt-10">
        <SectionHeading
          title="Distributional impact"
          description="Who bears the cost in 2027-28, stacked by channel and split by income quintile (Q1 = lowest income), country, housing tenure, or household type. Switch between cash cost and share of income: higher-income households pay more in cash, but the burden is far heavier as a share of income at the bottom. The share is each channel over the group's mean net income."
        />
      </div>

      {hasData ? (
        <div className="section-card">
          {/* View toggle, and cash vs share of income */}
          <div className="mb-6 flex flex-wrap items-center gap-2">
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
            <span className="mx-1 h-5 w-px bg-slate-300" aria-hidden="true" />
            {[
              { id: "cash", label: "Cash cost" },
              { id: "share", label: "Share of income" },
            ].map((m) => (
              <button
                key={m.id}
                disabled={m.id === "share" && !shareAvailable}
                title={
                  m.id === "share" && !shareAvailable
                    ? "Share of income is unavailable: this breakdown has no usable income figure"
                    : undefined
                }
                className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                  m.id === "share" && !shareAvailable
                    ? "cursor-not-allowed bg-slate-100 text-slate-400"
                    : (showingShare ? "share" : "cash") === m.id
                      ? "bg-slate-800 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
                onClick={() => setMeasure(m.id)}
              >
                {m.label}
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
                    tickFormatter={(v) =>
                      showingShare ? `${v.toFixed(1)}%` : `\u00A3${v}`
                    }
                  />
                  <Tooltip
                    content={
                      <CustomTooltip
                        formatter={(v) =>
                          showingShare ? `${v.toFixed(2)}%` : formatCurrency(v)
                        }
                      />
                    }
                  />
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
                    tickFormatter={(v) => (showingShare ? `${v.toFixed(1)}%` : `\u00A3${v}`)}
                  />
                  <YAxis
                    type="category"
                    dataKey={labelKey}
                    tick={{ ...AXIS_STYLE, fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                    width={180}
                  />
                  <Tooltip content={<CustomTooltip formatter={(v) => (showingShare ? `${v.toFixed(2)}%` : formatCurrency(v))} />} />
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
  const preConflict = data?.metadata?.pre_conflict_baseline;
  // Every field the baseline callout renders. A missing one would publish a
  // blank or NaN rather than failing, so the block is omitted instead (#54).
  // Presence is not enough: a present but invalid value still publishes
  // "£oops", "NaNp" or "2027-271" (#54 re-review A2). Numbers must be finite
  // and positive, the period a non-blank string, the year a real integer.
  const isPositiveNumber = (value) =>
    typeof value === "number" && Number.isFinite(value) && value > 0;
  const baselineCalloutReady =
    [
      preConflict?.energy_price_cap_old_basis_gbp,
      preConflict?.energy_price_cap_new_basis_gbp,
      preConflict?.petrol_pence_per_litre,
      preConflict?.diesel_pence_per_litre,
    ].every(isPositiveNumber) &&
    typeof preConflict?.pump_price_period === "string" &&
    preConflict.pump_price_period.trim() !== "" &&
    typeof preConflict?.energy_cap_period === "string" &&
    preConflict.energy_cap_period.trim() !== "" &&
    // A plausible four-digit year: Number.isInteger alone renders "0-",
    // "99-0" and "10000-001" (#54 re-review A2).
    Number.isInteger(data?.year) &&
    data.year >= 1000 &&
    data.year <= 9999;
  const [scenario, setScenario] = useState("low_shock");

  const scenarioData = getScenario(data, scenario);
  // Poverty rate before and after the shock, on the anchored HBAI BHC basis.
  const povertySummary = data?.scenarios?.[scenario]?.summary;
  const povertyBaseline = povertySummary?.poverty_rate_baseline_pct;
  const povertyShocked = povertySummary?.below_anchored_line_shocked_pct;
  const quintileData = getQuintileBreakdown(data, scenario);
  const countryData = getCountryBreakdown(data, scenario);
  const tenureData = getTenureBreakdown(data, scenario);
  const channels = getChannelDecomposition(data, scenario);
  const hhTypeData = getHouseholdTypeBreakdown(data, scenario);

  // External-comparison table: each row is a metric that BOTH a published
  // source and our model put a number on, computed live from the pipeline
  // output so it stays in sync when the data regenerates.
  const comparisonRows = useMemo(() => {
    const observed = data?.metadata?.pre_conflict_baseline;
    // Omitted, not NaN, if an older results file lacks the household count.
    const householdsPart = (sc) =>
      Number.isFinite(sc.summary?.n_households_newly_below_anchored_line)
        ? `${formatCount(sc.summary.n_households_newly_below_anchored_line)} households, `
        : "";
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
        ours: `${formatCurrency(low.channel_decomposition.energy_shock)} (near current prices) to ${formatCurrency(central.channel_decomposition.energy_shock)} (sustained escalation)`,
        note: "Our near-current-prices scenario is anchored to the observed cap rise; the Resolution Foundation sustained case sits between it and sustained escalation.",
      },
      {
        metric: "Newly below the anchored poverty line in 2027-28",
        external: [
          { label: "NIESR Economic Outlook, Spring 2026: ~200,000 additional households in absolute poverty", url: "https://niesr.ac.uk/reports/economic-outlook-spring-2026" },
        ],
        ours: `${householdsPart(low)}${formatCount(low.summary.n_pushed_into_poverty)} people (near current prices) to ${householdsPart(central)}${formatCount(central.summary.n_pushed_into_poverty)} people (sustained escalation)`,
        note: "Context, not validation: the two are not comparable. NIESR counts households below an absolute line at 60% of 2023-24 median income after housing costs, from a model of an oil-price shock. We count below a line at 60% of the 2027-28 pre-shock median income before housing costs, after netting modelled energy, fuel and food costs off income. The income concept, base year, housing-cost treatment and mechanism all differ.",
      },
      {
        metric: "CPI addition implied by scenario prices (not a forecast)",
        external: [
          { label: "OBR (David Miles, Treasury Committee, 10 March 2026): prices about 1% higher by end-2026, inflation nearer 3% than 2%, if that day's energy prices persisted", url: "https://committees.parliament.uk/oralevidence/17299/html/" },
          { label: "NIESR: total 2026 CPI of ~3% (optimistic), ~4% (central), ~5% (pessimistic)", url: "https://niesr.ac.uk/blog/possible-effects-uk-inflation-2026-us-iran-conflict" },
          { label: "Bank of England: total CPI ~3% Q3, ~3¼% Q4 2026", url: "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026" },
        ],
        ours: `+${low.params.cpi_increase_pp}pp (near current prices), +${central.params.cpi_increase_pp}pp (sustained escalation), +${severe.params.cpi_increase_pp}pp (severe escalation)`,
        note: `These are not CPI forecasts: each is the addition that scenario's own energy, fuel and food prices imply, and it is used only to size the benefit uprating gap and the accelerated-uprating option, never the household cost. ${getUpratingInputs(central) && Number.isFinite(observed?.observed_energy_rise_by_sept_2026_pct) && Number.isFinite(observed?.observed_fuel_rise_by_sept_2026_pct) ? `Observed prices are energy +${observed.observed_energy_rise_by_sept_2026_pct}% (July cap) and fuel +${observed.observed_fuel_rise_by_sept_2026_pct}% (mid-September pumps), close to the near-current-prices scenario. The latest ONS indices put the conflict's contribution to the annual CPI rate at about ${central.cpi_captured_by_sept_2026_pp}pp (August data, a proxy until the September figures on 21 October). ` : ""}Sustained escalation assumes energy +${central.params.cap_increase_pct}% and fuel +${central.params.fuel_pct}%, well beyond that. Our figures are additions to CPI against a no-conflict path. The OBR's is also an addition, conditional on 10 March energy prices persisting; near current prices (+${low.params.cpi_increase_pp}pp) is close to it. NIESR and the Bank of England publish total CPI rates, not additions: against a roughly 2% pre-conflict expectation, which is our assumption rather than theirs, NIESR's totals imply about +1pp to +3pp. Each figure is the first-round effect of that scenario's own energy, fuel and food price rises on ONS 2026 basket weights: a price-level effect over the stress-test year, not a floor on annual inflation, which also depends on timing, second-round effects and demand. For sustained escalation that effect is ${central.first_round_floor_pp}pp, just above the +1pp to +3pp we derive from NIESR's totals, because its price rises are larger. The severe escalation figure is a judgemental tail-risk assumption rather than a published UK figure, extrapolated from the Oxford Economics escalation case, which reports a 5.8% peak in world CPI with no stated equation linking that to a UK addition. Other severe published scenarios exist on a total-CPI basis and are not directly comparable with an addition.`,
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
        title="Select a scenario"
        description="These are stress tests, not forecasts: none is a prediction of what will happen. Near current prices assumes energy and fuel stay close to their observed rises, with a judgement for food, for all of 2027-28; the two escalation paths assume prices rise well beyond them. Choose a path to see its estimated impact on UK households over the 2027-28 tax year. Each applies a different magnitude of energy, fuel, food and inflation shock, sustained for 12 months."
      />
      <ScenarioSelector data={data} selected={scenario} onSelect={setScenario} />

      {/* What each percentage is measured FROM, and applied TO. The two
          channels use different reference periods, so state both (#42).
          Rendered only when every field is present: optional chaining stops
          an exception but would still publish "£ on…" or "NaNp a litre"
          (#54 review A2). */}
      {baselineCalloutReady && (
      <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
        <div className="font-semibold text-slate-900">
          What the percentages are measured from
        </div>
        <dl className="mt-3 space-y-2">
          <div className="sm:flex sm:gap-3">
            <dt className="shrink-0 font-medium text-slate-700 sm:w-40">
              Energy spending
            </dt>
            <dd>
              measured from each household&apos;s own modelled gas and electricity
              spending at pre-conflict levels ({preConflict?.energy_cap_period}).
              For context only, Ofgem&apos;s published cap for that period was{" "}
              {`£${preConflict?.energy_price_cap_old_basis_gbp?.toLocaleString("en-GB")} on`}{" "}
              the typical-consumption basis then in use; the &pound;
              {preConflict?.energy_price_cap_new_basis_gbp?.toLocaleString("en-GB")}{" "}
              like-for-like figure on the basis Ofgem adopted in July is{" "}
              <em>inferred by this study</em>, not published. No cap value enters the
              calculation.
            </dd>
          </div>
          <div className="sm:flex sm:gap-3">
            <dt className="shrink-0 font-medium text-slate-700 sm:w-40">
              Fuel prices
            </dt>
            <dd>
              measured from a <strong>different period</strong> &mdash;{" "}
              {preConflict?.pump_price_period} &mdash; at{" "}
              {Math.round(preConflict?.petrol_pence_per_litre)}p a litre for petrol
              and {Math.round(preConflict?.diesel_pence_per_litre)}p for diesel.
            </dd>
          </div>
          <div className="sm:flex sm:gap-3">
            <dt className="shrink-0 font-medium text-slate-700 sm:w-40">
              Applied to
            </dt>
            <dd>
              the whole of <strong>{data.year}-{String((data.year + 1) % 100).padStart(2, "0")}</strong>, as a flat annual amount. No
              time path, quarterly profile or shock duration is modelled, so a
              scenario that a source describes as a few months of disruption is
              being held for twelve.
            </dd>
          </div>
        </dl>
      </div>
      )}

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
            Additional cost per household in 2027-28 under the{" "}
            {getScenarioNarrative(scenario)?.shortLabel || scenario} scenario
          </div>
        </div>
        <div className="metric-card">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            Newly below the anchored poverty line
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight" style={{ color: colors.primary[800] }}>
            {scenarioData?.poverty_increase != null
              ? `+${formatCount(scenarioData.poverty_increase)}`
              : "--"}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            People pushed below the baseline poverty line in 2027-28 once modelled
            costs are netted off income. The line is HBAI (Households Below Average
            Income) before housing costs, held at its pre-shock level &mdash; an
            anchored threshold.
          </div>
        </div>
        <div className="metric-card">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            Poverty rate
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight" style={{ color: colors.primary[800] }}>
            {povertyBaseline != null && povertyShocked != null
              ? `+${(povertyShocked - povertyBaseline).toFixed(2)}pp`
              : "--"}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            Change in the share of people below the poverty line once modelled costs
            are netted off income
            {povertyBaseline != null && povertyShocked != null
              ? ` (${povertyBaseline.toFixed(2)}% to ${povertyShocked.toFixed(2)}%; the modelled baseline level is above DWP's published rate, so the change is the more reliable figure)`
              : ""}
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
          description="How the average household cost in 2027-28 splits across the three routes through which the shock reaches households: energy spending, fuel at the pump, and food prices (energy is a major input cost). The uprating compensation shortfall is reported separately rather than as a fourth cost. April 2027 uprating is set from September 2026 CPI, which already carries part of the shock; no offset arrives during the shock year for the residual, so the household's loss is the price rise itself. The shortfall is the size of the compensation an immediate uprating would deliver, and is what the accelerated-uprating policy pays."
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
      {/* DISTRIBUTIONAL IMPACT (quintile / country / tenure / hh type)        */}
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
