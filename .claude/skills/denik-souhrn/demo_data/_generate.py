#!/usr/bin/env python3
"""Deterministicky generator demo fixtures pro garmin_days.py - podle dennich poznamek.

Vytvori vedle sebe dva JSON soubory ve stejnem tvaru, jaky vraci garminconnect:
  daily_steps.json  - jako Garmin.get_daily_steps(start, end)       (seznam dni)
  activities.json   - jako Garmin.get_activities_by_date(start, end) (seznam aktivit, od nejnovejsi)

Obdobi 2025-10-01 .. 2026-09-30. Aktivity se berou z dennich poznamek Denik:
  - beh: kazda odrazka s "beh"/"vyklus" a "N km" (tempo "m:ss/km" z textu, jinak dopocitane podle mesice)
  - bouldering: odrazka zacinajici "Bouldering" (od ledna 2026, streda)
  - zavody, kolo, turistika, ferraty, parkrun: rucni tabulka MANUAL (cisla z textu poznamky)
  Dny bez denni poznamky: aktivita jen podle ritualu (ut/ct beh, ne dlouhy beh, st bouldering)
  a jen mimo pauzy (nachlazeni, Viden, Vanoce, natazene lytko, Lisabon, Dolomity, okoli zavodu).
  Kroky: zaklad podle typu dne (vsedni den, vikend, home office, nemoc, cestovani, Lisabon,
  Viden, chalupa, Dolomity, prochazka) + kroky z aktivit; NO_WATCH = zapomenute hodinky.
4 zavody maji pevna ID a cisla z _PERSONA.md; aktivity v zari 2026 drzi ID detailu ve
garmin-aktivita/demo_data (activity-<id>.json), kde aktivita ve stejny den existuje (SEPT_IDS).
Fixni seed -> opakovane spusteni vyrobi totozne soubory (dokud se nezmeni denni poznamky).

Pouziti: python .claude/skills/denik-souhrn/demo_data/_generate.py
Potom:   python .claude/skills/garmin-aktivita/demo_data/_generate.py   (detaily, useky, GPX)
"""
import json
import random
import re
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parents[3]
CARPE = VAULT / "Denik"
START, END = date(2025, 10, 1), date(2026, 9, 30)
rnd = random.Random(20261001)

# --- pevne udalosti -------------------------------------------------------------------------
RACES = {  # zavody: presne puvodni zaznamy (ID a cisla z _PERSONA.md), nemenit
    date(2025, 10, 11): {"activityId": 18412337051, "activityName": "Brdska dvacitka 2025", "startTimeLocal": "2025-10-11 09:30:00", "startTimeGMT": "2025-10-11 07:30:00", "activityType": {"typeKey": "trail_running", "typeId": 0, "parentTypeId": 0}, "distance": 20400.0, "duration": 7600.0, "movingDuration": 7583.0, "elevationGain": 520.0, "averageHR": 162.0, "maxHR": 183.0, "calories": 1383.0, "averageSpeed": 2.684},
    date(2026, 5, 16): {"activityId": 19287415560, "activityName": "Vltavsky pulmaraton 2026", "startTimeLocal": "2026-05-16 09:00:00", "startTimeGMT": "2026-05-16 07:00:00", "activityType": {"typeKey": "running", "typeId": 0, "parentTypeId": 0}, "distance": 21100.0, "duration": 6728.0, "movingDuration": 6719.0, "elevationGain": 64.0, "averageHR": 168.0, "maxHR": 192.0, "calories": 1212.0, "averageSpeed": 3.136},
    date(2026, 6, 20): {"activityId": 19468803217, "activityName": "Bahenni liska 2026", "startTimeLocal": "2026-06-20 10:40:00", "startTimeGMT": "2026-06-20 08:40:00", "activityType": {"typeKey": "obstacle_run", "typeId": 0, "parentTypeId": 0}, "distance": 8000.0, "duration": 4350.0, "movingDuration": 4343.0, "elevationGain": 180.0, "averageHR": 158.0, "maxHR": 182.0, "calories": 820.0, "averageSpeed": 1.839},
    date(2026, 9, 26): {"activityId": 20104559832, "activityName": "Brdska dvacitka 2026", "startTimeLocal": "2026-09-26 09:30:00", "startTimeGMT": "2026-09-26 07:30:00", "activityType": {"typeKey": "trail_running", "typeId": 0, "parentTypeId": 0}, "distance": 20400.0, "duration": 7092.0, "movingDuration": 7063.0, "elevationGain": 520.0, "averageHR": 160.0, "maxHR": 175.0, "calories": 1402.0, "averageSpeed": 2.876},
}
RACE_STEPS = {date(2025, 10, 11): 19800, date(2026, 5, 16): 20600, date(2026, 6, 20): 9800, date(2026, 9, 26): 19400}

# zari 2026: ID existujicich detailu v garmin-aktivita/demo_data, (den, typ) -> ID
SEPT_IDS = {
    (date(2026, 9, 1), "running"): 19909660837, (date(2026, 9, 2), "bouldering"): 19918016097,
    (date(2026, 9, 6), "running"): 19928066533, (date(2026, 9, 8), "running"): 19938521100,
    (date(2026, 9, 9), "bouldering"): 19949333325, (date(2026, 9, 10), "running"): 19958598197,
    (date(2026, 9, 13), "running"): 19977920445, (date(2026, 9, 15), "running"): 19986279982,
    (date(2026, 9, 16), "bouldering"): 19996602862, (date(2026, 9, 20), "running"): 20020211373,
    (date(2026, 9, 22), "running"): 20028235550, (date(2026, 9, 24), "running"): 20037940409,
    (date(2026, 9, 29), "running"): 20046107435,
    # nove - dny, ktere puvodni fixtures nemely
    (date(2026, 9, 19), "hiking"): 20013874126, (date(2026, 9, 23), "bouldering"): 20033016548,
    (date(2026, 9, 28), "running"): 20041592380, (date(2026, 9, 30), "bouldering"): 20051208813,
}
# kotvy pro ostatni ID (Garmin ID rostou s casem): mezi nimi linearni interpolace podle data
ID_ANCHORS = [(date(2025, 10, 1), 18381000000), (date(2025, 10, 11), 18412337051), (date(2026, 5, 16), 19287415560),
              (date(2026, 6, 20), 19468803217), (date(2026, 9, 1), 19909660837)]

# rucni aktivity podle textu poznamek: den -> [(typeKey, nazev, km, sekundy, start, prevyseni, tep)]
MANUAL = {
    date(2026, 2, 28): [("cycling", "Praha Kolo", 23.6, 4980, "13:40:00", 140, 118)],           # prvni vyjizdka k Vltave
    date(2026, 3, 14): [("running", "parkrun Stromovka", 5.0, 1490, "09:00:00", 12, 166)],      # parkrun s Radkem
    date(2026, 3, 28): [("running", "Praha Beh", 9.1, 3120, "08:20:00", 45, 146)],              # dlouhy beh, na 9. km lytko
    date(2026, 5, 8): [("cycling", "Krivoklatsko Kolo", 40.3, 8460, "09:40:00", 560, 121)],     # svatek, kolo s Lucii
    date(2026, 6, 9): [("cycling", "Posazavi Kolo", 44.8, 9120, "09:50:00", 430, 119)],         # Luciiny narozeniny
    date(2026, 6, 30): [("cycling", "Orlicke hory Kolo", 21.4, 5280, "14:30:00", 480, 124)],    # + beh po hrebenovce (z textu)
    date(2026, 7, 2): [("hiking", "Velka Destna Turistika", 15.2, 17400, "09:10:00", 640, 108)],
    date(2026, 7, 11): [("running", "Praha Beh", 3.0, 960, "08:10:00", 18, 141)],               # zkusebni kolecko 3 km
    date(2026, 8, 9): [("hiking", "Pralongia Turistika", 12.1, 13800, "09:30:00", 430, 104)],
    date(2026, 8, 10): [("mountaineering", "Ferrata Brigata Tridentina", 11.3, 22260, "07:30:00", 1060, 128)],
    date(2026, 8, 11): [("walking", "Lago di Braies Chuze", 4.1, 4200, "08:05:00", 45, 92)],
    date(2026, 8, 12): [("hiking", "Tre Cime Turistika", 10.2, 13500, "07:05:00", 470, 106)],
    date(2026, 8, 14): [("mountaineering", "Ferrata Col dei Bos", 5.6, 12600, "08:10:00", 610, 126)],
    date(2026, 9, 19): [("hiking", "Beroun Karlstejn Turistika", 11.2, 10200, "10:20:00", 290, 102)],
}
MANUAL_ONLY = {d for d in MANUAL if d != date(2026, 6, 30)}  # v techto dnech se text na behy neparsuje
TRAIL_DAYS = {date(2026, 6, 30), date(2026, 7, 1)}  # behy po hrebenovce
NO_WATCH = {date(2025, 10, 29), date(2026, 1, 2), date(2026, 2, 21), date(2026, 9, 3)}  # zapomenute hodinky

COLD = (date(2025, 11, 10), date(2025, 11, 16))
VIENNA = (date(2025, 12, 6), date(2025, 12, 7))
XMAS = (date(2025, 12, 22), date(2025, 12, 27))
CALF = (date(2026, 3, 28), date(2026, 4, 6))
LISBON = (date(2026, 4, 16), date(2026, 4, 20))
CHALUPA = (date(2026, 6, 28), date(2026, 7, 3))
DOLOMITY = (date(2026, 8, 8), date(2026, 8, 15))

RUN_RE = re.compile(r"\b(beh|vyklus)\b", re.I)
KM_RE = re.compile(r"(\d+(?:[.,]\d)?)\s*km")
PACE_RE = re.compile(r"(\d):(\d\d)/km")
NOT_RUN = ("->", "tydne", "odpada", "bez behu", "az po", "zpatky na beh", "rozvrh")


def within(d, period):
    return period[0] <= d <= period[1]


def note(d):
    p = CARPE / str(d.year) / d.strftime("%Y-%m") / f"{d.isoformat()}.md"
    if not p.exists():
        return None
    return [l for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip().startswith("-") and "Garmin:" not in l and not re.match(r"^\s*-\s*xjs\b", l)]


def pace_for(d):
    """Postupne zlepseni: rijen 2025 ~5:45/km, kveten 2026 ~5:20/km, zari 2026 ~5:10/km."""
    months = (d.year - 2025) * 12 + d.month - 10
    return round(345 - months * 3.0)


def gmt(local, d):
    summer = d < date(2025, 10, 26) or date(2026, 3, 29) <= d < date(2026, 10, 25)
    return local - timedelta(hours=2 if summer else 1)


def new_id(d, type_key, local):
    if (d, type_key) in SEPT_IDS:
        return SEPT_IDS[(d, type_key)]
    for (d0, i0), (d1, i1) in zip(ID_ANCHORS, ID_ANCHORS[1:]):
        if d0 <= d < d1:
            frac = ((d - d0).days + local.hour / 24) / (d1 - d0).days
            return int(i0 + (i1 - i0) * frac) + rnd.randint(1000, 90000)
    raise SystemExit(f"{d} {type_key}: chybi ID (doplnit SEPT_IDS)")


def act(d, type_key, name, meters, seconds, start, elev, hr):
    local = datetime.fromisoformat(f"{d.isoformat()} {start}")
    kcal_min = {"bouldering": 6.8, "walking": 4.5, "hiking": 6.5, "mountaineering": 7.5, "cycling": 8.0}.get(type_key, 11.0)
    return {
        "activityId": new_id(d, type_key, local),
        "activityName": name,
        "startTimeLocal": local.strftime("%Y-%m-%d %H:%M:%S"),
        "startTimeGMT": gmt(local, d).strftime("%Y-%m-%d %H:%M:%S"),
        "activityType": {"typeKey": type_key, "typeId": 0, "parentTypeId": 0},
        "distance": float(meters),
        "duration": float(seconds),
        "movingDuration": float(seconds - rnd.randint(0, 40 if seconds < 7200 else 900)),
        "elevationGain": float(elev),
        "averageHR": float(hr),
        "maxHR": float(min(hr + rnd.randint(12, 22), 190)),
        "calories": float(round(seconds / 60 * kcal_min * rnd.uniform(0.93, 1.07))),
        "averageSpeed": round(meters / seconds, 3) if meters else 0.0,
    }


def run_start(text, d, long_run):
    t = text.lower()
    if "rano" in t or "ranni" in t:
        return f"0{rnd.choice([6, 7])}:{rnd.choice(['05', '15', '24', '38'])}:00"
    if "vecer" in t:
        return f"19:{rnd.choice(['02', '14', '27'])}:00"
    if long_run or d.weekday() >= 5:
        return f"08:{rnd.choice(['20', '30', '45'])}:00"
    return f"{rnd.choice(['06', '07', '18', '18', '19'])}:{rnd.choice(['05', '12', '24', '41', '50'])}:00"


def place(text, d):
    t = text.lower()
    if within(d, LISBON):
        return "Lisboa"
    if "brne" in t or "svratk" in t:
        return "Brno"
    if "hradc" in t or "labe" in t:
        return "Hradec Kralove"
    if within(d, CHALUPA) and d != CHALUPA[0]:
        return "Orlicke hory"
    return "Praha"


def run_from(text, d, km, pace):
    t = text.lower()
    long_run = "dlouh" in t or km >= 12
    pace = pace or (pace_for(d) + (12 if long_run else 0))
    meters = round(km * 1000 + rnd.randint(-35, 45))
    secs = round(meters / 1000 * pace + rnd.randint(-3, 3))
    trail = d in TRAIL_DAYS
    hr = 158 if any(w in t for w in ("tempov", "interval", "parkrun")) else (148 if long_run else 145)
    hr += rnd.randint(-4, 4) - (6 if any(w in t for w in ("volne", "lehk", "vyklus", "opatrne")) else 0)
    if "prokop" in t or "sark" in t:
        elev = rnd.randint(150, 230)
    elif trail:
        elev = rnd.randint(260, 340)
    else:
        elev = rnd.randint(25, 80) + (40 if long_run else 0)
    name = f"{place(text, d)} {'Trailovy beh' if trail else 'Beh'}"
    return act(d, "trail_running" if trail else "running", name, meters, secs, run_start(text, d, long_run), elev, hr)


def bouldering(d, text=""):
    t = text.lower()
    mins = 50 if "lehce" in t else 60 if "hodin" in t else rnd.randint(75, 100)
    return act(d, "bouldering", "Praha Bouldering", 0, mins * 60 + rnd.randint(0, 50), "18:05:00", 0, rnd.randint(108, 122))


def steps_for(a):
    k = a["activityType"]["typeKey"]
    km = a["distance"] / 1000
    if k in ("running", "trail_running"):
        return int(km * rnd.randint(860, 940))
    if k in ("hiking", "walking"):
        return int(km * rnd.randint(1250, 1400))
    if k == "mountaineering":
        return int(km * rnd.randint(1500, 1700))
    if k == "bouldering":
        return rnd.randint(900, 1600)
    return 0


def base_steps(d, lines, hiked=False):
    t = " ".join(lines or []).lower()
    wd = d.weekday()
    if within(d, COLD):
        b = rnd.randint(1900, 3800) + (2600 if "prochazka" in t else 0)
    elif within(d, LISBON):  # 18. 4. Sintra: "nachozeno pres 25 tisic kroku"
        b = {16: 19500, 17: 22800, 18: 25900, 19: 13900, 20: 8200}[d.day] + rnd.randint(-400, 400)
    elif within(d, VIENNA):
        b = rnd.randint(15500, 18500)
    elif within(d, DOLOMITY):
        if d in (DOLOMITY[0], DOLOMITY[1]):  # cesta autem tam a zpet
            b = rnd.randint(3600, 4800)
        elif d == date(2026, 8, 13):  # bourky - Cortina, prochazka centrem
            b = rnd.randint(10500, 12500)
        else:
            b = rnd.randint(5000, 6500)
    elif within(d, XMAS):
        b = rnd.randint(3800, 7200)
    elif within(d, CHALUPA):
        b = rnd.randint(9000, 12500) if d not in (CHALUPA[0], CHALUPA[1]) else rnd.randint(6000, 8000)
    elif within(d, CALF):
        b = rnd.randint(3000, 5200)
    elif "home office" in t:
        b = rnd.randint(3200, 5200)
    elif wd < 5:
        b = rnd.randint(6200, 9000)
    else:
        b = rnd.randint(4800, 9500)
    if lines is not None and not hiked and not within(d, LISBON) and not within(d, DOLOMITY) and not within(d, COLD) \
            and any(w in t for w in ("prochazk", "pesky", "trh na", "vyklizeni", "vyklidili")):
        b += rnd.randint(3500, 6000)
    if hiked:  # vylet = vetsina kroku je v aktivite
        b = min(b, rnd.randint(4500, 6500))
    if d == date(2026, 9, 17):  # konference - cely den na nohou
        b = rnd.randint(10500, 12000)
    return b


steps_rows, acts = [], []
d = START
while d <= END:
    wd = d.weekday()
    lines = note(d)
    todays = []
    if d in RACES:
        todays.append(dict(RACES[d]))
    for k, name, km, secs, start, elev, hr in MANUAL.get(d, []):
        todays.append(act(d, k, name, round(km * 1000), secs, start, elev, hr))
    if lines is not None and d not in RACES and d not in MANUAL_ONLY:
        for l in lines:
            low = l.lower()
            if re.match(r"^\s*-\s*(prvni )?bouldering", low) and "vynechal" not in low:
                todays.append(bouldering(d, l))
                continue
            if not RUN_RE.search(low) or any(x in low for x in NOT_RUN):
                continue
            km_m, pace_m = KM_RE.search(l), PACE_RE.search(l)
            if not km_m:
                continue
            km = float(km_m.group(1).replace(",", "."))
            pace = int(pace_m.group(1)) * 60 + int(pace_m.group(2)) if pace_m else None
            todays.append(run_from(l, d, km, pace))
    elif lines is None:
        # bez denni poznamky: jen ritual a jen mimo pauzy
        paused = (within(d, COLD) or within(d, XMAS) or within(d, CALF) or within(d, LISBON) or within(d, DOLOMITY)
                  or within(d, VIENNA) or any(abs((d - r).days) <= 1 for r in RACES))
        if not paused and d not in NO_WATCH:
            if wd in (1, 3):
                todays.append(run_from("Beh", d, rnd.choice([7, 8, 8, 9]), None))
            elif wd == 6:
                todays.append(run_from("Dlouhy beh", d, 10 if d < date(2026, 3, 1) else 14, None))
            elif wd == 2 and d >= date(2026, 1, 7):
                # 23. 9.: plan W39 "bouldering lehce" (tyden pred Brdy)
                todays.append(bouldering(d, "lehce" if d == date(2026, 9, 23) else ""))
    if d in NO_WATCH:
        assert not todays, f"{d}: NO_WATCH, ale v poznamce je aktivita"
        total = 0
    else:
        hiked = any(a["activityType"]["typeKey"] in ("hiking", "walking", "mountaineering") for a in todays)
        total = base_steps(d, lines, hiked) + sum(RACE_STEPS[d] if d in RACES and a["activityId"] == RACES[d]["activityId"]
                                           else steps_for(a) for a in todays)
    steps_rows.append({
        "calendarDate": d.isoformat(),
        "totalSteps": total,
        "totalDistance": int(total * 0.78),
        "stepGoal": rnd.randint(7800, 10200) if total else 0,  # adaptivni cil, skript ho ignoruje
    })
    acts.extend(todays)
    d += timedelta(days=1)

ids = [a["activityId"] for a in acts]
assert len(ids) == len(set(ids)), "duplicitni activityId"
missing = {v for v in SEPT_IDS.values()} - set(ids)
assert not missing, f"SEPT_IDS bez aktivity: {missing}"
acts.sort(key=lambda a: a["startTimeLocal"], reverse=True)  # API vraci od nejnovejsich

(HERE / "daily_steps.json").write_text(json.dumps(steps_rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
(HERE / "activities.json").write_text(json.dumps(acts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"daily_steps.json: {len(steps_rows)} dni, activities.json: {len(acts)} aktivit")
