#!/usr/bin/env python3
"""Test which route reaches Telegram MTProto from this VM:
A) obfuscated direct, B) default via HTTP egress proxy, C) obfuscated via proxy.
Prints one line per mode: OK / FAIL <error>. Credentials are read from
env only, never printed.
"""
import asyncio
import os
import sys
from urllib.parse import urlparse

from telethon import TelegramClient
from telethon.network import ConnectionTcpAbridged, ConnectionTcpObfuscated

HERE = os.path.dirname(os.path.abspath(__file__))


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


async def try_mode(name: str, **kwargs) -> None:
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    client = TelegramClient(os.path.join(HERE, "telegram_api"), api_id, api_hash, **kwargs)
    try:
        await asyncio.wait_for(client.connect(), timeout=25)
        print(name, "OK connected", flush=True)
        await client.disconnect()
    except Exception as e:  # noqa: BLE001 - report any failure mode
        print(name, "FAIL", type(e).__name__, str(e)[:120], flush=True)


async def main() -> None:
    load_env()
    proxy = http_proxy_tuple()
    await try_mode("A-obfuscated-direct", connection=ConnectionTcpObfuscated)
    if proxy:
        await try_mode("B-default-via-http-proxy", proxy=proxy)
        await try_mode(
            "C-obfuscated-via-http-proxy",
            connection=ConnectionTcpObfuscated,
            proxy=proxy,
        )
    else:
        print("no http proxy in env", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
