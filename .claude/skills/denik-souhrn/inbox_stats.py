#!/usr/bin/env python3
"""
Calculate inbox and clippings folder stats from git history for a given date.
Usage: python inbox_stats.py 2026-08-03
Returns: inbox_start→end, clippings_start→end, with deltas
"""

import subprocess
import sys
from datetime import datetime, timedelta
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_file_count_at_time(folder: str, date: str, time: str = "23:59") -> int:
    """
    Get count of files in a folder at a specific date/time using git history.

    Args:
        folder: Path to folder (e.g., '__INBOX')
        date: YYYY-MM-DD format
        time: HH:MM format (default 23:59 for end of day)

    Returns:
        Number of files in that folder at that time
    """
    # Find the commit closest to date+time
    timestamp = f"{date} {time}"

    try:
        # Get the last commit before the given timestamp
        result = subprocess.run(
            ["git", "log", "-1", "--before", timestamp, "--format=%H", "--", folder],
            capture_output=True,
            text=True,
            check=True,
        )

        commit_hash = result.stdout.strip()
        if not commit_hash:
            # No commits found before this time, return 0
            return 0

        # List all files in folder at that commit
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", commit_hash, "--", folder],
            capture_output=True,
            text=True,
            check=True,
        )

        files = [line for line in result.stdout.strip().split('\n') if line]
        return len(files)

    except subprocess.CalledProcessError:
        return 0

def get_stats(date: str) -> dict:
    """
    Get inbox and clippings stats for a date.

    Args:
        date: YYYY-MM-DD format

    Returns:
        dict with inbox_start, inbox_end, clippings_start, clippings_end
    """
    # Get counts at start of day (00:00) and end of day (23:59)
    inbox_start = get_file_count_at_time("__INBOX", date, "00:00")
    inbox_end = get_file_count_at_time("__INBOX", date, "23:59")

    clippings_start = get_file_count_at_time("__INBOX/_Clippings", date, "00:00")
    clippings_end = get_file_count_at_time("__INBOX/_Clippings", date, "23:59")

    return {
        "inbox_start": inbox_start,
        "inbox_end": inbox_end,
        "clippings_start": clippings_start,
        "clippings_end": clippings_end,
    }

def format_stats(stats: dict) -> str:
    """
    Format stats for display in a daily note.

    Returns: "Inbox: 12→10 (-2) | Clippings: 5→3 (-2)"
    """
    inbox_delta = stats["inbox_end"] - stats["inbox_start"]
    clippings_delta = stats["clippings_end"] - stats["clippings_start"]

    inbox_str = f"Inbox: {stats['inbox_start']}→{stats['inbox_end']}"
    if inbox_delta != 0:
        sign = "+" if inbox_delta > 0 else ""
        inbox_str += f" ({sign}{inbox_delta})"

    clippings_str = f"Clippings: {stats['clippings_start']}→{stats['clippings_end']}"
    if clippings_delta != 0:
        sign = "+" if clippings_delta > 0 else ""
        clippings_str += f" ({sign}{clippings_delta})"

    return f"{inbox_str} | {clippings_str}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: inbox_stats.py YYYY-MM-DD")
        sys.exit(1)

    date = sys.argv[1]

    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {date}. Use YYYY-MM-DD")
        sys.exit(1)

    stats = get_stats(date)
    formatted = format_stats(stats)
    print(formatted)
