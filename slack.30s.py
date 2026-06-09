#!/usr/bin/env python3
# <swiftbar.title>Slack Status</swiftbar.title>
# <swiftbar.version>2.0</swiftbar.version>
# <swiftbar.desc>Shows Slack notification badge count from the macOS app</swiftbar.desc>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>false</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

import re
import subprocess

OPEN_SLACK = "bash=open param1=-a param2=Slack terminal=false"


def get_slack_badge():
    result = subprocess.run(
        ["lsappinfo", "info", "-only", "StatusLabel", "Slack"],
        capture_output=True, text=True,
    )
    m = re.search(r'"label"="(\d+)"', result.stdout)
    if m:
        return int(m.group(1))
    # Slack is running but badge is clear
    if "StatusLabel" in result.stdout:
        return 0
    # Slack is not running
    return None


badge = get_slack_badge()

if badge is None:
    print("— | sfimage=bubble.left color=#666666")
    print("---")
    print("Slack is not running")
    print(f"Launch Slack | {OPEN_SLACK}")
elif badge > 0:
    print(f"{badge} | sfimage=bubble.left.fill")
    print("---")
    print(f"{badge} notification{'s' if badge != 1 else ''}")
    print(f"Open Slack | {OPEN_SLACK}")
    print("Refresh | refresh=true")
else:
    print("| sfimage=bubble.left color=#666666")
    print("---")
    print("All clear")
    print(f"Open Slack | {OPEN_SLACK}")
    print("Refresh | refresh=true")
