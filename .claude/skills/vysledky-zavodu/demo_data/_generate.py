"""Generator fiktivnich vysledkovek (tvar API sport-base.eu) pro demo vault. Deterministicky."""
import json
import random
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parent
NS = uuid.UUID("6f1c2a64-0000-4000-8000-00000000d3e0")

M_FIRST = ["Jan", "Petr", "Tomas", "Martin", "Jakub", "Lukas", "David", "Michal", "Ondrej", "Pavel", "Jiri", "Viktor",
           "Adam", "Matej", "Daniel", "Marek", "Stepan", "Vit", "Roman", "Karel", "Ales", "Libor", "Josef"]
F_FIRST = ["Jana", "Petra", "Lenka", "Katerina", "Tereza", "Eva", "Lucie", "Veronika", "Barbora", "Anna", "Klara",
           "Marketa", "Zuzana", "Monika", "Simona", "Hana", "Nikola", "Adela"]
# povrch jmen: obecna ceska prijmeni, bez Kratochvil/Simek (ti jsou ve vysledcich jen jako Ondra a Radek)
M_LAST = ["Novák", "Svoboda", "Černý", "Procházka", "Kučera", "Veselý", "Horák", "Němec",
          "Pokorný", "Marek", "Pospíšil", "Hájek", "Jelínek", "Král", "Fiala", "Sedláček", "Doležal",
          "Zeman", "Kolář", "Navrátil", "Čermák", "Urban", "Vaněk", "Blažek", "Kříž", "Kovář", "Bartoš",
          "Vlček", "Polák", "Musil", "Kopecký", "Šťastný", "Holub", "Mach", "Staněk", "Štěpánek", "Kadlec",
          "Malý", "Vávra", "Bláha", "Říha", "Toman", "Hruška", "Kubát", "Sýkora", "Moravec", "Matějka", "Brož",
          "Hron", "Kratina", "Paur", "Lukeš", "Rybář", "Tichý", "Hudec", "Sobotka", "Konečný", "Vondra", "Hanák"]
FEM = {"ý": "á", "a": "ová"}

FIRST_FOLD = {"Tomas": "Tomáš", "Lukas": "Lukáš", "Jiri": "Jiří", "Matej": "Matěj", "Stepan": "Štěpán", "Vit": "Vít",
              "Ales": "Aleš", "Ondrej": "Ondřej", "Katerina": "Kateřina", "Klara": "Klára", "Marketa": "Markéta",
              "Adela": "Adéla"}


def fem(last):
    if last.endswith("ý"):
        return last[:-1] + "á"
    if last.endswith("a"):
        return last[:-1] + "ová"
    if last.endswith("ek"):
        return last[:-2] + "ková"
    if last.endswith("ec"):
        return last[:-2] + "cová"
    return last + "ová"


def hms(s):
    h, m, sec = (int(x) for x in s.split(":"))
    return (h * 3600 + m * 60 + sec) * 1000


def times_with_anchors(n, anchors, rnd):
    """Rostouci casy pro poradi 1..n, presne v kotvach {poradi: ms}."""
    pts = sorted(anchors.items())
    t = [0] * (n + 1)
    for (ra, ta), (rb, tb) in zip(pts, pts[1:]):
        t[ra] = ta
        w = [rnd.uniform(0.3, 1.7) for _ in range(rb - ra)]
        tot = sum(w)
        acc = 0
        for i in range(ra + 1, rb):
            acc += w[i - ra - 1]
            t[i] = ta + int((tb - ta) * acc / tot) // 1000 * 1000
        t[rb] = tb
    return t[1:]


def age_cat(sex, age):
    p = "M" if sex == "M" else "Z"
    if age < 30:
        return p + "20", ("Muži" if sex == "M" else "Ženy") + " do 29 let"
    if age < 40:
        return p + "30", ("Muži" if sex == "M" else "Ženy") + " 30–39 let"
    if age < 50:
        return p + "40", ("Muži" if sex == "M" else "Ženy") + " 40–49 let"
    return p + "50", ("Muži" if sex == "M" else "Ženy") + " 50+"


def gen_track(comp_slug, short, name, n, anchors, specials, female_share, rnd, dnf=2, teams=0):
    """specials: {poradi: (displayName, sex, age, bib)}"""
    times = times_with_anchors(n, anchors, rnd)
    used = set()
    entries = []
    for pos in range(1, n + 1):
        if pos in specials:
            dn, sex, age, bib = specials[pos]
        else:
            # zeny spis v druhe polovine
            p_f = female_share * (0.5 + pos / n)
            sex = "Z" if rnd.random() < p_f else "M"
            for _try in range(30):  # jmenovci se ve velkych zavodech vyskytuji, ale radeji vzacne
                last = rnd.choice(M_LAST)
                first = rnd.choice(F_FIRST if sex == "Z" else M_FIRST)
                dn = f"{fem(last) if sex == 'Z' else last} {FIRST_FOLD.get(first, first)}"
                if dn not in used:
                    break
            age = rnd.randint(19, 62)
            bib = None
        used.add(dn)
        entries.append(dict(sex=sex, age=age, displayName=dn, bib=bib, timeMs=times[pos - 1]))
    for _ in range(dnf):
        sex = "M" if rnd.random() > female_share else "Z"
        last = rnd.choice(M_LAST)
        first = rnd.choice(F_FIRST if sex == "Z" else M_FIRST)
        entries.append(dict(sex=sex, age=rnd.randint(22, 55),
                            displayName=f"{fem(last) if sex == 'Z' else last} {FIRST_FOLD.get(first, first)}",
                            bib=None, timeMs=None, dq="DNF"))
    bibs = list(range(101, 101 + len(entries) + 40))
    rnd.shuffle(bibs)
    winner = entries[0]["timeMs"]
    cat_names = {}
    sex_rank, cat_rank, sex_best, cat_best, cat_count = {}, {}, {}, {}, {}
    results = []
    for i, e in enumerate(entries):
        sexc = ("M", "Muži") if e["sex"] == "M" else ("Z", "Ženy")
        agec = age_cat(e["sex"], e["age"])
        cats = [{"short": sexc[0], "name": sexc[1]}, {"short": agec[0], "name": agec[1]}]
        ranks, losses = [], []
        for c in cats:
            k = c["short"]
            cat_names[k] = c["name"]
            cat_count[k] = cat_count.get(k, 0) + 1
            if e["timeMs"] is not None:
                cat_rank[k] = cat_rank.get(k, 0) + 1
                cat_best.setdefault(k, e["timeMs"])
                ranks.append({"categoryShort": k, "rank": cat_rank[k]})
                losses.append({"categoryShort": k, "lossTimeMs": e["timeMs"] - cat_best[k]})
            else:
                ranks.append({"categoryShort": k, "rank": None})
                losses.append({"categoryShort": k, "lossTimeMs": None})
        results.append({
            "trackPosition": i + 1 if e["timeMs"] is not None else None,
            "displayName": e["displayName"],
            "bibNumber": e["bib"] or bibs[i],
            "timeMs": e["timeMs"],
            "trackLossTimeMs": e["timeMs"] - winner if e["timeMs"] is not None else None,
            "disqualification": None,
            "categories": [{"short": c["short"]} for c in cats],
            "categoryRanks": ranks,
            "categoryLosses": losses,
            "members": [{"displayName": e["displayName"]}],
        })
    track_id = str(uuid.uuid5(NS, f"{comp_slug}/{short}"))
    cat_list = []
    for k in sorted(cat_count, key=lambda x: (len(x), x)):
        cat_list.append({"short": k, "name": cat_names[k],
                         "resultCount": cat_count[k]})
    track = {"id": track_id, "short": short, "name": name, "resultCount": len(results), "categories": cat_list}
    return track, {"trackId": track_id, "results": results}


COMPETITIONS = [
    dict(slug="brdska-dvacitka-2025", id=4182, name="Brdská dvacítka 2025", date="2025-10-11T09:30:00+02:00",
         location="Dobříš, Brdy", tracks=[
             dict(short="20K", name="Trail 20 km (+520 m)", n=148,
                  anchors={1: hms("1:28:41"), 10: hms("1:39:52"), 42: hms("1:57:15"), 61: hms("2:06:40"),
                           74: hms("2:13:05"), 120: hms("2:34:10"), 148: hms("3:12:47")},
                  specials={42: ("Šimek Radek", "M", 33, 214), 61: ("Kratochvíl Ondřej", "M", 33, 215)},
                  female=0.3),
             dict(short="10K", name="Trail 10 km (+240 m)", n=96,
                  anchors={1: hms("0:41:12"), 48: hms("1:04:30"), 96: hms("1:38:02")}, specials={}, female=0.45),
         ]),
    dict(slug="vltavsky-pulmaraton-2026", id=4519, name="Vltavský půlmaraton 2026", date="2026-05-16T09:00:00+02:00",
         location="Praha, náplavka", tracks=[
             dict(short="21K", name="Půlmaraton 21,1 km", n=1830,
                  anchors={1: hms("1:09:38"), 10: hms("1:16:40"), 100: hms("1:33:20"), 412: hms("1:52:08"),
                           915: hms("2:04:55"), 1500: hms("2:22:10"), 1830: hms("2:58:31")},
                  specials={412: ("Kratochvíl Ondřej", "M", 34, 3127)}, female=0.38, dnf=14),
         ]),
    dict(slug="bahenni-liska-2026", id=4603, name="Bahenní liška 2026", date="2026-06-20T10:40:00+02:00",
         location="Benešov, lom Kaliště", tracks=[
             dict(short="RACE", name="RACE 8 km, 25 překážek (měřená)", n=260,
                  anchors={1: hms("0:46:28"), 10: hms("0:54:51"), 74: hms("1:09:50"), 88: hms("1:12:30"),
                           130: hms("1:21:40"), 260: hms("2:18:05")},
                  specials={74: ("Šimek Radek", "M", 34, 1042), 88: ("Kratochvíl Ondřej", "M", 34, 1043)},
                  female=0.35, dnf=6),
             # FUN vlna se neměří - ve výsledcích není
         ]),
    dict(slug="brdska-dvacitka-2026", id=4777, name="Brdská dvacítka 2026", date="2026-09-26T09:30:00+02:00",
         location="Dobříš, Brdy", tracks=[
             dict(short="20K", name="Trail 20 km (+520 m)", n=162,
                  anchors={1: hms("1:27:58"), 10: hms("1:38:40"), 31: hms("1:55:03"), 39: hms("1:58:12"),
                           81: hms("2:12:20"), 130: hms("2:33:45"), 162: hms("3:09:30")},
                  specials={31: ("Šimek Radek", "M", 34, 307), 39: ("Kratochvíl Ondřej", "M", 34, 308)},
                  female=0.31),
             dict(short="10K", name="Trail 10 km (+240 m)", n=104,
                  anchors={1: hms("0:40:44"), 52: hms("1:03:15"), 104: hms("1:36:40")}, specials={}, female=0.47),
         ]),
]

index = {}
for c in COMPETITIONS:
    rnd = random.Random(c["slug"])
    tracks, total = [], 0
    for t in c["tracks"]:
        track, entries = gen_track(c["slug"], t["short"], t["name"], t["n"], t["anchors"], t["specials"], t["female"],
                                   rnd, dnf=t.get("dnf", 2))
        tracks.append(track)
        total += track["resultCount"]
        (OUT / f"entries-{track['id']}.json").write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")),
                                                         encoding="utf-8")
    comp = {"id": c["id"], "slug": c["slug"], "name": c["name"], "date": c["date"], "location": c["location"],
            "timing": "sport-base (fiktivní demo data)"}
    (OUT / f"competition-{c['slug']}.json").write_text(json.dumps(comp, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"results-{c['id']}.json").write_text(
        json.dumps({"competitionId": c["id"], "resultCount": total, "tracks": tracks}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(c["slug"], c["id"], [(t["short"], t["id"]) for t in tracks])
