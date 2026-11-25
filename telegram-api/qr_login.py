#!/usr/bin/env python3
"""One-time QR login for the Telethon Play 5 script.

Writes the login QR code to qr_login.png (refreshed every 25s while
waiting, since the token expires), waits until Hip scans it with
Telegram app -> Settings -> Devices -> Link Device, then saves the
session to telegram_api.session.
"""
import asyncio
import os
import sys
from urllib.parse import urlparse

import qrcode
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

HERE = os.path.dirname(os.path.abspath(__file__))
QR_PATH = os.path.join(HERE, "qr_login.png")
WAIT_SECS = 300  # give Hip up to 5 minutes to scan


def load_env() -> None:
    env_path = os.path.join(HERE, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def save_qr(url: str) -> None:
    img = qrcode.make(url)
    img.save(QR_PATH)


def http_proxy_tuple():
    """Egress HTTP proxy from env — direct MTProto is reset by the
    network, but CONNECT through this proxy reaches Telegram."""
    raw = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or ""
    u = urlparse(raw)
    if not u.hostname:
        return None
    return ("http", u.hostname, u.port or 3128, u.username, u.password)


async def main() -> int:
    load_env()
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    proxy = http_proxy_tuple()
    client = TelegramClient(
        os.path.join(HERE, "telegram_api"), api_id, api_hash, proxy=proxy
    )
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print("ALREADY_LOGGED_IN", me.username)
        await client.disconnect()
        return 0
    qr = await client.qr_login()
    save_qr(qr.url)
    print("QR_SAVED", QR_PATH, flush=True)
    deadline = asyncio.get_event_loop().time() + WAIT_SECS
    try:
        while True:
            try:
                await asyncio.wait_for(qr.wait(), timeout=25)
                break
            except asyncio.TimeoutError:
                if asyncio.get_event_loop().time() >= deadline:
                    print("QR_TIMEOUT", flush=True)
                    await client.disconnect()
                    return 3
                await qr.recreate()
                save_qr(qr.url)
                print("QR_REFRESHED", flush=True)
    except SessionPasswordNeededError:
        print("PASSWORD_NEEDED", flush=True)
        await client.disconnect()
        return 4
    me = await client.get_me()
    print("LOGGED_IN_AS", me.username)
    await client.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
