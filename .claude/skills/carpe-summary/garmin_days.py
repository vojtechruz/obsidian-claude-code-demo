#!/usr/bin/env python
"""Garmin kroky + aktivity (typ a cas) pro Carpe Diem.

Pouziti:
  python .claude/skills/carpe-summary/garmin_days.py 2026-08-31 2026-09-06            # vypis po dnech + souhrn
  python .claude/skills/carpe-summary/garmin_days.py 2026-08-31 2026-09-06 --write    # + zapise radek do dennich poznamek
  python .claude/skills/carpe-summary/garmin_days.py 2026-08-01 2026-08-31 --summary  # jen souhrnny radek (mesic/rok)

Radek v denni poznamce (idempotentni - existujici radek "⌚ Garmin:" se nahradi, ne zdvoji):
  - ⌚ Garmin: 11 575 kroků · Posilovna 45 min · Běh 23 min (2,9 km)
Souhrnny radek pro tydenni/mesicni/rocni souhrn (do ## Kondice a zdraví, posledni odrazka):
  - ⌚ Garmin: 62 340 kroků (Ø 8 906/den, 10k+ 3/7) · Běh 3× 1:45 h (18,2 km) · Posilovna 2× 1:30 h
Vzdalenost se uvadi jen u vzdalenostnich sportu (beh, kolo, chuze, turistika, plavani v metrech).

Denni poznamky, ktere neexistuji, se nevytvareji (jen se vypise upozorneni). Dny bez hodinek
(0 kroku a zadna aktivita) se preskakuji. check_late_edits.py radek ⌚ Garmin ignoruje v hashi.

Demo rezim: pokud vedle skriptu existuje slozka demo_data/ (nebo je nastavene DEMO_MODE=1),
skript nevola Garmin Connect a cte odpovedi API z demo_data/daily_steps.json a
demo_data/activities.json (fiktivni data 2025-10-01 .. 2026-09-30, generuje demo_data/_generate.py).
Bezi jen se stdlib.
Realna data: smaz demo_data/, nainstaluj `pip install garminconnect` a prihlas se pres
.claude/skills/garmin-aktivita/garmin_login.py (tokeny v ~/.garminconnect).
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
VAULT = Path(__file__).resolve().parents[3]
CARPE = VAULT / "Carpe Diem"
DEMO_DIR = Path(__file__).resolve().parent / "demo_data"
DEMO = DEMO_DIR.is_dir() or os.environ.get("DEMO_MODE") == "1"
sys.path.insert(0, str(VAULT / ".claude" / "skills" / "garmin-aktivita"))
try:
    from garmin_activity import TYPE_CZ  # noqa: E402
except ImportError:  # garminconnect neni nainstalovany (demo) - stejne preklady jako v garmin-aktivita
    TYPE_CZ = {
        "running": "Běh", "trail_running": "Trailový běh", "treadmill_running": "Běh na pásu",
        "cycling": "Kolo", "road_biking": "Silniční kolo", "mountain_biking": "MTB", "walking": "Chůze",
        "hiking": "Turistika", "mountaineering": "Horská turistika", "lap_swimming": "Plavání (bazén)",
        "strength_training": "Posilovna", "obstacle_run": "Překážkový běh", "bouldering": "Bouldering",
        "rock_climbing": "Lezení", "yoga": "Jóga", "cross_country_skiing": "Běžky",
    }

MARK = "⌚ Garmin:"
LINE_RE = re.compile(r"^\s*[-*]\s*" + re.escape(MARK) + r".*$", re.M)
CHUNK = 28  # get_daily_steps zvlada omezeny rozsah
STEP_GOAL = 10_000  # pevny cil; Garminuv adaptivni cil ("stepGoal") se nepouziva


def day_path(d: date) -> Path:
    return CARPE / str(d.year) / d.strftime("%Y-%m") / f"{d.isoformat()}.md"


def fmt_min(sec: float) -> str:
    m = int(round(sec / 60))
    return f"{m // 60}:{m % 60:02d} h" if m >= 60 else f"{m} min"


def fmt_int(n) -> str:
    return f"{int(round(n)):,}".replace(",", " ")


DIST_KEYS = {"running", "trail_running", "treadmill_running", "obstacle_run", "cycling", "road_biking", "mountain_biking",
             "gravel_cycling", "e_bike_fitness", "virtual_ride", "indoor_cycling", "walking", "hiking", "trail_hiking",
             "mountaineering", "snowshoeing", "cross_country_skiing", "skate_skiing", "inline_skating", "kayaking", "rowing",
             "stand_up_paddleboarding", "lap_swimming", "open_water_swimming"}
SWIM_KEYS = {"lap_swimming", "open_water_swimming"}


def key(a: dict) -> str:
    return (a.get("activityType") or {}).get("typeKey", "")


def fmt_dist(meters: float, swim: bool) -> str:
    if swim:
        return f"{fmt_int(meters)} m"
    return f"{meters / 1000:.1f} km".replace(".", ",")


def dist_of(a: dict) -> str:
    """'(2,9 km)' pro vzdalenostni sporty, jinak ''."""
    k = key(a)
    m = a.get("distance") or 0
    if k not in DIST_KEYS or m < 50:
        return ""
    return f" ({fmt_dist(m, k in SWIM_KEYS)})"


def typ(a: dict) -> str:
    key = (a.get("activityType") or {}).get("typeKey", "")
    return TYPE_CZ.get(key, key.replace("_", " ").capitalize() or "Aktivita")


class DemoClient:
    """Napodobi Garmin klienta nad fixtures v demo_data/ (stejny tvar odpovedi jako API)."""

    def __init__(self):
        if not DEMO_DIR.is_dir():
            sys.exit(f"DEMO_MODE=1, ale slozka {DEMO_DIR} neexistuje")
        self.steps = json.loads((DEMO_DIR / "daily_steps.json").read_text(encoding="utf-8"))
        self.acts = json.loads((DEMO_DIR / "activities.json").read_text(encoding="utf-8"))

    def get_daily_steps(self, start: str, end: str):
        return [r for r in self.steps if start <= r["calendarDate"] <= end]

    def get_activities_by_date(self, start: str, end: str):
        return [a for a in self.acts if start <= a["startTimeLocal"][:10] <= end]


def client():
    """Hranice site: v demu fixtures, jinak skutecny Garmin Connect."""
    if DEMO:
        return DemoClient()
    from garmin_activity import client as garmin_client  # vyzaduje garminconnect
    return garmin_client()


def fetch(start: date, end: date):
    g = client()
    steps = {}
    d = start
    while d <= end:
        e = min(d + timedelta(days=CHUNK - 1), end)
        for row in g.get_daily_steps(d.isoformat(), e.isoformat()) or []:
            steps[row["calendarDate"]] = {"steps": row.get("totalSteps") or 0, "goal": row.get("stepGoal") or 0}
        d = e + timedelta(days=1)
    acts = defaultdict(list)
    for a in g.get_activities_by_date(start.isoformat(), end.isoformat()) or []:
        acts[a["startTimeLocal"][:10]].append(a)
    return steps, acts


def day_line(iso: str, steps: dict, acts: dict) -> str | None:
    s = steps.get(iso, {}).get("steps", 0)
    todays = sorted(acts.get(iso, []), key=lambda a: a["startTimeLocal"])
    if not s and not todays:
        return None
    parts = [f"{fmt_int(s)} kroků"]
    parts += [f"{typ(a)} {fmt_min(a.get('duration') or 0)}{dist_of(a)}" for a in todays]
    return f"- {MARK} " + " · ".join(parts)


def summary_line(start: date, end: date, steps: dict, acts: dict) -> str:
    days = [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]
    tracked = [d for d in days if steps.get(d, {}).get("steps")]
    total = sum(steps[d]["steps"] for d in tracked)
    goal_ok = sum(1 for d in tracked if steps[d]["steps"] >= STEP_GOAL)
    parts = []
    if tracked:
        avg = total / len(tracked)
        parts.append(f"{fmt_int(total)} kroků (Ø {fmt_int(avg)}/den, 10k+ {goal_ok}/{len(tracked)})")
    agg = defaultdict(lambda: [0, 0.0, 0.0, False])  # pocet, sekundy, metry, je_plavani
    for lst in acts.values():
        for a in lst:
            e = agg[typ(a)]
            e[0] += 1
            e[1] += a.get("duration") or 0
            if key(a) in DIST_KEYS:
                e[2] += a.get("distance") or 0
                e[3] = key(a) in SWIM_KEYS
    for t, (n, sec, m, swim) in sorted(agg.items(), key=lambda kv: -kv[1][1]):
        parts.append(f"{t} {n}× {fmt_min(sec)}" + (f" ({fmt_dist(m, swim)})" if m >= 50 else ""))
    return f"- {MARK} " + (" · ".join(parts) if parts else "žádná data")


def write_day(p: Path, line: str) -> str:
    text = p.read_text(encoding="utf-8")
    if LINE_RE.search(text):
        new = LINE_RE.sub(line, text, count=1)
        status = "beze změny" if new == text else "aktualizován"
    else:
        new = text.rstrip("\n") + "\n" + line + "\n"
        status = "přidán"
    if new != text:
        p.write_text(new, encoding="utf-8")
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("start")
    ap.add_argument("end")
    ap.add_argument("--write", action="store_true", help="zapsat/aktualizovat řádek v denních poznámkách")
    ap.add_argument("--summary", action="store_true", help="vypsat jen souhrnný řádek")
    a = ap.parse_args()
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    if end < start:
        ap.error("end < start")
    steps, acts = fetch(start, end)

    if not a.summary:
        d = start
        while d <= end:
            iso = d.isoformat()
            line = day_line(iso, steps, acts)
            p = day_path(d)
            if line is None:
                print(f"{iso}: (bez dat)")
            elif a.write:
                if p.exists():
                    print(f"{iso}: {write_day(p, line)} — {line[2:]}")
                else:
                    print(f"{iso}: denní poznámka neexistuje, nezapsáno — {line[2:]}")
            else:
                print(f"{iso}: {line[2:]}")
            d += timedelta(days=1)
        print()
    print(summary_line(start, end, steps, acts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
