/**
 * src/auth.js — Step 2: login session (manual login, then save)
 * Run: npm run auth
 *
 * 1. Opens Telegram Web in a visible browser.
 * 2. YOU log in manually (phone number / QR code, as normal).
 * 3. When you see your chats, press ENTER in this terminal.
 * 4. Cookies + localStorage are saved to auth/session.json.
 *
 * Next run, the agent loads auth/session.json and you stay logged in.
 * NEVER share auth/session.json — it works like a password.
 * If login stops working, delete auth/session.json and run npm run auth again.
 */
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import readline from 'node:readline';

const SESSION_PATH = 'auth/session.json';
const LOGIN_URL = process.argv[2] || 'https://web.telegram.org/';

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const waitForEnter = (q) => new Promise((resolve) => rl.question(q, resolve));

const browser = await chromium.launch({ headless: false });
const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await context.newPage();

console.log(`Opening ${LOGIN_URL}`);
console.log('Log in manually in the browser window.');
await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded' });

await waitForEnter('\nAfter you are logged in and see your chats, press ENTER here... ');

mkdirSync('auth', { recursive: true });
await context.storageState({ path: SESSION_PATH });

console.log(`\nSession saved to ${SESSION_PATH}`);
console.log('Next: npm start');
await browser.close();
rl.close();
