#!/usr/bin/env python
"""Structural validation of the Carpe Diem journal.

Checks (beyond summary gaps, which check_gaps.py in carpe-summary covers):
  1. MISPLACED   - note in the wrong folder (day not in its YYYY/YYYY-MM/,
                   weekly not in its ISO-year Weekly/, monthly/yearly folder notes)
  2. DUPLICATE   - same period note existing in more than one place
  3. INVALID     - date/week that does not exist (2021-02-30, 2021-W54)
  4. FUTURE      - daily note dated after today (typo years)
  5. NAV         - missing, extra or stale navigation block (arrow lines);
                   e.g. a stale nav line above the H1 of a summary
  6. NO-AI       - weekly/monthly/yearly summary without '## AI shrnutí'
                   (build_moc.py depends on it; old notes predate the
                   convention - informational, backfill on request)

Usage: python .claude/skills/verifikace-vaultu/verify_carpe.py
Exit code 0 = clean, 1 = findings.
"""
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VAULT = Path(__file__).resolve().parents[3]
CARPE = VAULT / "Carpe Diem"

RE_DAY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
RE_WEEK = re.compile(r"^(\d{4})-W(\d{2})$")
RE_MONTH = re.compile(r"^(\d{4})-(\d{2})$")
RE_YEAR = re.compile(r"^(\d{4})$")
ARROW = re.compile(r"^\s*(?:[←→↑↓]|\[\[[^\]]+\]\]\s*→)")

problems = {"MISPLACED": [], "DUPLICATE": [], "INVALID": [], "FUTURE": [], "NAV": [], "NO-AI": []}
seen = {}
today = date.today()


def rel(p):
    return str(p.relative_to(VAULT)).replace("\\", "/")


def check_nav(p, kind, lines):
    """kind: 'day' -> exactly 1 arrow line at top; summary -> none above H1, 1-2 below."""
    if kind == "day":
        arrows = [i for i, l in enumerate(lines) if ARROW.match(l)]
        if not arrows:
            problems["NAV"].append(f"{rel(p)} - chybi navigacni blok (spust link_carpe.py)")
        elif len(arrows) > 1:
            problems["NAV"].append(f"{rel(p)} - {len(arrows)} navigacnich radku (duplikat)")
        elif arrows[0] != 0 and any(l.strip() for l in lines[:arrows[0]]):
            problems["NAV"].append(f"{rel(p)} - navigace neni na zacatku poznamky")
        return
    h1 = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    if h1 is None:
        problems["NAV"].append(f"{rel(p)} - souhrn nema H1 nadpis")
        return
    if any(ARROW.match(l) for l in lines[:h1]):
        problems["NAV"].append(f"{rel(p)} - stale navigacni radek NAD H1 (spust link_carpe.py a smaz duplikat)")
    arrows_below = sum(1 for l in lines[h1:] if ARROW.match(l))
    if arrows_below == 0:
        problems["NAV"].append(f"{rel(p)} - chybi navigacni blok (spust link_carpe.py)")
    elif arrows_below > 2:
        problems["NAV"].append(f"{rel(p)} - {arrows_below} navigacnich radku (duplikat)")


for p in sorted(CARPE.rglob("*.md")):
    stem = p.stem
    parts = p.relative_to(CARPE).parts
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    if m := RE_DAY.match(stem):
        y, mo, d = map(int, m.groups())
        try:
            dt = date(y, mo, d)
        except ValueError:
            problems["INVALID"].append(f"{rel(p)} - neexistujici datum")
            continue
        if dt > today:
            problems["FUTURE"].append(f"{rel(p)} - datum v budoucnosti")
        expected = (str(y), f"{y}-{mo:02d}", p.name)
        if parts != expected:
            problems["MISPLACED"].append(f"{rel(p)} - patri do {expected[0]}/{expected[1]}/")
        seen.setdefault(("day", stem), []).append(p)
        check_nav(p, "day", lines)

    elif m := RE_WEEK.match(stem):
        y, w = int(m.group(1)), int(m.group(2))
        try:
            date.fromisocalendar(y, w, 1)
        except ValueError:
            problems["INVALID"].append(f"{rel(p)} - neexistujici ISO tyden")
            continue
        if parts != (str(y), "Weekly", p.name):
            problems["MISPLACED"].append(f"{rel(p)} - patri do {y}/Weekly/")
        seen.setdefault(("week", stem), []).append(p)
        check_nav(p, "summary", lines)
        if "## AI shrnutí" not in text:
            problems["NO-AI"].append(rel(p))

    elif m := RE_MONTH.match(stem):
        y, mo = m.groups()
        if not 1 <= int(mo) <= 12:
            problems["INVALID"].append(f"{rel(p)} - neplatny mesic")
            continue
        if parts != (y, stem, p.name):
            problems["MISPLACED"].append(f"{rel(p)} - patri do {y}/{stem}/ (folder note)")
        seen.setdefault(("month", stem), []).append(p)
        check_nav(p, "summary", lines)
        if "## AI shrnutí" not in text:
            problems["NO-AI"].append(rel(p))

    elif RE_YEAR.match(stem):
        if parts != (stem, p.name):
            problems["MISPLACED"].append(f"{rel(p)} - patri do {stem}/ (folder note)")
        seen.setdefault(("year", stem), []).append(p)
        check_nav(p, "summary", lines)
        if "## AI shrnutí" not in text:
            problems["NO-AI"].append(rel(p))

for (kind, stem), paths in seen.items():
    if len(paths) > 1:
        problems["DUPLICATE"].append(f"{stem}: " + " | ".join(rel(x) for x in paths))

total = sum(len(v) for k, v in problems.items() if k != "NO-AI")
noai = problems["NO-AI"]

for key in ["MISPLACED", "DUPLICATE", "INVALID", "FUTURE", "NAV"]:
    if problems[key]:
        print(f"=== {key} ({len(problems[key])}) ===")
        for item in problems[key]:
            print(f"  {item}")

if noai:
    print(f"=== NO-AI: souhrny bez '## AI shrnutí' ({len(noai)}) - informativni ===")
    for item in noai[-10:]:
        print(f"  {item}")
    if len(noai) > 10:
        print(f"  ... a {len(noai) - 10} starsich (predchazeji konvenci; backfill jen na vyzadani)")

if total == 0:
    print("OK - struktura Carpe Diem je v poradku." + (f" ({len(noai)} starych souhrnu bez AI shrnuti - informativni)" if noai else ""))
sys.exit(1 if total else 0)
