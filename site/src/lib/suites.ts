import { readdirSync, readFileSync } from "node:fs";
import { basename, join } from "node:path";
import { load } from "js-yaml";
import { parseModelSelector, type ModelSelector } from "./models";
import { getRepoRoot } from "./paths";

export interface Question {
  id: string;
  question: string;
  copyBack?: string[];
  plugins?: string[];
  distro?: string;
  validators?: unknown[];
  /**
   * Any scalar field beyond the known ones above — the runner's schema
   * allows arbitrary extra string/number/boolean fields on a question for
   * `{{ field }}` substitution in the suite's prompt_template.
   */
  extras: Record<string, string | number | boolean>;
}

export interface Suite {
  id: string;
  file: string;
  title: string;
  promptTemplate: string;
  questions: Question[];
  models: ModelSelector[];
  marketplaces: string[];
  plugins: string[];
  mcpServers: string[];
  copyFiles: string[];
  copyBack: string[];
  distro: string | null;
  repeat: number;
  threads: number;
  timeoutSeconds: number | null;
  output: string | null;
}

/** Fields on a question entry that are never template-substitution extras. */
const KNOWN_QUESTION_FIELDS = new Set([
  "id",
  "question",
  "copy_back",
  "plugins",
  "distro",
  "validators",
]);

/**
 * Turns a filename stem like "no-title-here" into "No Title Here" — the
 * fallback used only when a suite's YAML has no `title:` (every spec in this
 * repo has one; this exists so a future suite added without a title still
 * renders something reasonable instead of a raw filename).
 */
function humanize(id: string): string {
  return id
    .split(/[-_]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * A suite's `title:` sometimes doubles as a Markdown report heading (e.g.
 * agc-tests.yaml's "# Analysis Grand Challenge Related Tests") — strip a
 * leading "# " so it renders as plain text here.
 */
function normalizeTitle(rawTitle: unknown, id: string): string {
  if (typeof rawTitle !== "string" || rawTitle.trim() === "") {
    return humanize(id);
  }
  return rawTitle.replace(/^#\s+/, "");
}

function toStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === "string");
}

/** True when a parsed YAML document looks like a test-wsl2-llm suite spec. */
function isSuiteSpec(doc: unknown): doc is Record<string, unknown> {
  if (doc === null || typeof doc !== "object") return false;
  const record = doc as Record<string, unknown>;
  return (
    typeof record.prompt_template === "string" &&
    Array.isArray(record.questions)
  );
}

function normalizeModels(doc: Record<string, unknown>): ModelSelector[] {
  if (typeof doc.model === "string") {
    return [parseModelSelector(doc.model)];
  }
  if (Array.isArray(doc.models)) {
    return doc.models
      .filter((m): m is string => typeof m === "string")
      .map(parseModelSelector);
  }
  return [];
}

function normalizeQuestion(raw: unknown): Question {
  const record = raw as Record<string, unknown>;
  const extras: Record<string, string | number | boolean> = {};

  for (const [key, value] of Object.entries(record)) {
    if (KNOWN_QUESTION_FIELDS.has(key)) continue;
    if (
      typeof value === "string" ||
      typeof value === "number" ||
      typeof value === "boolean"
    ) {
      extras[key] = value;
    }
  }

  const question: Question = {
    id: String(record.id),
    question: String(record.question),
    extras,
  };
  if (Array.isArray(record.copy_back))
    question.copyBack = toStringArray(record.copy_back);
  if (Array.isArray(record.plugins))
    question.plugins = toStringArray(record.plugins);
  if (typeof record.distro === "string") question.distro = record.distro;
  if (Array.isArray(record.validators)) question.validators = record.validators;

  return question;
}

function normalizeSuite(
  id: string,
  file: string,
  doc: Record<string, unknown>,
): Suite {
  return {
    id,
    file,
    title: normalizeTitle(doc.title, id),
    promptTemplate: doc.prompt_template as string,
    questions: (doc.questions as unknown[]).map(normalizeQuestion),
    models: normalizeModels(doc),
    marketplaces: toStringArray(doc.marketplaces),
    plugins: toStringArray(doc.plugins),
    mcpServers: toStringArray(doc.mcp_servers),
    copyFiles: toStringArray(doc.copy_files),
    copyBack: toStringArray(doc.copy_back),
    distro: typeof doc.distro === "string" ? doc.distro : null,
    repeat: typeof doc.repeat === "number" ? doc.repeat : 1,
    threads: typeof doc.threads === "number" ? doc.threads : 1,
    timeoutSeconds:
      typeof doc.timeout_seconds === "number" ? doc.timeout_seconds : null,
    output: typeof doc.output === "string" ? doc.output : null,
  };
}

/**
 * Discovers benchmark suites by scanning every `*.yaml` file directly under
 * `repoRoot` and keeping the ones that parse as a test-wsl2-llm suite spec
 * (both `prompt_template` and `questions` present) — self-describing, so a
 * new suite file needs no change here.
 */
export function loadSuites(repoRoot: string = getRepoRoot()): Suite[] {
  const suites: Suite[] = [];

  for (const file of readdirSync(repoRoot)) {
    if (!file.endsWith(".yaml")) continue;

    const doc = load(readFileSync(join(repoRoot, file), "utf8"));
    if (!isSuiteSpec(doc)) continue;

    suites.push(normalizeSuite(basename(file, ".yaml"), file, doc));
  }

  return suites.sort((a, b) => a.id.localeCompare(b.id));
}
