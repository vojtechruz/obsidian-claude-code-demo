#!/usr/bin/env python3
"""Helper for the Java features tracker (Oblasti/Blog/Java features).

Subcommands (all print JSON to stdout):
  release N [--details]   JEPs of JDK N from openjdk.org/projects/jdk/N, classified against the tracker
  jep N [N ...]           details of JEPs from openjdk.org/jeps/N (title, status, release, summary, related JEPs)
  check                   consistency check of the tracker (duplicates, missing fields, Finalni verze vs. tables)
  articles                topics with articles that are outdated or have a problem, sorted by Views 6mo

Classification of each JEP:
  topic            already in a topic table          -> nothing to do (maybe update the V článku column)
  ignored          already in the ignore list        -> nothing to do
  pending          parked in MOC `## Nerozhodnuté JEPy` -> user decides later
  suggest_pending  same chain as a parked JEP        -> park it too (or decide the whole chain now)
  suggest_topic    same feature chain as a topic row -> add a row to that topic
  suggest_ignore   same feature chain as an ignored JEP -> add to ignore (unless it just went final)
  untriaged        nothing known                     -> the user decides (new topic / existing topic / ignore)
Chains are matched by normalized title (without "(Second Preview)" etc.) and, with --details or in
`jep`, by JEPs referenced on the JEP page ("Relates to", History section).
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

VAULT = Path(__file__).resolve().parents[3]
BLOG = VAULT / "Oblasti" / "Blog"
TOPICS_DIR = BLOG / "Java features"
IGNORE = TOPICS_DIR / "Java features - ignorované.md"
MOC = TOPICS_DIR / "Java features.md"
ARTICLES_DIR = BLOG / "Blog Articles"

STAGE_RE = re.compile(r"\s*\(([^)]*(preview|incubator|experimental|production)[^)]*)\)\s*$", re.I)


# ---------- helpers ----------

def fetch(url, tries=6):
    """openjdk.org answers 403 when hit too fast – fetch sequentially and back off."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (java-features skill)"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(0.5)
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429, 503) or attempt == tries - 1:
                raise
            time.sleep(10 * (attempt + 1))


def strip_tags(h):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))).strip()


def stage(title):
    """'preview 2' style stage from the title, or 'final'."""
    m = STAGE_RE.search(title)
    return m.group(1).strip() if m else "final"


def norm(title):
    t = STAGE_RE.sub("", title)
    return re.sub(r"[^a-z0-9]", "", t.lower())


def split_fm(text):
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def parse_fm(fm):
    """Tiny YAML subset: `key: scalar`, `key: []`, `key:` followed by `  - item` lines."""
    out, key = {}, None
    for line in fm.splitlines():
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and key:
            out.setdefault(key, [])
            if not isinstance(out[key], list):
                out[key] = []
            out[key].append(item.group(1).strip().strip('"').strip("'"))
            continue
        kv = re.match(r"^([^\s:][^:]*):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1).strip(), kv.group(2).strip()
            if val == "[]":
                out[key] = []
            elif val == "":
                out[key] = None
            else:
                out[key] = val.strip('"').strip("'")
    return out


# ---------- tracker state ----------

def load_topics():
    topics = []
    for p in sorted(TOPICS_DIR.glob("Java feature - *.md")):
        fm_raw, body = split_fm(p.read_text(encoding="utf-8"))
        rows = []
        for m in re.finditer(
            r"^\|\s*\[(\d+)\]\([^)]*\)\s*([^|]*?)\s*\|\s*(\d+)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$",
            body, re.M,
        ):
            rows.append({"jep": int(m[1]), "title": m[2], "java": int(m[3]), "typ": m[4], "v_clanku": m[5]})
        topics.append({"name": p.stem, "file": p.relative_to(VAULT).as_posix(), "fm": parse_fm(fm_raw), "rows": rows})
    return topics


def load_ignore():
    out, ver = {}, None
    if not IGNORE.exists():
        return out
    for line in IGNORE.read_text(encoding="utf-8").splitlines():
        h = re.match(r"^## Java (\d+)", line)
        if h:
            ver = int(h[1])
            continue
        m = re.match(r"^\|\s*\[(\d+)\]\([^)]*\)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|", line)
        if m:
            out[int(m[1])] = {"jep": int(m[1]), "title": m[2], "java": ver, "reason": m[3]}
    return out


def load_pending():
    """JEPs deliberately left for later: table under `## Nerozhodnuté JEPy` in the MOC."""
    out = {}
    if not MOC.exists():
        return out
    text = MOC.read_text(encoding="utf-8")
    sec = re.search(r"^## Nerozhodnuté JEPy\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not sec:
        return out
    for m in re.finditer(r"^\|\s*\[(\d+)\]\([^)]*\)\s*\|\s*([^|]*?)\s*\|\s*(\d+)\s*\|", sec.group(1), re.M):
        out[int(m[1])] = {"jep": int(m[1]), "title": m[2], "java": int(m[3])}
    return out


def known_index(topics, ignore, pending=None):
    by_jep, by_norm = {}, {}
    for t in topics:
        for r in t["rows"]:
            by_jep[r["jep"]] = ("topic", t["name"])
            by_norm.setdefault(norm(r["title"]), ("topic", t["name"]))
    for n, r in ignore.items():
        by_jep.setdefault(n, ("ignored", None))
        by_norm.setdefault(norm(r["title"]), ("ignored", None))
    for n, r in (pending or {}).items():
        by_jep.setdefault(n, ("pending", None))
        by_norm.setdefault(norm(r["title"]), ("pending", None))
    return by_jep, by_norm


def classify(jeps, details=False):
    topics, ignore = load_topics(), load_ignore()
    by_jep, by_norm = known_index(topics, ignore, load_pending())
    out = []
    for j in jeps:
        rec = dict(j)
        rec["stage"] = stage(j["title"])
        if details:
            try:
                rec.update(jep_details(j["jep"]))
            except Exception as e:  # network hiccup: keep going with the title only
                rec["details_error"] = str(e)
        if j["jep"] in by_jep:
            kind, topic = by_jep[j["jep"]]
            rec["status"] = kind
            if topic:
                rec["topic"] = topic
        else:
            hit = by_norm.get(norm(j["title"]))
            if not hit:
                for rel in rec.get("related", []):
                    if rel in by_jep:
                        hit = by_jep[rel]
                        rec["matched_via"] = rel
                        break
            if hit and hit[0] == "topic":
                rec["status"], rec["topic"] = "suggest_topic", hit[1]
            elif hit and hit[0] == "pending":
                rec["status"] = "suggest_pending"
            elif hit:
                rec["status"] = "suggest_ignore"
                if rec["stage"] == "final":
                    rec["note"] = "ignorovaný řetězec je teď final – znovu zvážit"
            else:
                rec["status"] = "untriaged"
        out.append(rec)
    return out


# ---------- openjdk.org ----------

def release_jeps(n):
    h = fetch(f"https://openjdk.org/projects/jdk/{n}/")
    status = ""
    s = re.search(r'<h2 id="Status">Status</h2>(.*?)<h2', h, re.S)
    if s:
        status = strip_tags(s.group(1))
    # Features section: a <table class="jeps"> on newer pages, "NNN: <a>Title</a><br />" on JDK 10-13;
    # commented-out rows (e.g. withdrawn JEP 326 on the JDK 12 page) are skipped.
    feats = re.search(r'<h2 id="Features">Features</h2>(.*?)(?=<h2|\Z)', h, re.S)
    jeps = []
    if feats:
        body = re.sub(r"<!--.*?-->", "", feats.group(1), flags=re.S)
        for m in re.finditer(r"(\d{3,4}):\s*(?:</td>\s*<td>)?\s*<a [^>]*jeps/(\d+)[^>]*>(.*?)</a>", body, re.S):
            if m[1] == m[2]:
                jeps.append({"jep": int(m[1]), "title": strip_tags(m[3]), "java": n})
    return status, jeps


def jep_details(n):
    h = fetch(f"https://openjdk.org/jeps/{n}")
    d = {"jep": n, "url": f"https://openjdk.org/jeps/{n}"}
    t = re.search(r"<title>JEP \d+: (.*?)</title>", h, re.S)
    d["title"] = strip_tags(t.group(1)) if t else ""
    for key in ("Status", "Release", "Type", "Component"):
        m = re.search(rf"<tr><td>{key}</td><td>(.*?)</td></tr>", h, re.S)
        if m:
            d[key.lower()] = strip_tags(m.group(1)).replace(" ", "")
    summ = re.search(r'<h2 id="Summary">Summary</h2>(.*?)<h2', h, re.S)
    if summ:
        d["summary"] = strip_tags(summ.group(1))[:600]
    head = re.search(r'<table class="head">(.*?)</table>', h, re.S)
    hist = re.search(r'<h2 id="History">History</h2>(.*?)<h2', h, re.S)
    rel_src = (head.group(1) if head else "") + (hist.group(1) if hist else "")
    related = [int(x) for x in re.findall(r'href="(?:https://openjdk\.org/jeps/|/jeps/)?(\d{3,4})"', rel_src)]
    d["related"] = sorted({r for r in related if r != n})
    return d


# ---------- checks ----------

def check():
    topics, ignore = load_topics(), load_ignore()
    issues = []
    where = {}
    for t in topics:
        for r in t["rows"]:
            where.setdefault(r["jep"], []).append(t["name"])
    for n in ignore:
        where.setdefault(n, []).append("ignore")
    for n in load_pending():
        where.setdefault(n, []).append("nerozhodnuté")
    for n, places in sorted(where.items()):
        if len(places) > 1:
            issues.append(f"JEP {n} je na víc místech: {', '.join(places)}")
    for t in topics:
        fm, name = t["fm"], t["name"]
        clanky = fm.get("Clanky") or []
        if clanky and not fm.get("Pokryto do"):
            issues.append(f"{name}: má článek, ale chybí Pokryto do")
        for c in clanky:
            target = re.sub(r"^\[\[|\]\]$", "", c).split("|")[0]
            if not (ARTICLES_DIR / f"{target}.md").exists():
                issues.append(f"{name}: článek {c} neexistuje v Blog Articles")
        declared = sorted(int(x) for x in (fm.get("Finalni verze") or []) if str(x).isdigit())
        finals = sorted({r["java"] for r in t["rows"] if "final" in r["typ"].lower()})
        if declared != finals:
            issues.append(f"{name}: Finalni verze {declared} neodpovídá řádkům **final** v tabulce {finals}")
        previews = [r for r in t["rows"] if "preview" in r["typ"].lower() or "incubator" in r["typ"].lower()]
        if previews:
            last = max(t["rows"], key=lambda r: r["java"])
            if "final" not in last["typ"].lower() and not fm.get("Sleduje se"):
                issues.append(f"{name}: poslední JEP {last['jep']} je {last['typ']}, ale Sleduje se je prázdné")
        if not t["rows"]:
            issues.append(f"{name}: nemá žádnou tabulku JEPů")
    return {"topics": len(topics), "ignored": len(ignore), "pending": len(load_pending()), "issues": issues}


def articles():
    out = []
    for t in load_topics():
        fm = t["fm"]
        clanky = fm.get("Clanky") or []
        if not clanky:
            continue
        pokryto = int(fm["Pokryto do"]) if str(fm.get("Pokryto do") or "").isdigit() else None
        finals = [int(x) for x in (fm.get("Finalni verze") or []) if str(x).isdigit()]
        outdated = [v for v in finals if pokryto is not None and v > pokryto]
        views = 0
        for c in clanky:
            p = ARTICLES_DIR / (re.sub(r"^\[\[|\]\]$", "", c).split("|")[0] + ".md")
            if p.exists():
                m = re.search(r"^Views 6mo:\s*(\d+)", p.read_text(encoding="utf-8"), re.M)
                views += int(m.group(1)) if m else 0
        if outdated or fm.get("Problem"):
            out.append({"topic": t["name"], "articles": clanky, "pokryto_do": pokryto,
                        "outdated_by": outdated, "problem": fm.get("Problem"), "views_6mo": views})
    return sorted(out, key=lambda x: -x["views_6mo"])


# ---------- main ----------

def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd, args = argv[0], argv[1:]
    details = "--details" in args
    args = [a for a in args if a != "--details"]
    if cmd == "release":
        status, jeps = release_jeps(int(args[0]))
        res = {"release": int(args[0]), "status": status, "count": len(jeps), "jeps": classify(jeps, details)}
    elif cmd == "jep":
        res = [jep_details(int(a)) for a in args]
    elif cmd == "check":
        res = check()
    elif cmd == "articles":
        res = articles()
    else:
        print(__doc__)
        return 1
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
