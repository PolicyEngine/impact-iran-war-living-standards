/**
 * Contract for the distributional chart's share-of-income mode.
 *
 * In a separate file from ScenariosTab.test.jsx so this PR and #54 do not
 * collide on the same path; they cover different components' behaviour.
 */
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ScenariosTab from "./ScenariosTab";
import data from "../../public/data/iran_impact_results.json";

function shareButton(container) {
  return [...container.querySelectorAll("button")].find(
    (b) => b.textContent === "Share of income",
  );
}

describe("share-of-income mode", () => {
  it("offers the toggle when every row has a usable denominator", () => {
    const { container } = render(<ScenariosTab data={data} />);
    const button = shareButton(container);
    expect(button).toBeTruthy();
    expect(button.disabled).toBe(false);
  });

  it("never labels cash amounts as percentages", () => {
    // toShare previously returned the row unchanged when income was missing,
    // so pounds were formatted with a percent sign: energy £100 rendered as
    // "100.00%", and a denominator of -1 as "-10000.00%" (#57 review A1).
    for (const bad of [undefined, 0, -1, Number.NaN, Infinity, "57000"]) {
      const broken = structuredClone(data);
      for (const scenario of Object.values(broken.scenarios)) {
        scenario.by_quintile[0].mean_net_income = bad;
      }
      const { container } = render(<ScenariosTab data={broken} />);
      expect(
        shareButton(container)?.disabled,
        `income=${String(bad)} left share enabled`,
      ).toBe(true);
      expect(container.textContent).not.toContain("NaN");
    }
  });

  it("reports every quintile's income, so the share can be computed", () => {
    for (const scenario of Object.values(data.scenarios)) {
      for (const row of scenario.by_quintile) {
        expect(typeof row.mean_net_income).toBe("number");
        expect(row.mean_net_income).toBeGreaterThan(0);
      }
    }
  });
});
