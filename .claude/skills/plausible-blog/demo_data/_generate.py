"""Generator fiktivnich dennich dat blogu ondrakodi.example pro demo Plausible (deterministicky)."""
import datetime as dt
import json
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent
rnd = random.Random(42)
START, TODAY = dt.date(2024, 10, 1), dt.date(2026, 10, 1)
DAYS = (TODAY - START).days + 1
RESTART = dt.date(2025, 10, 1)  # Ondra zacina zase psat

# path, publikovano, zralá denni zobrazeni, spicka v den vydani, bounce %, delka navstevy s
PAGES = [
    ("/", None, 14, 0, 48, 95),
    ("/junit5-parametrizovane-testy/", "2023-05-14", 18, 0, 78, 150),
    ("/testcontainers-spring-boot/", "2024-02-08", 38, 0, 74, 210),
    ("/spring-boot-actuator/", "2024-09-22", 27, 120, 76, 175),
    ("/virtual-threads-v-praxi/", "2025-11-20", 22, 520, 70, 240),
    ("/records-a-pattern-matching/", "2026-01-18", 11, 160, 72, 190),
    ("/assertj-tipy/", "2026-02-22", 9, 140, 75, 165),
    ("/spring-modulith-uvod/", "2026-03-15", 15, 260, 66, 230),
    ("/testovani-kafka-consumeru/", "2026-04-26", 12, 150, 73, 220),
    ("/spring-modulith-udalosti/", "2026-05-24", 10, 210, 64, 235),
    ("/archunit-pravidla-architektury/", "2026-06-28", 7, 120, 71, 200),
    ("/spring-modulith-testovani/", "2026-08-30", 7, 190, 65, 225),
    ("/modularni-monolit-v-praxi/", "2026-09-20", 6, 380, 62, 260),
    ("/tags/java/", None, 3, 0, 40, 120),
    ("/tags/spring/", None, 3, 0, 40, 120),
    ("/tags/testovani/", None, 1.5, 0, 45, 100),
    ("/archiv/", None, 1.8, 0, 35, 140),
    ("/o-mne/", None, 2.2, 0, 52, 70),
    ("/prednasky/", "2026-04-10", 1.2, 25, 50, 80),
]


def season(d):
    f = 0.55 if d.weekday() >= 5 else 1.0
    if (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 3):
        f *= 0.55
    if d.month in (7, 8):
        f *= 0.8
    # rust blogu po obnoveni psani (vic obsahu, lepsi pozice ve vyhledavani)
    years = (d - RESTART).days / 365
    f *= 0.8 if years < 0 else 0.8 + 0.35 * years
    return f


out_pages = []
for path, pub, level, spike, bounce, dur in PAGES:
    pubd = dt.date.fromisoformat(pub) if pub else START - dt.timedelta(days=400)
    pv, vis = [], []
    ratio = rnd.uniform(0.8, 0.9)
    for i in range(DAYS):
        d = START + dt.timedelta(days=i)
        age = (d - pubd).days
        if age < 0:
            pv.append(0)
            vis.append(0)
            continue
        ramp = min(1.0, 0.35 + age / 90) if pub else 1.0
        v = level * ramp * season(d) + spike * math.exp(-age / 3.5)
        v *= math.exp(rnd.gauss(0, 0.22))
        if d == TODAY:
            v *= 0.45  # dnesek je neuplny
        n = max(0, int(round(v)))
        pv.append(n)
        vis.append(int(round(n * ratio)))
    out_pages.append({"path": path, "bounce_rate": bounce, "visit_duration": dur, "pageviews": pv, "visitors": vis})

# podily navstev podle dimenzi: [hodnota, podil, bounce %, delka s]
BREAKDOWNS = {
    "visit:source": [["Google", 0.52, 72, 190], ["Direct / None", 0.15, 58, 160], ["LinkedIn", 0.07, 64, 150],
                     ["Seznam", 0.045, 74, 170], ["ChatGPT", 0.035, 55, 240], ["Bing", 0.03, 73, 180],
                     ["DuckDuckGo", 0.028, 70, 200], ["Reddit", 0.025, 68, 130], ["Feedly", 0.02, 60, 210],
                     ["GitHub", 0.018, 50, 230], ["Perplexity", 0.012, 57, 220], ["Facebook", 0.01, 80, 90],
                     ["javapivo.example", 0.009, 45, 260], ["Hacker News", 0.006, 75, 110]],
    "visit:referrer": [["Direct / None", 0.15, 58, 160], ["https://www.google.com/", 0.48, 72, 190],
                       ["https://www.linkedin.com/", 0.06, 64, 150], ["https://search.seznam.cz/", 0.045, 74, 170],
                       ["https://chatgpt.com/", 0.035, 55, 240], ["https://www.bing.com/", 0.03, 73, 180],
                       ["https://duckduckgo.com/", 0.028, 70, 200], ["https://www.reddit.com/r/java/", 0.02, 68, 130],
                       ["https://github.com/", 0.018, 50, 230], ["https://javapivo.example/", 0.009, 45, 260]],
    "visit:channel": [["Organic Search", 0.64, 72, 185], ["Direct", 0.15, 58, 160], ["Organic Social", 0.11, 66, 140],
                      ["Referral", 0.085, 52, 225], ["Email", 0.015, 40, 280]],
    "visit:country_name": [["Czechia", 0.71, 69, 200], ["Slovakia", 0.12, 70, 190], ["Germany", 0.035, 74, 150],
                           ["United States", 0.03, 80, 110], ["Poland", 0.015, 76, 130],
                           ["United Kingdom", 0.014, 77, 120], ["Austria", 0.012, 72, 160],
                           ["Netherlands", 0.01, 75, 140], ["Ukraine", 0.009, 73, 150], ["India", 0.008, 85, 70]],
    "visit:city_name": [["Prague", 0.36, 68, 205], ["Brno", 0.13, 69, 200], ["Bratislava", 0.06, 70, 190],
                        ["Ostrava", 0.045, 71, 185], ["Pilsen", 0.03, 70, 190], ["Olomouc", 0.025, 72, 180],
                        ["Hradec Kralove", 0.02, 70, 195], ["Kosice", 0.02, 71, 180], ["Liberec", 0.015, 72, 175],
                        ["Berlin", 0.012, 76, 140]],
    "visit:device": [["Desktop", 0.79, 67, 215], ["Mobile", 0.195, 80, 105], ["Tablet", 0.015, 76, 140]],
    "visit:browser": [["Chrome", 0.6, 70, 195], ["Firefox", 0.15, 66, 220], ["Edge", 0.09, 72, 180],
                      ["Safari", 0.08, 76, 140], ["Brave", 0.035, 64, 230], ["Opera", 0.02, 71, 170],
                      ["Samsung Internet", 0.01, 82, 90]],
    "visit:os": [["Windows", 0.47, 70, 195], ["Mac", 0.21, 68, 210], ["Linux", 0.14, 63, 240],
                 ["Android", 0.12, 80, 105], ["iOS", 0.06, 79, 110]],
    "visit:utm_source": [["linkedin", 0.03, 62, 160], ["javapivo", 0.008, 45, 260], ["newsletter", 0.006, 40, 280]],
    "visit:utm_medium": [["social", 0.03, 62, 160], ["meetup", 0.008, 45, 260], ["email", 0.006, 40, 280]],
    "visit:utm_campaign": [["novy-clanek", 0.025, 62, 170], ["java-pivo-praha", 0.008, 45, 260],
                           ["spring-modulith-serie", 0.007, 58, 240], ["czech-java-days", 0.004, 50, 250]],
}
GOALS = [["Outbound Link: Click", 0.06, 1.4], ["File Download", 0.012, 1.1], ["404", 0.008, 1.0],
         ["Copy Code", 0.09, 2.3]]

data = {"_note": "Fiktivni data blogu ondrakodi.example pro demo. Generovano deterministicky.",
        "site_id": "ondrakodi.example", "today": TODAY.isoformat(), "start": START.isoformat(),
        "pages": out_pages, "breakdowns": BREAKDOWNS, "goals": GOALS}
(OUT / "site.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
tot = sum(sum(p["pageviews"]) for p in out_pages)
print("pageviews celkem", tot, "posl. 30 dni", sum(sum(p["pageviews"][-31:-1]) for p in out_pages))
