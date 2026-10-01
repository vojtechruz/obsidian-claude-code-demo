#!/usr/bin/env python
"""Completeness check for Carpe Diem summaries.

Lists periods that have daily notes but are missing their summary note:
  - weeks  (>=1 daily in the ISO week, no Weekly/YYYY-Www.md)
  - months (>=1 daily in the month, no YYYY-MM/YYYY-MM.md folder note)
  - years  (>=1 daily in the year, no YYYY/YYYY.md folder note)

Current in-progress week/month/year is excluded (nothing to backfill yet).

Usage: python .claude/skills/carpe-summary/check_gaps.py
Exit code 0 = complete, 1 = gaps found.
"""
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VAULT = Path(__file__).resolve().parents[3]
CARPE = VAULT / "Carpe Diem"
RE_DAY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

today = date.today()
cur_iso = today.isocalendar()
cur_week = f"{cur_iso[0]}-W{cur_iso[1]:02d}"
cur_month = f"{today.year}-{today.month:02d}"
cur_year = str(today.year)

weeks_needed = {}   # 'YYYY-Www' -> day count
months_needed = set()
years_needed = set()

for p in CARPE.rglob("*.md"):
    m = RE_DAY.match(p.stem)
    if not m:
        continue
    d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    iy, iw, _ = d.isocalendar()
    wk = f"{iy}-W{iw:02d}"
    weeks_needed[wk] = weeks_needed.get(wk, 0) + 1
    months_needed.add(f"{d.year}-{d.month:02d}")
    years_needed.add(str(d.year))

missing_w = []
for wk, cnt in sorted(weeks_needed.items()):
    if wk == cur_week:
        continue
    iy = int(wk[:4])
    if not (CARPE / str(iy) / "Weekly" / f"{wk}.md").exists():
        missing_w.append(f"{wk} ({cnt} dennich poznamek)")

missing_m = []
for mo in sorted(months_needed):
    if mo == cur_month:
        continue
    y = mo[:4]
    if not (CARPE / y / mo / f"{mo}.md").exists():
        missing_m.append(mo)

missing_y = []
for y in sorted(years_needed):
    if y == cur_year:
        continue
    if not (CARPE / y / f"{y}.md").exists():
        missing_y.append(y)

if not (missing_w or missing_m or missing_y):
    print("OK - vsechny souhrny existuji (tydenni, mesicni i rocni).")
    sys.exit(0)

if missing_w:
    print(f"CHYBI TYDNY ({len(missing_w)}):")
    for w in missing_w:
        print(f"  {w}")
if missing_m:
    print(f"CHYBI MESICE ({len(missing_m)}):")
    for m in missing_m:
        print(f"  {m}")
if missing_y:
    print(f"CHYBI ROKY ({len(missing_y)}):")
    for y in missing_y:
        print(f"  {y}")
sys.exit(1)
