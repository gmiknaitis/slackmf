#!/usr/bin/env python3
# <swiftbar.title>Slack Status</swiftbar.title>
# <swiftbar.version>1.1</swiftbar.version>
# <swiftbar.desc>Shows unread DMs and channel mentions</swiftbar.desc>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>false</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

import json
import os
import urllib.request
from pathlib import Path

TOKEN_FILE = Path.home() / ".config" / "slack-menubar" / "token"

CLEAR_SYMBOL = "·"
ERROR_SYMBOL = "⚡"
OPEN_SLACK = "bash=open param1=-a param2=Slack terminal=false"


def get_token():
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return os.environ.get("SLACK_TOKEN", "")


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


token = get_token()

if not token:
    print("Slack: no token")
    print("---")
    print(f"Create token → https://api.slack.com/apps | href=https://api.slack.com/apps")
    print(f"Then save it to: {TOKEN_FILE}")
    raise SystemExit(0)

try:
    dm_unreads, channel_unreads, mention_count = fetch_counts(token)

    # mention_count (unread_count_display) is a subset of channel_unreads (unread_count)
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
    print(f"Open Slack | {OPEN_SLACK}")
    print("Refresh | refresh=true")

except Exception as e:
    print(ERROR_SYMBOL)
    print("---")
    print(f"Error: {e}")
    print("Refresh | refresh=true")
