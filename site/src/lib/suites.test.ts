import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { loadSuites } from "./suites";

let dir: string;

function write(name: string, contents: string) {
  writeFileSync(join(dir, name), contents);
}

beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), "suites-"));
});

afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
});

describe("loadSuites", () => {
  it("loads a minimal suite with its title, prompt template, and questions", () => {
    write(
      "a-suite.yaml",
      `
title: "A Suite"
prompt_template: |
  {{ question }}
questions:
  - id: q1
    question: "Do the thing."
model: gpt-5.6-luna:medium
`,
    );

    const [suite] = loadSuites(dir);

    expect(suite.id).toBe("a-suite");
    expect(suite.file).toBe("a-suite.yaml");
    expect(suite.title).toBe("A Suite");
    expect(suite.promptTemplate).toBe("{{ question }}\n");
    expect(suite.questions).toEqual([
      { id: "q1", question: "Do the thing.", extras: {} },
    ]);
    expect(suite.models).toEqual([{ name: "gpt-5.6-luna", effort: "medium" }]);
  });

  it("strips a leading '# ' from a report-header-style title", () => {
    write(
      "hashed.yaml",
      `
title: "# Analysis Grand Challenge Related Tests"
prompt_template: "{{ question }}"
questions:
  - id: q1
    question: "x"
model: gpt-5
`,
    );

    expect(loadSuites(dir)[0].title).toBe(
      "Analysis Grand Challenge Related Tests",
    );
  });

  it("humanizes the filename when title is absent", () => {
    write(
      "no-title-here.yaml",
      `
prompt_template: "{{ question }}"
questions:
  - id: q1
    question: "x"
model: gpt-5
`,
    );

    expect(loadSuites(dir)[0].title).toBe("No Title Here");
  });

  it("ignores a yaml file that is not a suite spec", () => {
    write(
      "a-suite.yaml",
      `title: "A"\nprompt_template: "{{ question }}"\nquestions: [{id: q1, question: x}]\nmodel: gpt-5\n`,
    );
    write("not-a-suite.yaml", `some: config\nvalue: 1\n`);

    expect(loadSuites(dir).map((s) => s.id)).toEqual(["a-suite"]);
  });

  it("normalizes a plural models: list", () => {
    write(
      "multi-model.yaml",
      `
title: "Multi"
prompt_template: "{{ question }}"
questions:
  - id: q1
    question: "x"
models:
  - gpt-5:high
  - gpt-4o
`,
    );

    expect(loadSuites(dir)[0].models).toEqual([
      { name: "gpt-5", effort: "high" },
      { name: "gpt-4o", effort: null },
    ]);
  });

  it("defaults missing arrays to empty and missing scalars to null, repeat/threads to 1", () => {
    write(
      "sparse.yaml",
      `
title: "Sparse"
prompt_template: "{{ question }}"
questions:
  - id: q1
    question: "x"
model: gpt-5
`,
    );

    const suite = loadSuites(dir)[0];
    expect(suite.marketplaces).toEqual([]);
    expect(suite.plugins).toEqual([]);
    expect(suite.mcpServers).toEqual([]);
    expect(suite.copyFiles).toEqual([]);
    expect(suite.copyBack).toEqual([]);
    expect(suite.distro).toBeNull();
    expect(suite.timeoutSeconds).toBeNull();
    expect(suite.output).toBeNull();
    expect(suite.repeat).toBe(1);
    expect(suite.threads).toBe(1);
  });

  it("captures unrecognized scalar question fields as extras for template substitution", () => {
    write(
      "extras.yaml",
      `
title: "Extras"
prompt_template: "{{ question }} {{ dataset }}"
questions:
  - id: q1
    question: "x"
    dataset: "user.zmarshal:foo"
model: gpt-5
`,
    );

    expect(loadSuites(dir)[0].questions[0].extras).toEqual({
      dataset: "user.zmarshal:foo",
    });
  });

  it("carries a question-level copy_back override separately from extras", () => {
    write(
      "override.yaml",
      `
title: "Override"
prompt_template: "{{ question }}"
questions:
  - id: q1
    question: "x"
    copy_back: ["results.md"]
model: gpt-5
copy_back: ["default.png"]
`,
    );

    const suite = loadSuites(dir)[0];
    expect(suite.copyBack).toEqual(["default.png"]);
    expect(suite.questions[0].copyBack).toEqual(["results.md"]);
    expect(suite.questions[0].extras).toEqual({});
  });

  it("sorts suites by id for a deterministic listing", () => {
    write(
      "z-suite.yaml",
      `title: "Z"\nprompt_template: "{{ question }}"\nquestions: [{id: q1, question: x}]\nmodel: gpt-5\n`,
    );
    write(
      "a-suite.yaml",
      `title: "A"\nprompt_template: "{{ question }}"\nquestions: [{id: q1, question: x}]\nmodel: gpt-5\n`,
    );

    expect(loadSuites(dir).map((s) => s.id)).toEqual(["a-suite", "z-suite"]);
  });
});
