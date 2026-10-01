"""Generator fiktivnich Garmin fixtures pro demo vault (deterministicky). Spust: python _generate.py

Seznam aktivit (ID, souhrnna cisla) se kopiruje z denik-souhrn/demo_data/activities.json; tady se k zavodum
a aktivitam od 1. 9. 2026 dopocitaji detaily (summaryDTO), useky po km a male fiktivni GPX u zavodu.
Soubory zavodu (activity-/splits-/garmin-<id>) se pri opakovanem spusteni neprepisuji - z jejich cisel
vychazeji race notes. Poradi: nejdriv denik-souhrn/demo_data/_generate.py, pak tento skript.
"""
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent
rnd = random.Random(20261001)

TYPE_IDS = {"running": 1, "trail_running": 6, "obstacle_run": 158, "bouldering": 165}


def type_dto(t):
    return {"typeId": TYPE_IDS[t], "typeKey": t, "parentTypeId": 1 if t != "bouldering" else 17}


def gmt(local):
    d = datetime.fromisoformat(local) - timedelta(hours=2)  # CEST
    return d


def lap_paces(profile, n, last_frac):
    """relativni tempo (koeficient) a prevyseni pro kazdy usek"""
    out = []
    for i in range(n):
        x = i / max(n - 1, 1)
        if profile == "trail":
            # kopce v 3.-6. km a 12.-15. km, sbehy po nich
            hill = math.sin(x * math.pi * 2.2) * 0.18
            k = 1.0 + hill + rnd.uniform(-0.04, 0.04)
            gain = max(0, hill) * 260 + rnd.uniform(5, 18)
            loss = max(0, -hill) * 260 + rnd.uniform(5, 18)
        elif profile == "halfmarathon_fade":
            k = 0.965 if x < 0.48 else 1.0 if x < 0.72 else 1.06
            k += rnd.uniform(-0.012, 0.012)
            gain = rnd.uniform(2, 7)
            loss = rnd.uniform(2, 7)
        elif profile == "ocr":
            k = 1.0 + rnd.uniform(-0.2, 0.25)
            gain = rnd.uniform(10, 30)
            loss = rnd.uniform(10, 30)
        else:
            k = 1.0 + rnd.uniform(-0.035, 0.035)
            gain = rnd.uniform(3, 12)
            loss = rnd.uniform(3, 12)
        out.append([k, gain, loss])
    return out


def build(aid, start, name, typ, loc, dist, dur, moving, hr, maxhr, gain, minel, maxel, cad, te, ane, load,
          vo2, tmin, tmax, cal, profile):
    n_full = int(dist // 1000)
    rest = dist - n_full * 1000
    dists = [1000.0] * n_full + ([rest] if rest > 1 else [])
    prof = lap_paces(profile, len(dists), rest / 1000)
    weights = [p[0] * d for p, d in zip(prof, dists)]
    scale = dur / sum(weights)
    gscale = gain / sum(p[1] for p in prof)
    lscale = gain / sum(p[2] for p in prof)
    t0 = gmt(start)
    laps = []
    elapsed = 0.0
    for i, (d, p) in enumerate(zip(dists, prof)):
        ld = round(weights[i] * scale, 1)
        lmov = round(ld * moving / dur, 1)
        frac = i / max(len(dists) - 1, 1)
        lhr = round(hr - 6 + 10 * frac + (p[0] - 1) * 12 + rnd.uniform(-2, 2))
        laps.append({
            "lapIndex": i + 1,
            "startTimeGMT": (t0 + timedelta(seconds=elapsed)).strftime("%Y-%m-%dT%H:%M:%S.0"),
            "distance": round(d, 2),
            "duration": ld,
            "movingDuration": lmov,
            "elapsedDuration": ld,
            "averageSpeed": round(d / ld, 3),
            "averageMovingSpeed": round(d / lmov, 3),
            "maxSpeed": round(d / ld * rnd.uniform(1.12, 1.3), 3),
            "averageHR": lhr,
            "maxHR": min(maxhr, lhr + rnd.randint(4, 9)),
            "elevationGain": round(p[1] * gscale),
            "elevationLoss": round(p[2] * lscale),
            "averageRunCadence": round(cad + rnd.uniform(-4, 4), 1),
            "calories": round(cal * ld / dur),
        })
        elapsed += ld
    avg_speed = dist / dur
    summary_common = dict(
        distance=float(dist), duration=dur, movingDuration=moving, elapsedDuration=dur,
        elevationGain=float(gain), elevationLoss=float(gain), minElevation=float(minel), maxElevation=float(maxel),
        averageSpeed=round(avg_speed, 3), averageMovingSpeed=round(dist / moving, 3),
        maxSpeed=round(max(l["maxSpeed"] for l in laps), 3), calories=float(cal),
        averageHR=float(hr), maxHR=float(maxhr), steps=int(dur / 60 * cad),
        anaerobicTrainingEffect=ane, activityTrainingLoad=float(load),
        minTemperature=float(tmin), maxTemperature=float(tmax),
    )
    detail = {
        "activityId": aid, "activityName": name, "locationName": loc,
        "activityTypeDTO": type_dto(typ),
        "summaryDTO": dict(startTimeLocal=start.replace(" ", "T") + ".0",
                           startTimeGMT=t0.strftime("%Y-%m-%dT%H:%M:%S.0"),
                           averageRunCadence=float(cad), trainingEffect=te, **summary_common),
    }
    listing = dict(activityId=aid, activityName=name, startTimeLocal=start,
                   startTimeGMT=t0.strftime("%Y-%m-%d %H:%M:%S"), activityType=type_dto(typ), locationName=loc,
                   averageRunningCadenceInStepsPerMinute=float(cad), aerobicTrainingEffect=te, vO2MaxValue=vo2,
                   **summary_common)
    splits = {"activityId": aid, "lapDTOs": laps}
    return detail, listing, splits


def gpx(aid, name, start, laps, center):
    """Maly fiktivni GPX: smycka kolem stredu, jeden bod na usek."""
    lat0, lon0 = center
    t = gmt(start)
    pts = []
    n = len(laps)
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        lat = lat0 + 0.035 * math.sin(a)
        lon = lon0 + 0.055 * math.cos(a) - 0.055
        ele = 420 + 140 * max(0, math.sin(a * 2.2))
        pts.append(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}"><ele>{ele:.1f}</ele>'
                   f'<time>{t.strftime("%Y-%m-%dT%H:%M:%SZ")}</time></trkpt>')
        if i < n:
            t += timedelta(seconds=laps[i]["duration"])
    return ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<gpx version=\"1.1\" creator=\"demo fixtures (fiktivni trasa)\" xmlns=\"http://www.topografix.com/GPX/1/1\">\n"
            f"  <trk>\n    <name>{name}</name>\n    <trkseg>\n" + "\n".join(pts) + "\n    </trkseg>\n  </trk>\n</gpx>\n")


# --- listing = kopie denik-souhrn/demo_data/activities.json (jediny zdroj pravdy pro ID a souhrnna cisla) ---
SRC = OUT.parents[1] / "denik-souhrn" / "demo_data" / "activities.json"
listing = json.loads(SRC.read_text(encoding="utf-8"))
RACE_IDS = {"18412337051", "19287415560", "19468803217", "20104559832"}  # detaily zavodu jsou zamrazene (cisla v race notes)
for f in OUT.glob("*"):
    if f.name != Path(__file__).name and f.stem.split("-")[-1] not in RACE_IDS:
        f.unlink()
(OUT / "activities.json").write_text(json.dumps(listing, ensure_ascii=False, indent=1), encoding="utf-8")

RACE_EXTRA = {
    18412337051: dict(loc="Dobříš", minel=398, maxel=716, cad=166, te=4.6, ane=2.1, load=312, vo2=49, tmin=9, tmax=14,
                      profile="trail", center=(49.78, 14.12)),
    19287415560: dict(loc="Praha", minel=187, maxel=231, cad=174, te=4.9, ane=2.4, load=356, vo2=51, tmin=14, tmax=19,
                      profile="halfmarathon_fade", center=(50.07, 14.42)),
    19468803217: dict(loc="Benešov", minel=352, maxel=448, cad=158, te=4.1, ane=3.2, load=241, vo2=51, tmin=21, tmax=25,
                      profile="ocr", center=(49.78, 14.69)),
    20104559832: dict(loc="Dobříš", minel=398, maxel=716, cad=169, te=4.8, ane=2.6, load=338, vo2=52, tmin=11, tmax=16,
                      profile="trail", center=(49.78, 14.12)),
}

for a in listing:
    aid = a["activityId"]
    typ = a["activityType"]["typeKey"]
    if aid not in RACE_EXTRA and a["startTimeLocal"] < "2026-09-01":
        continue  # starsi treninky: detail si DemoGarmin poskladá z listingu (bez useku)
    if aid in RACE_EXTRA and (OUT / f"activity-{aid}.json").is_file():
        continue  # zavod: existujici detail, useky a GPX se neprepisuji (odkazuji na ne race notes)
    if typ in ("bouldering", "hiking", "mountaineering", "cycling") and aid not in RACE_EXTRA:
        loc = "Karlštejn" if "Karlstejn" in a["activityName"] else "Praha"
        t0 = gmt(a["startTimeLocal"])
        detail = {"activityId": aid, "activityName": a["activityName"], "locationName": loc,
                  "activityTypeDTO": a["activityType"],
                  "summaryDTO": dict(startTimeLocal=a["startTimeLocal"].replace(" ", "T") + ".0",
                                     startTimeGMT=t0.strftime("%Y-%m-%dT%H:%M:%S.0"),
                                     **{k: a[k] for k in a if k not in ("activityId", "activityName", "activityType",
                                                                         "startTimeLocal", "startTimeGMT")})}
        splits = {"activityId": aid, "lapDTOs": []}
    else:
        x = RACE_EXTRA.get(aid) or dict(loc="Praha", minel=188, maxel=188 + int(a["elevationGain"] // 2) + 20, cad=168,
                                        te=round(2.4 + (a["averageHR"] - 138) / 10, 1),
                                        ane=2.1 if a["averageHR"] >= 150 else 0.6, load=round(a["duration"] / 60 * 1.3),
                                        vo2=51, tmin=11, tmax=18, profile="flat", center=None)
        detail, _l, splits = build(aid, a["startTimeLocal"], a["activityName"], typ, x["loc"], a["distance"],
                                   a["duration"], a["movingDuration"], a["averageHR"], a["maxHR"], a["elevationGain"],
                                   x["minel"], x["maxel"], x["cad"], x["te"], x["ane"], x["load"], x["vo2"], x["tmin"],
                                   x["tmax"], a["calories"], x["profile"])
        if x.get("center"):
            (OUT / f"garmin-{aid}.gpx").write_text(gpx(aid, a["activityName"], a["startTimeLocal"], splits["lapDTOs"],
                                                       x["center"]), encoding="utf-8")
    (OUT / f"activity-{aid}.json").write_text(json.dumps(detail, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"splits-{aid}.json").write_text(json.dumps(splits, ensure_ascii=False, indent=1), encoding="utf-8")
    print(aid, a["startTimeLocal"], a["activityName"])
