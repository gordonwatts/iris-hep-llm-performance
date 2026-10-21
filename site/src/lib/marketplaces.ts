export interface MarketplaceRef {
  url: string;
  ref: string | null;
}

/**
 * A suite's `marketplaces` entries are plain git URLs, sometimes with a
 * `@ref` (branch/tag) suffix appended directly onto the URL itself — e.g.
 * "https://github.com/iris-hep/marketplace.git@spec-updates" — which is not
 * itself a navigable link. Splits the two apart so the repo URL can be
 * rendered as a real `<a href>` and the ref shown alongside as plain text.
 */
export function parseMarketplaceUrl(spec: string): MarketplaceRef {
  const atIndex = spec.indexOf("@");
  if (atIndex === -1) {
    return { url: spec, ref: null };
  }

  return { url: spec.slice(0, atIndex), ref: spec.slice(atIndex + 1) };
}

/**
 * Shortens a marketplace git URL to "owner/repo" for display — the full
 * URL is still the link's `href`, this is only the visible label. Falls
 * back to the input unchanged if it isn't a `scheme://host/owner/repo[.git]`
 * shape, rather than guessing.
 */
export function formatMarketplaceLabel(url: string): string {
  const match = url.match(/^https?:\/\/[^/]+\/(.+?)(?:\.git)?$/);
  return match ? match[1] : url;
}
