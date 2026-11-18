import { defineConfig, devices } from "@playwright/test";

const PORT = 4322;
const EMPTY_RESULTS_PORT = 4323;
const BASE_PATH = "/iris-hep-llm-performance";
const BASE_URL = `http://localhost:${PORT}${BASE_PATH}/`;
const EMPTY_RESULTS_URL = `http://localhost:${EMPTY_RESULTS_PORT}${BASE_PATH}/`;
const EMPTY_RESULTS_DIST = ".generated/e2e-empty-results";
const EMPTY_RESULTS_SPEC = "**/empty-results.spec.ts";
// Playwright needs a foreground process. `astro preview` starts a daemon
// and exits, which Playwright treats as the server having crashed.
const STATIC_SERVER = "node scripts/e2e-static-server.ts";

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
    baseURL: BASE_URL,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      testIgnore: EMPTY_RESULTS_SPEC,
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "chromium-empty-results",
      testMatch: EMPTY_RESULTS_SPEC,
      use: { ...devices["Desktop Chrome"], baseURL: EMPTY_RESULTS_URL },
    },
  ],
  webServer: [
    {
      // Playwright starts these servers in order. Build the empty fixture first
      // so the normal build leaves the shared report and index in their usual state.
      command: `npm run build -- --outDir ${EMPTY_RESULTS_DIST} && ${STATIC_SERVER}`,
      env: {
        RESULTS_DIR: "e2e/fixtures/empty-results",
        DIST_DIR: EMPTY_RESULTS_DIST,
        BASE_PATH,
        PORT: String(EMPTY_RESULTS_PORT),
      },
      url: EMPTY_RESULTS_URL,
      timeout: 120_000,
    },
    {
      command: `npm run build && ${STATIC_SERVER}`,
      env: { BASE_PATH, DIST_DIR: "dist", PORT: String(PORT) },
      url: BASE_URL,
      timeout: 120_000,
    },
  ],
});
