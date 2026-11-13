# Personal Automation Agent — Node.js + Playwright

မင်းရဲ့ ကိုယ်ပိုင် Telegram Web နဲ့ TikTok အကောင့်တွေကို browser ဖွင့်ပြီး အခြေခံ task တွေ လုပ်ပေးတဲ့ agent ရဲ့ အခြေခံပုံစံ။

## အဆင့် ၁ — Setup

```bash
npm install
npm run setup
```

`setup.js` က Node နဲ့ Playwright Chromium ကို စစ်ပြီး သွင်းပေးတယ်။

## အဆင့် ၂ — Login (တစ်ခါပဲ ကိုယ်တိုင် ဝင်ရမယ်)

```bash
npm run auth
```

- Browser ပွင့်လာမယ်၊ `web.telegram.org` မှာ ကိုယ်တိုင် log in လုပ် (QR / ဖုန်းနံပါတ် — ပုံမှန်အတိုင်း)။
- Chat တွေ မြင်ရပြီဆိုရင် terminal မှာ ENTER နှိပ်။
- Cookies + localStorage က `auth/session.json` မှာ သိမ်းသွားမယ်။

TikTok အတွက်လည်း `npm run auth https://www.tiktok.com/` လို့ URL ပေးပြီး အလားတူ လုပ်လို့ရတယ်။

## ဖုန်းပဲရှိရင် — QR နဲ့ log in လုပ်နည်း (အသစ်)

မင်းမှာ ဖုန်းပဲရှိပြီး laptop / Mac မရှိတော့၊ အပေါ်က `npm run auth` (browser မြင်ရတဲ့အတိုင်း ပွင့်တာ) က cloud box ပေါ်မှာ run လို့မရဘူး။ အဲ့အစား QR နည်းကို သုံး —

```bash
npm run auth:qr
```

- Headless browser (မျက်နှာပြင် မပြဘဲ) ပွင့်ပြီး Telegram Web ရဲ့ QR ကို `auth/login-qr.png` အဖြစ် သိမ်းပေးတယ်။
- အဲ့ပုံကို Muse က chat မှာ ပြမယ် — မင်း ဖုန်းက Telegram app ထဲက **Settings > Devices > Link Desktop Device** နဲ့ scan လုပ်။
- Chat တွေ load ဖြစ်လာရင် (၃ မိနစ်အထိ စောင့်တယ်) session က `auth/session.json` မှာ သိမ်းသွားမယ်။ ပြီးရင် `npm start` ပဲ။
- QR သက်တမ်းကုန်သွားရင် `npm run auth:qr` ပြန်လုပ်ပြီး QR အသစ် ယူ။

**သတိထား:** `auth/login-qr.png` က log in code ပဲ — ဘယ်သူ့ကိုမှ မပြ၊ သုံးပြီးရင် ဖျက်ပစ်။ `auth/` တစ်ဖိုင်လုံး `.gitignore` မှာ ပါပြီးသား။

မှတ်ချက် (2026-11-13 စစ်ထားတာ): `npm install` ရပြီး file တွေ syntax မှန်တယ်၊ session မရှိသေးရင် `npm start` က "No saved session found. Run first: npm run auth" လို့ မှန်မှန်ပြတယ်။ ဒါပေမယ့် Chromium browser download (`npx playwright install chromium`) က ဒီ Muse ကွန်ပျူတာမှာ အခု run လို့မရသေးဘူး — download ပိတ်ထားလို့။ ဒါကြောင့် QR login ကို အပြည့်အစုံ live စမ်းဖို့ `npx playwright install chromium` အရင် run ရမယ့် စက်မှာ လုပ်ရမယ်။

**သတိထား:** `auth/session.json` က password နဲ့ တူတယ် — ဘယ်သူ့ကိုမှ မပေး၊ GitHub မှာ မတင်။ `.gitignore` မှာ ပါပြီးသား။ Login ပျက်သွားရင် အဲ့ဖိုင်ကို ဖျက်ပြီး `npm run auth` ပြန်လုပ်။

## အဆင့် ၃ — Telegram စာဖတ်ခြင်း

```bash
npm start
```

- Headless (မျက်နှာပြင် မပြဘဲ) run တယ် — cloud box / ဖုန်းပဲ ရှိတဲ့အခါ အဆင်ပြေအောင်။ ကိုယ်တိုင် log in လုပ်ရတဲ့ `npm run auth` ကတော့ browser မြင်ရတဲ့အတိုင်း (headed) ပွင့်တယ်။
- Saved session ကို load လုပ်တယ်။
- Telegram Web ကို သွားတယ်၊ chat list load ဖြစ်အောင် စောင့်တယ်။
- Active chat မရှိရင် ပထမ chat ကို ဖွင့်တယ်။
- နောက်ဆုံး message ရဲ့ စာကို print ထုတ်တယ် — `src/telegram.js` က `getLatestMessage()` မှာ ရှိတယ်။

Telegram Web က HTML မကြာခဏ ပြောင်းတယ်။ Selector တွေ အလုပ်မလုပ်တော့ရင် `src/telegram.js` က `SELECTORS` ကို ပြင်ရမယ်။ ရေရှည် သုံးဖို့ဆိုရင် Telegram official API / Bot API က ပိုခိုင်မာတယ်။

## TikTok

`src/tiktok.js` က `checkTikTokNotifications()` — inbox page load ဖြစ်မဖြစ် စစ်တာပဲ။ TikTok က automation ကို ပြင်းပြင်းထန်ထန် ပိတ်တယ်၊ captcha / login wall ပေါ်လာရင် ရပ်ပြီး ကိုယ်တိုင် ဝင်ရမယ်။ Official TikTok API သုံးတာ အကောင်းဆုံးပဲ။ Terms နဲ့ rate limit ကို လေးစားပါ။

## ဖိုင်များ

- `package.json` — dependencies + scripts
- `setup.js` — အဆင့် ၁ setup
- `src/auth.js` — အဆင့် ၂ manual login + session save
- `src/browser.js` — browser launch + session load
- `src/telegram.js` — အဆင့် ၃ latest message
- `src/tiktok.js` — TikTok notifications စစ်တာ
- `src/index.js` — main entry (`npm start`)

## boxes.dev မှာ သုံးဖို့

ဒီ project folder ကို boxes.dev ရဲ့ template box အဖြစ် တင်ဖို့ — boxes.dev app မှာ Step 2 prompt ကို Claude Code / Codex ထဲမှာ paste လုပ်၊ `npm i -g @boxes-dev/cli`, `dvb agent-init` run လုပ်၊ approve လုပ်ပါ။ Coarena API သုံးမယ်ဆိုရင်:
```bash
export ANTHROPIC_BASE_URL=https://coarena.ai/api
export ANTHROPIC_AUTH_TOKEN=မင်းရဲ့-key
```
API key ကို chat မှာ မမျှ၊ session file လိုပဲ လျှို့ဝှက်ထားပါ။
