import { describe, expect, it } from "vitest";
import { renderPrompt } from "./prompt";

describe("renderPrompt", () => {
  it("substitutes a tightly-spaced {{field}} placeholder", () => {
    expect(
      renderPrompt("Do this:\n\n{{question}}\n", {
        question: "Plot the ETmiss.",
      }),
    ).toBe("Do this:\n\nPlot the ETmiss.\n");
  });

  it("substitutes a loosely-spaced {{ field }} placeholder", () => {
    expect(renderPrompt("{{ question }}", { question: "Plot the pT." })).toBe(
      "Plot the pT.",
    );
  });

  it("substitutes the same field more than once", () => {
    expect(renderPrompt("{{question}} / {{question}}", { question: "x" })).toBe(
      "x / x",
    );
  });

  it("throws on a placeholder with no matching field", () => {
    expect(() =>
      renderPrompt("{{question}} {{missing}}", { question: "x" }),
    ).toThrow(/missing/);
  });
});
