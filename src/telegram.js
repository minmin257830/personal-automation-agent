/**
 * src/telegram.js — Step 3: read the most recent message
 *
 * getLatestMessage(page)
 *  - Goes to Telegram Web (assumes session is already loaded).
 *  - Waits for the chat list to load.
 *  - Opens the first / active chat if none is open.
 *  - Returns the text of the most recent message.
 *
 * NOTE: Telegram Web changes its HTML often. The selectors below try
 * several common patterns and fall back gracefully. If Telegram changes
 * its layout, update SELECTORS below — do not hard-code one fragile selector.
 * For reliable, long-term use, prefer Telegram's official API / Bot API
 * instead of scraping the web UI.
 */
const SELECTORS = {
  chatList: '.chat-list, [class*="chat-list"], .sidebar, #LeftColumn',
  chatItem: '.chat-list-item, [class*="chat-list-item"], .dialog, [data-peer-id]',
  messageText: '.text-content, .message .text, [class*="message"] .text-content, .bubble .text-content',
  messageBubble: '.message, .bubble, [class*="Message"]',
};

export async function getLatestMessage(page) {
  await page.goto('https://web.telegram.org/', { waitUntil: 'domcontentloaded' });

  // Wait for the chat list — this proves we are logged in.
  try {
    await page.waitForSelector(SELECTORS.chatList, { timeout: 30000 });
  } catch {
    throw new Error('Telegram chat list did not load. Are you logged in? Run: npm run auth');
  }

  // If no chat is open, open the first chat in the list.
  const hasOpenChat = await page.locator(SELECTORS.messageBubble).first().isVisible().catch(() => false);
  if (!hasOpenChat) {
    const firstChat = page.locator(SELECTORS.chatItem).first();
    await firstChat.waitFor({ timeout: 15000 });
    await firstChat.click();
    await page.waitForTimeout(2000);
  }

  // Read all visible message texts, return the last one.
  const texts = await page.locator(SELECTORS.messageText).allTextContents();
  const clean = texts.map((t) => t.trim()).filter(Boolean);
  if (clean.length === 0) {
    return { text: null, note: 'No message text found in the active chat (selectors may have changed).' };
  }
  return { text: clean[clean.length - 1], count: clean.length };
}
