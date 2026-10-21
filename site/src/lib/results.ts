import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { load } from "js-yaml";
import { getRepoRoot } from "./paths";

/**
 * A single benchmark run, normalized from a test-wsl2-llm YAML report.
 *
 * test-wsl2-llm's report format is documented only in prose (no published
 * schema), so every field here is best-effort and nullable. This is
 * deliberately the one place that will need to change once a real results
 * tree exists to validate the mapping against.
 */
export interface RunResult {
  suiteId: string | null;
  questionId: string | null;
  model: string | null;
  effort: string | null;
  index: number | null;
  raw: unknown;
}

function defaultResultsDir(): string {
  return process.env.RESULTS_DIR ?? join(getRepoRoot(), "results");
}

function stringOrNull(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

/** Maps a parsed run-report document onto {@link RunResult}, never throwing. */
export function normalizeRunReport(raw: unknown): RunResult {
  const record =
    raw !== null && typeof raw === "object"
      ? (raw as Record<string, unknown>)
      : {};

  return {
    suiteId: stringOrNull(record.suite),
    questionId: stringOrNull(record.question_id),
    model: stringOrNull(record.model),
    effort: stringOrNull(record.effort),
    index: typeof record.index === "number" ? record.index : null,
    raw,
  };
}

/**
 * Loads every run report under `resultsDir` (default: `RESULTS_DIR`, or
 * `<repo root>/results`).
 *
 * Results are deliberately not committed to this repo (`.gitignore:
 * results/*`) and no ingest transport has been decided yet — a missing or
 * unreadable directory is expected, not exceptional, so this returns `[]`
 * (never throws) and warns once so a misconfigured `RESULTS_DIR` isn't
 * silently swallowed. A single malformed report is skipped the same way,
 * so one bad file can't fail the whole build.
 */
export function loadResults(
  resultsDir: string = defaultResultsDir(),
): RunResult[] {
  let entries: string[];
  try {
    entries = readdirSync(resultsDir);
  } catch {
    console.warn(
      `loadResults(): RESULTS_DIR "${resultsDir}" does not exist or is not readable; ` +
        `rendering with no results.`,
    );
    return [];
  }

  const results: RunResult[] = [];
  for (const entry of entries) {
    if (!entry.endsWith(".yaml")) continue;

    try {
      const raw = load(readFileSync(join(resultsDir, entry), "utf8"));
      results.push(normalizeRunReport(raw));
    } catch {
      console.warn(
        `loadResults(): skipping unparseable result file "${entry}".`,
      );
    }
  }

  return results;
}
