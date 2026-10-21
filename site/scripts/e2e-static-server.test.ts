import { describe, expect, it } from "vitest";
import { resolveStaticPath } from "./e2e-static-server";

const DIST = "/repo/site/dist";
const BASE = "/iris-hep-llm-performance";

describe("resolveStaticPath", () => {
  it("maps the base root to dist/index.html", () => {
    expect(resolveStaticPath(`${BASE}/`, BASE, DIST)).toBe(
      `${DIST}/index.html`,
    );
  });

  it("maps a directory-style route to its index.html", () => {
    expect(
      resolveStaticPath(`${BASE}/suites/iris-hep-llm-questions/`, BASE, DIST),
    ).toBe(`${DIST}/suites/iris-hep-llm-questions/index.html`);
  });

  it("maps a real file with an extension as-is", () => {
    expect(resolveStaticPath(`${BASE}/favicon.svg`, BASE, DIST)).toBe(
      `${DIST}/favicon.svg`,
    );
  });

  it("maps a hashed asset under _astro/ as-is", () => {
    expect(
      resolveStaticPath(`${BASE}/_astro/suites.2qRrLFx1.css`, BASE, DIST),
    ).toBe(`${DIST}/_astro/suites.2qRrLFx1.css`);
  });

  it("strips a query string before resolving", () => {
    expect(resolveStaticPath(`${BASE}/favicon.svg?v=2`, BASE, DIST)).toBe(
      `${DIST}/favicon.svg`,
    );
  });

  it("returns null for a path outside the configured base", () => {
    expect(resolveStaticPath("/some-other-path/", BASE, DIST)).toBeNull();
  });

  it("returns null for a path attempting to escape dist via ..", () => {
    expect(
      resolveStaticPath(`${BASE}/../../etc/passwd`, BASE, DIST),
    ).toBeNull();
  });
});
