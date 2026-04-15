"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import ScenariosTab from "../src/components/ScenariosTab";
import PolicyTab from "../src/components/PolicyTab";
import MethodologyTab from "../src/components/MethodologyTab";
import initialData from "../public/data/iran_impact_results.json";

const TAB_OPTIONS = [
  { id: "scenarios", label: "Impact Scenarios" },
  { id: "policy", label: "Policy Responses" },
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
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    setActiveTab(getInitialTab(tabParam));
  }, [searchParams]);

  useEffect(() => {
    async function loadData() {
      try {
        const response = await fetch("/data/iran_impact_results.json");
        if (!response.ok) {
          throw new Error("iran_impact_results.json not found");
        }
        const json = await response.json();
        setData(json);
      } catch (err) {
        if (!initialData) {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

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
            &apos;s microsimulation model to estimate how energy price increases from a
            sustained disruption to Middle East oil and gas supply would affect UK household
            living standards. The{" "}
            <strong>Impact Scenarios</strong> tab models three scenarios and their
            distributional effects across income deciles, regions, and countries. The{" "}
            <strong>Policy Responses</strong> tab evaluates eight potential government
            interventions and their fiscal costs. The{" "}
            <strong>Methodology</strong> tab explains the modelling approach,
            assumptions, and data sources.
          </p>
        </div>

        <div className="mb-8 mt-8 flex w-fit flex-wrap border-b-2 border-slate-200">
          {TAB_OPTIONS.map((tab) => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => handleTabChange(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {error && (
          <p className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
            Error: {error}
          </p>
        )}
        {loading && !error && (
          <p className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
            Loading data...
          </p>
        )}

        {!loading && !error && data && (
          <>
            {activeTab === "scenarios" && <ScenariosTab data={data} />}
            {activeTab === "policy" && <PolicyTab data={data} />}
            {activeTab === "methodology" && <MethodologyTab data={data} />}
          </>
        )}

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
            .
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
