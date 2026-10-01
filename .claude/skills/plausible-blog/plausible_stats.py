#!/usr/bin/env python3
"""Statistiky blogu z Plausible Analytics (Stats API v2).

Konfigurace (mimo vault, nesynchronizuje se):
  ~/.plausible/config.json   {"api_key": "...", "site_id": "ondrakodi.example"}
  nebo env PLAUSIBLE_API_KEY / PLAUSIBLE_SITE_ID (maji prednost).

Demo: kdyz vedle skriptu existuje demo_data/ (nebo DEMO_MODE=1), skript nevola Plausible, odpovedi
pocita demo_data/fake_api.py z fiktivnich dat v demo_data/site.json a "dnes" je den z fixtures (2026-10-01).

Priklady:
  plausible_stats.py overview --period 30d
  plausible_stats.py pages --period 12mo --limit 30
  plausible_stats.py page testcontainers-spring-boot --period all
  plausible_stats.py breakdown visit:source --period 30d
  plausible_stats.py timeseries --period 12mo --interval month
  plausible_stats.py goals --period 30d
  plausible_stats.py query '{"metrics": ["visitors"], "date_range": "7d"}'
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import importlib.util
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://plausible.io/api/v2/query"
CONFIG_PATH = Path.home() / ".plausible" / "config.json"
DEFAULT_SITE_ID = "ondrakodi.example"
BLOG_URL = "https://ondrakodi.example"
ARTICLES_DIR = Path(__file__).resolve().parents[3] / "Oblasti" / "Blog" / "Blog Articles"
# Demo rezim: existuje-li vedle skriptu slozka demo_data/ (nebo DEMO_MODE=1), API se nevola.
DEMO_DIR = Path(__file__).resolve().parent / "demo_data"
DEMO = DEMO_DIR.is_dir() or os.environ.get("DEMO_MODE") == "1"
_demo_api = None


def demo_api():
    """Nacte demo_data/fake_api.py (falesne Stats API nad fixtures) - jen v demo rezimu."""
    global _demo_api
    if _demo_api is None:
        sys.dont_write_bytecode = True  # zadny __pycache__ ve fixtures
        spec = importlib.util.spec_from_file_location("fake_api", DEMO_DIR / "fake_api.py")
        _demo_api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_demo_api)
        print(f"[demo] Plausible se nevola, data jsou fiktivni z demo_data/ (dnes = {_demo_api.TODAY})", file=sys.stderr)
    return _demo_api


def current_date():
    return demo_api().TODAY if DEMO else dt.date.today()

# Periody, ktere skript prevadi na explicitni rozsah (kvuli porovnani s predchozim obdobim).
# Posledni N dni = N celych dni konci vcerejskem (dnesek je neuplny a zkresluje srovnani).
DAY_PERIODS = {"7d": 7, "28d": 28, "30d": 30, "91d": 91, "365d": 365}

METRIC_LABELS = {
    "visitors": "Navstevnici",
    "visits": "Navstevy",
    "pageviews": "Zobrazeni",
    "views_per_visit": "Stranek/navsteva",
    "bounce_rate": "Bounce rate",
    "visit_duration": "Delka navstevy",
    "events": "Udalosti",
}


class PlausibleError(Exception):
    pass


# ---------- konfigurace a API ----------

def load_config():
    cfg = {}
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as e:
            raise PlausibleError(f"Neplatny JSON v {CONFIG_PATH}: {e}")
    api_key = os.environ.get("PLAUSIBLE_API_KEY") or cfg.get("api_key")
    site_id = os.environ.get("PLAUSIBLE_SITE_ID") or cfg.get("site_id") or DEFAULT_SITE_ID
    if not api_key:
        raise PlausibleError(
            f"Chybi API klic. Vytvor ho v Plausible (Account settings -> API Keys -> Stats API) "
            f"a uloz do {CONFIG_PATH} jako {{\"api_key\": \"...\", \"site_id\": \"{DEFAULT_SITE_ID}\"}}."
        )
    return api_key, site_id


def run_query(body):
    if DEMO:
        try:
            return demo_api().query({"site_id": DEFAULT_SITE_ID, **body})
        except ValueError as e:
            raise PlausibleError(f"[demo] {e}")
    api_key, site_id = load_config()
    body = {"site_id": site_id, **body}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        try:
            detail = json.loads(detail).get("error", detail)
        except (json.JSONDecodeError, AttributeError):
            pass
        hint = ""
        if e.code == 401:
            hint = " (neplatny API klic)"
        elif e.code == 404 or "site" in str(detail).lower():
            hint = f" (zkontroluj site_id '{site_id}' - musi odpovidat domene v Plausible)"
        elif e.code == 429:
            hint = " (rate limit 600 dotazu/hod)"
        raise PlausibleError(f"HTTP {e.code}{hint}: {detail}")
    except urllib.error.URLError as e:
        raise PlausibleError(f"Nelze se spojit s Plausible: {e.reason}")


def rows(resp):
    """Vrati radky jako seznam (dimensions, metrics)."""
    return [(r.get("dimensions", []), r.get("metrics", [])) for r in resp.get("results", [])]


# ---------- obdobi ----------

def resolve_period(period, date_from=None, date_to=None):
    """Vrati (date_range pro API, predchozi obdobi nebo None, citelny popis)."""
    today = current_date()
    if date_from or date_to:
        start = dt.date.fromisoformat(date_from) if date_from else None
        end = dt.date.fromisoformat(date_to) if date_to else today
        if not start:
            raise PlausibleError("--to bez --from nedava smysl")
        return _explicit(start, end)
    if period in DAY_PERIODS:
        end = today - dt.timedelta(days=1)
        return _explicit(end - dt.timedelta(days=DAY_PERIODS[period] - 1), end)
    # "tento mesic/rok" se porovnava se stejne dlouhym usekem od zacatku predchoziho mesice/roku
    if period == "month":
        start = today.replace(day=1)
        return _explicit(start, today, prev_start=_add_months(start, -1))
    if period == "last-month":
        end = today.replace(day=1) - dt.timedelta(days=1)
        start = end.replace(day=1)
        prev_end = start - dt.timedelta(days=1)
        return [start.isoformat(), end.isoformat()], [prev_end.replace(day=1).isoformat(), prev_end.isoformat()], f"{start:%Y-%m}"
    if period == "year":
        start = today.replace(month=1, day=1)
        return _explicit(start, today, prev_start=start.replace(year=start.year - 1))
    if period == "last-year":
        start, end = dt.date(today.year - 1, 1, 1), dt.date(today.year - 1, 12, 31)
        return [start.isoformat(), end.isoformat()], [f"{today.year - 2}-01-01", f"{today.year - 2}-12-31"], str(today.year - 1)
    if period in ("12mo", "6mo"):
        months = int(period[:-2])
        end = today.replace(day=1) - dt.timedelta(days=1)
        start = _add_months(end.replace(day=1), -(months - 1))
        prev_end = start - dt.timedelta(days=1)
        prev_start = _add_months(prev_end.replace(day=1), -(months - 1))
        return ([start.isoformat(), end.isoformat()], [prev_start.isoformat(), prev_end.isoformat()],
                f"{start:%Y-%m} az {end:%Y-%m} ({months} celych mesicu)")
    if period in ("day", "24h", "all"):
        return period, None, {"day": "dnes", "24h": "poslednich 24 h", "all": "od zacatku mereni"}[period]
    if re.fullmatch(r"\d{4}-\d{2}", period):
        start = dt.date.fromisoformat(period + "-01")
        end = _add_months(start, 1) - dt.timedelta(days=1)
        prev_end = start - dt.timedelta(days=1)
        return [start.isoformat(), end.isoformat()], [prev_end.replace(day=1).isoformat(), prev_end.isoformat()], period
    if re.fullmatch(r"\d{4}", period):
        y = int(period)
        return [f"{y}-01-01", f"{y}-12-31"], [f"{y - 1}-01-01", f"{y - 1}-12-31"], period
    raise PlausibleError(f"Neznama perioda '{period}'")


def _explicit(start, end, prev_start=None):
    """prev_start: zacatek srovnavaciho useku stejne delky; default = tesne pred `start`."""
    days = (end - start).days + 1
    if prev_start is None:
        prev_start = start - dt.timedelta(days=days)
    prev_end = prev_start + dt.timedelta(days=days - 1)
    return [start.isoformat(), end.isoformat()], [prev_start.isoformat(), prev_end.isoformat()], f"{start} az {end} ({days} dni)"


def _add_months(d, n):
    m = d.month - 1 + n
    return d.replace(year=d.year + m // 12, month=m % 12 + 1, day=1)


# ---------- clanky ve vaultu ----------

def normalize_path(p):
    p = p.strip()
    p = re.sub(r"^https?://[^/]+", "", p)
    p = p.split("?")[0].split("#")[0]
    if not p.startswith("/"):
        p = "/" + p
    if not p.endswith("/"):
        p += "/"
    return p


def load_articles():
    """Mapa normalizovana cesta -> {title, date, reviewed}."""
    articles = {}
    if not ARTICLES_DIR.is_dir():
        return articles
    for f in ARTICLES_DIR.glob("*.md"):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        if not m:
            continue
        fm = m.group(1)
        path = re.search(r"^Path:\s*['\"]?([^'\"\n]+)", fm, re.M)
        if not path:
            continue
        date = re.search(r"^Date:\s*['\"]?([\d-]+)", fm, re.M)
        articles[normalize_path(path.group(1))] = {
            "title": f.stem,
            "date": date.group(1) if date else "",
        }
    return articles


# ---------- formatovani ----------

def fmt_value(metric, v):
    if v is None:
        return "–"
    if metric == "bounce_rate" or metric in ("conversion_rate", "exit_rate", "percentage"):
        return f"{v:.0f} %".replace(".", ",")
    if metric in ("visit_duration", "time_on_page"):
        v = int(round(v))
        return f"{v // 60}:{v % 60:02d}"
    if metric == "scroll_depth":
        return f"{v:.0f} %"
    if isinstance(v, float):
        return f"{v:.2f}".replace(".", ",")
    return f"{v:,}".replace(",", " ")


def fmt_change(metric, cur, prev):
    if cur is None or prev is None:
        return ""
    if metric == "bounce_rate":
        d = cur - prev
        return f"{d:+.0f} p.b."
    if not prev:
        return "nove" if cur else ""
    pct = (cur - prev) / prev * 100
    arrow = "▲" if pct > 0.5 else "▼" if pct < -0.5 else "="
    return f"{arrow} {pct:+.0f} %".replace(".", ",")


def md_table(headers, body, align=None):
    align = align or ["---"] + ["--:"] * (len(headers) - 1)
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(align) + " |"]
    for r in body:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
    return "\n".join(out)


def page_label(path, articles, link=True):
    a = articles.get(normalize_path(path))
    if a and link:
        return f"[[{a['title']}]]"
    if a:
        return a["title"]
    return f"`{path}`"


# ---------- prikazy ----------

def cmd_overview(args):
    dr, prev, label = resolve_period(args.period, args.date_from, args.date_to)
    metrics = ["visitors", "visits", "pageviews", "views_per_visit", "bounce_rate", "visit_duration"]
    filters = page_filter(args.page) if getattr(args, "page", None) else []
    cur = run_query({"metrics": metrics, "date_range": dr, "filters": filters})
    prv = run_query({"metrics": metrics, "date_range": prev, "filters": filters}) if prev and not args.no_compare else None
    if args.json:
        return {"period": dr, "current": cur, "previous_period": prev, "previous": prv}
    cm = cur["results"][0]["metrics"] if cur.get("results") else [None] * len(metrics)
    pm = prv["results"][0]["metrics"] if prv and prv.get("results") else None
    headers = ["Metrika", "Hodnota"] + (["Predchozi obdobi", "Zmena"] if pm else [])
    body = []
    for i, m in enumerate(metrics):
        row = [METRIC_LABELS[m], fmt_value(m, cm[i])]
        if pm:
            row += [fmt_value(m, pm[i]), fmt_change(m, cm[i], pm[i])]
        body.append(row)
    out = f"**Obdobi:** {label}" + (f" · srovnani s {prev[0]} az {prev[1]}" if pm else "") + "\n\n"
    return out + md_table(headers, body) + warnings(cur)


def cmd_pages(args):
    dr, prev, label = resolve_period(args.period, args.date_from, args.date_to)
    articles = load_articles()
    # Razeni podle zobrazeni: visitors u event:page pocitaji i custom eventy (napr. Copy Code)
    metrics = ["pageviews", "visitors", "bounce_rate"]
    body = {"metrics": metrics, "date_range": dr, "dimensions": ["event:page"],
            "order_by": [["pageviews", "desc"]], "pagination": {"limit": args.limit}}
    if args.articles_only:
        paths = sorted(articles)
        body["filters"] = [["is", "event:page", paths]] if paths else []
    cur = run_query(body)
    prev_map = {}
    if prev and not args.no_compare:
        pbody = dict(body, date_range=prev, pagination={"limit": 10000})
        pbody.pop("order_by", None)
        prev_map = {normalize_path(d[0]): m[0] for d, m in rows(run_query(pbody))}
    if args.json:
        return {"period": dr, "current": cur, "previous_visitors": prev_map}
    table = []
    for i, (d, m) in enumerate(rows(cur), 1):
        path = d[0]
        a = articles.get(normalize_path(path))
        r = [i, page_label(path, articles, link=not args.plain), a["date"] if a else ""]
        r += [fmt_value(mm, v) for mm, v in zip(metrics, m)]
        if prev and not args.no_compare:
            r.append(fmt_change("pageviews", m[0], prev_map.get(normalize_path(path), 0)))
        table.append(r)
    headers = ["#", "Stranka", "Publikovano", "Zobrazeni", "Navstevnici", "Bounce"]
    if prev and not args.no_compare:
        headers.append("Zmena zobr.")
    align = ["--:", "---", "---"] + ["--:"] * (len(headers) - 3)
    return f"**Obdobi:** {label}\n\n" + md_table(headers, table, align) + warnings(cur)


def page_filter(page):
    page = page.strip()
    if page.startswith("http") or page.startswith("/"):
        path = normalize_path(page)
    else:
        # slug nebo nazev poznamky clanku
        articles = load_articles()
        by_title = {a["title"].lower(): p for p, a in articles.items()}
        path = by_title.get(page.lower()) or normalize_path(page)
    # Plausible uklada cestu tak, jak prisla; pokryjeme variantu s i bez lomitka
    return [["is", "event:page", [path, path.rstrip("/")]]]


def cmd_page(args):
    articles = load_articles()
    flt = page_filter(args.page)
    path = flt[0][2][0]
    dr, prev, label = resolve_period(args.period, args.date_from, args.date_to)
    title = page_label(path, articles)
    ov = cmd_overview(argparse.Namespace(period=args.period, date_from=args.date_from, date_to=args.date_to,
                                          no_compare=args.no_compare, json=args.json, page=args.page))
    # zdroje navstev pro sessions, ktere tuto stranku videly
    src = run_query({"metrics": ["visitors"], "date_range": dr, "dimensions": ["visit:source"],
                     "filters": flt, "order_by": [["visitors", "desc"]], "pagination": {"limit": 10}})
    interval = "time:month" if (dr == "all" or isinstance(dr, list) and _days(dr) > 92) else "time:week" if isinstance(dr, list) and _days(dr) > 31 else "time:day"
    ts = run_query({"metrics": ["visitors", "pageviews"], "date_range": dr, "dimensions": [interval],
                    "filters": flt, "order_by": [[interval, "asc"]]})
    if args.json:
        return {"path": path, "overview": ov, "sources": src, "timeseries": ts}
    out = [f"### {title} (`{path}`)", "", ov, "", "**Zdroje navstev**", "",
           md_table(["Zdroj", "Navstevnici"], [[d[0], fmt_value("visitors", m[0])] for d, m in rows(src)]),
           "", f"**Vyvoj ({interval.split(':')[1]})**", "",
           md_table(["Obdobi", "Navstevnici", "Zobrazeni"],
                    [[d[0], fmt_value("visitors", m[0]), fmt_value("pageviews", m[1])] for d, m in rows(ts)])]
    return "\n".join(out)


def _days(dr):
    return (dt.date.fromisoformat(dr[1][:10]) - dt.date.fromisoformat(dr[0][:10])).days + 1


def cmd_breakdown(args):
    dr, _, label = resolve_period(args.period, args.date_from, args.date_to)
    dim = args.dimension if ":" in args.dimension else DIM_ALIASES.get(args.dimension, args.dimension)
    metrics = args.metrics.split(",") if args.metrics else ["visitors", "visits", "bounce_rate", "visit_duration"]
    if dim.startswith("event:") and not args.metrics:
        metrics = ["visitors", "pageviews"] if dim == "event:page" else ["visitors", "events"]
    body = {"metrics": metrics, "date_range": dr, "dimensions": [dim],
            "order_by": [[metrics[0], "desc"]], "pagination": {"limit": args.limit}}
    if args.filter:
        body["filters"] = json.loads(args.filter)
    resp = run_query(body)
    if args.json:
        return resp
    headers = [dim] + [METRIC_LABELS.get(m, m) for m in metrics]
    table = [[d[0] if d[0] is not None else "(none)"] + [fmt_value(mm, v) for mm, v in zip(metrics, m)] for d, m in rows(resp)]
    return f"**Obdobi:** {label} · **{dim}**\n\n" + md_table(headers, table) + warnings(resp)


DIM_ALIASES = {
    "source": "visit:source", "sources": "visit:source", "referrer": "visit:referrer",
    "channel": "visit:channel", "country": "visit:country_name", "countries": "visit:country_name",
    "city": "visit:city_name", "device": "visit:device", "browser": "visit:browser", "os": "visit:os",
    "entry": "visit:entry_page", "exit": "visit:exit_page", "utm_source": "visit:utm_source",
    "utm_campaign": "visit:utm_campaign", "utm_medium": "visit:utm_medium", "goal": "event:goal",
    "page": "event:page",
}


def cmd_timeseries(args):
    dr, _, label = resolve_period(args.period, args.date_from, args.date_to)
    dim = f"time:{args.interval}"
    metrics = ["visitors", "visits", "pageviews"]
    resp = run_query({"metrics": metrics, "date_range": dr, "dimensions": [dim], "order_by": [[dim, "asc"]]})
    if args.json:
        return resp
    table = [[d[0]] + [fmt_value(mm, v) for mm, v in zip(metrics, m)] for d, m in rows(resp)]
    return f"**Obdobi:** {label} · po {args.interval}\n\n" + md_table(["Obdobi"] + [METRIC_LABELS[m] for m in metrics], table)


def cmd_goals(args):
    args.dimension, args.metrics, args.filter = "event:goal", "visitors,events", None
    return cmd_breakdown(args)


def cmd_summary(args):
    """Blok pro Denik souhrny: celkova zobrazeni webu + top N clanku podle zobrazeni."""
    dr = [args.start, args.end]
    total = run_query({"metrics": ["pageviews"], "date_range": dr})
    total_pv = total["results"][0]["metrics"][0] if total.get("results") else 0
    articles = load_articles()
    top = []
    if articles:
        variants = sorted({v for p in articles for v in (p, p.rstrip("/"))})
        resp = run_query({"metrics": ["pageviews"], "date_range": dr, "dimensions": ["event:page"],
                          "filters": [["is", "event:page", variants]], "order_by": [["pageviews", "desc"]],
                          "pagination": {"limit": args.top * 2}})
        merged = {}
        for d, m in rows(resp):
            p = normalize_path(d[0])
            merged[p] = merged.get(p, 0) + m[0]
        top = sorted(merged.items(), key=lambda kv: -kv[1])[:args.top]
    if args.json:
        return {"period": dr, "pageviews": total_pv, "top": top}
    if not total_pv:
        return ""
    lines = [f"- 📈 Blog: {fmt_value('pageviews', total_pv)} zobrazení"]
    lines += [f"    - {page_label(p, articles)} {fmt_value('pageviews', pv)}" for p, pv in top]
    return "\n".join(lines)


def cmd_query(args):
    return run_query(json.loads(args.body))


def warnings(resp):
    w = (resp.get("meta") or {}).get("warning") or (resp.get("meta") or {}).get("metric_warnings")
    return f"\n\n> [!warning] Plausible: {json.dumps(w, ensure_ascii=False)}" if w else ""


# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser(description="Statistiky blogu z Plausible Analytics")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, period="30d"):
        sp.add_argument("--period", default=period,
                        help="7d, 28d, 30d, 91d, 365d, month, last-month, 6mo, 12mo, year, last-year, "
                             "YYYY, YYYY-MM, day, 24h, all")
        sp.add_argument("--from", dest="date_from", help="YYYY-MM-DD (prebije --period)")
        sp.add_argument("--to", dest="date_to", help="YYYY-MM-DD (default dnes)")
        sp.add_argument("--json", action="store_true", help="surova odpoved API")

    sp = sub.add_parser("overview", help="souhrnne metriky webu + srovnani s predchozim obdobim")
    common(sp)
    sp.add_argument("--no-compare", action="store_true")
    sp.set_defaults(func=cmd_overview, page=None)

    sp = sub.add_parser("pages", help="nejctenejsi stranky, namapovane na poznamky v Blog Articles")
    common(sp)
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--articles-only", action="store_true", help="jen clanky (bez homepage, tagu...)")
    sp.add_argument("--no-compare", action="store_true")
    sp.add_argument("--plain", action="store_true", help="nazvy bez [[wikilinku]]")
    sp.set_defaults(func=cmd_pages)

    sp = sub.add_parser("page", help="detail jednoho clanku (souhrn, zdroje, vyvoj)")
    sp.add_argument("page", help="slug, /cesta/, URL nebo nazev poznamky clanku")
    common(sp, period="12mo")
    sp.add_argument("--no-compare", action="store_true")
    sp.set_defaults(func=cmd_page)

    sp = sub.add_parser("breakdown", help="rozpad podle dimenze (source, country, device, utm_campaign...)")
    sp.add_argument("dimension", help="alias (source, referrer, channel, country, device, browser, os, entry, "
                                      "utm_campaign...) nebo plny nazev visit:/event:")
    common(sp)
    sp.add_argument("--limit", type=int, default=15)
    sp.add_argument("--metrics", help="carkou oddelene, napr. visitors,pageviews")
    sp.add_argument("--filter", help="JSON pole filtru Stats API v2")
    sp.set_defaults(func=cmd_breakdown)

    sp = sub.add_parser("timeseries", help="vyvoj navstevnosti v case")
    common(sp, period="12mo")
    sp.add_argument("--interval", choices=["day", "week", "month"], default="month")
    sp.set_defaults(func=cmd_timeseries)

    sp = sub.add_parser("goals", help="konverze / custom eventy (goals)")
    common(sp)
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(func=cmd_goals)

    sp = sub.add_parser("summary", help="blok do Denik souhrnu: zobrazeni celkem + top clanky")
    sp.add_argument("start", help="YYYY-MM-DD")
    sp.add_argument("end", help="YYYY-MM-DD (vcetne)")
    sp.add_argument("--top", type=int, default=5)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_summary)

    sp = sub.add_parser("query", help="libovolny dotaz Stats API v2 (JSON bez site_id)")
    sp.add_argument("body")
    sp.set_defaults(func=cmd_query, json=True)

    args = p.parse_args()
    try:
        result = args.func(args)
    except PlausibleError as e:
        print(f"CHYBA: {e}", file=sys.stderr)
        sys.exit(2)
    if isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
