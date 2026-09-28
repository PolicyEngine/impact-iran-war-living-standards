"use client";

import { getUpratingInputs } from "../lib/dataHelpers";
import {
  getScenarioNarrative,
  getScenarioOptions,
  getScenarioPathLabels,
} from "../lib/scenarioContent";

export default function MethodologyTab({ data }) {
  const householdCount = data?.baseline?.n_households_m;
  const currentEnergyCap = data?.current_energy_cap;
  // Pre-conflict baseline, so the prose quotes the generated figures and
  // their periods rather than hard-coding either (#39).
  // `data` is a static import, so the block is always present; read it
  // unconditionally rather than re-hard-coding every value in a fallback.
  const baseline = data.metadata.pre_conflict_baseline;
  // Read the evaluated ranges rather than restating them, so the prose cannot
  // drift from the model the way the hard-coded figures here could (#37).
  const sensitivity = data.scenarios?.central_shock?.sensitivity;
  const central = data.scenarios?.central_shock;
  const upr = getUpratingInputs(central);
  const notCoveredBoundBn =
    data.metadata?.uprating_not_covered?.upper_bound_bn?.central_shock;
  const scenarioOptions = getScenarioOptions(data);

  return (
    <div className="space-y-8">
      {/* ================================================================ */}
      {/* AT A GLANCE                                                       */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">At a glance</div>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
          The short version
        </h2>
        <dl className="mt-4 grid gap-x-8 gap-y-4 text-sm sm:grid-cols-2">
          <div>
            <dt className="font-semibold text-slate-900">What it estimates</dt>
            <dd className="mt-1 leading-6 text-slate-600">
              What energy, motor fuel and food price rises from the Middle East
              conflict cost UK households in the {data.year}-{String(data.year + 1).slice(2)} tax
              year, and who bears them.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-slate-900">How</dt>
            <dd className="mt-1 leading-6 text-slate-600">
              Three price channels across {data.baseline.n_households_m}m households
              in PolicyEngine UK. Energy uses each household&apos;s own modelled gas
              and electricity spending; <strong>fuel and food use ONS spending
              averages by gross-income decile</strong>, not household-level figures.
              A fourth figure, the uprating shortfall, is reported separately and
              deliberately not added.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-slate-900">Result</dt>
            <dd className="mt-1 leading-6 text-slate-600">
              If energy and fuel stayed near their summer 2026 levels (the July cap and
              August pump prices) through{" "}
              {data.year}-{String(data.year + 1).slice(2)} (energy +
              {data.scenarios.low_shock.params.cap_increase_pct}%, fuel +
              {data.scenarios.low_shock.params.fuel_pct}%, food +
              {data.scenarios.low_shock.params.food_increase_pct}%),{" "}
              <strong>
                &pound;{data.scenarios.low_shock.summary.mean_net_impact.toLocaleString("en-GB")}
              </strong>{" "}
              per household a year (&pound;{data.scenarios.low_shock.summary.total_impact_bn}bn).
              If gas stayed at about twice its pre-conflict price through{" "}
              {data.year}-{String(data.year + 1).slice(2)}, as in sustained escalation,{" "}
              <strong>
                &pound;{data.scenarios.central_shock.summary.mean_net_impact.toLocaleString("en-GB")}
              </strong>{" "}
              (<strong>&pound;{data.scenarios.central_shock.summary.total_impact_bn}bn</strong>).
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-slate-900">Who it hits</dt>
            <dd className="mt-1 leading-6 text-slate-600">
              Under sustained escalation, the poorest fifth lose roughly{" "}
              <strong>
                {Math.round(
                  data.scenarios.central_shock.by_quintile[0].mean_impact /
                    data.baseline.by_quintile[0].mean_net_income /
                    (data.scenarios.central_shock.by_quintile[4].mean_impact /
                      data.baseline.by_quintile[4].mean_net_income),
                )}
                &times;
              </strong>{" "}
              the share of income the richest fifth lose, even though the cash
              amounts run the other way.
            </dd>
          </div>
        </dl>
        <p className="mt-5 rounded-lg bg-amber-50 p-4 text-sm leading-7 text-slate-700">
          <strong>These are stress tests, not forecasts.</strong> Each scenario holds a
          set of prices at a stated level for a full year. Nothing here predicts which
          path the conflict takes, or when.
        </p>
      </div>

      {/* ================================================================ */}
      {/* OVERVIEW                                                          */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Overview</div>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
          How the model works
        </h2>
        <ul className="mt-4 list-disc space-y-2 pl-5 text-sm leading-7 text-slate-600">
          <li>
            <strong>What:</strong> the cost to UK households in 2027-28 of higher
            energy, pump fuel and food prices, with the Middle East conflict (since late
            February 2026) as the context.
          </li>
          <li>
            <strong>Scenarios:</strong> three price paths ({getScenarioPathLabels().join(", ")}).
          </li>
          <li>
            <strong>Model:</strong>{" "}
            <a href="https://policyengine.org" target="_blank" rel="noreferrer" className="underline">PolicyEngine UK</a>{" "}
            on the Enhanced Family Resources Survey
            {householdCount ? `, about ${householdCount.toFixed(1)} million households` : ""}.
          </li>
          <li>
            <strong>Policies:</strong> ten responses, including two Autumn Budget
            decisions due on 28 October 2026.
          </li>
        </ul>
      </div>

      {/* ================================================================ */}
      {/* SCENARIO ASSUMPTIONS                                              */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Scenarios</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          Scenario assumptions
        </h3>
        <ul className="mt-4 list-disc space-y-3 pl-5 text-sm leading-7 text-slate-600">
          <li>
            <strong>What the percentages are.</strong> Full-year 2027-28 price rises. No
            time path or shock duration is modelled, and pass-through rates are
            judgements anchored to the cited sources.
          </li>
          <li>
            <strong>How uncertain.</strong> Each price assumption has a range. Under
            sustained escalation the total runs from{" "}
            {`£${sensitivity?.combined?.total_impact_bn_low}bn to £${sensitivity?.combined?.total_impact_bn_high}bn`}{" "}
            around &pound;{data.scenarios.central_shock.summary.total_impact_bn}bn. This is
            a spread of judgements, <em>not</em> a confidence interval.
          </li>
          <li>
            <strong>Where CPI acts.</strong> Not an inflation forecast. It only sizes the
            uprating shortfall, and so the accelerated-uprating option and combined
            package ({`£${sensitivity?.combined?.uprating_shortfall_bn_low}bn–£${sensitivity?.combined?.uprating_shortfall_bn_high}bn`}),
            never the household cost.
          </li>
          <li>
            <strong>Energy baseline.</strong>{" "}April&ndash;June 2026, the cap Ofgem set
            before the conflict:{" "}
            {`£${baseline.energy_price_cap_new_basis_gbp.toLocaleString("en-GB")}`} on
            the new basis ({`£${baseline.energy_price_cap_old_basis_gbp.toLocaleString("en-GB")}`}{" "}
            on the old). The October cap of{" "}
            {`£${baseline.announced_oct_2026_cap_gbp.toLocaleString("en-GB")}`} is +
            {baseline.announced_oct_2026_vs_pre_conflict_pct}% on it, so summer 2026
            prices&apos; +{data.scenarios.low_shock.params.cap_increase_pct}% is that premium
            partly unwinding.
          </li>
          <li>
            <strong>Fuel baseline.</strong> {baseline.pump_price_period}: about{" "}
            {Math.round(baseline.petrol_pence_per_litre)}p petrol,{" "}
            {Math.round(baseline.diesel_pence_per_litre)}p diesel.
          </li>
          <li>
            <strong>Energy is gas-driven.</strong> Hormuz reaches UK bills through Qatari
            LNG (about 19% of global exports), not crude. Summer 2026 prices follows the{" "}
            <a href="https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-july-and-30-september-2026" target="_blank" rel="noreferrer" className="underline">July cap rise (+13.5%)</a>;
            sustained escalation assumes gas at about twice pre-conflict levels, severe
            about triple (the October 2022 cap rose 178%).
          </li>
          <li>
            <strong>Fuel is oil-driven.</strong> Sustained escalation follows{" "}
            <a href="https://oilprice.com/Latest-Energy-News/World-News/Goldman-Another-Month-of-Hormuz-Closure-Means-Over-100-Brent-Throughout-2026.html" target="_blank" rel="noreferrer" className="underline">Goldman Sachs&apos; extended-closure case</a>{" "}
            (Brent above $100; a client note reported by OilPrice); severe follows{" "}
            <a href="https://www.oxfordeconomics.com/resource/iran-war-scenarios-the-oil-price-that-breaks-parts-of-the-economy/" target="_blank" rel="noreferrer" className="underline">Oxford Economics&apos; $140 case</a>.
            Fixed fuel duty (52.95p) damps the percentage rise, putting $140 at about +60%
            to +70% on pre-conflict pump prices.
          </li>
          <li>
            <strong>CPI figures.</strong>{" "}The first-round effect of each scenario&apos;s
            own price rises on ONS 2026 basket weights: a price-level effect, not a floor
            on inflation.
            {upr ? ` The latest ONS indices put the conflict's contribution to the annual CPI rate at about ${upr.captured}pp.` : null}{" "}
            Sources:{" "}
            <a href="https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026" target="_blank" rel="noreferrer" className="underline">Bank of England, June 2026</a>;{" "}
            <a href="https://commonslibrary.parliament.uk/research-briefings/cbp-10601/" target="_blank" rel="noreferrer" className="underline">Commons Library CBP-10601</a>.
          </li>
        </ul>
        <div className="mt-4 overflow-x-auto">
          <table className="data-table" style={{ tableLayout: "fixed" }}>
            {/* The description carries most of the content, so it gets most
                of the width; the two numeric columns need only enough for
                "+45%" plus their headers. */}
            <colgroup>
              <col style={{ width: "12%" }} />
              <col style={{ width: "13%" }} />
              <col style={{ width: "13%" }} />
              <col style={{ width: "62%" }} />
            </colgroup>
            <thead>
              <tr>
                <th>Scenario</th>
                <th style={{ textAlign: "right" }}>Fuel price</th>
                <th style={{ textAlign: "right" }}>Energy spending</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {scenarioOptions.map((scenario) => {
                const params = data?.scenarios?.[scenario.id]?.params;
                const narrative = getScenarioNarrative(scenario.id, data);
                return (
                  <tr key={scenario.id}>
                    <td className="font-medium">{narrative?.shortLabel || scenario.label}</td>
                    <td style={{ textAlign: "right" }}>
                      {params?.fuel_pct != null ? `+${params.fuel_pct}%` : "--"}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      {params?.cap_increase_pct != null ? `+${params.cap_increase_pct}%` : "--"}
                    </td>
                    <td className="text-xs text-slate-500">
                      {narrative?.description || "Scenario description not available."}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ================================================================ */}
      {/* TRANSMISSION CHANNELS                                             */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Channels</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          Transmission channels
        </h3>
        <div className="mt-4 space-y-4 text-sm leading-7 text-slate-600">
          <div>
            <strong className="text-slate-800">Energy bills:</strong>{" "}
            Higher wholesale gas prices feed through to the{" "}
            <a href="https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-july-and-30-september-2026" target="_blank" rel="noreferrer" className="underline">Ofgem price cap</a>{" "}
            (&pound;{currentEnergyCap.toLocaleString("en-GB")}/yr for
            July&ndash;September 2026 on Ofgem&apos;s new typical-consumption basis,
            equivalent to ~&pound;1,862 on the pre-July basis; &pound;1,723 for
            October&ndash;December 2026). The scenario percentage is applied to each
            household&apos;s <strong>own baseline gas and electricity expenditure</strong>{" "}
            in the microdata &mdash; the cap figures above are context and do not enter
            the calculation. The model does not represent unit rates, standing charges,
            the gas/electricity split, region, payment method, quarterly cap periods or
            fixed-tariff coverage. About 40% of accounts were on fixed tariffs for the
            July 2026 cap period, and the cap does not set the price those accounts pay.
          </div>
          <div>
            <strong className="text-slate-800">Fuel costs:</strong>{" "}
            Oil price increases translate to higher petrol and diesel prices at the pump.
            Fuel spending comes from <a href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/april2023tomarch2024" target="_blank" rel="noreferrer" className="underline">ONS Family Spending</a> Table A6
            (FYE 2024): &pound;19.80/wk on petrol, diesel and other motor oils at the UK
            mean, ranging from &pound;7.40/wk in the lowest gross-income decile to
            &pound;30.90/wk in the highest. A6 groups households by gross household
            income, so the model applies it on that grouping. Each decile&apos;s mean is
            spread across that decile&apos;s vehicle-owning households only, so households
            with no vehicle spend nothing on fuel and receive no fuel-duty benefit. These
            remain decile-level averages rather than household microdata: within-decile
            variation among vehicle owners is not captured, and the survey&apos;s sampling
            uncertainty is not carried into the results.
          </div>
          <div>
            <strong className="text-slate-800">Food prices:</strong>{" "}
            Energy is a major input cost in food production, processing, and distribution.
            We apply scenario-specific annual food price increases of 2.0%, 4.0%, and
            6.5% to food spending from <a href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/april2023tomarch2024" target="_blank" rel="noreferrer" className="underline">ONS Family Spending</a> Table A6
            (FYE 2024): &pound;70.50/wk (&pound;3,666/yr) at the UK mean, ranging from
            &pound;38.10/wk in the lowest gross-income decile to &pound;100.90/wk in the
            highest &mdash; the published decile gradient rather than an assumed one. As
            with fuel, these are
            decile-level spending estimates rather than household-level microdata.
            Severe escalation is anchored to IGD&apos;s severe 2026 food-inflation warning
            reported in March 2026.
          </div>
          <div>
            <strong className="text-slate-800">Benefit uprating &mdash; a shortfall, not a fourth cost:</strong>{" "}
            {upr ? (<ul className="mt-2 list-disc space-y-2 pl-5">
              <li>
                <strong>Timing.</strong> April 2027 uprating uses September 2026 CPI,
                which already carries about {upr.captured}pp from the conflict to the
                annual rate (ONS energy and fuel indices, August proxy). Only the rest of
                each scenario&apos;s addition goes unindexed, until April 2028.
              </li>
              <li>
                <strong>Calculation.</strong> Every CPI-uprated benefit rate, the reported
                ESA, contribution-based JSA, industrial injuries, incapacity benefit and
                armed forces awards, and additional State Pension are raised by the
                residual in PolicyEngine UK, and the benefit rules (tapers, the cap, award
                floors) set each household&apos;s gain. Factor {upr.factor}: the residual
                lasts the whole year.
              </li>
              <li>
                <strong>Left out.</strong> Amounts not CPI-uprated: basic and new State
                Pension (triple lock), the Pension Credit minimum guarantee (earnings),
                UC&apos;s LCWRA element (frozen), caps and thresholds. The savings credit
                maximum and partly linked maternity and sick pay are also not raised: at
                most
                {Number.isFinite(notCoveredBoundBn) ? ` £${notCoveredBoundBn}bn` : " a published bound"}{" "}
                under sustained escalation.
              </li>
              <li>
                <strong>Not a cost.</strong> The shortfall is what an immediate uprating
                would pay, which is the accelerated-uprating option. Adding it to the price
                rises would count the shock twice.
              </li>
              <li>
                <strong>Caveats.</strong> The captured figure omits food, so the shortfall
                is an upper bound; it will use the September outturn once published. The
                factor and captured figure are not varied in the ranges above (at a factor
                of 0 the option would cost nothing).
              </li>
              <li>
                <strong>Precedent.</strong> In 2022 the indexation gap cut benefits&apos;
                real value by about 5% (&pound;12bn): April uprating of 3.1% against 9%
                inflation (<a href="https://ifs.org.uk/news/many-benefit-recipients-will-be-worse-until-april-2025-because-failure-payments-keep" target="_blank" rel="noreferrer" className="underline">IFS</a>;{" "}
                <a href="https://commonslibrary.parliament.uk/research-briefings/cbp-10403/" target="_blank" rel="noreferrer" className="underline">Commons Library CBP-10403</a>).
              </li>
            </ul>) : (
              "The uprating figures are unavailable in this results file."
            )}
          </div>
        </div>
      </div>

      {/* ================================================================ */}
      {/* KEY ASSUMPTIONS                                                    */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Assumptions</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          Key assumptions and parameters
        </h3>
        <div className="mt-4 overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Value</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="font-medium">Food price increase</td>
                <td>2.0% / 4.0% / 6.5%</td>
                <td className="text-xs text-slate-500">
                  Scenario-specific annual food inflation, scaled to shock severity.
                  Consistent with Resolution Foundation&apos;s finding that bottom-decile
                  inflation reaches 3.8% vs 2.9% for the top decile by end-2026.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Average household fuel spending</td>
                <td>&pound;1,029.60/yr</td>
                <td className="text-xs text-slate-500">
                  ONS Family Spending FYE 2024, Table A6, &ldquo;Petrol, diesel and other
                  motor oils&rdquo;: &pound;19.80/wk at the UK mean. Lowest gross-income
                  decile &pound;7.40/wk; highest &pound;30.90/wk.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Average household food spending</td>
                <td>&pound;3,666/yr</td>
                <td className="text-xs text-slate-500">
                  ONS Family Spending FYE 2024, Table A6, &ldquo;Food &amp;
                  non-alcoholic drinks&rdquo;: &pound;70.50/wk at the UK mean. Lowest
                  gross-income decile &pound;38.10/wk; highest &pound;100.90/wk.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Uprating compensation shortfall</td>
                <td>{upr ? `Residual CPI addition, full year (factor ${upr.factor})` : "Unavailable in this results file"}</td>
                <td className="text-xs text-slate-500">
                  Benefits uprated each April by prior September CPI, which already
                  carries part of the shock; the residual is not offset during the
                  shock year. Reported as the compensation an
                  immediate uprating would deliver and <strong>not</strong> counted as a
                  cost. Basic and new State Pension excluded (triple lock); additional State Pension included (CPI). IFS (2022); Commons
                  Library CBP-10403.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Energy price cap (context only)</td>
                <td>&pound;{currentEnergyCap.toLocaleString("en-GB")}/yr</td>
                <td className="text-xs text-slate-500">
                  Ofgem, 1 July&ndash;30 September 2026, typical dual-fuel direct debit
                  household on the new typical-consumption basis (revised 1 July 2026;
                  ~&pound;1,862 on the old basis). The October&ndash;December 2026 cap is
                  &pound;1,723. <strong>Not used in the calculation</strong> &mdash; the
                  scenario percentage is applied to each household&apos;s own baseline
                  gas and electricity expenditure.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Poverty measure</td>
                <td>60% median equivalised HBAI income (BHC), anchored</td>
                <td className="text-xs text-slate-500">
                  The baseline rate is people (not households) below 60% of the
                  person-weighted median of <code>equiv_hbai_household_net_income</code>
                  &mdash; HBAI before-housing-costs relative poverty, comparable in
                  definition with official statistics. The post-shock figure counts people
                  below that <strong>same baseline line</strong> once modelled energy,
                  fuel and food costs are netted off HBAI income. Because
                  consumption costs are deducted and the line is not recalculated, that
                  figure is a consumption-adjusted resource measure against an
                  <strong> anchored</strong> threshold &mdash; not official HBAI poverty,
                  and not a contemporaneous relative measure.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* ================================================================ */}
      {/* INCLUDED / EXCLUDED                                               */}
      {/* ================================================================ */}
      <div className="grid gap-8 xl:grid-cols-2">
        <div className="section-card">
          <div className="eyebrow text-slate-500">Included</div>
          <h3 className="mt-2 text-lg font-semibold text-slate-900">
            What the model captures
          </h3>
          <ul className="mt-4 list-disc pl-5 text-sm leading-7 text-slate-600 space-y-1">
            <li>Direct energy bill increases from wholesale price rises (household-level microdata from PolicyEngine)</li>
            <li>Fuel cost increases from higher oil prices (decile-average spending estimates from ONS)</li>
            <li>Second-round food price inflation from energy input costs (ONS Family Spending Table A6 spending by gross-income decile)</li>
            <li>The compensation an immediate benefit uprating would deliver, reported separately from the cost channels (household-level benefit data from PolicyEngine)</li>
            <li>Distributional analysis by income quintile, country, tenure, and household type</li>
            <li>Ten policy responses with gross outlay and targeting analysis, including the enacted electricity VAT cut and fuel duty extension, a social tariff, and a combined package. Every cost is a gross modelled household transfer, not an Exchequer costing; the fuel duty figure covers household road-fuel volumes only, where an Exchequer estimate would also cover business and freight use and the associated VAT</li>
          </ul>
        </div>

        <div className="section-card">
          <div className="eyebrow text-slate-500">Excluded</div>
          <h3 className="mt-2 text-lg font-semibold text-slate-900">
            What the model omits
          </h3>
          <ul className="mt-4 list-disc pl-5 text-sm leading-7 text-slate-600 space-y-1">
            <li>Household-level fuel and food expenditure (these channels use decile-average estimates, not microdata)</li>
            <li>Labour market effects (unemployment, wage responses)</li>
            <li>General equilibrium and macroeconomic feedback</li>
            <li>Financial market disruption and wealth effects</li>
            <li>Supply chain disruptions beyond energy inputs</li>
            <li>Housing and mortgage cost increases from higher interest rates</li>
            <li>Monetary policy response (interest rate changes)</li>
            <li>International trade effects and exchange rate movements</li>
            <li>Offsetting fiscal effects (higher VAT and duty receipts from higher prices)</li>
            <li>Behavioural responses (changes in driving, heating, or food purchasing patterns)</li>
          </ul>
        </div>
      </div>



    </div>
  );
}
