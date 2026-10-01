#!/usr/bin/env python
"""
Collect everything needed to plan a week from the vault (Tasks/, Projekty/, Lide/,
Denik/, previous weekly plan). Prints a Markdown report to stdout.

Usage:
  python .claude/skills/tydenni-plan/collect.py            # auto: next ISO week if today is Fri-Sun, else current
  python .claude/skills/tydenni-plan/collect.py 2026-W36   # explicit ISO week

Read-only. Does not modify the vault.
"""
import re
import sys
from datetime import date, datetime, timedelta
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


sys.stdout.reconfigure(encoding="utf-8")

VAULT = Path(__file__).resolve().parents[3]
TASKS = VAULT / "Tasks"
PROJEKTY = VAULT / "Projekty"
LIDE = VAULT / "Lide"
CARPE = VAULT / "Denik"

DONE = {"Done"}
STALE_DAYS = 30
ALIAS = "Aktualni plan"  # rolling alias of the current week plan
CZ_DAYS = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]

# ---------------------------------------------------------------- helpers


def read_fm(path: Path):
    """Return (frontmatter dict, body) for a markdown file."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return {}, ""
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    try:
        fm = load_yaml(m.group(1))
    except Exception:
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, m.group(2)


def to_date(v):
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def link_name(v):
    """'[[Projekty/X/X|X]]' -> 'X'."""
    s = str(v).strip().strip('"').strip("'")
    m = re.match(r"^\[\[([^\]|]+)(?:\|[^\]]*)?\]\]$", s)
    if m:
        s = m.group(1)
    return s.split("/")[-1].strip()


def as_list(v):
    if v is None or v == "":
        return []
    if isinstance(v, list):
        return [x for x in v if x]
    return [v]


def iso_week_range(year: int, week: int):
    monday = date.fromisocalendar(year, week, 1)
    return monday, monday + timedelta(days=6)


def prague_offset(d: date) -> str:
    """CET/CEST offset for a date (EU DST: last Sun of March -> last Sun of Oct)."""
    def last_sunday(y, m):
        dd = date(y, m + 1, 1) - timedelta(days=1) if m < 12 else date(y, 12, 31)
        return dd - timedelta(days=(dd.weekday() + 1) % 7)
    return "+02:00" if last_sunday(d.year, 3) <= d < last_sunday(d.year, 10) else "+01:00"


def fmt(d):  # date | None
    return d.strftime("%Y-%m-%d") if d else "—"


def dm(d: date):
    return f"{CZ_DAYS[d.weekday()]} {d.day}.{d.month}."


def wl(path: Path):
    return f"[[{path.stem}]]"


# ---------------------------------------------------------------- resolve week

today = date.today()
if len(sys.argv) > 1 and re.match(r"^\d{4}-W\d{2}$", sys.argv[1]):
    y, w = sys.argv[1].split("-W")
    year, week = int(y), int(w)
else:
    base = today + timedelta(days=7) if today.weekday() >= 4 else today
    year, week, _ = base.isocalendar()

start, end = iso_week_range(year, week)
prev_start, prev_end = start - timedelta(days=7), end - timedelta(days=7)
py, pw, _ = prev_start.isocalendar()
week_id = f"{year}-W{week:02d}"
prev_id = f"{py}-W{pw:02d}"
month_id = start.strftime("%Y-%m")
plan_dir = CARPE / str(year) / "Weekly"
plan_path = plan_dir / f"{week_id}-plan.md"
prev_plan_path = CARPE / str(py) / "Weekly" / f"{prev_id}-plan.md"
prev_summary_path = CARPE / str(py) / "Weekly" / f"{prev_id}.md"
prev_review_path = CARPE / str(py) / "Weekly" / f"{prev_id}-review.md"          # to be written now (evaluates prev week)
ppy, ppw, _ = (prev_start - timedelta(days=7)).isocalendar()
prev_prev_review_path = CARPE / str(ppy) / "Weekly" / f"{ppy}-W{ppw:02d}-review.md"  # last existing review (its Poučení carries forward)

out = []
P = out.append

P(f"# Podklady pro plán týdne {week_id}")
P("")
P(f"- Dnes: {fmt(today)} ({dm(today)})")
P(f"- Týden: {week_id} = {dm(start)} – {dm(end)} {end.year} ({fmt(start)} … {fmt(end)})")
P(f"- Minulý týden: {prev_id} = {fmt(prev_start)} … {fmt(prev_end)}")
P(f"- Plán zapsat do: `{plan_path.relative_to(VAULT).as_posix()}`" + ("  ⚠️ UŽ EXISTUJE" if plan_path.exists() else ""))
P(f"- Předchozí plán: `{prev_plan_path.relative_to(VAULT).as_posix()}`" + (" (existuje)" if prev_plan_path.exists() else " (neexistuje – první plán, vyhodnocení jen z tasků)"))
P(f"- Souhrn minulého týdne: `{prev_summary_path.relative_to(VAULT).as_posix()}`" + (" (existuje)" if prev_summary_path.exists() else " (neexistuje)"))
P(f"- Vyhodnocení minulého týdne zapsat do: `{prev_review_path.relative_to(VAULT).as_posix()}`" + ("  ⚠️ UŽ EXISTUJE" if prev_review_path.exists() else ""))
P(f"- Odkazy pro nav: souhrn [[{week_id}]], měsíc [[{month_id}]], předchozí plán [[{prev_id}-plan]], vyhodnocení [[{prev_id}-review]], souhrn minulého týdne [[{prev_id}]]")
holders = []
for wp in sorted(CARPE.glob("*/Weekly/*-plan.md")):
    afm, _ = read_fm(wp)
    if ALIAS in [str(a) for a in as_list(afm.get("aliases"))] and wp != plan_path:
        holders.append(wp.relative_to(VAULT).as_posix())
P(f"- Alias `{ALIAS}` drží: " + (", ".join(f"`{h}`" for h in holders) if holders else "nikdo") + " → odebrat a dát novému plánu")
P("")
P("## Kalendář dotaz (MCP demo-calendar → list_events, primary; v reálu Google Calendar MCP)")
P(f"- startTime: `{fmt(start)}T00:00:00{prague_offset(start)}`")
nxt = end + timedelta(days=1)
P(f"- endTime: `{fmt(nxt)}T00:00:00{prague_offset(nxt)}`")
P("- timeZone: `Europe/Prague`, orderBy: `startTime`, pageSize: 100")
P("")

# ---------------------------------------------------------------- tasks

tasks = []
for p in sorted(TASKS.glob("*.md")):
    fm, body = read_fm(p)
    tags = as_list(fm.get("tags"))
    if "task" not in [str(t) for t in tags]:
        continue
    tasks.append({
        "path": p,
        "name": p.stem,
        "status": str(fm.get("status") or ""),
        "priority": str(fm.get("priority") or ""),
        "due": to_date(fm.get("due")),
        "scheduled": to_date(fm.get("scheduled")),
        "completed": to_date(fm.get("completedDate")),
        "modified": to_date(fm.get("dateModified")) or date.fromtimestamp(p.stat().st_mtime),
        "created": to_date(fm.get("dateCreated")),
        "projects": [link_name(x) for x in as_list(fm.get("projects"))],
        "oblast": [link_name(x) for x in as_list(fm.get("oblast"))],
        "popis": str(fm.get("popis") or "").strip(),
        "body": body.strip(),
    })

open_tasks = [t for t in tasks if t["status"] not in DONE]


def trow(t, extra=""):
    parts = [wl(t["path"]), f"status={t['status']}", f"prio={t['priority'] or '—'}"]
    if t["due"]:
        parts.append(f"due={fmt(t['due'])}")
    if t["scheduled"]:
        parts.append(f"sched={fmt(t['scheduled'])}")
    if t["projects"]:
        parts.append("proj=" + ", ".join(t["projects"]))
    if extra:
        parts.append(extra)
    line = "- " + " | ".join(parts)
    if t["popis"]:
        line += f"\n    - popis: {t['popis']}"
    return line


def section(title, items, empty="- (nic)"):
    P(f"## {title}")
    if items:
        out.extend(items)
    else:
        P(empty)
    P("")


in_week = lambda d: d is not None and start <= d <= end

section("Po termínu (due < dnes, nehotové)",
        [trow(t, f"zpoždění={(today - t['due']).days} d") for t in sorted(open_tasks, key=lambda t: t["due"] or date.max)
         if t["due"] and t["due"] < today])

section("Due tento týden",
        [trow(t) for t in sorted(open_tasks, key=lambda t: t["due"] or date.max) if in_week(t["due"])])

section("Scheduled tento týden",
        [trow(t) for t in sorted(open_tasks, key=lambda t: t["scheduled"] or date.max) if in_week(t["scheduled"])])

section("Prošlé scheduled (scheduled < začátek týdne, nehotové – TaskNotes je bude tahat dál; přeplánovat nebo zrušit)",
        [trow(t) for t in sorted(open_tasks, key=lambda t: t["scheduled"] or date.max) if t["scheduled"] and t["scheduled"] < start])

section("Rozpracované (In Progress)",
        [trow(t) for t in open_tasks if t["status"] == "In Progress"])

section("Priorita dnes/tyden bez termínu v tomto týdnu (kandidáti do plánu; overdue/prošlé viz výše)",
        [trow(t) for t in open_tasks if t["priority"] in ("dnes", "tyden")
         and not in_week(t["due"]) and not in_week(t["scheduled"]) and t["status"] != "Waiting"
         and not (t["due"] and t["due"] < today) and not (t["scheduled"] and t["scheduled"] < start)])

section("Priorita mesic (záloha, když zbude kapacita)",
        [trow(t) for t in open_tasks if t["priority"] == "mesic" and not in_week(t["due"]) and not in_week(t["scheduled"])])

section("Pevné termíny (status Scheduled – rezervováno, pevný den/čas; v kalendáři plánu jsou to fixní body)",
        [trow(t) for t in sorted([t for t in open_tasks if t["status"] == "Scheduled"], key=lambda t: t["due"] or t["scheduled"] or date.max)])

section("Čekám na (Waiting)",
        [trow(t, f"čeká={(today - t['modified']).days} d od poslední změny") for t in
         sorted(open_tasks, key=lambda t: t["modified"]) if t["status"] == "Waiting"])

section("Due do 30 dní po tomto týdnu (horizont)",
        [trow(t) for t in sorted(open_tasks, key=lambda t: t["due"] or date.max)
         if t["due"] and end < t["due"] <= end + timedelta(days=30)])

# ---------------------------------------------------------------- projects

P("## Projekty (aktivní)")
rows = []
for d in sorted(PROJEKTY.iterdir()):
    if not d.is_dir():
        continue
    note = d / f"{d.name}.md"
    if not note.exists():
        continue
    fm, body = read_fm(note)
    status = str(fm.get("status") or "")
    if status.lower() in ("done", "hotovo", "archived", "cancelled", "zruseno"):
        continue
    due = to_date(fm.get("due_date"))
    ptasks = [t for t in tasks if d.name in t["projects"]]
    popen = [t for t in ptasks if t["status"] not in DONE]
    last = max([t["modified"] for t in ptasks] + [date.fromtimestamp(note.stat().st_mtime)])
    stale = (today - last).days >= STALE_DAYS
    next_due = sorted([t for t in popen if t["due"]], key=lambda t: t["due"] or date.max)[:1]
    nxt_txt = f"nejbližší: {next_due[0]['name']} ({fmt(next_due[0]['due'])})" if next_due else "bez termínovaného kroku"
    m = re.search(r"##\s*Nejbližší kroky\s*\n(.*?)(?:\n##|\n---|$)", body, re.S)
    kroky = " / ".join(l.strip(" -*0123456789.").replace("**", "") for l in m.group(1).strip().splitlines() if l.strip())[:300] if m else ""
    rows.append(
        f"- [[{d.name}]] | status={status} | due={fmt(due)}"
        + (f" (zbývá {(due - today).days} d)" if due else "")
        + f" | otevřené={len(popen)} | poslední změna={fmt(last)}"
        + (" ⚠️ STALE" if stale else "")
        + f" | {nxt_txt}"
        + (f"\n    - Nejbližší kroky: {kroky}" if kroky else "")
    )
out.extend(rows or ["- (žádné)"])
P("")

# ---------------------------------------------------------------- people

P("## Lidé – svátky, narozeniny, výročí (tento + příští týden)")
rows = []
for p in sorted(LIDE.glob("*.md")):
    fm, _ = read_fm(p)
    # zemrele lidi neplanujeme - datum umrti v libovolne z techto polozek je vyrazuje
    if any(fm.get(k) for k in ("umrti", "zemrel", "zemrela")):
        continue
    for key, label in (("svatek", "svátek"), ("narozeniny", "narozeniny"), ("vyroci_svatby", "výročí svatby"),
                       ("vyroci_prvni_rande", "výročí prvního rande"), ("Narozeniny", "narozeniny")):
        v = fm.get(key)
        if not v:
            continue
        m = re.match(r"^\s*(\d{1,2})\.\s*(\d{1,2})\.?", str(v)) or (re.match(r"^\d{4}-(\d{2})-(\d{2})", str(v)))
        if not m:
            continue
        if str(v)[:4].isdigit() and "-" in str(v):
            mm, dd = int(m.group(1)), int(m.group(2))
        else:
            dd, mm = int(m.group(1)), int(m.group(2))
        for yy in (start.year, end.year + 1):
            try:
                ev = date(yy, mm, dd)
            except ValueError:
                continue
            if start <= ev <= end + timedelta(days=7):
                when = "TENTO týden" if ev <= end else "příští týden"
                rows.append(f"- {dm(ev)} {when}: [[{p.stem}]] – {label}")
out.extend(sorted(set(rows)) or ["- (nic)"])
P("")

# ---------------------------------------------------------------- previous week

section(f"Minulý týden {prev_id}: dokončené tasky",
        [f"- {wl(t['path'])} | dokončeno={fmt(t['completed'])}" + (f" | proj={', '.join(t['projects'])}" if t['projects'] else "")
         for t in sorted([t for t in tasks if t["completed"] and prev_start <= t["completed"] <= prev_end], key=lambda t: t["completed"] or date.max)])

section(f"Minulý týden {prev_id}: bylo due/scheduled a NENÍ hotové (propadlo)",
        [trow(t) for t in open_tasks if (t["due"] and prev_start <= t["due"] <= prev_end) or (t["scheduled"] and prev_start <= t["scheduled"] <= prev_end)])

def section_text(txt, heading_prefix):
    m = re.search(r"##\s*" + heading_prefix + r".*?\n(.*?)(?:\n## |\Z)", txt, re.S)
    return m.group(1) if m else ""


P(f"## Předchozí plán {prev_id}-plan: stav naplánovaných tasků (jen Big Rocks + Kalendář)")
if prev_plan_path.exists():
    txt = prev_plan_path.read_text(encoding="utf-8")
    planned = (section_text(txt, "Big Rocks") or section_text(txt, "Top 3")) + "\n" + section_text(txt, "Kalendář")
    names = []
    for m in re.finditer(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", planned):
        n = m.group(1).split("/")[-1].strip()
        if n not in names:
            names.append(n)
    by_name = {t["name"]: t for t in tasks}
    found = 0
    done = 0
    for n in names:
        t = by_name.get(n)
        if not t:
            continue
        found += 1
        if t["status"] in DONE:
            done += 1
        mark = "✅" if t["status"] in DONE else ("🔁" if t["status"] == "In Progress" else "❌")
        P(f"- {mark} [[{n}]] | status={t['status']}" + (f" | dokončeno={fmt(t['completed'])}" if t["completed"] else ""))
    P(f"- Celkem: {done}/{found} hotovo" if found else "- (plán neodkazuje na žádné tasky)")
    top3 = (section_text(txt, "Big Rocks") or section_text(txt, "Top 3")).strip()
    if top3:
        P("")
        P("Big Rocks z minulého plánu (doslovně):")
        for l in top3.splitlines():
            if l.strip():
                P("    " + l.rstrip())
else:
    P("- (předchozí plán neexistuje)")
P("")

P("## Poučení z posledního vyhodnocení (přenést do nového review, pokud stále platí)")
if prev_prev_review_path.exists():
    P(f"Zdroj: `{prev_prev_review_path.relative_to(VAULT).as_posix()}`")
    for l in section_text(prev_prev_review_path.read_text(encoding="utf-8"), "Poučení").strip().splitlines():
        if l.strip():
            P("    " + l.rstrip())
else:
    P("- (žádné předchozí vyhodnocení)")
P("")

# ---------------------------------------------------------------- daily notes of previous week

P(f"## Denní poznámky minulého týdne {prev_id} (pro retrospektivu)")
any_daily = False
for i in range(7):
    d = prev_start + timedelta(days=i)
    p = CARPE / str(d.year) / d.strftime("%Y-%m") / f"{d.isoformat()}.md"
    if p.exists():
        any_daily = True
        body = p.read_text(encoding="utf-8")
        body = "\n".join(l for l in body.splitlines() if not re.match(r"^\s*(?:[←→↑↓]|\[\[[^\]]+\]\]\s*→)", l)).strip()
        P(f"### {d.isoformat()} ({dm(d)})")
        P(body or "(prázdné)")
        P("")
if not any_daily:
    P("- (žádné denní poznámky)")
    P("")

print("\n".join(out))
