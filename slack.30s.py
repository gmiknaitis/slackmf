#!/usr/bin/env python3
# <swiftbar.title>Slack Status</swiftbar.title>
# <swiftbar.version>1.2</swiftbar.version>
# <swiftbar.desc>Shows unread DMs and channel mentions</swiftbar.desc>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>false</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "slack-menubar"
TOKEN_FILE = CONFIG_DIR / "token"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_FILE = CONFIG_DIR / "cache.json"
SCRIPT_PATH = Path(__file__).resolve()

CLEAR_SYMBOL = "·"
ERROR_SYMBOL = "⚡"
OPEN_SLACK = "bash=open param1=-a param2=Slack terminal=false"

DEFAULT_INTERVAL = 60
INTERVALS = [
    (30, "30 seconds"),
    (60, "1 minute"),
    (120, "2 minutes"),
    (300, "5 minutes"),
]


def get_token():
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return os.environ.get("SLACK_TOKEN", "")


def load_config():
    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {"interval": DEFAULT_INTERVAL}


def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config))


def load_cache():
    try:
        return json.loads(CACHE_FILE.read_text())
    except Exception:
        return None


def save_cache(dm_unreads, channel_unreads, mention_count):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({
        "dm_unreads": dm_unreads,
        "channel_unreads": channel_unreads,
        "mention_count": mention_count,
        "fetched_at": time.time(),
    }))


def slack_get(method, token, **params):
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"https://slack.com/api/{method}?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    if not data.get("ok"):
        raise RuntimeError(data.get("error", "unknown error"))
    return data


def fetch_counts(token):
    dm_unreads = 0
    channel_unreads = 0
    mention_count = 0

    cursor = None
    while True:
        kwargs = dict(
            types="im,mpim,public_channel,private_channel",
            limit=200,
            exclude_archived="true",
        )
        if cursor:
            kwargs["cursor"] = cursor
        data = slack_get("conversations.list", token, **kwargs)
        for ch in data.get("channels", []):
            if ch.get("is_im") or ch.get("is_mpim"):
                dm_unreads += ch.get("unread_count", 0) or 0
            else:
                channel_unreads += ch.get("unread_count", 0) or 0
                mention_count += ch.get("unread_count_display", 0) or 0
        cursor = (data.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break

    return dm_unreads, channel_unreads, mention_count


if len(sys.argv) == 3 and sys.argv[1] == "--set-interval":
    config = load_config()
    config["interval"] = int(sys.argv[2])
    save_config(config)
    sys.exit(0)


token = get_token()
config = load_config()
interval = config.get("interval", DEFAULT_INTERVAL)

if not token:
    print("Slack: no token")
    print("---")
    print(f"Create token → https://api.slack.com/apps | href=https://api.slack.com/apps")
    print(f"Then save it to: {TOKEN_FILE}")
    raise SystemExit(0)

try:
    cache = load_cache()
    now = time.time()

    if cache and (now - cache.get("fetched_at", 0)) < interval:
        dm_unreads = cache["dm_unreads"]
        channel_unreads = cache["channel_unreads"]
        mention_count = cache["mention_count"]
    else:
        dm_unreads, channel_unreads, mention_count = fetch_counts(token)
        save_cache(dm_unreads, channel_unreads, mention_count)

    other_channel = max(0, channel_unreads - mention_count)

    parts = []
    if dm_unreads:
        parts.append(f"✉{dm_unreads}")
    if mention_count:
        parts.append(f"@{mention_count}")
    if other_channel:
        parts.append(f"#{other_channel}")

    title = " ".join(parts) if parts else CLEAR_SYMBOL
    print(f"{title} | {OPEN_SLACK}")
    print("---")
    if dm_unreads:
        print(f"DMs: {dm_unreads} unread")
    if mention_count:
        print(f"Mentions: {mention_count}")
    if other_channel:
        print(f"Channels: {other_channel} unread")
    if not dm_unreads and not channel_unreads:
        print("All clear")
    print("---")
    print("Refresh interval")
    for secs, label in INTERVALS:
        check = " ✓" if secs == interval else ""
        print(f"-- {label}{check} | bash={SCRIPT_PATH} param1=--set-interval param2={secs} terminal=false refresh=true")
    print("---")
    print(f"Open Slack | {OPEN_SLACK}")
    print("Refresh | refresh=true")

except Exception as e:
    print(ERROR_SYMBOL)
    print("---")
    print(f"Error: {e}")
    print("Refresh | refresh=true")
