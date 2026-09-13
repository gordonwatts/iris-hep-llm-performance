import { describe, expect, it } from "vitest";
import { formatMarketplaceLabel, parseMarketplaceUrl } from "./marketplaces";

describe("parseMarketplaceUrl", () => {
  it("returns a plain git url as-is with no ref", () => {
    expect(
      parseMarketplaceUrl("https://github.com/iris-hep/marketplace.git"),
    ).toEqual({
      url: "https://github.com/iris-hep/marketplace.git",
      ref: null,
    });
  });

  it("splits a trailing @ref suffix from the linkable url", () => {
    expect(
      parseMarketplaceUrl(
        "https://github.com/iris-hep/marketplace.git@spec-updates",
      ),
    ).toEqual({
      url: "https://github.com/iris-hep/marketplace.git",
      ref: "spec-updates",
    });
  });

  it("handles a repo url with no .git suffix", () => {
    expect(
      parseMarketplaceUrl("https://github.com/gordonwatts/agc_marketplace"),
    ).toEqual({
      url: "https://github.com/gordonwatts/agc_marketplace",
      ref: null,
    });
  });
});

describe("formatMarketplaceLabel", () => {
  it("strips the scheme, host, and .git suffix down to owner/repo", () => {
    expect(
      formatMarketplaceLabel("https://github.com/iris-hep/marketplace.git"),
    ).toBe("iris-hep/marketplace");
  });

  it("leaves a repo url with no .git suffix as owner/repo", () => {
    expect(
      formatMarketplaceLabel("https://github.com/gordonwatts/agc_marketplace"),
    ).toBe("gordonwatts/agc_marketplace");
  });

  it("falls back to the full url when it doesn't look like a host/owner/repo path", () => {
    expect(formatMarketplaceLabel("not-a-url")).toBe("not-a-url");
  });
});
