import { describe, expect, it, vi } from "vitest";
vi.mock("node:fs", () => ({
  existsSync: () => true,
  readFileSync: () =>
    JSON.stringify([
      { directory: "suite a", question: "q1", model: "model:high" },
      { directory: "other", question: "q2", model: "model:low" },
    ]),
}));
import { performanceLink } from "./performance";
describe("performance report links", () => {
  it("links the homepage to all runs", () => {
    expect(performanceLink()).toMatch(/\/performance\.html$/);
  });
  it("encodes suite and question filters together", () => {
    const url = new URL(
      performanceLink({ directory: "suite a", question: "q1" })!,
      "https://example.test",
    );
    expect(url.searchParams.get("directory")).toBe("suite a");
    expect(url.searchParams.get("question")).toBe("q1");
  });
  it("does not link a question that only exists in another suite", () => {
    expect(
      performanceLink({ directory: "suite a", question: "q2" }),
    ).toBeNull();
  });
  it("keeps model effort in the filter", () => {
    const url = new URL(
      performanceLink({ model: "model:high" })!,
      "https://example.test",
    );
    expect(url.searchParams.get("model")).toBe("model:high");
    expect(performanceLink({ model: "missing" })).toBeNull();
  });
});
