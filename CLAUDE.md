# slackmf

SwiftBar plugin that shows Slack unread counts in the macOS menubar.

## How it works

SwiftBar runs `slack.2m.py` on a schedule (interval encoded in filename) and renders its stdout as a menubar item. The first line is the title; lines after `---` are the dropdown.

The script makes a single paginated `conversations.list` call to the Slack API, accumulating:
- `dm_unreads` — unread count across IMs and MPIMs
- `channel_unreads` — total unread count across channels
- `mention_count` — `unread_count_display` for channels (badge-worthy messages: mentions, etc.)

`other_channel = channel_unreads - mention_count` is shown separately so the user can distinguish general noise from direct attention.

## Files

- `slack.2m.py` — the SwiftBar plugin (rename to change refresh rate)

## Setup (dev)

```bash
# Install SwiftBar
brew install --cask swiftbar

# Save Slack token
mkdir -p ~/.config/slack-menubar
echo "xoxp-your-token" > ~/.config/slack-menubar/token

# Symlink plugin so edits here reflect immediately
ln -s "$(pwd)/slack.2m.py" "$HOME/Library/Application Support/SwiftBar/Plugins/slack.2m.py"

# Test the script directly (output goes to stdout)
python3 slack.2m.py
```

## Token

Stored in `~/.config/slack-menubar/token`. Required scopes: `channels:read`, `groups:read`, `im:read`, `mpim:read`.

## SwiftBar plugin format

```
<title line> | <params>   # menubar item; params can include bash=, href=, color=, etc.
---
<item> | <params>          # dropdown item
```

Appending `| bash=open param1=-a param2=Slack terminal=false` to the title line makes clicking it open Slack.
