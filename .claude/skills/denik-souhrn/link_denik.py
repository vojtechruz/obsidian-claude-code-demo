#!/usr/bin/env python
"""Denik hierarchical navigation links.

Adds/refreshes a nav block on daily notes and weekly/monthly/yearly summaries:

  day    YYYY-MM-DD : prev/next day  + up week, month
  week   YYYY-Www   : prev/next week + up month (Thursday's month), year + down days
  month  YYYY-MM    : prev/next month + up year + down weeks
  year   YYYY       : prev/next year  + down months

prev/next = nearest EXISTING sibling (skips gaps). up-links are canonical
(may be unresolved until that summary exists). down-links list existing children.

The nav block is just the visible arrow line(s) - no hidden comment markers
(those would show up in edit mode). It is identified for idempotent replacement
by leading arrow chars at the expected position (top for days, after H1 for
summaries). Old <!-- denik-nav --> marker blocks are cleaned up on sight.

Usage:
  python link_denik.py --all                      # whole archive
  python link_denik.py <file.md> [<file.md> ...]   # only these notes
"""
import re
import sys
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
CARPE = VAULT / "Denik"

RE_DAY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
RE_WEEK = re.compile(r"^(\d{4})-W(\d{2})$")
RE_MONTH = re.compile(r"^(\d{4})-(\d{2})$")
RE_YEAR = re.compile(r"^(\d{4})$")
# A nav line normally starts with an arrow (← prev / ↑ up / ↓ down). But the very
# first note of a sequence has no prev-link, so its line starts with the next-link
# instead: "[[2013]] →". Match that shape too, otherwise the old block is not
# recognised, a fresh one gets prepended, and the duplicate compounds on every run.
ARROW = re.compile(r"^\s*(?:[←→↑↓]|\[\[[^\]]+\]\]\s*→)")
OLD_MARKER = re.compile(r"<!-- denik-nav:start -->.*?<!-- denik-nav:end -->\n*", re.S)
WD = {1: "Po", 2: "Út", 3: "St", 4: "Čt", 5: "Pá", 6: "So", 7: "Ne"}


def classify(stem):
    if RE_DAY.match(stem): return "day"
    if RE_WEEK.match(stem): return "week"
    if RE_MONTH.match(stem): return "month"
    if RE_YEAR.match(stem): return "year"
    return None


def build_index():
    idx = {"day": {}, "week": {}, "month": {}, "year": {}}
    for p in CARPE.rglob("*.md"):
        t = classify(p.stem)
        if t:
            idx[t][p.stem] = p
    order = {t: sorted(d) for t, d in idx.items()}
    return idx, order


def neighbours(order_list, key):
    i = order_list.index(key)
    prev = order_list[i - 1] if i > 0 else None
    nxt = order_list[i + 1] if i < len(order_list) - 1 else None
    return prev, nxt


def link(target, alias=None):
    return f"[[{target}|{alias}]]" if alias else f"[[{target}]]"


def prevnext_line(prev, nxt):
    parts = []
    if prev: parts.append(f"← {link(prev)}")
    if nxt: parts.append(f"{link(nxt)} →")
    return "  ·  ".join(parts)


def week_dates(stem):
    y, w = RE_WEEK.match(stem).groups()
    y, w = int(y), int(w)
    return (date.fromisocalendar(y, w, 1), date.fromisocalendar(y, w, 4),
            date.fromisocalendar(y, w, 7), y, w)


def nav_lines(stem, t, idx, order):
    if t == "day":
        y, m, d = RE_DAY.match(stem).groups()
        dt = date(int(y), int(m), int(d))
        iy, iw, _ = dt.isocalendar()
        prev, nxt = neighbours(order["day"], stem)
        top = prevnext_line(prev, nxt)
        up = f"↑ {link(f'{iy}-W{iw:02d}')} · {link(f'{y}-{m}')}"
        return [f"{top}   ·   {up}" if top else up]

    if t == "week":
        _, thu, _, iy, iw = week_dates(stem)
        prev, nxt = neighbours(order["week"], stem)
        line1 = prevnext_line(prev, nxt)
        line1 = (f"{line1}   ·   " if line1 else "") + \
                f"↑ {link(f'{thu.year}-{thu.month:02d}')} · {link(str(iy))}"
        days = []
        for k in range(7):
            dd = date.fromisocalendar(iy, iw, k + 1)
            if dd.isoformat() in idx["day"]:
                days.append(link(dd.isoformat(), f"{WD[k + 1]} {dd.day}"))
        return [line1] + (["↓ " + " · ".join(days)] if days else [])

    if t == "month":
        y, _ = RE_MONTH.match(stem).groups()
        prev, nxt = neighbours(order["month"], stem)
        line1 = prevnext_line(prev, nxt)
        line1 = (f"{line1}   ·   " if line1 else "") + f"↑ {link(y)}"
        wk = [link(wid) for wid in order["week"]
              if f"{week_dates(wid)[1].year}-{week_dates(wid)[1].month:02d}" == stem]
        return [line1] + (["↓ " + " · ".join(wk)] if wk else [])

    if t == "year":
        prev, nxt = neighbours(order["year"], stem)
        line1 = prevnext_line(prev, nxt)
        line1 = (f"{line1}   ·   " if line1 else "") + f"↑ {link('Denik')}"
        months = [link(mid) for mid in order["month"] if mid.startswith(stem + "-")]
        return [line1] + (["↓ " + " · ".join(months)] if months else [])

    return []


def strip_leading_nav(lines, start):
    """From index `start`, skip blanks then consecutive arrow-lines then blanks."""
    i = start
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    while i < len(lines) and ARROW.match(lines[i]):
        i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    return i


def apply_nav(path, t, idx, order):
    text = OLD_MARKER.sub("", path.read_text(encoding="utf-8"))
    lines = text.split("\n")
    block = nav_lines(path.stem, t, idx, order)

    if t == "day":
        rest = lines[strip_leading_nav(lines, 0):]
        new = block + [""] + rest
    else:
        h1 = next((k for k, l in enumerate(lines) if l.startswith("#")), 0)
        rest = lines[strip_leading_nav(lines, h1 + 1):]
        new = lines[:h1 + 1] + [""] + block + [""] + rest

    path.write_text("\n".join(new).rstrip("\n") + "\n", encoding="utf-8")


def main():
    idx, order = build_index()
    args = sys.argv[1:]
    if args == ["--all"]:
        targets = [(p, t) for t in idx for p in idx[t].values()]
    else:
        targets = []
        for a in args:
            p = Path(a) if Path(a).is_absolute() else VAULT / a
            t = classify(p.stem)
            if t:
                targets.append((p, t))
    for p, t in targets:
        apply_nav(p, t, idx, order)
    print(f"Zpracovano {len(targets)} pozn.")


if __name__ == "__main__":
    main()
