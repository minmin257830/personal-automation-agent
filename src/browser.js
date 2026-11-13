/**
 * src/browser.js — shared browser helpers
 * - launchBrowser(): starts Chromium (headed by default so you can log in manually)
 * - loadSession(): reuses saved session if auth/session.json exists
 */
import { chromium } from 'playwright';
import { existsSync } from 'node:fs';

export const SESSION_PATH = 'auth/session.json';

export function hasSavedSession() {
  return existsSync(SESSION_PATH);
}

export async function launchBrowser({ headless = false } = {}) {
  // NOTE: storageState is a BrowserContext option, not a launch option —
  // it is applied to newContext() below. Do not pass it to launch().
  // PLAYWRIGHT_CHROMIUM_PATH lets a machine with a system Chromium
  // (instead of Playwright's downloaded one) point at it, e.g.:
  //   PLAYWRIGHT_CHROMIUM_PATH=/usr/bin/chromium npm start
  const browser = await chromium.launch({
    headless,
    ...(process.env.PLAYWRIGHT_CHROMIUM_PATH
      ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH }
      : {}),
  });
  const context = await browser.newContext({
    // Reuse the saved storageState if present, otherwise fresh context.
    ...(hasSavedSession() ? { storageState: SESSION_PATH } : {}),
    viewport: { width: 1280, height: 800 },
  });
  const page = await context.newPage();
  return { browser, context, page };
}
