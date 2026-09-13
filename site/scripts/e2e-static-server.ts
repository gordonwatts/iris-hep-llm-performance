/**
 * Serves a built `dist/` directory under a fixed base path, in the
 * foreground, for Playwright's `webServer` to drive in e2e.spec.ts.
 *
 * `astro preview` (Astro 7) manages its own persistent background daemon:
 * the CLI process that starts it exits immediately once the daemon is up,
 * which Playwright's webServer treats as "the server process exited early"
 * and fails the run even though the daemon itself is serving fine. This
 * script is a minimal foreground stand-in with no such daemonizing —
 * Playwright can track and kill it directly.
 *
 * Astro's static build writes `dist/` with no base-path prefix directory
 * (only hrefs *inside* the HTML carry `base`), so this has to add that
 * prefix back at request time — exactly what `astro preview` does
 * internally.
 */
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, resolve, sep } from "node:path";

const MIME_TYPES: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".txt": "text/plain; charset=utf-8",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
};

/**
 * Maps a request path to a file under `distDir`, as if `distDir` were
 * mounted at `basePath`. Returns null for anything outside `basePath` or
 * that would resolve outside `distDir` (e.g. via `..`) — this only ever
 * serves a local production build to a local test browser, but a static
 * file server should still never follow a path outside its own root.
 */
export function resolveStaticPath(
  urlPath: string,
  basePath: string,
  distDir: string,
): string | null {
  const withoutQuery = urlPath.split("?")[0] ?? "";
  const normalizedBase = basePath.endsWith("/")
    ? basePath.slice(0, -1)
    : basePath;

  if (
    withoutQuery !== normalizedBase &&
    !withoutQuery.startsWith(`${normalizedBase}/`)
  ) {
    return null;
  }

  let relative = withoutQuery.slice(normalizedBase.length);
  if (relative === "" || relative.endsWith("/")) {
    relative = `${relative}index.html`;
  }

  const resolvedDist = resolve(distDir);
  const resolvedTarget = resolve(resolvedDist, `.${relative}`);

  if (
    resolvedTarget !== resolvedDist &&
    !resolvedTarget.startsWith(`${resolvedDist}${sep}`)
  ) {
    return null;
  }

  return resolvedTarget;
}

async function main() {
  const port = Number(process.env.PORT ?? 4322);
  const basePath = process.env.BASE_PATH ?? "/iris-hep-llm-performance";
  const distDir = process.env.DIST_DIR ?? join(process.cwd(), "dist");

  const server = createServer(async (req, res) => {
    const filePath = req.url
      ? resolveStaticPath(req.url, basePath, distDir)
      : null;

    if (!filePath) {
      res.writeHead(404).end("Not found");
      return;
    }

    try {
      const info = await stat(filePath);
      const target = info.isDirectory()
        ? join(filePath, "index.html")
        : filePath;
      const body = await readFile(target);
      res.writeHead(200, {
        "content-type":
          MIME_TYPES[extname(target)] ?? "application/octet-stream",
      });
      res.end(body);
    } catch {
      res.writeHead(404).end("Not found");
    }
  });

  server.listen(port, () => {
    console.log(
      `e2e static server: http://localhost:${port}${basePath}/ (serving ${distDir})`,
    );
  });
}

// Guard so vitest can import resolveStaticPath without starting a server.
if (process.argv[1] && import.meta.url === `file://${process.argv[1]}`) {
  main();
}
