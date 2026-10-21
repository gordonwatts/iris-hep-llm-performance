import { defineConfig, devices } from "@playwright/test";

// Astro's `base` means every route sits under /iris-hep-llm-performance/ —
// baseURL carries that so tests can use page.goto("/") for the site root.
const PORT = 4322;
const BASE_PATH = "/iris-hep-llm-performance";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: "list",
  use: {
    // Trailing slash matters: with it, a relative goto("suites/x/") merges
    // onto this path; a *leading*-slash goto("/suites/x/") would still reset
    // to the origin root regardless, per URL resolution rules — so every
    // test navigates with relative (no leading slash) paths.
    baseURL: `http://localhost:${PORT}${BASE_PATH}/`,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    // Runs against a real production build, not the dev server, so the e2e
    // suite exercises exactly what gets deployed. Serves via
    // scripts/e2e-static-server.ts rather than `astro preview`: Astro 7's
    // preview command manages its own background daemon and the CLI process
    // that starts it exits immediately, which Playwright treats as the
    // server having crashed even though the daemon is still serving fine.
    command: `npm run build && PORT=${PORT} BASE_PATH=${BASE_PATH} node scripts/e2e-static-server.ts`,
    url: `http://localhost:${PORT}${BASE_PATH}/`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
