/**
 * src/index.js — main entry
 * Run: npm start
 * Loads the saved session, then checks Telegram (and TikTok, optional).
 */
import { launchBrowser, hasSavedSession } from './browser.js';
import { getLatestMessage } from './telegram.js';
import { checkTikTokNotifications } from './tiktok.js';

if (!hasSavedSession()) {
  console.log('No saved session found. Run first: npm run auth');
  process.exit(1);
}

// Unattended check: run headless. There is no display on a cloud box,
// and Hip has only a phone — a visible (headed) browser would fail there.
// Manual login still uses a headed browser in src/auth.js.
const { browser, page } = await launchBrowser({ headless: true });

try {
  console.log('Checking Telegram...');
  const latest = await getLatestMessage(page);
  console.log('Latest Telegram message:', latest.text ?? '(none)');
  if (latest.note) console.log('Note:', latest.note);

  // TikTok is optional — uncomment if you want it on every run.
  // console.log('\nChecking TikTok...');
  // const tiktok = await checkTikTokNotifications(page);
  // console.log('TikTok:', tiktok);
} finally {
  await browser.close();
}
