import { describe, expect, it } from "vitest";
import { summarizeModelUsage } from "./modelUsage";
import type { Suite } from "./suites";

function makeSuite(overrides: Partial<Suite>): Suite {
  return {
    id: "suite",
    file: "suite.yaml",
    title: "Suite",
    promptTemplate: "{{ question }}",
    questions: [],
    models: [],
    marketplaces: [],
    plugins: [],
    mcpServers: [],
    copyFiles: [],
    copyBack: [],
    distro: null,
    repeat: 1,
    threads: 1,
    timeoutSeconds: null,
    output: null,
    ...overrides,
  };
}

describe("summarizeModelUsage", () => {
  it("groups suites sharing the same model:effort selector", () => {
    const a = makeSuite({
      id: "a",
      title: "A",
      models: [{ name: "gpt-5", effort: "medium" }],
    });
    const b = makeSuite({
      id: "b",
      title: "B",
      models: [{ name: "gpt-5", effort: "medium" }],
    });

    const usage = summarizeModelUsage([a, b]);

    expect(usage).toHaveLength(1);
    expect(usage[0].name).toBe("gpt-5");
    expect(usage[0].effort).toBe("medium");
    expect(usage[0].suites.map((s) => s.suiteId)).toEqual(["a", "b"]);
  });

  it("keeps distinct effort levels of the same model name separate", () => {
    const a = makeSuite({
      id: "a",
      models: [{ name: "gpt-5", effort: "medium" }],
    });
    const b = makeSuite({
      id: "b",
      models: [{ name: "gpt-5", effort: "high" }],
    });

    const usage = summarizeModelUsage([a, b]);

    expect(usage).toHaveLength(2);
  });

  it("sorts entries by name then by effort", () => {
    const suite = makeSuite({
      models: [
        { name: "gpt-5", effort: "medium" },
        { name: "gpt-4o", effort: null },
        { name: "gpt-5", effort: "high" },
      ],
    });

    expect(
      summarizeModelUsage([suite]).map((u) => `${u.name}:${u.effort}`),
    ).toEqual(["gpt-4o:null", "gpt-5:high", "gpt-5:medium"]);
  });
});
