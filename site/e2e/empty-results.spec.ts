import { expect, test } from "@playwright/test";

test("home shows the empty results state before any runs exist", async ({
  page,
}) => {
  await page.goto("");
  const status = page.getByRole("status");
  await expect(status).toBeVisible();
  await expect(status).toHaveText("No runs recorded yet for any suite.");
  await expect(page.getByRole("link", { name: "View results" })).toHaveCount(0);
});

test("models shows the empty results state before any runs exist", async ({
  page,
}) => {
  await page.goto("models/");
  const status = page.getByRole("status").filter({ hasText: "for any model." });
  await expect(status).toBeVisible();
  await expect(status).toHaveText("No runs recorded yet for any model.");
});
