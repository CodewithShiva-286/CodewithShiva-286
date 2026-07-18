#!/usr/bin/env python3
"""
Fetch daily contribution counts from GitHub's public contributions endpoint.

No token required. Writes data/contributions.json with raw days and derived stats.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

from scripts import _bootstrap  # noqa: F401
from scripts.paths import CONTRIBUTIONS_JSON, PROFILE_JSON
from scripts.utils import load_json, write_text


def resolve_username() -> str:
    return os.environ.get("GH_PROFILE_USER") or load_json(PROFILE_JSON)["username"]


def fetch_days(username: str) -> list[dict[str, int | str]]:
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(url, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print("no calendar cells found -- github markup may have changed", file=sys.stderr)
        sys.exit(1)

    days: list[dict[str, int | str]] = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue
        cell_id = cell.get("id")
        tooltip = soup.find("tool-tip", attrs={"for": cell_id}) if cell_id else None
        text = tooltip.get_text(strip=True) if tooltip else ""
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            match = re.match(r"(\d+)", text)
            count = int(match.group(1)) if match else 0
        days.append({"date": date, "count": count})

    days.sort(key=lambda item: str(item["date"]))
    return days


def compute_current_streak(days: list[dict[str, int | str]]) -> tuple[int, str | None, str | None]:
    index = len(days) - 1
    if days[index]["count"] == 0:
        index -= 1
    streak = 0
    end_index = index
    while index >= 0 and days[index]["count"] > 0:
        streak += 1
        index -= 1
    start_index = index + 1
    if streak == 0:
        return 0, None, None
    return streak, str(days[start_index]["date"]), str(days[end_index]["date"])


def compute_longest_streak(days: list[dict[str, int | str]]) -> tuple[int, str | None, str | None]:
    longest = run = 0
    longest_start: str | None = None
    longest_end: str | None = None
    run_start_index: int | None = None
    for index, day in enumerate(days):
        if day["count"] > 0:
            if run == 0:
                run_start_index = index
            run += 1
            if run > longest:
                longest = run
                longest_start = str(days[run_start_index]["date"])
                longest_end = str(day["date"])
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(username: str, days: list[dict[str, int | str]]) -> dict:
    total = sum(int(day["count"]) for day in days)
    active_days = sum(1 for day in days if day["count"] > 0)
    best = max(days, key=lambda day: int(day["count"]))
    current_len, current_start, current_end = compute_current_streak(days)
    longest_len, longest_start, longest_end = compute_longest_streak(days)

    monthly: dict[str, int] = {}
    for day in days:
        key = str(day["date"])[:7]
        monthly[key] = monthly.get(key, 0) + int(day["count"])
    monthly_list = [{"month": key, "total": value} for key, value in sorted(monthly.items())]

    return {
        "username": username,
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": current_len, "start": current_start, "end": current_end},
        "longest_streak": {"length": longest_len, "start": longest_start, "end": longest_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_list,
        "days": days,
    }


def fetch_contributions(username: str | None = None, out_path: str | None = None) -> str:
    user = resolve_username() if username is None else username
    target = str(CONTRIBUTIONS_JSON) if out_path is None else out_path
    days = fetch_days(user)
    data = build_data(user, days)
    write_text(target, json.dumps(data, indent=2))
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch GitHub contribution data.")
    parser.add_argument("--user", default=None, help="GitHub username override")
    parser.add_argument("--out", default=str(CONTRIBUTIONS_JSON), help="Output JSON path")
    args = parser.parse_args()

    out = fetch_contributions(args.user, args.out)
    data = load_json(out)
    print(
        f"wrote {out}: {data['total_contributions']} contributions, "
        f"current streak {data['current_streak']['length']}, "
        f"longest streak {data['longest_streak']['length']}"
    )


if __name__ == "__main__":
    main()
