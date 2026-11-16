#!/usr/bin/env python3
"""Post the Field's Point (Providence) COVID-19 wastewater activity level to Slack.

Uses CDC's official site-level activity level (the figure RIDOH reports), from
data.cdc.gov dataset atcp-73re. Uses only the Python standard library.

Environment variables:
  SLACK_WEBHOOK_URL  Slack incoming webhook. If missing, the message is printed instead.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date

FIELDS_POINT_CDC_SITE = "1811"
PATHOGEN = "SARS-CoV-2"
CDC_URL = "https://data.cdc.gov/resource/atcp-73re.json"

# Level -> circle. Masks are required at High and above.
LEVELS = {
    "very low": ("Very Low", "🟢", False),
    "low": ("Low", "🟡", False),
    "moderate": ("Moderate", "🟠", False),
    "high": ("High", "🔴", True),
    "very high": ("Very High", "🟣", True),
}
STALE_AFTER_DAYS = 14  # add a note if CDC's newest data is older than this


def latest_level():
    """Return (week_end_date, category) for the newest week with a level."""
    site_id = FIELDS_POINT_CDC_SITE.replace("ID:", "").strip()
    params = {
        "$where": f"site in('ID:{site_id}', '{site_id}') AND pathogen_target='{PATHOGEN}'",
        "$order": "week_end DESC",
        "$limit": "10",
    }
    url = CDC_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "ri-wastewater-slack-bot"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        rows = json.loads(resp.read())
    for r in rows:
        category = (r.get("site_wval_category") or "").strip().lower()
        if category in LEVELS:
            return date.fromisoformat(r["week_end"][:10]), category
    raise ValueError(f"No activity level found in CDC's data for site {FIELDS_POINT_CDC_SITE}.")


def build_message(week_end, category):
    name, circle, masks = LEVELS[category]
    lines = [
        "*Providence wastewater: COVID-19*",
        f"Activity level: {name} {circle}",
        f"Masks: {'Required' if masks else 'Not required'}",
    ]
    if (date.today() - week_end).days > STALE_AFTER_DAYS:
        lines.append(f"_No new CDC data since the week ending {week_end:%b} {week_end.day}._")
    return "\n".join(lines)


def post_to_slack(webhook, text):
    body = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(webhook, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Slack returned HTTP {resp.status}")


def main():
    week_end, category = latest_level()
    message = build_message(week_end, category)
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        print(message)
        return
    post_to_slack(webhook, message)
    print(f"Posted (data for week ending {week_end}).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
