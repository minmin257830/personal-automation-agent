#!/usr/bin/env python3
"""Print the latest messages from @imimimhdbhbot (game status check)."""
import asyncio
import os
import sys
from urllib.parse import urlparse

from telethon import TelegramClient

HERE = os.path.dirname(os.path.abspath(__file__))
BOT = "@imimimhdbhbot"


def load_env() -> None:
    env_path = os.path.join(HERE, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def http_proxy_tuple():
    raw = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or ""
    u = urlparse(raw)
    if not u.hostname:
        return None
    return ("http", u.hostname, u.port or 3128, u.username, u.password)


async def main() -> int:
    load_env()
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    client = TelegramClient(
        os.path.join(HERE, "telegram_api"), api_id, api_hash, proxy=http_proxy_tuple()
    )
    await client.connect()
    if not await client.is_user_authorized():
        print("NOT_LOGGED_IN")
        await client.disconnect()
        return 2
    msgs = await client.get_messages(BOT, limit=5)
    for m in msgs:
        print(f"--- {m.date} (id {m.id}) ---")
        print(m.text or "(no text)")
    await client.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
