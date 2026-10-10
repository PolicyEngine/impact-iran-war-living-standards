/**
 * Render-level contract for the citation table (Telegraph, 9 October 2026).
 *
 * The forecast scenario is only reportable if a reader can see where each
 * number came from and when. These tests render the table from the
 * committed results file and assert the link, the publisher's name and the
 * publication date for every parameter of every scenario, then check by
 * property that the table follows the data rather than hard-coding it.
 */
import { render, within } from "@testing-library/react";
import fc from "fast-check";
import { describe, expect, it } from "vitest";

import ScenarioSources, { SOURCE_ROWS } from "./ScenarioSources";
import data from "../../public/data/iran_impact_results.json";
import { formatSourceDate } from "../lib/formatters";

function renderSources(withData, scenario) {
  const { container } = render(<ScenarioSources data={withData} scenario={scenario} />);
  return container;
}

function linkTo(container, href) {
  return [...container.querySelectorAll("a")].find((a) => a.getAttribute("href") === href);
}

describe("every scenario's citations", () => {
  for (const scenario of Object.keys(data.scenarios)) {
    it(`renders source, publisher and date for each ${scenario} parameter`, () => {
      const container = renderSources(data, scenario);
      const registry = data.parameters.registry[scenario].parameters;
      const text = container.textContent.replace(/\s+/g, " ");
      for (const { key } of SOURCE_ROWS) {
        const entry = registry[key];
        const link = linkTo(container, entry.source_url);
        expect(link, `${scenario}.${key} has no link to ${entry.source_url}`).toBeTruthy();
        expect(link.textContent).toBe(entry.source_name);
        expect(text).toContain(formatSourceDate(entry.source_date));
        for (const supporting of entry.supporting_sources) {
          expect(linkTo(container, supporting.url)?.textContent).toBe(supporting.name);
        }
      }
    });
  }
});

describe("the forecast scenario", () => {
  const registry = data.parameters.registry.external_forecast.parameters;

  it("names Cornwall Insight, the EIA and IGD with their publication dates", () => {
    const container = renderSources(data, "external_forecast");
    const text = container.textContent.replace(/\s+/g, " ");
    const rows = [...container.querySelectorAll("tbody tr")];
    const energy = rows.find((row) => row.textContent.startsWith("Energy spending"));
    expect(within(energy).getByText("Cornwall Insight, price cap forecast").getAttribute("href")).toBe(
      "https://www.cornwall-insight.com/press-releases/16-price-cap-rise-forecast-in-january/",
    );
    expect(energy.textContent).toContain("30 Sep 2026");
    expect(energy.textContent).toContain(`+${registry.cap_increase_pct.value}%`);
    expect(text).toContain("US EIA, Short-Term Energy Outlook, October 2026");
    expect(text).toContain("6 Oct 2026");
    expect(text).toContain("IGD, food inflation forecast, September 2026");
    expect(text).toContain("17 Sep 2026");
  });

  it("labels each price by what was forecast, and the CPI figure as derived", () => {
    const container = renderSources(data, "external_forecast");
    const rows = [...container.querySelectorAll("tbody tr")];
    const basisOf = (label) =>
      rows.find((r) => r.textContent.startsWith(label)).querySelectorAll("td")[2].textContent;
    expect(basisOf("Energy spending")).toBe("Published forecast");
    expect(basisOf("Food")).toBe("Published forecast");
    // The EIA forecasts Brent, not pump prices: the label must not let
    // "+12.2%" be read as the EIA's own figure (#67 review).
    expect(basisOf("Petrol and diesel")).toBe("Published Brent forecast, our pass-through");
    expect(basisOf("CPI addition")).toBe("Derived from this scenario's prices");
  });

  it("says the fuel figure leans high and assumes the duty cut continues", () => {
    const text = renderSources(data, "external_forecast").textContent.replace(/\s+/g, " ");
    expect(text).toContain("probably leans high");
    expect(text).toContain("assumes the 5p cut continues");
    expect(text).toContain("The EIA forecasts crude, not UK pump prices");
  });

  it("states the vintage, what no forecast covers, and when it goes stale", () => {
    const text = renderSources(data, "external_forecast").textContent.replace(/\s+/g, " ");
    expect(text).toContain(`as of ${formatSourceDate(data.metadata.forecast_vintage.as_of)}`);
    expect(text).toContain("What the forecasts do not cover");
    for (const gap of data.metadata.forecast_vintage.gaps) expect(text).toContain(gap);
    // The duty assumption has to be in view without opening a derivation:
    // the fuel duty option is compared with this cost (#67 second review).
    expect(text).toContain("What this scenario assumes");
    for (const assumption of data.metadata.forecast_vintage.assumptions) {
      expect(text).toContain(assumption);
    }
    expect(text).toContain("Fuel duty stays at 52.95p a litre");
    expect(text).toContain("Next updates");
    expect(text).toContain("28 Oct 2026");
  });
});

describe("the stress tests", () => {
  it("say they are stress tests and mark judgements as judgements", () => {
    for (const scenario of ["low_shock", "central_shock", "severe_shock"]) {
      const container = renderSources(data, scenario);
      const text = container.textContent.replace(/\s+/g, " ");
      expect(text, scenario).toContain("A stress test, not a forecast");
      expect(text, scenario).not.toContain("What the forecasts do not cover");
      expect(text, scenario).not.toContain("What this scenario assumes");
      const energy = [...container.querySelectorAll("tbody tr")].find((r) =>
        r.textContent.startsWith("Energy spending"),
      );
      expect(energy.textContent, scenario).toContain("Judgement");
    }
  });
});

describe("fails closed", () => {
  it("renders nothing for a scenario the results file does not register", () => {
    expect(renderSources(data, "no_such_scenario").textContent).toBe("");
    const stripped = structuredClone(data);
    delete stripped.parameters.registry;
    expect(renderSources(stripped, "external_forecast").textContent).toBe("");
  });

  it("drops a row whose source is not a usable https link rather than show a bare value", () => {
    const broken = structuredClone(data);
    broken.parameters.registry.external_forecast.parameters.fuel_pct.source_url = "javascript:alert(1)";
    const container = renderSources(broken, "external_forecast");
    expect(container.textContent).not.toContain("Petrol and diesel");
    expect(container.innerHTML).not.toContain("javascript:");
    expect(container.textContent).toContain("Energy spending");
  });
});

describe("the table follows the data (property)", () => {
  const isoDate = fc
    .record({
      y: fc.integer({ min: 2000, max: 2099 }),
      m: fc.integer({ min: 1, max: 12 }),
      d: fc.integer({ min: 1, max: 28 }),
    })
    .map(({ y, m, d }) => `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`);
  const name = fc.string({ minLength: 3, maxLength: 40 }).filter((s) => s.trim().length >= 3 && s === s.trim());
  const path = fc.stringMatching(/^[a-z0-9-]{1,20}$/);

  it("renders whatever source, name, date and value the registry holds", () => {
    fc.assert(
      fc.property(
        name,
        path,
        isoDate,
        fc.double({ min: 0, max: 500, noNaN: true }).map((v) => Math.round(v * 10) / 10),
        fc.constantFrom(...SOURCE_ROWS.map((row) => row.key)),
        (sourceName, slug, date, value, key) => {
          const moved = structuredClone(data);
          const entry = moved.parameters.registry.external_forecast.parameters[key];
          entry.source_name = sourceName;
          entry.source_url = `https://example.org/${slug}`;
          entry.source_date = date;
          entry.value = value;
          const { container, unmount } = render(
            <ScenarioSources data={moved} scenario="external_forecast" />,
          );
          const link = linkTo(container, `https://example.org/${slug}`);
          expect(link?.textContent).toBe(sourceName);
          const row = link.closest("tr");
          expect(row.textContent).toContain(formatSourceDate(date));
          expect(row.textContent).toContain(`+${value}`);
          unmount();
        },
      ),
      { numRuns: 40 },
    );
  });
});
