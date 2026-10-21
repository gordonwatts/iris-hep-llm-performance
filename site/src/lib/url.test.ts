import { describe, expect, it } from "vitest";
import { href } from "./url";

describe("href", () => {
  it("joins a leading-slash path onto the configured base", () => {
    expect(
      href("/suites/iris-hep-llm-questions/", "/iris-hep-llm-performance/"),
    ).toBe("/iris-hep-llm-performance/suites/iris-hep-llm-questions/");
  });

  it("returns the bare base for the root path", () => {
    expect(href("/", "/iris-hep-llm-performance/")).toBe(
      "/iris-hep-llm-performance/",
    );
  });

  it("does not duplicate the slash between base and path", () => {
    expect(href("suites/", "/iris-hep-llm-performance/")).toBe(
      "/iris-hep-llm-performance/suites/",
    );
  });

  it("works when the base is just a bare slash (dev server)", () => {
    expect(href("/suites/", "/")).toBe("/suites/");
  });
});
