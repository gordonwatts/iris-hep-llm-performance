/**
 * Joins `path` onto `base` for an internal link.
 *
 * Every internal href in the site must go through this function rather than
 * a bare `/suites/...` string literal: with `base: "/iris-hep-llm-performance"`
 * set in astro.config.mjs, a bare absolute path resolves correctly in
 * `astro dev` (base "/") but 404s once deployed to GitHub Pages — the most
 * likely way this site could ship a broken deploy.
 *
 * `base` defaults to Astro's own `import.meta.env.BASE_URL`, which always
 * ends in a trailing slash; tests pass it explicitly instead.
 */
export function href(
  path: string,
  base: string = import.meta.env.BASE_URL,
): string {
  const trimmedBase = base.endsWith("/") ? base.slice(0, -1) : base;
  const trimmedPath = path.startsWith("/") ? path.slice(1) : path;

  if (trimmedPath === "") {
    return `${trimmedBase}/`;
  }

  return `${trimmedBase}/${trimmedPath}`;
}
