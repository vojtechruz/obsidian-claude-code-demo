#!/usr/bin/env python
"""Carpe Diem MOC (rozcestnik) generator.

Rebuilds "Carpe Diem/Carpe Diem.md" - the folder note for the whole journal -
from the existing summaries. Reverse chronological, detail decreasing with age:

  quick index    : one line per year, just month links, no detail
  current year   : month by month (week links + Hlavni udalosti of each month)
  last N closed  : AI shrnuti + Hlavni udalosti + month links   (RECENT_YEARS)
  older years    : Hlavni udalosti only, nested + collapsible

Everything is derived from the yearly / monthly notes, so the MOC never holds
information of its own and can be regenerated at any time.

Hand-written intro is preserved: the script keeps everything ABOVE the first
"## " heading and rewrites the rest. No HTML comment markers (they would show
up in Obsidian's edit mode).

Usage:
  python build_moc.py            # rebuild Carpe Diem/Carpe Diem.md
  python build_moc.py --print    # print to stdout, write nothing
"""
import re
import sys
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
CARPE = VAULT / "Carpe Diem"
MOC = CARPE / "Carpe Diem.md"

RECENT_YEARS = 3  # kolik uzavrenych let dostane detailni sekci

CZ_MONTHS = ["", "Leden", "Únor", "Březen", "Duben", "Květen", "Červen",
             "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"]

# Vse nad prvnim '## ' je rucni zona - zachovava se beze zmeny. Zamerne je
# prazdna (jen H1): poznamka ma zacinat rovnou rozcestnikem, bez uvodniho textu.
DEFAULT_INTRO = "# Carpe Diem"


# --------------------------------------------------------------------- cteni

def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def section(text, title):
    """Radky sekce '## <title>' az po dalsi '## ' nadpis."""
    out, inside = [], False
    for line in text.split("\n"):
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower() == title.lower()
            continue
        if inside:
            out.append(line)
    return out


def ai_summary(text):
    """Prvni odstavec pod '## AI shrnuti'."""
    para = []
    for line in section(text, "AI shrnutí"):
        s = line.strip()
        if not s:
            if para:
                break
            continue
        para.append(s)
    return " ".join(para)


def events(text):
    """Odrazky pod '## Hlavni udalosti'."""
    out = []
    for line in section(text, "Hlavní události"):
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
        elif not s and out:
            break
    return out


# ------------------------------------------------------------------ struktura

def years():
    return sorted(int(p.name) for p in CARPE.iterdir()
                  if p.is_dir() and re.fullmatch(r"\d{4}", p.name))


def months(y):
    return sorted(p.name for p in (CARPE / str(y)).iterdir()
                  if p.is_dir() and re.fullmatch(rf"{y}-\d{{2}}", p.name))


def weeks_by_month(y):
    """Tyden patri do mesice, ve kterem lezi jeho ctvrtek (ISO 8601)."""
    out = {}
    wdir = CARPE / str(y) / "Weekly"
    if not wdir.exists():
        return out
    for p in sorted(wdir.glob(f"{y}-W??.md")):
        thu = date.fromisocalendar(int(p.stem[:4]), int(p.stem[6:8]), 4)
        out.setdefault(f"{thu.year}-{thu.month:02d}", []).append(p.stem)
    return out


def year_note(y):
    return read(CARPE / str(y) / f"{y}.md")


def month_note(m):
    return read(CARPE / m[:4] / m / f"{m}.md")


def links(items):
    return " · ".join(f"[[{i}]]" for i in items)


def year_link(y):
    """Odkaz jen kdyz rocni poznamka existuje (jinak by byl neresolvovatelny)."""
    return f"[[{y}]]" if (CARPE / str(y) / f"{y}.md").exists() else str(y)


WD = {1: "Po", 2: "Út", 3: "St", 4: "Čt", 5: "Pá", 6: "So", 7: "Ne"}


def day_links(m):
    """Odkazy na denni zapisy mesice (pro rozjety mesic bez tydennich souhrnu)."""
    mdir = CARPE / m[:4] / m
    out = []
    for p in sorted(mdir.glob(f"{m}-??.md")):
        d = date(int(p.stem[:4]), int(p.stem[5:7]), int(p.stem[8:10]))
        out.append(f"[[{p.stem}|{WD[d.isoweekday()]} {d.day}]]")
    return out


# ------------------------------------------------------------------- sekce

def current_year_section(y):
    out = [f"## {year_link(y)} — probíhá", ""]
    wbm = weeks_by_month(y)
    for m in reversed(months(y)):
        mi = int(m[5:7])
        out.append(f"### [[{m}|{CZ_MONTHS[mi]} {y}]]")
        if wbm.get(m):
            out.append(f"↓ {links(wbm[m])}")
        else:
            # rozjety mesic, ktery jeste nema tydenni souhrny -> primo dny
            days = day_links(m)
            if days:
                out.append("↓ " + " · ".join(days))
        ev = events(month_note(m))
        if ev:
            out.append("")
            out += [f"- {e}" for e in ev]
        out.append("")
    return out


def recent_year_section(y):
    text = year_note(y)
    out = [f"## [[{y}]]", ""]
    summary = ai_summary(text)
    if summary:
        out += [summary, ""]
    ev = events(text)
    if ev:
        out += [f"- {e}" for e in ev] + [""]
    ms = months(y)
    if ms:
        out += [f"↓ {links(ms)}", ""]
    return out


def archive_section(ys):
    out = [f"## Starší roky ({ys[-1]}–{ys[0]})", ""]
    for y in ys:
        out.append(f"- **[[{y}]]**")  # tucne, viz quick_index()
        ev = events(year_note(y)) or ["(bez hlavních událostí)"]
        out += [f"    - {e}" for e in ev]
    out.append("")
    return out


def quick_index(ys):
    """Radek na rok, na nem jen odkazy na mesice. Zadne dalsi detaily.

    Roky jdou tesne po sobe bez prazdneho radku (Obsidian ma 'strict line
    breaks' vypnuty, takze se kazdy radek zalomi). Rok je tucne - aby si
    tucny odkaz udrzel barvu odkazu, je potreba zapnuty snippet
    `.obsidian/snippets/bold-links.css` (AnuPpuccin ho jinak prebarvi).
    """
    out = ["## Rychlý rozcestník", ""]
    for y in ys:
        ms = " · ".join(f"[[{m}|{m[5:7]}]]" for m in months(y))
        out.append(f"**{year_link(y)}** — {ms}" if ms else f"**{year_link(y)}**")
    out.append("")
    return out


# -------------------------------------------------------------------- build

def build():
    ys = sorted(years(), reverse=True)
    if not ys:
        raise SystemExit("Carpe Diem: zadne rocni slozky nenalezeny")
    cur, rest = ys[0], ys[1:]
    recent, older = rest[:RECENT_YEARS], rest[RECENT_YEARS:]

    body = quick_index(ys) + ["---", ""] + current_year_section(cur)
    for y in recent:
        body += recent_year_section(y)
    if older:
        body += archive_section(older)
    return body


def intro():
    """Rucni zona nad prvnim '## ' nadpisem - zachova se, jak je.

    Ve vychozim stavu je to jen H1; kdo si sem napise poznamku, o ni pri
    pregenerovani neprijde. Prazdny nebo chybejici soubor dostane H1.
    """
    lines = read(MOC).split("\n")
    cut = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
    kept = [l for l in lines[:cut]]
    while kept and not kept[-1].strip():
        kept.pop()
    return kept or DEFAULT_INTRO.split("\n")


def main():
    out = intro() + [""] + build()
    text = "\n".join(out).rstrip("\n") + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    if "--print" in sys.argv:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(text)
        return
    MOC.write_text(text, encoding="utf-8")
    print(f"Zapsano {MOC.relative_to(VAULT)} ({len(text.splitlines())} radku)")


if __name__ == "__main__":
    main()
