import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { href } from "./url";

export interface ResultFilters {
  directory?: string;
  question?: string;
  model?: string;
}
const index = resolve(".generated/performance.json");
const records: ResultFilters[] = existsSync(index)
  ? JSON.parse(readFileSync(index, "utf8"))
  : [];

export function performanceLink(filters: ResultFilters = {}): string | null {
  const entries = Object.entries(filters);
  if (
    !records.some((record) =>
      entries.every(
        ([key, value]) => record[key as keyof ResultFilters] === value,
      ),
    )
  )
    return null;
  const query = new URLSearchParams(entries).toString();
  return href("/performance.html") + (query ? `?${query}` : "");
}
