/**
 * Render-level contract for the methodology tab's headline figures.
 *
 * Renders the component with the committed results file and asserts the
 * user-visible text. This is what #53 review A2 asked for. An earlier
 * attempt parsed the source for `data.…` paths instead; mutation testing
 * showed it accepted seven display-breaking changes — a wrong-but-valid key,
 * an out-of-range quintile index, a hard-coded literal — while failing on a
 * comment. Asserting rendered output is the only thing that closes it.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import MethodologyTab from "./MethodologyTab";
import data from "../../public/data/iran_impact_results.json";

// The contract, derived from the committed data rather than hard-coded, so
// a deliberate results change updates it and an accidental binding change
// does not.
const central = data.scenarios.central_shock;
const sensitivity = central.sensitivity.combined;
const ratioOfMeans = Math.round(
  central.by_quintile[0].mean_impact /
    data.baseline.by_quintile[0].mean_net_income /
    (central.by_quintile[4].mean_impact /
      data.baseline.by_quintile[4].mean_net_income),
);

function renderTab() {
  const { container } = render(<MethodologyTab data={data} />);
  return container.textContent.replace(/\s+/g, " ");
}

describe("MethodologyTab headline figures", () => {
  it("renders the household count from the data", () => {
    expect(renderTab()).toContain(`${data.baseline.n_households_m}m households`);
  });

  it("renders the central cost per household and total", () => {
    const text = renderTab();
    expect(text).toContain(
      `£${central.summary.mean_net_impact.toLocaleString("en-GB")}`,
    );
    expect(text).toContain(`£${central.summary.total_impact_bn}bn`);
  });

  it("renders the regressivity ratio on the ratio-of-means basis", () => {
    expect(renderTab()).toContain(`${ratioOfMeans}×`);
  });

  it("renders both ends of the evaluated total range", () => {
    const text = renderTab();
    expect(text).toContain(`£${sensitivity.total_impact_bn_low}bn`);
    expect(text).toContain(`£${sensitivity.total_impact_bn_high}bn`);
  });

  it("renders the uprating shortfall range, which was stale before #53", () => {
    const text = renderTab();
    expect(text).toContain(`£${sensitivity.uprating_shortfall_bn_low}bn`);
    expect(text).toContain(`£${sensitivity.uprating_shortfall_bn_high}bn`);
  });

  it("does not claim fuel and food use household-level spending", () => {
    const text = renderTab();
    // #53 review A1: only energy is household-specific.
    expect(text).toContain("gross-income decile");
    expect(text).not.toContain(
      "Three price channels applied to each household's own modelled spending",
    );
  });

  it("follows the data rather than hard-coding it", () => {
    // A literal that happens to equal today's value renders identically, so
    // the only way to catch one is to render DIFFERENT data and check the
    // output moves with it (#53 review A2, mutation 7).
    const moved = structuredClone(data);
    moved.baseline.n_households_m = 99.9;
    moved.scenarios.central_shock.summary.mean_net_impact = 4321;
    moved.scenarios.central_shock.summary.total_impact_bn = 99.9;
    moved.scenarios.central_shock.sensitivity.combined.total_impact_bn_low = 11.1;
    moved.scenarios.central_shock.sensitivity.combined.uprating_shortfall_bn_high = 8.88;

    const { container } = render(<MethodologyTab data={moved} />);
    const text = container.textContent.replace(/\s+/g, " ");

    expect(text).toContain("99.9m households");
    expect(text).toContain("£4,321");
    expect(text).toContain("£11.1bn");
    expect(text).toContain("£8.88bn");
    // And the real values must be gone, or something is hard-coded.
    expect(text).not.toContain(
      `£${central.summary.mean_net_impact.toLocaleString("en-GB")}`,
    );
  });
});
