#!/usr/bin/env python3
"""
Press "▶️ Play 5 ပွဲ" in @imimimhdbhbot WITHOUT a browser — via the
Telegram MTProto API (Telethon user client).

Why this exists: the cloud browser asks for approval every time it opens
web.telegram.org, and that approval cannot be made permanent, so the
00:02 scheduled run fails while Hip is offline. This script runs on
Muse's computer, needs no browser and no approval card.

Setup (one time, Hip does the login himself):
  1. Create an app at https://my.telegram.org/apps to get api_id / api_hash.
  2. Set env vars TELEGRAM_API_ID and TELEGRAM_API_HASH.
  3. Run:  .venv/bin/python press_play5.py --login
     - QR login: scan the QR code with the Telegram app
       (Settings -> Devices -> Link Device), same as Telegram Web.
     - The session is saved to telegram_api.session — it is
       password-equivalent: NEVER share it, never commit it.

Daily run (no login needed, session is reused):
  .venv/bin/python press_play5.py
Finds the most recent message in @imimimhdbhbot carrying the inline
button "▶️ Play 5 ပွဲ" (it moves up as new messages arrive, so the
script scans back through recent messages), clicks it ONCE, then
WATCHES until the bot's "5 ပွဲလုံး ကစားခြင်း ပြီးဆုံးပါပြီ" message
appears. If the bot goes quiet for 5 minutes (no new message at all),
it presses the button again (up to 3 presses total) and keeps
watching, for up to 45 minutes.
"""
import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

from telethon import TelegramClient


def http_proxy_tuple():
    """Egress HTTP proxy from env — direct MTProto is reset by the
    network, but CONNECT through this proxy reaches Telegram."""
    raw = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or ""
    u = urlparse(raw)
    if not u.hostname:
        return None
    return ("http", u.hostname, u.port or 3128, u.username, u.password)

BOT = "@imimimhdbhbot"
BUTTON_TEXT = "▶️ Play 5 ပွဲ"
COMPLETION_TEXT = "ပြီးဆုံးပါပြီ"
SCAN_LIMIT = 200  # how far back to look for the button message
POLL_SECS = 60  # check the bot's messages every minute
STALL_SECS = 300  # no new bot message for 5 min = stalled, press again
MAX_PRESSES = 3  # at most 3 presses per run
WATCH_SECS = 2700  # give up watching after 45 minutes total


async def login(client: TelegramClient) -> None:
    """QR login — Hip scans the code with his Telegram app."""
    print("QR login: Telegram app -> Settings -> Devices -> Link Device,")
    print("then scan the QR code printed below.")
    qr = await client.qr_login()
    qr.print()
    await qr.wait()
    print("Logged in as:", (await client.get_me()).username)


async def press_once(client: TelegramClient) -> bool:
    """Find the Play 5 button and click it once. Returns True if clicked."""
    async for msg in client.iter_messages(BOT, limit=SCAN_LIMIT):
        if not msg.reply_markup:
            continue
        for row in msg.reply_markup.rows:
            for btn in row.buttons:
                if BUTTON_TEXT in (btn.text or ""):
                    if getattr(btn, "url", None):
                        print("Button is a URL button, not a callback:", btn.url)
                        return False
                    print(f"Found button in message {msg.id} ({msg.date}), clicking once...")
                    await msg.click(text=btn.text)
                    return True
    print(f"Button '{BUTTON_TEXT}' not found in the last {SCAN_LIMIT} messages.")
    return False


async def latest_bot_messages(client: TelegramClient, limit: int = 10):
    """Newest bot messages first."""
    return await client.get_messages(BOT, limit=limit)


async def check_completion(client: TelegramClient, since) -> bool:
    """True if the bot's '5 games finished' message newer than `since`
    has appeared."""
    for msg in await latest_bot_messages(client):
        if (
            msg.date
            and msg.date > since
            and COMPLETION_TEXT in (msg.text or "")
        ):
            print(f"Completion message found: {msg.text.splitlines()[0]}")
            return True
    return False


async def press_and_watch(client: TelegramClient) -> bool:
    """Press once, then watch until the 5 games finish. If the bot goes
    quiet for STALL_SECS (no new message), press again (up to
    MAX_PRESSES total) and keep watching, up to WATCH_SECS total.
    Returns True if a completion message was seen."""
    loop = asyncio.get_event_loop()
    if not await press_once(client):
        return False
    presses = 1
    since = datetime.now(timezone.utc)
    msgs = await latest_bot_messages(client)
    last_id = max((m.id for m in msgs), default=0)
    last_progress = loop.time()
    started = loop.time()
    while True:
        if await check_completion(client, since):
            return True
        msgs = await latest_bot_messages(client)
        newest_id = max((m.id for m in msgs), default=0)
        if newest_id > last_id:
            # Any new bot message counts as progress (match started,
            # Level 50, ...).
            last_id = newest_id
            last_progress = loop.time()
        if loop.time() - last_progress >= STALL_SECS and presses < MAX_PRESSES:
            print(
                f"Stalled: no new bot message for {STALL_SECS // 60} min, "
                f"pressing again ({presses + 1}/{MAX_PRESSES})..."
            )
            if not await press_once(client):
                return False
            presses += 1
            last_progress = loop.time()
            msgs = await latest_bot_messages(client)
            last_id = max((m.id for m in msgs), default=last_id)
        if loop.time() - started >= WATCH_SECS:
            print("Gave up watching after 45 minutes, no completion message.")
            return False
        await asyncio.sleep(POLL_SECS)


def load_env(here: str) -> None:
    """Load TELEGRAM_API_ID / TELEGRAM_API_HASH from .env next to the script."""
    env_path = os.path.join(here, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", action="store_true", help="QR login, save session")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    load_env(here)
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    client = TelegramClient(
        os.path.join(here, "telegram_api"), api_id, api_hash, proxy=http_proxy_tuple()
    )

    await client.connect()
    if args.login:
        if not await client.is_user_authorized():
            await login(client)
        else:
            print("Already logged in as:", (await client.get_me()).username)
        await client.disconnect()
        return 0

    if not await client.is_user_authorized():
        print("Not logged in yet. Run with --login first.")
        await client.disconnect()
        return 2

    clicked = await press_and_watch(client)
    last = await client.get_messages(BOT, limit=1)
    print("Latest bot message:", last[0].text if last else "(none)")
    await client.disconnect()
    return 0 if clicked else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
