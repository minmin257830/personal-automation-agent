/**
 * src/tiktok.js — TikTok notifications (starter, with a warning)
 *
 * TikTok Web aggressively blocks automation and changes its layout often.
 * This function only opens TikTok with your saved session and checks
 * whether the inbox/notifications page loads. It does NOT bypass
 * logins, captchas, or blocks, and it does NOT scrape at scale.
 *
 * For reliable use, prefer TikTok's official API / Research API where
 * available, and respect TikTok's Terms of Service and rate limits.
 * If TikTok shows a captcha / login wall, stop and log in manually.
 */
export async function checkTikTokNotifications(page) {
  await page.goto('https://www.tiktok.com/inbox', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);
  const title = await page.title();
  const bodyText = (await page.locator('body').innerText().catch(() => '')).slice(0, 500);
  return { title, snippet: bodyText, note: 'If you see a login/captcha page, TikTok blocked automation — log in manually and try later.' };
}
