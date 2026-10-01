"""Stahne aktivitu z Garmin Connect a vypise ji jako Markdown blok pro poznamku ve vaultu.

Pouziti:
    python garmin_activity.py 20104559832                 # ID nebo cela URL aktivity
    python garmin_activity.py <id> --gpx "Oblasti/Kondice a Zdravi/Attachments"   # + stahne GPX
    python garmin_activity.py <id> --json                 # surova data (summary + splity)
    python garmin_activity.py --recent 10                 # poslednich N aktivit (tabulka)

Vyzaduje jednorazove prihlaseni pres garmin_login.py (tokeny v ~/.garminconnect).
Demo: kdyz vedle skriptu existuje demo_data/ (nebo DEMO_MODE=1), cte fixtures misto Garmin Connect
a knihovnu garminconnect nepotrebuje.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
TOKENSTORE = os.path.expanduser("~/.garminconnect")
# Demo rezim: existuje-li vedle skriptu slozka demo_data/ (nebo DEMO_MODE=1), nevola se Garmin Connect
# a odpovedi API se ctou z JSON fixtures. Pro realna data slozku smaz.
DEMO_DIR = Path(__file__).resolve().parent / "demo_data"
DEMO = DEMO_DIR.is_dir() or os.environ.get("DEMO_MODE") == "1"
ACTIVITY_URL = "https://connect.garmin.com/modern/activity/{id}"

TYPE_CZ = {
    "running": "Běh", "trail_running": "Trailový běh", "treadmill_running": "Běh na pásu",
    "cycling": "Kolo", "road_biking": "Silniční kolo", "mountain_biking": "MTB", "indoor_cycling": "Cycling (indoor)",
    "e_bike_fitness": "Elektrokolo", "walking": "Chůze", "hiking": "Turistika",
    "lap_swimming": "Plavání (bazén)", "open_water_swimming": "Plavání (otevřená voda)",
    "strength_training": "Posilovna", "indoor_cardio": "Indoor cardio", "diving": "Potápění",
    "obstacle_run": "Překážkový běh", "multi_sport": "Multisport",
    "mountaineering": "Horská turistika", "trail_hiking": "Turistika", "elliptical": "Eliptical", "yoga": "Jóga",
    "pilates": "Pilates", "hiit": "HIIT", "cardio": "Cardio", "resort_skiing_snowboarding": "Lyže", "skate_skiing": "Běžky",
    "cross_country_skiing": "Běžky", "gravel_cycling": "Gravel", "virtual_ride": "Cycling (virtual)", "stand_up_paddleboarding": "Paddleboard",
    "kayaking": "Kajak", "rowing": "Veslování", "indoor_rowing": "Veslování (indoor)", "other": "Jiné", "fitness_equipment": "Fitness",
    "breathwork": "Dýchání", "meditation": "Meditace", "bouldering": "Bouldering", "rock_climbing": "Lezení", "tennis": "Tenis",
    "table_tennis": "Ping-pong", "badminton": "Badminton", "golf": "Golf", "snowshoeing": "Sněžnice", "ice_skating": "Brusle", "inline_skating": "Inline",
}


class DemoGarmin:
    """Stejne metody jako garminconnect.Garmin, data z demo_data/ (tvar = skutecna odpoved API)."""

    def _load(self, name):
        path = DEMO_DIR / name
        if not path.is_file():
            sys.exit(f"[demo] Aktivita není ve fixtures ({path.name}) — dostupná ID vypíše --recent 30")
        return json.loads(path.read_text(encoding="utf-8"))

    def get_activities(self, start, limit):
        return self._load("activities.json")[start:start + limit]

    def _from_listing(self, aid):
        """Starsi aktivity maji ve fixtures jen radek v activities.json -> detail bez useku."""
        for a in self._load("activities.json"):
            if str(a["activityId"]) == str(aid):
                rest = {k: v for k, v in a.items() if k not in ("activityId", "activityName", "activityType")}
                return {"activityId": a["activityId"], "activityName": a["activityName"],
                        "activityTypeDTO": a["activityType"], "summaryDTO": rest}
        return None

    def get_activity(self, aid):
        if (DEMO_DIR / f"activity-{aid}.json").is_file():
            return self._load(f"activity-{aid}.json")
        return self._from_listing(aid) or self._load(f"activity-{aid}.json")

    def get_activity_splits(self, aid):
        if (DEMO_DIR / f"splits-{aid}.json").is_file():
            return self._load(f"splits-{aid}.json")
        return {"activityId": aid, "lapDTOs": []}

    def download_gpx(self, aid):
        path = DEMO_DIR / f"garmin-{aid}.gpx"
        if not path.is_file():
            sys.exit(f"[demo] GPX pro aktivitu {aid} ve fixtures není (jen u závodů)")
        return path.read_bytes()


def client():
    if DEMO:
        print("[demo] Garmin Connect se nevolá, data jsou z demo_data/", file=sys.stderr)
        return DemoGarmin()
    from garminconnect import Garmin
    from garminconnect.exceptions import GarminConnectAuthenticationError

    class RealGarmin(Garmin):
        def download_gpx(self, aid):
            return self.download_activity(aid, dl_fmt=Garmin.ActivityDownloadFormat.GPX)

    if not os.path.isdir(TOKENSTORE):
        sys.exit(f"Nejsi přihlášen — spusť nejdřív ručně: python .claude/skills/garmin-aktivita/garmin_login.py")
    g = RealGarmin()
    try:
        g.login(TOKENSTORE)
    except GarminConnectAuthenticationError as e:
        sys.exit(f"Přihlášení z tokenů selhalo ({e}) — spusť znovu garmin_login.py")
    return g


def parse_id(s: str) -> str:
    m = re.search(r"(\d{6,})", s)
    if not m:
        sys.exit(f"Nerozpoznal jsem ID aktivity v: {s}")
    return m.group(1)


def fmt_dur(sec) -> str:
    if sec is None:
        return "–"
    sec = int(round(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_pace(speed_ms) -> str:
    if not speed_ms or speed_ms <= 0:
        return "–"
    sec_per_km = 1000 / speed_ms
    m, s = divmod(int(round(sec_per_km)), 60)
    return f"{m}:{s:02d} /km"


def fmt_date(s) -> str:
    try:
        d = datetime.fromisoformat(s)
        return d.strftime("%-d. %-m. %Y %H:%M") if os.name != "nt" else d.strftime("%#d. %#m. %Y %H:%M")
    except Exception:
        return s or "–"


def num(v, nd=0, unit=""):
    if v is None:
        return "–"
    return f"{v:.{nd}f}{unit}" if nd else f"{int(round(v))}{unit}"


def flatten(a: dict) -> dict:
    """get_activity() vraci vnorene DTO (summaryDTO, activityTypeDTO) - sloucit do jednoho slovniku."""
    f = dict(a)
    f.update(a.get("summaryDTO") or {})
    f.setdefault("activityType", a.get("activityTypeDTO") or a.get("activityType") or {})
    # sjednoceni nazvu poli mezi get_activity a get_activities
    f.setdefault("averageRunningCadenceInStepsPerMinute", f.get("averageRunCadence"))
    f.setdefault("aerobicTrainingEffect", f.get("trainingEffect"))
    return f


def summary_md(a: dict, splits: dict | None) -> str:
    a = flatten(a)
    aid = a.get("activityId")
    url = ACTIVITY_URL.format(id=aid)
    t = (a.get("activityType") or {}).get("typeKey", "")
    typ = TYPE_CZ.get(t, t)
    dist_km = (a.get("distance") or 0) / 1000
    lines = [
        "## 📊 Výsledek z Garminu",
        f"- **Aktivita:** [{a.get('activityName', 'aktivita')}]({url}) — {typ}, {fmt_date(a.get('startTimeLocal'))}"
        + (f", {a['locationName']}" if a.get("locationName") else ""),
        f"- **Vzdálenost:** {dist_km:.2f} km · **Čas:** {fmt_dur(a.get('duration'))}"
        + (f" (v pohybu {fmt_dur(a.get('movingDuration'))})" if a.get("movingDuration") else "")
        + (f" · celkem vč. pauz {fmt_dur(a.get('elapsedDuration'))}" if a.get("elapsedDuration") and abs(a["elapsedDuration"] - (a.get("duration") or 0)) > 60 else ""),
        f"- **Tempo:** Ø {fmt_pace(a.get('averageSpeed'))}"
        + (f" · v pohybu {fmt_pace(a.get('averageMovingSpeed'))}" if a.get("averageMovingSpeed") else "")
        + f" · nejrychlejší {fmt_pace(a.get('maxSpeed'))}",
        f"- **Tep:** Ø {num(a.get('averageHR'))} · max {num(a.get('maxHR'))} bpm",
        f"- **Převýšení:** +{num(a.get('elevationGain'))} / −{num(a.get('elevationLoss'))} m"
        + (f" (min {num(a.get('minElevation'))}, max {num(a.get('maxElevation'))} m n. m.)" if a.get("maxElevation") is not None else ""),
        f"- **Kalorie:** {num(a.get('calories'))} kcal",
    ]
    extras = []
    if a.get("averageRunningCadenceInStepsPerMinute"):
        extras.append(f"kadence Ø {num(a['averageRunningCadenceInStepsPerMinute'])} spm")
    if a.get("steps"):
        extras.append(f"{a['steps']} kroků")
    if a.get("vO2MaxValue"):
        extras.append(f"VO2max {a['vO2MaxValue']}")
    if a.get("aerobicTrainingEffect") is not None:
        extras.append(f"Training Effect {a['aerobicTrainingEffect']:.1f} aerobní / {(a.get('anaerobicTrainingEffect') or 0):.1f} anaerobní")
    if a.get("activityTrainingLoad"):
        extras.append(f"Training Load {num(a['activityTrainingLoad'])}")
    if a.get("minTemperature") is not None:
        extras.append(f"teplota {num(a['minTemperature'])}–{num(a.get('maxTemperature'))} °C")
    if extras:
        lines.append("- **Další:** " + " · ".join(extras))

    laps = (splits or {}).get("lapDTOs") or []
    if laps and 1 < len(laps) <= 60:
        lines += ["", "### Úseky", "", "| # | Vzdálenost | Čas | Tempo | Ø tep |", "|---|---|---|---|---|"]
        for i, lap in enumerate(laps, 1):
            lines.append(
                f"| {i} | {(lap.get('distance') or 0) / 1000:.2f} km | {fmt_dur(lap.get('duration'))} | "
                f"{fmt_pace(lap.get('averageSpeed'))} | {num(lap.get('averageHR'))} |"
            )
    return "\n".join(lines)


def recent_md(acts: list[dict]) -> str:
    lines = ["| Datum | Aktivita | Typ | km | Čas | Ø tep | ID |", "|---|---|---|---|---|---|---|"]
    for a in acts:
        t = (a.get("activityType") or {}).get("typeKey", "")
        lines.append(
            f"| {fmt_date(a.get('startTimeLocal'))} | {a.get('activityName', '')} | {TYPE_CZ.get(t, t)} | "
            f"{(a.get('distance') or 0) / 1000:.2f} | {fmt_dur(a.get('duration'))} | {num(a.get('averageHR'))} | {a.get('activityId')} |"
        )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("activity", nargs="?", help="ID aktivity nebo URL z Garmin Connect")
    p.add_argument("--recent", type=int, metavar="N", help="vypsat posledních N aktivit")
    p.add_argument("--gpx", metavar="DIR", help="stáhnout GPX do složky (název <id>.gpx)")
    p.add_argument("--json", action="store_true", help="vypsat surová data jako JSON")
    p.add_argument("--no-splits", action="store_true", help="bez tabulky úseků")
    args = p.parse_args()

    g = client()

    if args.recent:
        print(recent_md(g.get_activities(0, args.recent)))
        return 0
    if not args.activity:
        p.error("zadej ID/URL aktivity nebo --recent N")

    aid = parse_id(args.activity)
    a = g.get_activity(aid)
    splits = None if args.no_splits else g.get_activity_splits(aid)

    if args.json:
        print(json.dumps({"summary": a, "splits": splits}, ensure_ascii=False, indent=2))
    else:
        print(summary_md(a, splits))

    if args.gpx:
        data = g.download_gpx(aid)
        os.makedirs(args.gpx, exist_ok=True)
        path = os.path.join(args.gpx, f"garmin-{aid}.gpx")
        with open(path, "wb") as f:
            f.write(data)
        print(f"\nGPX uloženo: {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
