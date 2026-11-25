#!/usr/bin/env python3
"""
Hip's own Telegram bot — starter template (Telethon bot client).

What it does now (ready to run once a bot token exists):
  /start  -> Burmese welcome message
  /help   -> what the bot can do
  /ping   -> replies "pong" (proves the bot is alive)
  any other text -> echoes it back

What it does NOT do yet: whatever Hip wants it to do next.
Tell Muse the bot's job (e.g. reply to messages, play a game,
send a daily message, forward something) and the behaviour goes
in the `handle_message` section marked TODO below.

Setup (one time, Hip does this himself):
  1. In Telegram, open @BotFather -> /newbot -> pick a name and a
     username ending in "bot" -> BotFather gives a token.
  2. Set env var BOT_TOKEN to that token. Never paste the token
     in chat and never share it — it is password-equivalent.
  3. Run:  ../telegram-api/.venv/bin/python bot.py
     (reuses the Telethon install from the Play 5 script)

The bot session is saved to mybot.session next to this file.
"""
import asyncio
import os
import sys

from telethon import TelegramClient, events

API_ID = int(os.environ.get("TELEGRAM_API_ID", "0") or 0)
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

WELCOME = (
    "မင်္ဂလာပါ။ ကျွန်တော် Hip ရဲ့ bot ပါ။\n"
    "/help လို့ ရိုက်ရင် ကျွန်တော် ဘာလုပ်နိုင်လဲ ပြမယ်။"
)
HELP = (
    "လုပ်နိုင်တာတွေ:\n"
    "/start — ကြိုဆိုစာ\n"
    "/ping — bot အသက်ရှင်လား စမ်းတာ\n"
    "တခြားစာ — ပြန်ပြောပေးတာ (echo)\n"
    "\n"
    "နောက်ထပ် ဘာလုပ်စေချင်လဲ Hip ကို မေးဦး။"
)


async def main() -> None:
    if not BOT_TOKEN:
        print("BOT_TOKEN env var is not set. Set it, then run again.")
        print("Get a token from @BotFather (/newbot) — do not paste it in chat.")
        sys.exit(2)
    # Bot API via Telethon still needs api_id/api_hash; reuse the
    # Play 5 app's credentials if they exist, else fall back to
    # Telegram's test values are NOT used — fail clearly instead.
    if not API_ID or not API_HASH:
        print("TELEGRAM_API_ID / TELEGRAM_API_HASH are not set.")
        print("These come from the my.telegram.org/apps app (Play5).")
        print("Once the 18:00 app retry succeeds, set them and run again.")
        sys.exit(2)

    client = TelegramClient("mybot", API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    me = await client.get_me()
    print(f"Bot running as @{me.username}")

    @client.on(events.NewMessage(pattern="/start"))
    async def start(event):
        await event.reply(WELCOME)

    @client.on(events.NewMessage(pattern="/help"))
    async def help_(event):
        await event.reply(HELP)

    @client.on(events.NewMessage(pattern="/ping"))
    async def ping(event):
        await event.reply("pong")

    @client.on(events.NewMessage)
    async def handle_message(event):
        # Ignore our own command handlers above (they already replied).
        if event.raw_text.startswith("/"):
            return
        # TODO: Hip's bot job goes here — replace the echo with it.
        await event.reply(f"မင်း ပို့လိုက်တာ: {event.raw_text}")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
