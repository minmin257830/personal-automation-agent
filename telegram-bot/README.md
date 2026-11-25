# Hip's Telegram Bot — စတင်ပုံစံ (starter)

အခု ရပြီ: `/start`, `/help`, `/ping`, စာပြန်ပြောတာ (echo) — `bot.py` မှာ ရှိတယ်။
Telethon သုံးထားတယ် (Play 5 script နဲ့ အတူတူ venv)။

## Bot token ယူနည်း (Hip ကိုယ်တိုင် လုပ်ရမှာ)
1. Telegram မှာ `@BotFather` ဖွင့် → `/newbot`
2. နာမည် ပေး → username ပေး (`bot` နဲ့ ဆုံးရမယ်)
3. ရလာတဲ့ token ကို ဘယ်သူ့ကိုမှ မပေး၊ chat မှာ မပို့နဲ့

## Run နည်း
```bash
BOT_TOKEN=<token> TELEGRAM_API_ID=<id> TELEGRAM_API_HASH=<hash> \
  ../telegram-api/.venv/bin/python bot.py
```
`TELEGRAM_API_ID` / `API_HASH` က Play5 app က ဟာတွေ — ဒီနေ့ 18:00 retry
အောင်မှ ရမယ်။ အဲ့ဒါတွေ မရှိသေးရင် bot က စလို့ မရဘူး (ရှင်းရှင်းပြောပြလိမ့်မယ်)။

## နောက်တစ်ဆင့်
Hip ပြောပေး: ဒီ bot က ဘာလုပ်စေချင်လဲ?
ဥပမာ — စာပြန်တဲ့ bot, ဂိမ်းဆော့တဲ့ bot, နေ့တိုင်း စာပို့တဲ့ bot။
ပြောပြီးရင် `bot.py` ထဲက TODO နေရာမှာ အဲ့ဒီအလုပ် ထည့်ပေးမယ်။
