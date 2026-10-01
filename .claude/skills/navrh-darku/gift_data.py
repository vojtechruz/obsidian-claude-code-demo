#!/usr/bin/env python3
"""
Vytahne z vaultu vsechna data o darcich pro jednu osobu a vypise je jako JSON.

Pouziti:
    python gift_data.py "Mama"          # data pro osobu
    python gift_data.py --lide          # seznam vsech osob + pocty

Vystup (JSON): {osoba, napady[], dane[], dostane[], statistiky}
"""

import argparse
import json
json.JSONEncoder.default = lambda self, o: o.isoformat() if hasattr(o, "isoformat") else str(o)  # YAML data (narozeniny: 1963-11-22)
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

try:
    import yaml  # PyYAML, pokud je nainstalovany
except ImportError:  # demo/workshop: staci stdlib, viz _mini_yaml
    yaml = None


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    if v in ("", "~", "null"):
        return None
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def _mini_yaml(text):
    """Minimalni parser frontmatteru bez PyYAML: `klic: hodnota`, `klic: [a, b]`
    a blokove seznamy (`- x`). Vnorene mapy nepodporuje (ve vaultu nejsou potreba)."""
    data, key = {}, None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*-\s+(.*)$", line) or re.match(r"^\s*-$", line)
        if m and key is not None:
            if not isinstance(data.get(key), list):
                data[key] = []
            item = _scalar(m.group(1)) if m.groups() else None
            if item is not None:
                data[key].append(item)
            continue
        m = re.match(r"^([^\s:#-][^:]*):(?:\s+(.*))?$", line)
        if not m:
            continue
        key, val = m.group(1).strip(), (m.group(2) or "").strip()
        if val.startswith("[") and val.endswith("]") and not val.startswith("[["):
            data[key] = [_scalar(x) for x in val[1:-1].split(",") if x.strip()]
        else:
            data[key] = _scalar(val)
    return data


def load_yaml(text):
    return (yaml.safe_load(text) if yaml else _mini_yaml(text)) or {}

VAULT = Path(__file__).resolve().parents[3]
DARKY = VAULT / "Oblasti/Rodina a Pratele/Darky"
NAPADY = VAULT / "Oblasti/Rodina a Pratele/Napady na darky"
LIDE = VAULT / "Lide"


def _utf8_stdout():
    """Windows: pri presmerovani vystupu jinak spadne na cp1250 a rozbije JSON."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def norm(s):
    """Bezdiakritiky, lowercase - pro fuzzy porovnani jmen."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return s.lower().strip()


def frontmatter(path):
    try:
        t = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except Exception:
        return {}, ""
    if not t.startswith("---\n"):
        return {}, t
    end = t.find("\n---\n", 4)
    if end == -1:
        return {}, t
    try:
        fm = load_yaml(t[4:end])
    except Exception:
        fm = {}
    return fm, t[end + 5:].strip()


def link_names(val):
    """['[[Oblasti/X/Mama|Mama]]'] -> ['Mama']"""
    out = []
    for it in (val if isinstance(val, list) else [val]) if val else []:
        m = re.search(r"\[\[([^\]|]+)", str(it))
        out.append((m.group(1).split("/")[-1] if m else str(it)).strip())
    return out


OCCASION_DATES = {  # property v poznamce cloveka -> nazev prilezitosti
    "narozeniny": "Narozeniny",
    "svatek": "Svatek",
    "vyroci_prvni_rande": "Vyroci",
}


def _mmdd(val):
    """Datum -> (mesic, den). Tolerantni k obema tvarum:
       cesky '4. 11.' / '4.11.' (den prvni)  a  ISO '1955-03-12' / '11-04' (mesic prvni)."""
    if not val:
        return None
    s = str(val).strip()
    m = re.match(r"^(\d{1,2})\.\s*(\d{1,2})\.?$", s)      # cesky: D. M.
    if m:
        return (int(m.group(2)), int(m.group(1)))
    m = re.match(r"^(?:\d{4}-)?(\d{1,2})-(\d{1,2})$", s)  # ISO: [YYYY-]MM-DD
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return None


def next_occurrence(val, today=None):
    """Kolik dni zbyva do dalsiho vyskytu (opakuje se rocne)."""
    md = _mmdd(val)
    if not md:
        return None
    today = today or date.today()
    m, d = md
    try:
        nxt = date(today.year, m, d)
    except ValueError:
        return None
    if nxt < today:
        nxt = date(today.year + 1, m, d)
    return {"datum": nxt.isoformat(), "za_dni": (nxt - today).days}


def person_meta(name):
    """Frontmatter + nadchazejici prilezitosti pro jednu osobu."""
    p = LIDE / f"{name}.md"
    if not p.exists():
        return {}, []
    fm, _ = frontmatter(p)
    occ = fm.get("darky_prilezitosti") or []
    occ = [str(x) for x in (occ if isinstance(occ, list) else [occ])]
    info = {
        "darky": fm.get("darky"),
        "darky_prilezitosti": occ,
        "narozeniny": fm.get("narozeniny"),
        "svatek": fm.get("svatek"),
        "vyroci_prvni_rande": fm.get("vyroci_prvni_rande"),
        "vyroci_svatby": fm.get("vyroci_svatby"),
    }
    nadchazejici = []
    for key, label in OCCASION_DATES.items():
        if occ and label not in occ:      # na tuhle prilezitost si darky nedavame
            continue
        n = next_occurrence(fm.get(key))
        if n:
            nadchazejici.append({"prilezitost": label, **n})
    if not occ or "Vanoce" in occ:
        n = next_occurrence("12-24")
        if n:
            nadchazejici.append({"prilezitost": "Vanoce", **n})
    if not occ or "Valentyn" in occ:
        n = next_occurrence("02-14")
        if n:
            nadchazejici.append({"prilezitost": "Valentyn", **n})
    if "Advent" in occ:      # jen kdo ji ma vyslovne (nema vychozi platnost pro vsechny)
        n = next_occurrence("12-01")
        if n:
            nadchazejici.append({"prilezitost": "Advent", **n})
    nadchazejici.sort(key=lambda x: x["za_dni"])
    return info, nadchazejici


def collect(folder, tag):
    rows = []
    if not folder.is_dir():
        return rows
    for f in sorted(folder.glob("*.md")):
        fm, body = frontmatter(f)
        tags = fm.get("tags") or []
        tags = [str(x) for x in (tags if isinstance(tags, list) else [tags])]
        if tag not in tags:
            continue
        rows.append((f, fm, body))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("osoba", nargs="?", help="jmeno osoby (staci cast, bez diakritiky)")
    ap.add_argument("--lide", action="store_true", help="vypsat vsechny osoby")
    ap.add_argument("--nadchazejici", type=int, nargs="?", const=90, metavar="DNI",
                    help="co se blizi u vsech aktivnich lidi (default 90 dni)")
    args = ap.parse_args()
    _utf8_stdout()

    if args.nadchazejici is not None:
        out = []
        for p in sorted(LIDE.glob("*.md")):
            fm, _ = frontmatter(p)
            if fm.get("darky") != "ano":
                continue
            _, nad = person_meta(p.stem)
            for n in nad:
                if n["za_dni"] <= args.nadchazejici:
                    out.append({"osoba": p.stem, **n})
        out.sort(key=lambda x: x["za_dni"])
        print(json.dumps({"do_dni": args.nadchazejici, "nadchazejici": out},
                         ensure_ascii=False, indent=2))
        return 0

    darky = collect(DARKY, "darek")
    napady = collect(NAPADY, "darek-napad")

    if args.lide or not args.osoba:
        c = Counter()
        for _, fm, _ in darky:
            for n in link_names(fm.get("osoba")):
                c[n] += 1
        for _, fm, _ in napady:
            for n in link_names(fm.get("osoba")):
                c[n] += 1
        print(json.dumps({"osoby": c.most_common()}, ensure_ascii=False, indent=2))
        return 0

    q = norm(args.osoba)
    # presna shoda ma prednost pred castecnou
    everyone = {n for _, fm, _ in darky + napady for n in link_names(fm.get("osoba"))}
    exact = [n for n in everyone if norm(n) == q]
    partial = [n for n in everyone if q in norm(n)]
    match = exact or partial
    if not match:
        print(json.dumps({"chyba": f"osoba '{args.osoba}' nenalezena",
                          "dostupne": sorted(everyone)}, ensure_ascii=False, indent=2))
        return 1
    if len(match) > 1:
        print(json.dumps({"chyba": "nejednoznacne jmeno", "kandidati": sorted(match)},
                         ensure_ascii=False, indent=2))
        return 1
    osoba = match[0]

    def mine(rows):
        return [(f, fm, b) for f, fm, b in rows if osoba in link_names(fm.get("osoba"))]

    out_nap = [{"nazev": f.stem, "cena": fm.get("cena") or "", "odkaz": fm.get("odkaz") or "",
                "popis": b} for f, fm, b in mine(napady)]
    dane, dostane = [], []
    for f, fm, _ in mine(darky):
        rec = {"rok": fm.get("rok"), "prilezitost": fm.get("prilezitost"),
               "darek": fm.get("darek") or ""}
        (dane if fm.get("typ") == "dano" else dostane).append(rec)
    dane.sort(key=lambda r: (-(r["rok"] or 0), r["prilezitost"] or ""))
    dostane.sort(key=lambda r: (-(r["rok"] or 0), r["prilezitost"] or ""))

    roky = [r["rok"] for r in dane + dostane if r["rok"]]
    stats = {
        "pocet_napadu": len(out_nap),
        "pocet_danych": len(dane),
        "pocet_dostanych": len(dostane),
        "rozsah_let": [min(roky), max(roky)] if roky else None,
        "prilezitosti_dane": dict(Counter(r["prilezitost"] for r in dane)),
        "posledni_rok_darku": max(roky) if roky else None,
    }

    # osobni poznamka + sekce "Info k darkum" (velikosti, preference, co ma rad/nerad)
    pnote, info = "", ""
    pf = LIDE / f"{osoba}.md"
    if pf.exists():
        _, body = frontmatter(pf)
        pnote = re.split(r"^## ", body, maxsplit=1, flags=re.M)[0].strip()
        m = re.search(r"^## Info k dárkům[ \t]*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
        info = m.group(1).strip() if m else ""
        # zahodit HTML komentar-placeholder, at nevypada jako realny obsah
        info = re.sub(r"<!--.*?-->", "", info, flags=re.S).strip()

    meta, nadchazejici = person_meta(osoba)

    print(json.dumps({"osoba": osoba, "poznamka_o_osobe": pnote,
                      "o_osobe": meta, "nadchazejici": nadchazejici,
                      "info_k_darkum": info, "statistiky": stats,
                      "napady": out_nap, "dane": dane, "dostane": dostane},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
