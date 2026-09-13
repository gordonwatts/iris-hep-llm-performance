import { expect, test } from "@playwright/test";

test("with nothing stored, the page follows the OS dark preference", async ({
  page,
}) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.goto("");
  await expect(page.locator("html")).not.toHaveAttribute("data-theme", /.+/);
  const background = await page
    .locator("body")
    .evaluate((el) => getComputedStyle(el).backgroundColor);
  // The dark surface-page token (#0c0c0d) — confirms the prefers-color-scheme
  // block actually took effect rather than the light default.
  expect(background).toBe("rgb(12, 12, 13)");
});

test("the toggle flips data-theme and persists the choice across navigation", async ({
  page,
}) => {
  await page.emulateMedia({ colorScheme: "light" });
  await page.goto("");

  const toggle = page.locator("#theme-toggle");
  await toggle.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");

  await page.goto("models/");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");

  await toggle.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});

test("an explicit light choice overrides a dark OS preference", async ({
  page,
}) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.goto("");

  await page.locator("#theme-toggle").click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");

  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});
