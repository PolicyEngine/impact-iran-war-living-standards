"use client";

import { getScenarioNarrative, getScenarioOptions } from "../lib/scenarioContent";

export default function MethodologyTab({ data }) {
  const householdCount = data?.baseline?.n_households_m;
  const currentEnergyCap = data?.current_energy_cap;
  const scenarioOptions = getScenarioOptions(data);

  return (
    <div className="space-y-8">
      {/* ================================================================ */}
      {/* OVERVIEW                                                          */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Overview</div>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
          How the model works
        </h2>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          This dashboard estimates how energy price rises from the ongoing Middle East
          conflict — active since late February 2026, with recurrent Strait of Hormuz
          disruption — affect UK household living standards. We model three forward
          paths for the conflict (de-escalation, sustained disruption, prolonged war),
          each transmitted to households through four channels: higher energy bills,
          increased fuel costs, food price inflation, and the real-value loss from
          delayed benefit uprating. The analysis covers the 2027-28 tax year. The model
          is built on{" "}
          <a href="https://policyengine.org" target="_blank" rel="noreferrer" className="underline">PolicyEngine UK</a>{" "}
          microsimulation using the Enhanced Family Resources Survey, covering approximately
          {householdCount ? ` ${householdCount.toFixed(1)} million ` : " "}
          UK households. Ten policy responses are evaluated for their fiscal
          cost, distributional impact, and fuel poverty reduction — including the
          decisions facing the government at the Autumn Budget on 28 October 2026.
        </p>
      </div>

      {/* ================================================================ */}
      {/* SCENARIO ASSUMPTIONS                                              */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Scenarios</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          Scenario assumptions
        </h3>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          Each scenario represents a forward path for the conflict from the August 2026
          position. The low scenario tracks the observed price path assuming
          de-escalation (<a href="https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-july-and-30-september-2026" target="_blank" rel="noreferrer" className="underline">Ofgem cap +13% in July 2026</a>;
          Brent ~$85/bbl in early August). The central scenario follows{" "}
          <a href="https://oilprice.com/Latest-Energy-News/World-News/Goldman-Another-Month-of-Hormuz-Closure-Means-Over-100-Brent-Throughout-2026.html" target="_blank" rel="noreferrer" className="underline">Goldman Sachs&apos; extended Strait of Hormuz closure case</a>{" "}
          (Brent above $100/bbl through 2026). The high scenario reflects
          Goldman&apos;s extreme-adverse case (Brent above $115-120) and{" "}
          <a href="https://www.oxfordeconomics.com/resource/iran-war-scenarios-the-oil-price-that-breaks-parts-of-the-economy/" target="_blank" rel="noreferrer" className="underline">Oxford Economics&apos; prolonged-war scenario</a>.
          CPI transmission draws on{" "}
          <a href="https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026" target="_blank" rel="noreferrer" className="underline">Bank of England June 2026 projections</a>{" "}
          and the{" "}
          <a href="https://commonslibrary.parliament.uk/research-briefings/cbp-10601/" target="_blank" rel="noreferrer" className="underline">Commons Library briefing on the conflict and the UK economy</a>.
        </p>
        <div className="mt-4 overflow-x-auto">
          <table className="data-table" style={{ tableLayout: "fixed" }}>
            <colgroup>
              <col style={{ width: "25%" }} />
              <col style={{ width: "25%" }} />
              <col style={{ width: "25%" }} />
              <col style={{ width: "25%" }} />
            </colgroup>
            <thead>
              <tr>
                <th>Scenario</th>
                <th style={{ textAlign: "right" }}>Fuel price increase</th>
                <th style={{ textAlign: "right" }}>Energy cap increase</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {scenarioOptions.map((scenario) => {
                const params = data?.scenarios?.[scenario.id]?.params;
                const narrative = getScenarioNarrative(scenario.id);
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
            (model baseline: &pound;{currentEnergyCap.toLocaleString("en-GB")}/yr,
            the July&ndash;September 2026 cap on Ofgem&apos;s new typical-consumption basis,
            equivalent to ~&pound;1,862 on the pre-July basis). We model the pass-through from wholesale to
            retail energy prices using historical cap-setting methodology, applying the
            increase to household gas and electricity bills proportionally.
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
            6.5% to average food spending of &pound;5,000/yr (<a href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/april2023tomarch2024" target="_blank" rel="noreferrer" className="underline">ONS</a>; DEFRA Family Food),
            scaled by decile following Engel&apos;s Law. As with fuel, these are
            decile-level spending estimates rather than household-level microdata. The
            high scenario is anchored to IGD&apos;s severe 2026 food-inflation warning
            reported in March 2026.
          </div>
          <div>
            <strong className="text-slate-800">Benefit uprating lag:</strong>{" "}
            CPI-linked benefits are uprated each April using the previous September&apos;s
            CPI — a lag of up to 18 months. Between uprating dates, higher prices reduce
            the real value of benefit payments. During the 2022 energy crisis, this
            mechanism eroded benefit real value by approximately 5% (&pound;12bn total),
            with April 2022 uprating at 3.1% against 9% actual inflation (<a href="https://ifs.org.uk/news/many-benefit-recipients-will-be-worse-until-april-2025-because-failure-payments-keep" target="_blank" rel="noreferrer" className="underline">IFS</a>;{" "}
            <a href="https://commonslibrary.parliament.uk/research-briefings/cbp-10403/" target="_blank" rel="noreferrer" className="underline">Commons Library CBP-10403</a>). The model estimates the annual real loss as:
            CPI-linked benefit income &times; CPI increase &times; 0.5, where the 0.5
            factor is the expected fraction of the year a mid-year shock goes un-indexed
            (rather than the 12-month maximum). The state pension is excluded because it
            is uprated by the triple lock (+4.8% via earnings in April 2026), not CPI.
            For the 2027-28 year, the April 2027 uprating is set from September 2026
            CPI, so the channel captures conflict inflation running ahead of that
            indexation point while the shock is sustained.
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
                <td className="font-medium">Fuel poverty indicator</td>
                <td>10% of income</td>
                <td className="text-xs text-slate-500">
                  Boardman (1991) 10%-of-income ratio, computed on
                  <code> household_net_income</code>. Indicative only &mdash; this is
                  <strong> not</strong> England&apos;s official LILEE metric and is not
                  comparable with official fuel poverty statistics. Households with
                  non-positive income and a positive energy bill are counted as fuel
                  poor, and are excluded from statistics expressed as a share of income;
                  the results file reports how many households that affects.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Benefit uprating lag</td>
                <td>Expected 6 months (factor 0.5)</td>
                <td className="text-xs text-slate-500">
                  Benefits uprated each April by prior September CPI (up to 18 months
                  lag at the extreme); the model applies the expected-value erosion for
                  a mid-year shock. State pension excluded (triple lock). IFS (2022);
                  Commons Library CBP-10403.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Energy price cap (Q3 2026)</td>
                <td>&pound;{currentEnergyCap.toLocaleString("en-GB")}/yr</td>
                <td className="text-xs text-slate-500">
                  Ofgem, 1 July&ndash;30 September 2026, typical dual-fuel direct debit
                  household on the new typical-consumption basis (revised 1 July 2026;
                  ~&pound;1,862 on the old basis). Cornwall Insight forecasts
                  ~&pound;1,700 for Q4 2026 after the electricity VAT removal.
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
                  fuel, food and uprating-lag costs are netted off HBAI income. Because
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
            <li>Second-round food price inflation from energy input costs (decile-average spending estimates from ONS/DEFRA)</li>
            <li>Real-value loss of means-tested benefits between uprating dates (household-level benefit data from PolicyEngine)</li>
            <li>Distributional analysis by income quintile, country, tenure, and household type</li>
            <li>Fuel poverty impact using the indicative 10%-of-income ratio</li>
            <li>Ten policy responses with fiscal cost and targeting analysis, including the enacted electricity VAT cut and fuel duty extension, a social tariff, and a combined package</li>
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
