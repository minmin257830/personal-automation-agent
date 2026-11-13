/**
 * src/auth-qr.js — Phone-only login (QR code, headless)
 * Run: npm run auth:qr
 *
 * Hip has only a phone — no laptop/Mac — so the headed login in
 * src/auth.js cannot run for him. This script is the phone-only path:
 *
 * 1. Opens Telegram Web in a headless browser (no visible window needed).
 * 2. Saves a screenshot of the login / QR page to auth/login-qr.png.
 *    Muse shows that screenshot in chat.
 * 3. Hip scans the QR with his phone: Telegram app > Settings >
 *    Devices > Link Desktop Device (or he logs in by phone number
 *    in the Telegram app — the QR is the desktop-web login).
 * 4. This script waits up to 3 minutes for his chats to load,
 *    then saves cookies + localStorage to auth/session.json.
 * 5. Next run, `npm start` loads that session — no login again.
 *
 * NEVER share auth/login-qr.png or auth/session.json — the QR is a
 * login code and the session file works like a password. Both live
 * under auth/, which is gitignored. If the QR expires, just re-run
 * this script for a fresh one. If login stops working later, delete
 * auth/session.json and run this again.
 */
import { chromium } from 'playwright';
import { mkdirSync, existsSync } from 'node:fs';

const SESSION_PATH = 'auth/session.json';
const QR_PATH = 'auth/login-qr.png';
const LOGIN_URL = 'https://web.telegram.org/';
const CHAT_LIST = '.chat-list, [class*="chat-list"], .sidebar, #LeftColumn';

mkdirSync('auth', { recursive: true });

let browser;
try {
  browser = await chromium.launch({
    headless: true,
    ...(process.env.PLAYWRIGHT_CHROMIUM_PATH
      ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH }
      : {}),
  });
} catch (err) {
  console.error('Could not start Chromium:', err.message);
  console.error('\nChromium is not installed on this machine yet. Run:');
  console.error('  npx playwright install chromium');
  console.error('then run this script again: npm run auth:qr');
  process.exit(1);
}

const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await context.newPage();

console.log(`Opening ${LOGIN_URL} ...`);
await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(6000);
await page.screenshot({ path: QR_PATH });
console.log(`\nLogin QR screenshot saved to ${QR_PATH}`);
console.log('Scan it with your phone: Telegram > Settings > Devices > Link Desktop Device.');
console.log('Waiting up to 3 minutes for your chats to load...');

try {
  await page.waitForSelector(CHAT_LIST, { timeout: 180000 });
} catch {
  console.error('\nChats did not load in 3 minutes — the QR may have expired.');
  console.error('Re-run for a fresh QR: npm run auth:qr');
  await browser.close();
  process.exit(1);
}

await context.storageState({ path: SESSION_PATH });
console.log(`\nLogged in. Session saved to ${SESSION_PATH}`);
console.log('Next: npm start');
await browser.close();

// Keep the QR screenshot out of any shared copy: it is a login code.
// It stays under auth/ (gitignored) and should be deleted after use.
if (existsSync(QR_PATH)) {
  console.log(`Note: delete ${QR_PATH} after login — it is a login code, do not share it.`);
}
