import { existsSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { getRepoRoot } from "./paths";

describe("getRepoRoot", () => {
  const originalEnv = process.env.REPO_ROOT;

  afterEach(() => {
    if (originalEnv === undefined) {
      delete process.env.REPO_ROOT;
    } else {
      process.env.REPO_ROOT = originalEnv;
    }
  });

  it("returns REPO_ROOT when it points at a directory containing the benchmark specs", () => {
    const dir = mkdtempSync(join(tmpdir(), "repo-root-"));
    writeFileSync(join(dir, "iris-hep-llm-questions.yaml"), "questions: []\n");
    process.env.REPO_ROOT = dir;

    try {
      expect(getRepoRoot()).toBe(dir);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("throws a named, actionable error when REPO_ROOT does not contain the benchmark specs", () => {
    const dir = mkdtempSync(join(tmpdir(), "repo-root-empty-"));
    process.env.REPO_ROOT = dir;

    try {
      expect(() => getRepoRoot()).toThrow(/iris-hep-llm-questions\.yaml/);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

describe("getRepoRoot (no REPO_ROOT override)", () => {
  it("resolves to the parent of the site/ directory, which holds the real specs", () => {
    delete process.env.REPO_ROOT;
    const root = getRepoRoot();
    expect(existsSync(join(root, "iris-hep-llm-questions.yaml"))).toBe(true);
  });
});
