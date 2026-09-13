import { expect, test } from "@playwright/test";

test("the skip link is the first focus stop and jumps to main content", async ({
  page,
}) => {
  await page.goto("");

  await page.keyboard.press("Tab");
  const skipLink = page.locator(".skip-link");
  await expect(skipLink).toBeFocused();

  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeInViewport();
});

test("focus moves from the skip link into the header nav in document order", async ({
  page,
}) => {
  await page.goto("");

  await page.keyboard.press("Tab"); // skip link
  await page.keyboard.press("Tab"); // brand link
  await expect(page.locator(".site-header__brand")).toBeFocused();

  await page.keyboard.press("Tab"); // first nav link
  await expect(page.locator(".site-header__link").first()).toBeFocused();
});
