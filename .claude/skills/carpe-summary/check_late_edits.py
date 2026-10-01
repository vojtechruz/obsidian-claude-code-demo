#!/usr/bin/env python
"""Late-edit check for Carpe Diem weekly summaries.

Problem: a weekly summary is often generated on Sunday afternoon (as part of planning the
next week) and the user then adds more bullets to that Sunday's (or another day's) daily note.
Those bullets never make it into the summary - and through it into the month/year.

Solution: each weekly summary carries a frontmatter property `carpe_src` with a content hash
of every daily note it was built from:

    ---
    carpe_src:
      - 2026-08-24=1a2b3c4d
      - 2026-08-25=...
    ---

Hashes ignore the nav block (arrow lines), blank lines, `xjs` meta-bullets and the `⌚ Garmin:` line, so re-running
link_carpe.py or logging `xjs week` does not trigger a false positive.

Usage:
  python .claude/skills/carpe-summary/check_late_edits.py              # check last 4 weeks that have a summary
  python .claude/skills/carpe-summary/check_late_edits.py --weeks 8    # look further back
  python .claude/skills/carpe-summary/check_late_edits.py --stamp 2026-W35   # (re)write the stamp of that summary

Output per week:
  OK        - all source days unchanged since the stamp
  CHANGED   - day's content differs from the stamped hash  -> read the day, merge missing bullets
  NEW       - day note exists but was not stamped (created after the summary)
  NOSTAMP   - summary has no stamp (older note); falls back to mtime: lists days modified after
              the summary and always flags Sunday as "check anyway"
Exit code 0 = nothing to do / stamp written, 1 = findings, 2 = error.
"""
import hashlib
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VAULT = Path(__file__).resolve().parents[3]
CARPE = VAULT / "Carpe Diem"
KEY = "carpe_src"
ARROW = re.compile(r"^\s*(?:[←→↑↓]|\[\[[^\]]+\]\]\s*→)")
XJS = re.compile(r"^\s*[-*]\s*xjs\b", re.I)
GARMIN = re.compile(r"^\s*[-*]\s*⌚\s*Garmin:")
FM = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.S)
LEGACY = re.compile(r"\n*<!--\s*carpe-src:[^>]*-->\n*")  # old HTML-comment stamp, removed on --stamp
CZ = "Po Út St Čt Pá So Ne".split()


def day_path(d: date) -> Path:
    return CARPE / str(d.year) / d.strftime("%Y-%m") / f"{d.isoformat()}.md"


def week_path(year: int, week: int) -> Path:
    return CARPE / str(year) / "Weekly" / f"{year}-W{week:02d}.md"


def content_hash(p: Path) -> str:
    lines = []
    for l in p.read_text(encoding="utf-8").splitlines():
        if not l.strip() or ARROW.match(l) or XJS.match(l) or GARMIN.match(l):
            continue
        lines.append(l.rstrip())
    return hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()[:8]


def week_days(year: int, week: int):
    mon = date.fromisocalendar(year, week, 1)
    return [mon + timedelta(days=i) for i in range(7)]


def split_fm(text: str):
    """Return (frontmatter text or None, body)."""
    m = FM.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def parse_stamp(text: str):
    fm, _ = split_fm(text)
    if fm is None:
        return None
    # minimal YAML reader (stdlib only): `carpe_src:` as a block list or an inline scalar
    vals, inside = [], False
    for line in fm.splitlines():
        if line.startswith(KEY + ":"):
            inside = True
            inline = line[len(KEY) + 1:].strip().strip("[]").replace(",", " ")
            vals += inline.split()
            continue
        if inside:
            item = line.strip()
            if item.startswith("-") and line[:1] in (" ", "\t", "-"):
                vals.append(item[1:].strip().strip("'\""))
            else:
                break
    if not vals:
        return None
    out = {}
    for tok in vals:
        tok = str(tok)
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def stamp(year: int, week: int) -> int:
    wp = week_path(year, week)
    if not wp.exists():
        print(f"[chyba] souhrn {wp.relative_to(VAULT).as_posix()} neexistuje")
        return 2
    parts = [f"{d.isoformat()}={content_hash(day_path(d))}" for d in week_days(year, week) if day_path(d).exists()]
    block = f"{KEY}:\n" + "".join(f"  - {x}\n" for x in parts)
    text = wp.read_text(encoding="utf-8")
    text = LEGACY.sub("\n", text).rstrip("\n") + "\n"  # drop legacy HTML-comment stamp
    fm, body = split_fm(text)
    if fm is None:
        text = f"---\n{block}---\n{body}"
    else:
        # replace an existing carpe_src key (scalar or block list), else append it
        fm2, n = re.subn(rf"^{KEY}:.*?(?=^\S|\Z)", block, fm + "\n", count=1, flags=re.S | re.M)
        fm2 = fm2.rstrip("\n")
        if n == 0:
            fm2 = fm2 + "\n" + block.rstrip("\n")
        text = f"---\n{fm2}\n---\n{body}"
    wp.write_text(text, encoding="utf-8")
    print(f"[stamp] {wp.relative_to(VAULT).as_posix()}: {len(parts)} dní")
    return 0


def check(weeks_back: int) -> int:
    today = date.today()
    findings = 0
    checked = 0
    # iterate completed weeks backwards, starting with the previous ISO week
    mon = today - timedelta(days=today.weekday()) - timedelta(days=7)
    while checked < weeks_back:
        y, w, _ = mon.isocalendar()
        wp = week_path(y, w)
        mon -= timedelta(days=7)
        if not wp.exists():
            if (today - mon).days > 365:
                break
            continue
        checked += 1
        wid = f"{y}-W{w:02d}"
        text = wp.read_text(encoding="utf-8")
        stamped = parse_stamp(text)
        days = [d for d in week_days(y, w) if day_path(d).exists()]
        if stamped is None:
            smtime = datetime.fromtimestamp(wp.stat().st_mtime)
            late = [d for d in days if datetime.fromtimestamp(day_path(d).stat().st_mtime) > smtime]
            sunday = days[-1] if days and days[-1].weekday() == 6 else None
            print(f"NOSTAMP {wid}: souhrn bez razítka (zapsán {smtime:%Y-%m-%d %H:%M}).")
            for d in late:
                print(f"    - {d.isoformat()} změněn po souhrnu ({datetime.fromtimestamp(day_path(d).stat().st_mtime):%Y-%m-%d %H:%M})")
            if sunday and sunday not in late:
                print(f"    - {sunday.isoformat()} (neděle) – zkontrolovat pro jistotu")
            print(f"    → porovnej s {wp.relative_to(VAULT).as_posix()}, doplň chybějící a spusť --stamp {wid}")
            findings += 1
            continue
        changed = [d for d in days if d.isoformat() in stamped and stamped[d.isoformat()] != content_hash(day_path(d))]
        new = [d for d in days if d.isoformat() not in stamped]
        if not changed and not new:
            print(f"OK      {wid}")
            continue
        findings += 1
        print(f"CHANGED {wid}: denní poznámky změněné po vytvoření souhrnu {wp.relative_to(VAULT).as_posix()}")
        for d in changed:
            print(f"    - CHANGED {d.isoformat()} ({CZ[d.weekday()]})")
        for d in new:
            print(f"    - NEW     {d.isoformat()} (nebyl v razítku)")
        print(f"    → přečti tyto dny, doplň do souhrnu {wid} co chybí (a do měsíčního souhrnu, pokud už existuje), pak spusť --stamp {wid}")
    if checked == 0:
        print("(žádné týdenní souhrny ke kontrole)")
    return 1 if findings else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stamp" in args:
        wid = args[args.index("--stamp") + 1]
        m = re.match(r"^(\d{4})-W(\d{2})$", wid)
        if not m:
            print("usage: --stamp YYYY-Www")
            sys.exit(2)
        sys.exit(stamp(int(m.group(1)), int(m.group(2))))
    n = 4
    if "--weeks" in args:
        n = int(args[args.index("--weeks") + 1])
    sys.exit(check(n))
