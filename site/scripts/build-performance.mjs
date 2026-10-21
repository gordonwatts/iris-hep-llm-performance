import { load } from "js-yaml";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
  readdirSync,
} from "node:fs";
import { resolve, join } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(process.env.REPO_ROOT ?? "..");
const source = resolve(process.env.RESULTS_DIR ?? join(root, "results"));
const output = resolve("public/performance.html");
const index = resolve(".generated/performance.json");
function findReports(path) {
  if (!existsSync(path)) return [];
  return readdirSync(path, { withFileTypes: true }).flatMap((entry) => {
    const file = join(path, entry.name);
    if (entry.isDirectory()) {
      return ["node_modules", ".venv", "tools-env", ".git"].includes(entry.name)
        ? []
        : findReports(file);
    }
    if (!/\.ya?ml$/i.test(entry.name)) return [];
    const report = load(readFileSync(file, "utf8"));
    // Results folders can also contain copied templates and tool environments.
    return report && typeof report === "object" && report.run && report.prompt
      ? [file]
      : [];
  });
}
mkdirSync(resolve("public"), { recursive: true });
mkdirSync(resolve(".generated"), { recursive: true });
// Never leave stale links or a stale report after a failed/empty build.
rmSync(output, { force: true });
writeFileSync(index, "[]\n");
if (process.env.RESULTS_DIR && !existsSync(source)) {
  throw new Error(`RESULTS_DIR does not exist: ${source}`);
}
const reports = findReports(source);
if (reports.length) {
  const result = spawnSync(
    "uvx",
    [
      "--python",
      "3.13",
      "--from",
      "git+https://github.com/gordonwatts/test-wsl2-llm.git@608d04c9c35083ee9df13e41513acd9d6cbd190b",
      "test-wsl2-llm",
      "performance",
      ...reports.flatMap((file) => ["--source", file]),
      "--output",
      output,
      "--force",
    ],
    { stdio: "inherit" },
  );
  if (result.error) throw result.error;
  if (result.status !== 0)
    throw new Error(`performance failed: ${result.status}`);
  const html = readFileSync(output, "utf8");
  const match = html.match(
    /<script id="records" type="application\/json">([\s\S]*?)<\/script>/,
  );
  if (!match)
    throw new Error("Performance report is missing its records dataset");
  const records = JSON.parse(match[1]);
  // Keep prompts and responses in the report only; the site needs just link keys.
  writeFileSync(
    index,
    JSON.stringify(
      records.map(({ directory, question, model }) => ({
        directory,
        question,
        model,
      })),
    ),
  );
  console.log(`Published performance report with ${records.length} runs`);
} else {
  console.log("No saved results: building catalogue without performance links");
}
