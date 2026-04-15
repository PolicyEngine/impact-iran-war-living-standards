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
          This dashboard estimates how energy price increases from a sustained disruption to
          Middle East oil and gas supply would affect UK household living standards. We model
          three scenarios, each representing a different magnitude of price increase. These
          are transmitted to households through four channels: higher energy bills, increased
          fuel costs, food price inflation, and the real-value loss from delayed benefit
          uprating. The analysis covers the 2026-27 tax year. The model is built on{" "}
          <a href="https://policyengine.org" target="_blank" rel="noreferrer" className="underline">PolicyEngine UK</a>{" "}
          microsimulation using the Enhanced Family Resources Survey, covering approximately
          {householdCount ? ` ${householdCount.toFixed(1)} million ` : " "}
          UK households. Eight policy responses are evaluated for their fiscal
          cost, distributional impact, and fuel poverty reduction.
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
          Each scenario represents a different magnitude of energy price shock from
          a sustained disruption to Middle East oil and gas supply. Scenario magnitudes
          are calibrated to Hamilton (2003) and IMF (2024) oil price literature, with
          CPI transmission based on Bank of England (2022) supply-side pass-through
          estimates.
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
            current model baseline: &pound;{currentEnergyCap?.toLocaleString("en-GB") || "1,641"}/yr). We model the pass-through from wholesale to
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
            We apply scenario-specific annual food price increases of 2.0%, 4.5%, and
            6.4% to average food spending of &pound;5,000/yr (ONS, 2025; DEFRA, 2025),
            scaled by decile following Engel&apos;s Law. As with fuel, these are
            decile-level spending estimates rather than household-level microdata. The
            high scenario is anchored to IGD&apos;s severe 2026 food-inflation warning
            reported in March 2026.
          </div>
          <div>
            <strong className="text-slate-800">Benefit uprating lag:</strong>{" "}
            Means-tested benefits are uprated each April using the previous September&apos;s
            CPI — a lag of up to 18 months. Between uprating dates, higher prices reduce
            the real value of benefit payments. During the 2022 energy crisis, this
            mechanism eroded benefit real value by approximately 5% (&pound;12bn total),
            with April 2022 uprating at 3.1% against 9% actual inflation (IFS, 2022;
            House of Commons Library, 2023). The model estimates the annual real loss as:
            benefit income &times; CPI increase &times; (lag months / 12).
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
                <td>2.0% / 4.5% / 6.4%</td>
                <td className="text-xs text-slate-500">
                  Scenario-specific annual food inflation. High scenario anchored to
                  IGD severe food-price warning reported in March 2026; lower scenarios
                  scaled to shock severity.
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
                <td className="font-medium">Fuel poverty threshold</td>
                <td>10% of income</td>
                <td className="text-xs text-slate-500">
                  Boardman (1991), <em>Fuel Poverty: From Cold Homes to Affordable
                  Warmth</em>. Official definition in Scotland, Wales and NI.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Benefit uprating lag</td>
                <td>Up to 18 months</td>
                <td className="text-xs text-slate-500">
                  IFS (2022); OBR (2023) &ldquo;Benefit uprating during and after
                  recessions&rdquo;. Benefits uprated each April by prior September CPI.
                </td>
              </tr>
              <tr>
                <td className="font-medium">Energy price cap (Q2 2026)</td>
                <td>&pound;{currentEnergyCap?.toLocaleString("en-GB") || "1,641"}/yr</td>
                <td className="text-xs text-slate-500">
                  Ofgem (2026), typical dual-fuel direct debit household.
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
            <li>Distributional analysis by income decile, region, country, and tenure</li>
            <li>Fuel poverty impact using the 10% threshold metric</li>
            <li>Eight policy responses with fiscal cost and targeting analysis, including a social tariff</li>
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
            <li>Government spending responses and their fiscal implications</li>
            <li>Behavioural responses (changes in driving, heating, or food purchasing patterns)</li>
          </ul>
        </div>
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
            <li>IGD food inflation warning reported by The Independent (2026), discussing sharp food-price rises under a Middle East supply disruption scenario.</li>
            <li>Boardman, B. (1991) <em>Fuel Poverty: From Cold Homes to Affordable Warmth</em>. London: Belhaven Press.</li>
            <li>OBR (2024) &lsquo;Fiscal implications of personal tax threshold freezes and reductions&rsquo;, Economic and Fiscal Outlook.</li>
            <li>IFS (2022) &lsquo;Many benefit recipients will be worse off until April 2025 because of failure of payments to keep up with inflation&rsquo;.</li>
            <li>ONS (2025) &lsquo;Family spending in the UK: April 2023 to March 2024&rsquo;.</li>
            <li>DEFRA (2025) &lsquo;Family Food FYE 2024&rsquo;.</li>
            <li>Ofgem (2026) &lsquo;Changes to energy price cap between 1 April and 30 June 2026&rsquo;.</li>
            <li>ONS (2022) &lsquo;Energy prices and their effect on households&rsquo;.</li>
            <li>Hamilton, J.D. (2003) &lsquo;What is an oil shock?&rsquo;, <em>Journal of Econometrics</em>, 113(2), pp. 363-398.</li>
            <li>IMF (2024) &lsquo;Oil price shocks and the global economy&rsquo;, World Economic Outlook.</li>
            <li>HMRC (2024) &lsquo;Income Tax liabilities statistics&rsquo;.</li>
            <li>DWP (2024) &lsquo;Benefit expenditure and caseload tables&rsquo;.</li>
            <li>Dimitropoulos, A., Hunt, L.C. & Judge, G. (2005) &lsquo;Estimating underlying energy demand trends using UK annual data&rsquo;, <em>Applied Economics Letters</em>, 12, pp. 239-244.</li>
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
