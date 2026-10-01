"""Stahne vysledky zavodu z casomiry sport-base.eu (trailove a OCR zavody apod.) pres jejich verejne API.

Pouziti:
    python sportbase_results.py <slug-nebo-URL>                      # prehled trati a kategorii
    python sportbase_results.py <slug-nebo-URL> --find "Kratoch"     # najdi zavodnika (regex, bez ohledu na diakritiku/velikost)
    python sportbase_results.py <slug-nebo-URL> --track OPEN --top 10
    python sportbase_results.py <slug-nebo-URL> --track OPEN --json  # surova data

Slug je cast URL: https://sport-base.eu/competitions/<slug>/results?track=open
API: https://sport-base.eu/api/public/competition/<slug>  ->  id
     https://sport-base.eu/api/public/competition/<id>/results            (tratě + kategorie)
     https://sport-base.eu/api/public/competition/<id>/results/entries?trackId=<uuid>
Pozn.: nemerene kategorie (napr. FUN vlny u OCR zavodu) ve vysledcich nejsou vubec.
Demo: kdyz vedle skriptu existuje demo_data/ (nebo DEMO_MODE=1), cte fixtures misto API.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
API = "https://sport-base.eu/api/public"
# Demo rezim: existuje-li vedle skriptu slozka demo_data/ (nebo DEMO_MODE=1), sit se nevola
# a odpovedi API se ctou z JSON fixtures (stejny tvar). Pro realna data slozku smaz.
DEMO_DIR = Path(__file__).resolve().parent / "demo_data"
DEMO = DEMO_DIR.is_dir() or os.environ.get("DEMO_MODE") == "1"


def demo_get(url):
    """URL verejneho API -> soubor v demo_data/ (None = 'nenalezeno', jako prazdna odpoved API)."""
    path = url[len(API):]
    for pattern, name in ((r"/competition/(\d+)/results/entries\?trackId=([\w-]+)$", "entries-{1}.json"),
                          (r"/competition/(\d+)/results$", "results-{0}.json"),
                          (r"/competition/([^/?#]+)$", "competition-{0}.json")):
        m = re.match(pattern, path)
        if m:
            f = DEMO_DIR / name.format(*m.groups())
            return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else None
    return None


def get(url):
    if DEMO:
        return demo_get(url)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return json.loads(data) if data else None


def slug_of(s: str) -> str:
    m = re.search(r"/competitions/([^/?#]+)", s)
    return m.group(1) if m else s.strip("/ ")


def ms(t):
    if t is None:
        return "–"
    s = int(round(t / 1000))
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower()


def row(r):
    cats = ", ".join(f"{c['short']} {rk['rank']}." for c, rk in zip(r["categories"], r["categoryRanks"]) if rk.get("rank"))
    members = "; ".join(m["displayName"] or "" for m in r["members"]) if len(r["members"]) > 1 else ""
    dq = f" ❌ {r['disqualification']}" if r.get("disqualification") else ""
    return f"| {r['trackPosition'] or '–'} | {r['displayName']}{(' (' + members + ')') if members else ''} | {r['bibNumber']} | {ms(r['timeMs'])} | +{ms(r['trackLossTimeMs'])} | {cats}{dq} |"


HEADER = "| Poř. | Jméno | BIB | Čas | Ztráta | Kategorie |\n|---|---|---|---|---|---|"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("competition", help="slug nebo URL závodu na sport-base.eu")
    p.add_argument("--track", help="zkratka tratě (OPEN, RACE, …); bez ní jen přehled tratí")
    p.add_argument("--find", help="regex na jméno závodníka / člena týmu (hledá ve všech tratích, když není --track)")
    p.add_argument("--top", type=int, default=0, help="vypsat prvních N z tratě")
    p.add_argument("--json", action="store_true", help="surová data tratě")
    a = p.parse_args()
    if DEMO:
        print("[demo] sport-base.eu se nevolá, výsledky jsou z demo_data/ "
              f"({', '.join(sorted(f.stem[12:] for f in DEMO_DIR.glob('competition-*.json')))})", file=sys.stderr)

    comp = get(f"{API}/competition/{slug_of(a.competition)}")
    if not comp:
        sys.exit("Závod nenalezen" + (" ve fixtures demo_data/" if DEMO else ""))
    idx = get(f"{API}/competition/{comp['id']}/results") or {}
    tracks = idx.get("tracks", [])
    print(f"# {comp['name']} — {comp.get('date', '')[:10]}, {comp.get('location', '')}  (výsledků: {idx.get('resultCount', 0)})")

    wanted = [t for t in tracks if not a.track or t["short"].upper() == a.track.upper()]
    if a.track and not wanted:
        sys.exit(f"Trať {a.track} neexistuje; k dispozici: {[t['short'] for t in tracks]}")

    if not a.track and not a.find:
        for t in tracks:
            print(f"- **{t['short']}** ({t['name']}): " + ", ".join(f"{c['short']} {c['resultCount']}" for c in t["categories"]))
        return 0

    for t in wanted:
        data = get(f"{API}/competition/{comp['id']}/results/entries?trackId={t['id']}") or {}
        res = data.get("results", [])
        if a.json:
            print(json.dumps(data, ensure_ascii=False, indent=1))
            continue
        finishers = [r for r in res if r.get("timeMs")]
        if finishers:
            times = sorted(r["timeMs"] for r in finishers)
            print(f"\n## {t['short']} — {len(finishers)} finisherů, vítěz {ms(times[0])}, medián {ms(times[len(times) // 2])}")
        if a.find:
            pat = re.compile(fold(a.find), re.I)
            hits = [r for r in res if pat.search(fold(r["displayName"] + " " + " ".join(m["displayName"] or "" for m in r["members"])))]
            print(f"Hledání „{a.find}“: {len(hits)} shod")
            if hits:
                print(HEADER)
                for r in hits:
                    print(row(r))
        if a.top:
            print(HEADER)
            for r in res[: a.top]:
                print(row(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
