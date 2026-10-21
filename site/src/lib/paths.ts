import { existsSync } from "node:fs";
import { resolve } from "node:path";

/**
 * The one file that must exist directly under the repo root for a directory
 * to count as "the repo root" — every suite loader below assumes sibling
 * YAML files live next to it.
 */
const MARKER_FILE = "iris-hep-llm-questions.yaml";

/**
 * Resolves the repository root that holds the benchmark spec YAMLs.
 *
 * Every pixi task and vitest run has `cwd` set to `site/`, so the default is
 * the parent of the current working directory — mirroring the CWD-relative
 * `readFileSync` pattern both reference repos use, but with an explicit,
 * actionable failure instead of a silent ENOENT deep in a YAML loader.
 *
 * `REPO_ROOT` overrides the default, which lets tests point at a fixture
 * directory without touching the real repo.
 */
export function getRepoRoot(): string {
  const root = process.env.REPO_ROOT ?? resolve(process.cwd(), "..");

  if (!existsSync(resolve(root, MARKER_FILE))) {
    throw new Error(
      `getRepoRoot(): expected to find ${MARKER_FILE} under "${root}", but it is not there. ` +
        `Set REPO_ROOT to the iris-hep-llm-performance checkout, or run this from site/.`,
    );
  }

  return root;
}
