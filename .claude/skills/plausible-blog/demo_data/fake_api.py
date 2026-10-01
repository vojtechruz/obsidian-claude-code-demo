"""Falesne Plausible Stats API v2 pro demo vault.

Odpovida na stejne dotazy jako POST /api/v2/query (metrics, date_range, dimensions, filters na event:page,
order_by, pagination) a vraci odpoved stejneho tvaru ({"results": [{"dimensions", "metrics"}], "meta", "query"}).
Data jsou fiktivni denni cisla blogu ondrakodi.example v site.json vedle tohoto souboru.
Smazanim slozky demo_data/ se plausible_stats.py prepne na skutecne API.
"""
import datetime as dt
import json
from pathlib import Path

DATA = json.loads((Path(__file__).with_name("site.json")).read_text(encoding="utf-8"))
START = dt.date.fromisoformat(DATA["start"])
TODAY = dt.date.fromisoformat(DATA["today"])
PAGES = DATA["pages"]

# Prekryv: navstevnik webu casto vidi vic stranek, proto unikatni navstevnici webu < soucet pres stranky.
SITE_VISITOR_FACTOR = 0.78
VISITS_PER_VISITOR = 1.18


def _range(date_range):
    if isinstance(date_range, list):
        a = dt.date.fromisoformat(date_range[0][:10])
        b = dt.date.fromisoformat(date_range[1][:10])
        return a, b
    r = date_range
    if r in ("day", "24h"):
        return TODAY, TODAY
    if r == "all":
        return START, TODAY
    if r.endswith("d") and r[:-1].isdigit():
        return TODAY - dt.timedelta(days=int(r[:-1])), TODAY - dt.timedelta(days=1)
    if r == "month":
        return TODAY.replace(day=1), TODAY
    if r == "year":
        return TODAY.replace(month=1, day=1), TODAY
    if r.endswith("mo") and r[:-2].isdigit():
        m = TODAY.month - int(r[:-2])
        y = TODAY.year + (m - 1) // 12
        return dt.date(y, (m - 1) % 12 + 1, 1), TODAY
    raise ValueError(f"date_range '{r}' demo nezna")


def _idx(a, b):
    lo = max(0, (a - START).days)
    hi = min(len(PAGES[0]["pageviews"]) - 1, (b - START).days)
    return lo, hi


def _pages(filters):
    sel = PAGES
    for f in filters or []:
        op, dim, vals = f[0], f[1], f[2]
        if dim != "event:page":
            continue
        vals = set(vals)
        if op == "is":
            sel = [p for p in sel if p["path"] in vals or p["path"].rstrip("/") in vals]
        elif op == "is_not":
            sel = [p for p in sel if p["path"] not in vals]
        elif op == "contains":
            sel = [p for p in sel if any(v in p["path"] for v in vals)]
    return sel


def _sum(page, key, lo, hi):
    return sum(page[key][lo:hi + 1]) if hi >= lo else 0


def _agg(pages, lo, hi, filtered):
    """Souhrnne metriky pro vybrane stranky a dny."""
    pv = sum(_sum(p, "pageviews", lo, hi) for p in pages)
    pvis = sum(_sum(p, "visitors", lo, hi) for p in pages)
    visitors = round(pvis * (0.97 if filtered else SITE_VISITOR_FACTOR))
    visits = round(visitors * VISITS_PER_VISITOR)
    w = pv or 1
    bounce = sum(p["bounce_rate"] * _sum(p, "pageviews", lo, hi) for p in pages) / w if pv else None
    dur = sum(p["visit_duration"] * _sum(p, "pageviews", lo, hi) for p in pages) / w if pv else None
    return {
        "visitors": visitors, "visits": visits, "pageviews": pv,
        "views_per_visit": round(pv / visits, 2) if visits else 0.0,
        "bounce_rate": round(bounce) if bounce is not None else None,
        "visit_duration": round(dur) if dur is not None else None,
        "events": pv,
    }


def _metrics(agg, metrics):
    return [agg.get(m) for m in metrics]


def _buckets(a, b, unit):
    d = a
    while d <= b:
        if unit == "day":
            e = d
        elif unit == "week":
            e = min(b, d + dt.timedelta(days=6 - d.weekday()))
        else:
            nxt = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
            e = min(b, nxt - dt.timedelta(days=1))
        start_label = d - dt.timedelta(days=d.weekday()) if unit == "week" else d.replace(day=1) if unit == "month" else d
        yield start_label.isoformat(), d, e
        d = e + dt.timedelta(days=1)


def query(body):
    metrics = body["metrics"]
    a, b = _range(body.get("date_range", "30d"))
    dims = body.get("dimensions") or []
    filters = body.get("filters") or []
    filtered = any(f[1] == "event:page" for f in filters)
    pages = _pages(filters)
    lo, hi = _idx(a, b)
    total = _agg(pages, lo, hi, filtered)
    results = []
    if not dims:
        results.append({"dimensions": [], "metrics": _metrics(total, metrics)})
    else:
        dim = dims[0]
        if dim.startswith("time:"):
            for label, s, e in _buckets(max(a, START), min(b, TODAY), dim.split(":")[1]):
                l2, h2 = _idx(s, e)
                results.append({"dimensions": [label], "metrics": _metrics(_agg(pages, l2, h2, filtered), metrics)})
        elif dim in ("event:page", "visit:entry_page", "visit:exit_page"):
            for p in pages:
                agg = _agg([p], lo, hi, True)
                if dim != "event:page":  # vstupni/vystupni stranky: zhruba podil navstev
                    agg = {k: (round(v * 0.85) if k in ("visitors", "visits", "pageviews") and v else v)
                           for k, v in agg.items()}
                if agg["pageviews"]:
                    results.append({"dimensions": [p["path"]], "metrics": _metrics(agg, metrics)})
        elif dim == "event:goal":
            for name, share, per in DATA["goals"]:
                v = round(total["visitors"] * share)
                agg = {"visitors": v, "events": round(v * per), "conversion_rate": round(share * 100, 1)}
                if v:
                    results.append({"dimensions": [name], "metrics": _metrics(agg, metrics)})
        elif dim in DATA["breakdowns"]:
            for value, share, bounce, dur in DATA["breakdowns"][dim]:
                agg = {"visitors": round(total["visitors"] * share), "visits": round(total["visits"] * share),
                       "pageviews": round(total["pageviews"] * share), "bounce_rate": bounce, "visit_duration": dur,
                       "events": round(total["pageviews"] * share)}
                agg["views_per_visit"] = round(agg["pageviews"] / agg["visits"], 2) if agg["visits"] else 0.0
                if agg["visitors"]:
                    results.append({"dimensions": [value], "metrics": _metrics(agg, metrics)})
        else:
            raise ValueError(f"Dimenzi '{dim}' demo nezna")
    for key, direction in reversed(body.get("order_by") or []):
        if key in metrics:
            i = metrics.index(key)
            results.sort(key=lambda r: (r["metrics"][i] is None, r["metrics"][i] or 0), reverse=(direction == "desc"))
        elif key in dims:
            results.sort(key=lambda r: r["dimensions"][0], reverse=(direction == "desc"))
    pag = body.get("pagination") or {}
    off = pag.get("offset", 0)
    results = results[off:off + pag.get("limit", 10000)]
    return {"results": results, "meta": {}, "query": {**body, "date_range": [f"{a}T00:00:00+02:00", f"{b}T23:59:59+02:00"]}}
