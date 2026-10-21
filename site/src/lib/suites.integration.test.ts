/**
 * Runs loadSuites/renderPrompt against the real benchmark specs at the repo
 * root — no fixtures, no mocks. This is what actually guarantees the site
 * renders every suite and question that exists today.
 */
import { describe, expect, it } from "vitest";
import { renderPrompt } from "./prompt";
import { loadSuites } from "./suites";

const suites = loadSuites();

describe("loadSuites against the real repo specs", () => {
  it("discovers exactly the five known suites", () => {
    expect(suites.map((s) => s.id)).toEqual([
      "agc-tests",
      "analyiss-base-questions",
      "iris-hep-llm-questions",
      "spec-tests",
      "uchicago-mcp",
    ]);
  });

  it.each([
    ["iris-hep-llm-questions", 18],
    ["analyiss-base-questions", 5],
    ["uchicago-mcp", 5],
    ["agc-tests", 1],
    ["spec-tests", 1],
  ])("%s has %i questions", (id, count) => {
    const suite = suites.find((s) => s.id === id);
    expect(suite?.questions).toHaveLength(count);
  });

  it("gives every suite a non-empty, plain-text title", () => {
    for (const suite of suites) {
      expect(suite.title.length).toBeGreaterThan(0);
      expect(suite.title.startsWith("#")).toBe(false);
    }
  });

  it("renders every question's effective prompt with no unresolved placeholders", () => {
    for (const suite of suites) {
      for (const question of suite.questions) {
        const rendered = renderPrompt(suite.promptTemplate, {
          question: question.question,
          ...question.extras,
        });
        expect(rendered).not.toContain("{{");
      }
    }
  });

  it("gives every suite at least one parseable model selector", () => {
    for (const suite of suites) {
      expect(suite.models.length).toBeGreaterThan(0);
      for (const model of suite.models) {
        expect(model.name.length).toBeGreaterThan(0);
      }
    }
  });
});
