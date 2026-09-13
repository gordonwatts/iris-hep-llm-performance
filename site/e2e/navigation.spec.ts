import { expect, test } from "@playwright/test";

const SUITE_IDS = [
  "agc-tests",
  "analyiss-base-questions",
  "iris-hep-llm-questions",
  "spec-tests",
  "uchicago-mcp",
];

test("home lists every suite and each card links to a page that loads", async ({
  page,
}) => {
  await page.goto("");

  for (const id of SUITE_IDS) {
    await expect(page.locator(`a[href$="/suites/${id}/"]`)).toHaveCount(1);
  }

  await page
    .locator('a[href$="/suites/iris-hep-llm-questions/"]')
    .first()
    .click();
  await expect(page).toHaveURL(/\/suites\/iris-hep-llm-questions\/$/);
  await expect(page.locator("h1")).toContainText("IRIS-HEP analysis stack");
});

test("home shows the empty results state before any runs exist", async ({
  page,
}) => {
  await page.goto("");
  await expect(page.getByRole("status")).toContainText("No runs recorded yet");
});

test("a suite page lists every one of its questions and each link resolves", async ({
  page,
}) => {
  await page.goto("suites/iris-hep-llm-questions/");

  const questionLinks = page.locator(
    'a[href*="/suites/iris-hep-llm-questions/q"]',
  );
  await expect(questionLinks).toHaveCount(18);

  const firstHref = await questionLinks.first().getAttribute("href");
  const response = await page.request.get(firstHref!);
  expect(response.ok()).toBe(true);
});

test("a question page shows the fully rendered prompt, not the raw template", async ({
  page,
}) => {
  await page.goto("suites/iris-hep-llm-questions/q1/");

  const prompt = page.locator("#effective-prompt");
  await expect(prompt).toContainText(
    "Plot the ETmiss of all events in the rucio dataset user.zmarshal",
  );
  await expect(prompt).not.toContainText("{{");
});

test("the models page groups suites under each model selector", async ({
  page,
}) => {
  await page.goto("models/");
  await expect(page.locator("h1")).toContainText("Models");
  await expect(page.getByRole("status")).toContainText("No runs recorded yet");
});
