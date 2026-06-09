# slackmf

A minimal macOS menubar indicator for Slack unread counts. Shows DMs, mentions, and channel unreads as a quiet status icon — no badges, no sounds, no distractions.

## What it shows

- `·` — all clear
- `✉3` — 3 unread DMs / group DMs
- `@2` — 2 channel mentions
- `#41` — 41 other unread channel messages
- `⚡` — error (see dropdown for details)

Clicking the menubar item opens Slack.

## Prerequisites

- macOS
- [SwiftBar](https://github.com/swiftbar/SwiftBar) (`brew install --cask swiftbar`)
- Python 3 (`brew install python3`)
- A Slack user token (see below)

## Setup

### 1. Get a Slack token

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Under **OAuth & Permissions → User Token Scopes**, add:
   - `channels:read`
   - `groups:read`
   - `im:read`
   - `mpim:read`
3. Click **Install to Workspace** and copy the **User OAuth Token** (starts with `xoxp-`)

### 2. Save the token

```bash
mkdir -p ~/.config/slack-menubar
echo "xoxp-your-token-here" > ~/.config/slack-menubar/token
```

### 3. Install the plugin

Copy (or symlink) the plugin into your SwiftBar plugins folder:

```bash
cp slack.2m.py "$HOME/Library/Application Support/SwiftBar/Plugins/"
```

Or symlink to keep it in sync with this repo:

```bash
ln -s "$(pwd)/slack.2m.py" "$HOME/Library/Application Support/SwiftBar/Plugins/slack.2m.py"
```

### 4. Launch SwiftBar

```bash
open /Applications/SwiftBar.app
```

Point it to `~/Library/Application Support/SwiftBar/Plugins` when prompted.

## Configuration

**Refresh rate** is controlled by the filename. Rename to change it:

| Filename | Refresh |
|---|---|
| `slack.30s.py` | Every 30 seconds |
| `slack.2m.py` | Every 2 minutes (default) |
| `slack.5m.py` | Every 5 minutes |

If you rename, update the symlink/copy in the SwiftBar plugins folder to match.
