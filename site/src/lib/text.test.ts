import { describe, expect, it } from "vitest";
import { truncateText } from "./text";

describe("truncateText", () => {
  it("returns short text unchanged and reports no truncation", () => {
    expect(truncateText("Plot the ETmiss.", 160)).toEqual({
      excerpt: "Plot the ETmiss.",
      truncated: false,
    });
  });

  it("truncates long text at a word boundary and marks it truncated", () => {
    const text =
      "Implement a complete pipeline in the template file with several stages.";
    const { excerpt, truncated } = truncateText(text, 30);

    expect(truncated).toBe(true);
    expect(excerpt.length).toBeLessThanOrEqual(31); // 30 + the ellipsis char
    expect(excerpt.endsWith("…")).toBe(true);
    expect(text.startsWith(excerpt.slice(0, -1).trimEnd())).toBe(true);
  });

  it("collapses internal newlines into spaces before truncating", () => {
    const text = "Line one.\n\nLine two is here to push this past the limit.";
    const { excerpt } = truncateText(text, 20);
    expect(excerpt).not.toContain("\n");
  });

  it("does not truncate text exactly at the limit", () => {
    const text = "x".repeat(30);
    expect(truncateText(text, 30)).toEqual({ excerpt: text, truncated: false });
  });
});
