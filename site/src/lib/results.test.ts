import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { loadResults, normalizeRunReport } from "./results";

describe("normalizeRunReport", () => {
  it("maps known fields from a run report", () => {
    expect(
      normalizeRunReport({
        suite: "iris-hep-llm-questions",
        question_id: "q1",
        model: "gpt-5.6-luna",
        effort: "medium",
        index: 1,
      }),
    ).toEqual({
      suiteId: "iris-hep-llm-questions",
      questionId: "q1",
      model: "gpt-5.6-luna",
      effort: "medium",
      index: 1,
      raw: {
        suite: "iris-hep-llm-questions",
        question_id: "q1",
        model: "gpt-5.6-luna",
        effort: "medium",
        index: 1,
      },
    });
  });

  it("defaults every field to null for a report missing them, without throwing", () => {
    expect(normalizeRunReport({})).toEqual({
      suiteId: null,
      questionId: null,
      model: null,
      effort: null,
      index: null,
      raw: {},
    });
  });

  it("defaults every field to null for a non-object report", () => {
    expect(normalizeRunReport(null).suiteId).toBeNull();
    expect(normalizeRunReport("oops").suiteId).toBeNull();
  });
});

describe("loadResults", () => {
  let dir: string;
  let warnSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), "results-"));
    warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
  });

  afterEach(() => {
    rmSync(dir, { recursive: true, force: true });
    warnSpy.mockRestore();
  });

  it("returns an empty array and warns once when the directory does not exist", () => {
    const missing = join(dir, "does-not-exist");
    expect(loadResults(missing)).toEqual([]);
    expect(warnSpy).toHaveBeenCalledTimes(1);
    expect(warnSpy.mock.calls[0][0]).toContain(missing);
  });

  it("parses every run report yaml file in the directory", () => {
    writeFileSync(
      join(dir, "run-1.yaml"),
      "suite: iris-hep-llm-questions\nquestion_id: q1\nmodel: gpt-5\n",
    );
    writeFileSync(
      join(dir, "run-2.yaml"),
      "suite: iris-hep-llm-questions\nquestion_id: q2\nmodel: gpt-5\n",
    );

    const results = loadResults(dir);
    expect(results).toHaveLength(2);
    expect(results.map((r) => r.questionId).sort()).toEqual(["q1", "q2"]);
  });

  it("ignores non-yaml files (e.g. the paired markdown report)", () => {
    writeFileSync(join(dir, "run-1.yaml"), "suite: s\nquestion_id: q1\n");
    writeFileSync(join(dir, "run-1.md"), "# report\n");

    expect(loadResults(dir)).toHaveLength(1);
  });

  it("skips a malformed yaml file and warns, without throwing", () => {
    writeFileSync(join(dir, "good.yaml"), "suite: s\nquestion_id: q1\n");
    writeFileSync(join(dir, "bad.yaml"), "suite: [unterminated\n");

    const results = loadResults(dir);
    expect(results).toHaveLength(1);
    expect(results[0].questionId).toBe("q1");
    expect(warnSpy).toHaveBeenCalledTimes(1);
    expect(warnSpy.mock.calls[0][0]).toContain("bad.yaml");
  });
});
