"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import ScenariosTab from "../src/components/ScenariosTab";
import PolicyTab from "../src/components/PolicyTab";
import MethodologyTab from "../src/components/MethodologyTab";
import data from "../public/data/iran_impact_results.json";

const TAB_OPTIONS = [
  { id: "scenarios", label: "Household Impacts" },
  { id: "policy", label: "Policy Options" },
  { id: "methodology", label: "Methodology" },
];

function getInitialTab(tabParam) {
  if (TAB_OPTIONS.some((tab) => tab.id === tabParam)) {
    return tabParam;
  }
  return "scenarios";
}

function Dashboard() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState(() => getInitialTab(searchParams.get("tab")));

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    setActiveTab(getInitialTab(tabParam));
  }, [searchParams]);

  function handleTabChange(tab) {
    setActiveTab(tab);
    if (tab === "scenarios") {
      router.replace("/", { scroll: false });
      return;
    }
    router.replace(`/?tab=${tab}`, { scroll: false });
  }

  return (
    <div className="app-shell min-h-screen">
      <header className="title-row">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between px-6 py-4 md:px-8">
          <h1>Energy Price Shock: Impact on UK Living Standards</h1>
        </div>
      </header>

      <main className="relative z-[1] mx-auto max-w-[1400px] px-6 py-10 md:px-8 md:py-12">
        <div className="animate-[fadeIn_0.4s_ease-out]">
          <p className="mb-3 text-[1.05rem] leading-relaxed text-slate-600">
            This dashboard uses{" "}
            <a href="https://policyengine.org" target="_blank" rel="noreferrer" className="underline">
              PolicyEngine UK
            </a>
            &apos;s microsimulation model to estimate how energy price rises from the
            ongoing Middle East conflict and Strait of Hormuz disruption affect UK
            household living standards. The{" "}
            <strong>Household Impacts</strong> tab models three conflict paths (de-escalation,
            sustained disruption, prolonged war) and their distributional effects across
            income deciles, regions, countries, tenures, and household types. The{" "}
            <strong>Policy Options</strong> tab evaluates ten interventions — including
            the live Budget decisions on extending the electricity VAT cut and the 5p fuel
            duty cut, and the benefits-targeted winter energy payment under consideration —
            with their fiscal costs and targeting. The{" "}
            <strong>Methodology</strong> tab explains the modelling approach,
            assumptions, and data sources. For recent coverage of the government&apos;s
            likely next steps, see{" "}
            <a
              href="https://www.bloomberg.com/news/articles/2026-07-21/burnham-cuts-taxes-energy-bills-ease-cost-of-living-burden"
              target="_blank"
              rel="noreferrer"
              className="underline"
            >
              Bloomberg on the Burnham government&apos;s electricity VAT cut
            </a>{" "}
            and the{" "}
            <a
              href="https://www.resolutionfoundation.org/press-releases/poorest-households-are-set-to-see-inflation-nearly-a-third-higher-than-the-richest/"
              target="_blank"
              rel="noreferrer"
              className="underline"
            >
              Resolution Foundation&apos;s analysis of who the energy shock hits hardest
            </a>
            .
          </p>
        </div>

        <div
          className="mb-8 mt-8 flex w-fit flex-wrap border-b-2 border-slate-200"
          role="tablist"
          aria-label="Dashboard sections"
        >
          {TAB_OPTIONS.map((tab) => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              className={`tab-button ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => handleTabChange(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "scenarios" && <ScenariosTab data={data} />}
        {activeTab === "policy" && <PolicyTab data={data} />}
        {activeTab === "methodology" && <MethodologyTab data={data} />}

        <footer className="mt-12 border-t border-slate-200 pt-8 text-center text-sm text-slate-500">
          <p>
            Replication code:{" "}
            <a
              href="https://github.com/PolicyEngine/impact-iran-war-living-standards"
              target="_blank"
              rel="noreferrer"
            >
              PolicyEngine/impact-iran-war-living-standards
            </a>
            . Built with policyengine-uk 2.89.4 and policyengine-uk-data 1.11.1.
          </p>
        </footer>
      </main>
    </div>
  );
}

export default function Page() {
  return (
    <Suspense
      fallback={
        <p className="p-12 text-center text-slate-500">Loading...</p>
      }
    >
      <Dashboard />
    </Suspense>
  );
}
