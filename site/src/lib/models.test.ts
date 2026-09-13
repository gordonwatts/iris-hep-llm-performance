import { describe, expect, it } from "vitest";
import { parseModelSelector } from "./models";

describe("parseModelSelector", () => {
  it("splits a name:effort selector", () => {
    expect(parseModelSelector("gpt-5.6-luna:medium")).toEqual({
      name: "gpt-5.6-luna",
      effort: "medium",
    });
  });

  it("returns a null effort for a bare model name", () => {
    expect(parseModelSelector("gpt-5.6-luna")).toEqual({
      name: "gpt-5.6-luna",
      effort: null,
    });
  });
});
