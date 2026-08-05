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
          delayed benefit uprating. The analysis covers the 2026-27 tax year. The model
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
          de-escalation (Ofgem cap +13% in July 2026; Brent ~$85/bbl in early August).
          The central scenario follows Goldman Sachs&apos; extended Strait of Hormuz
          closure case (Brent above $100/bbl through 2026). The high scenario reflects
          Goldman&apos;s extreme-adverse case (Brent above $115-120) and Oxford
          Economics&apos; prolonged-war scenario. CPI transmission draws on Bank of
          England June 2026 projections and the Commons Library briefing on the conflict
          and the UK economy (CBP-10601).
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
            Higher wholesale gas prices feed through to the Ofgem price cap (Ofgem, 2026;
            model baseline: &pound;{currentEnergyCap.toLocaleString("en-GB")}/yr,
            the July&ndash;September 2026 cap on Ofgem&apos;s new typical-consumption basis,
            equivalent to ~&pound;1,862 on the pre-July basis). We model the pass-through from wholesale to
            retail energy prices using historical cap-setting methodology, applying the
            increase to household gas and electricity bills proportionally.
          </div>
          <div>
            <strong className="text-slate-800">Fuel costs:</strong>{" "}
            Oil price increases translate to higher petrol and diesel prices at the pump.
            Fuel spending is estimated at &pound;1,300/yr on average (ONS, 2025), scaled
            by income decile using ONS ad-hoc fuel expenditure tables (70% of average for
            the lowest deciles to 125% for the highest). These are decile-level averages,
            not household-level microdata; within-decile variation in fuel spending is not
            captured.
          </div>
          <div>
            <strong className="text-slate-800">Food prices:</strong>{" "}
            Energy is a major input cost in food production, processing, and distribution.
            We apply scenario-specific annual food price increases of 2.0%, 4.0%, and
            6.5% to average food spending of &pound;5,000/yr (ONS, 2025; DEFRA, 2025),
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
            with April 2022 uprating at 3.1% against 9% actual inflation (IFS, 2022;
            House of Commons Library, 2023). The model estimates the annual real loss as:
            CPI-linked benefit income &times; CPI increase &times; 0.5, where the 0.5
            factor is the expected fraction of the year a mid-year shock goes un-indexed
            (rather than the 12-month maximum). The state pension is excluded because it
            is uprated by the triple lock (+4.8% via earnings in April 2026), not CPI.
            The April 2027 uprating will use September 2026 CPI, so under sustained
            conflict inflation this channel unwinds from April 2027.
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
                <td>&pound;1,300/yr</td>
                <td className="text-xs text-slate-500">
                  ONS (2025), Family Spending FYE 2024. ~&pound;25/wk average.
                  Lowest decile: &pound;7.10/wk; highest: &pound;31.30/wk.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Average household food spending</td>
                <td>&pound;5,000/yr</td>
                <td className="text-xs text-slate-500">
                  ONS (2025), Family Spending FYE 2024. 11.3% of expenditure.
                  DEFRA (2025), Family Food FYE 2024.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Fuel poverty indicator</td>
                <td>10% of income</td>
                <td className="text-xs text-slate-500">
                  Boardman (1991) 10%-of-income ratio, computed on net income.
                  Indicative only — this is <strong>not</strong> England&apos;s official
                  LILEE metric and is not comparable with official fuel poverty statistics.
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
                <td>60% median equivalised income</td>
                <td className="text-xs text-slate-500">
                  People (not households) below 60% of median equivalised household net
                  income, before housing costs, holding the poverty line at its baseline
                  level. Consumption-cost shocks are converted to equivalent income losses.
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
            <li>Distributional analysis by income decile, region, country, tenure, and household type</li>
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

      {/* ================================================================ */}
      {/* AUTUMN BUDGET 2026 CONTEXT                                        */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Policy context</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          Autumn Budget 2026: the decisions this analysis informs
        </h3>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          The Budget on <strong>28 October 2026</strong> (Chancellor John Healey, under
          the Burnham government) faces a set of live cost-of-living decisions that map
          directly onto the policies modelled here, against thin fiscal headroom
          (NIESR estimates ~&pound;3.4bn; IPPR puts the conflict&apos;s fiscal hit at up
          to &pound;8bn):
        </p>
        <ul className="mt-4 list-disc pl-5 text-sm leading-7 text-slate-600 space-y-1">
          <li>
            <strong>Electricity VAT cut</strong> — the 0% rate runs 1 October 2026 to
            31 March 2027 (~&pound;45/household, ~&pound;850m); whether to extend it will
            be decided at the Budget. Modelled as the &ldquo;Electricity VAT cut&rdquo; policy.
          </li>
          <li>
            <strong>Fuel duty</strong> — the 5p cut is legislated to expire 31 December
            2026, with staged restoration in January and March 2027; whether the
            restoration proceeds is a live Budget question. Modelled as the
            &ldquo;Fuel duty cut extension&rdquo; policy.
          </li>
          <li>
            <strong>Targeted winter energy support</strong> — officials have built a
            delivery mechanism for energy-bill support routed via means-tested benefit
            receipt, awaiting a Budget decision. Modelled as the
            &ldquo;Means-tested payment&rdquo; policy.
          </li>
          <li>
            <strong>April 2027 benefit uprating</strong> — will use September 2026 CPI,
            elevated by the conflict; the &ldquo;Accelerated uprating&rdquo; policy shows
            the effect of bringing that support forward.
          </li>
          <li>
            <strong>Social tariff</strong> — the government is &ldquo;open to further
            action&rdquo;; NIESR instead proposes a variable (rising-block) price cap.
            Modelled as the &ldquo;Social tariff&rdquo; policy.
          </li>
        </ul>
      </div>

      {/* ================================================================ */}
      {/* REFERENCES                                                        */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">References</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          Academic and institutional sources
        </h3>
        <ul className="mt-4 list-disc pl-5 text-sm leading-7 text-slate-600 space-y-1">
            <li>Labandeira, X., Labeaga, J.M. & Lopez-Otero, X. (2017) &lsquo;A meta-analysis on the price elasticity of energy demand&rsquo;, <em>Energy Policy</em>, 102, pp. 549-568.</li>
            <li>Espey, M. (1998) &lsquo;Gasoline demand revisited: an international meta-analysis of elasticities&rsquo;, <em>Energy Economics</em>, 20(3), pp. 273-295.</li>
            <li>Dahl, C. & Sterner, T. (1991) &lsquo;Analysing gasoline demand elasticities: a survey&rsquo;, <em>Energy Economics</em>, 13(3), pp. 203-210.</li>
            <li>Bonciani, D., Ploeckl, F. & Tong, M. (2023) &lsquo;How do firms pass energy and food costs through the supply chain&rsquo;, Bank of England (Bank Underground).</li>
            <li>Boardman, B. (1991) <em>Fuel Poverty: From Cold Homes to Affordable Warmth</em>. London: Belhaven Press.</li>
            <li>Ofgem (2026) &lsquo;Changes to energy price cap between 1 July and 30 September 2026&rsquo;.</li>
            <li>Cornwall Insight (2026) &lsquo;Default tariff cap forecasts&rsquo; (updated after the electricity VAT reduction).</li>
            <li>Bank of England (2026) Monetary Policy Summary and minutes, June 2026.</li>
            <li>House of Commons Library (2026) &lsquo;Economic update: Middle East conflict and the UK economy&rsquo;, CBP-10601.</li>
            <li>House of Commons Library (2026) &lsquo;Benefits uprating 2026/27&rsquo;, CBP-10403.</li>
            <li>Resolution Foundation (2026) &lsquo;Living Standards Outlook 2026&rsquo; and distributional inflation analysis of the energy shock.</li>
            <li>NIESR (2026) &lsquo;The impact of the Middle East conflict on UK energy prices and fiscal policy&rsquo;.</li>
            <li>Oxford Economics (2026) &lsquo;Iran war scenarios: the oil price that breaks parts of the economy&rsquo; and &lsquo;Drawn-out Iran conflict prompts broad-based forecast revisions&rsquo;.</li>
            <li>Goldman Sachs (2026) Strait of Hormuz closure oil-price scenarios (reported June-July 2026).</li>
            <li>IFS (2022) &lsquo;Many benefit recipients will be worse off until April 2025 because of failure of payments to keep up with inflation&rsquo;.</li>
            <li>HM Treasury / Prime Minister&apos;s Office (2026) &lsquo;New PM cuts tax on household electricity bills&rsquo;, July 2026.</li>
            <li>HMRC (2026) &lsquo;Amended fuel duty rates for 2026 to 2027&rsquo;.</li>
            <li>ONS (2025) &lsquo;Family spending in the UK: April 2023 to March 2024&rsquo;.</li>
            <li>ONS (2026) Consumer price inflation, June 2026.</li>
            <li>DEFRA (2025) &lsquo;Family Food FYE 2024&rsquo;.</li>
            <li>Hamilton, J.D. (2003) &lsquo;What is an oil shock?&rsquo;, <em>Journal of Econometrics</em>, 113(2), pp. 363-398.</li>
          </ul>
      </div>

      {/* ================================================================ */}
      {/* DATA SOURCES                                                      */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Data</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          Data sources
        </h3>
        <ul className="mt-4 list-disc pl-5 text-sm leading-7 text-slate-600 space-y-1">
          <li>
            <a href="https://policyengine.org" target="_blank" rel="noreferrer" className="underline">PolicyEngine UK</a>{" "}
            microsimulation (Enhanced FRS 2023-24)
          </li>
          <li>
            <a href="https://www.ofgem.gov.uk/check-if-energy-price-cap-affects-you" target="_blank" rel="noreferrer" className="underline">Ofgem</a>{" "}
            energy price cap methodology and historical data
          </li>
          <li>
            <a href="https://www.ons.gov.uk/economy/inflationandpriceindices" target="_blank" rel="noreferrer" className="underline">ONS</a>{" "}
            CPI, household expenditure data, and Family Spending tables
          </li>
          <li>
            <a href="https://obr.uk/" target="_blank" rel="noreferrer" className="underline">OBR</a>{" "}
            fiscal forecasts, tax threshold schedules, and Economic &amp; Fiscal Outlook
          </li>
          <li>
            <a href="https://www.gov.uk/government/organisations/department-for-work-pensions" target="_blank" rel="noreferrer" className="underline">DWP</a>{" "}
            benefit expenditure and caseload statistics
          </li>
          <li>
            <a href="https://www.gov.uk/government/organisations/hm-revenue-customs" target="_blank" rel="noreferrer" className="underline">HMRC</a>{" "}
            income tax liabilities statistics
          </li>
        </ul>
      </div>

      {/* ================================================================ */}
      {/* REPLICATION                                                       */}
      {/* ================================================================ */}
      <div className="section-card">
        <div className="eyebrow text-slate-500">Replication</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          Code and data
        </h3>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          The Python pipeline generates{" "}
          <code>iran_impact_results.json</code>, which the dashboard consumes.
          All source code is in the{" "}
          <a
            href="https://github.com/PolicyEngine/impact-iran-war-living-standards"
            target="_blank"
            rel="noreferrer"
            className="underline"
          >
            public repository
          </a>.
        </p>
      </div>
    </div>
  );
}
