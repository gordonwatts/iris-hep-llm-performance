import type { Suite } from "./suites";

export interface ModelUsage {
  name: string;
  effort: string | null;
  suites: { suiteId: string; suiteTitle: string }[];
}

/**
 * Groups every suite's model selectors by `name:effort`, for the /models/
 * page. A model used at two different effort levels across suites shows up
 * as two separate rows, since the runner treats them as distinct selectors.
 */
export function summarizeModelUsage(suites: Suite[]): ModelUsage[] {
  const byKey = new Map<string, ModelUsage>();

  for (const suite of suites) {
    for (const model of suite.models) {
      const key = `${model.name}:${model.effort ?? ""}`;
      let usage = byKey.get(key);
      if (!usage) {
        usage = { name: model.name, effort: model.effort, suites: [] };
        byKey.set(key, usage);
      }
      usage.suites.push({ suiteId: suite.id, suiteTitle: suite.title });
    }
  }

  return [...byKey.values()].sort((a, b) => {
    if (a.name !== b.name) return a.name.localeCompare(b.name);
    return (a.effort ?? "").localeCompare(b.effort ?? "");
  });
}
