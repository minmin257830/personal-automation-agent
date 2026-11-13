/**
 * setup.js — Step 1: initial setup
 * Run: npm install && npm run setup
 * This only checks Node + Playwright and installs the Chromium browser.
 * It does NOT log in for you and does NOT store any password.
 */
import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';

console.log('Personal Automation Agent — setup');
console.log('Node:', process.version);

if (!existsSync('node_modules/playwright')) {
  console.log('Installing dependencies...');
  execSync('npm install', { stdio: 'inherit' });
} else {
  console.log('Dependencies already installed.');
}

console.log('Installing Playwright Chromium...');
execSync('npx playwright install chromium', { stdio: 'inherit' });

console.log('\nSetup done.');
console.log('Next: npm run auth   (log in manually once, session will be saved)');
console.log('Then: npm start      (load session and check Telegram)');
