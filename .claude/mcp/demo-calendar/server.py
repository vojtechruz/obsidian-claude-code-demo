#!/usr/bin/env python3
"""
Demo kalendar jako MCP server (stdio, JSON-RPC 2.0, jedna zprava = jeden radek).

Nahrazuje v demo vaultu Google Calendar MCP: tooly i parametry kopiruji to, co skill
`tydenni-plan` vola na Google Calendar MCP (list_events se startTime/endTime/timeZone/
orderBy/pageSize), takze skill funguje stejne nad demo daty i nad realnym kalendarem.

Jen cteni. Udalosti jsou v `events.json` vedle tohoto souboru (tvar jako Google Calendar
Event: id, summary, location, description, start/end s `dateTime` nebo `date` u celodennich).

Jen stdlib, Python 3.8+, Windows i Linux. Spusteni: python server.py  (cte stdin, pise stdout)
"""
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

EVENTS_FILE = Path(__file__).resolve().parent / "events.json"
SERVER_INFO = {"name": "demo-calendar", "version": "1.0.0"}
SUPPORTED_PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
TZ_NAME = "Europe/Prague"

# ---------------------------------------------------------------- casy (bez zoneinfo/tzdata)


def _last_sunday(y, m):
    d = (date(y, m + 1, 1) if m < 12 else date(y + 1, 1, 1)) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() + 1) % 7)


def prague_tz(d):
    """CET/CEST pro dany den (EU letni cas: posledni nedele v breznu -> posledni nedele v rijnu)."""
    summer = _last_sunday(d.year, 3) <= d < _last_sunday(d.year, 10)
    return timezone(timedelta(hours=2 if summer else 1))


def parse_ts(s):
    """ISO 8601 -> aware datetime. Bez offsetu / jen datum = mistni cas v Praze."""
    s = str(s).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    if len(s) == 10:
        s += "T00:00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=prague_tz(dt.date()))
    return dt


def event_bounds(ev):
    """(start, end) jako aware datetime; celodenni udalost = od pulnoci do pulnoci (end exkluzivni)."""
    def one(x):
        if "dateTime" in x:
            return parse_ts(x["dateTime"])
        d = date.fromisoformat(x["date"])
        return datetime(d.year, d.month, d.day, tzinfo=prague_tz(d))
    return one(ev["start"]), one(ev["end"])


# ---------------------------------------------------------------- data


def load():
    with EVENTS_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def _matches(ev, text):
    if not text:
        return True
    hay = " ".join(str(ev.get(k, "")) for k in ("summary", "description", "location")).lower()
    return all(term in hay for term in text.lower().split())


def _check_calendar(args, data):
    cal = args.get("calendarId") or "primary"
    if cal not in ("primary", data["calendar"]["id"]):
        raise ValueError(f"Kalendar '{cal}' neexistuje (demo ma jen 'primary').")


def list_events(args, search=False):
    data = load()
    _check_calendar(args, data)
    now = datetime.now(timezone.utc)
    start = parse_ts(args["startTime"]) if args.get("startTime") else (None if search else now)
    end = parse_ts(args["endTime"]) if args.get("endTime") else (
        None if search else (start + timedelta(days=7)))
    text = args.get("fullText") or args.get("query") or ""
    out = []
    for ev in data["events"]:
        s, e = event_bounds(ev)
        if start and e <= start:
            continue
        if end and s >= end:
            continue
        if not _matches(ev, text):
            continue
        out.append((s, ev))
    order = args.get("orderBy") or "startTime"
    if order in ("startTime", "default", "lastModified"):
        out.sort(key=lambda x: x[0])
    elif order == "startTimeDesc":
        out.sort(key=lambda x: x[0], reverse=True)
    page_size = max(1, min(int(args.get("pageSize") or 100), 250))
    offset = int(args.get("pageToken") or 0)
    page = [ev for _, ev in out[offset:offset + page_size]]
    res = {"calendarId": "primary", "timeZone": TZ_NAME, "events": page}
    if offset + page_size < len(out):
        res["nextPageToken"] = str(offset + page_size)
    return res


def get_event(args):
    data = load()
    _check_calendar(args, data)
    for ev in data["events"]:
        if ev["id"] == args.get("eventId"):
            return ev
    raise ValueError(f"Udalost '{args.get('eventId')}' nenalezena.")


def list_calendars(_args):
    cal = load()["calendar"]
    return {"calendars": [{**cal, "primary": True, "accessRole": "reader"}]}


# ---------------------------------------------------------------- tool definice

_RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
_TIME_PROPS = {
    "calendarId": {"type": "string", "description": "ID kalendare. Default: primary (demo ma jen ten)."},
    "startTime": {"type": "string", "description": "Dolni mez casoveho okna, ISO 8601 (napr. 2026-10-05T00:00:00+02:00). Default: ted."},
    "endTime": {"type": "string", "description": "Horni mez (exkluzivni), ISO 8601. Default: startTime + 7 dni."},
    "timeZone": {"type": "string", "description": "IANA zona pro casy bez offsetu. Demo vzdy Europe/Prague."},
    "orderBy": {"type": "string", "enum": ["default", "startTime", "startTimeDesc", "lastModified"], "description": "Razeni. Default startTime."},
    "pageSize": {"type": "integer", "description": "Max udalosti na stranku (default 100, max 250)."},
    "pageToken": {"type": "string", "description": "nextPageToken z predchozi stranky."},
    "fullText": {"type": "string", "description": "Fulltext v nazvu, popisu a miste (vsechna slova, AND)."},
}

TOOLS = [
    {
        "name": "list_events",
        "description": "Vrati udalosti z demo kalendare v casovem okne startTime..endTime "
                       "(stejne parametry jako list_events v Google Calendar MCP). Jen cteni. "
                       "Celodenni udalosti maji start.date/end.date (end exkluzivni), casovane start.dateTime.",
        "inputSchema": {"type": "object", "properties": _TIME_PROPS},
        "annotations": {"title": "List events", **_RO},
    },
    {
        "name": "search_events",
        "description": "Fulltextove hledani udalosti (nazev, popis, misto); casove okno je volitelne. Jen cteni.",
        "inputSchema": {"type": "object", "properties": _TIME_PROPS, "required": ["fullText"]},
        "annotations": {"title": "Search events", **_RO},
    },
    {
        "name": "get_event",
        "description": "Vrati jednu udalost podle eventId (z list_events/search_events). Jen cteni.",
        "inputSchema": {"type": "object", "properties": {
            "calendarId": _TIME_PROPS["calendarId"],
            "eventId": {"type": "string", "description": "ID udalosti."}},
            "required": ["eventId"]},
        "annotations": {"title": "Get event", **_RO},
    },
    {
        "name": "list_calendars",
        "description": "Seznam kalendaru (demo ma jediny: primary).",
        "inputSchema": {"type": "object", "properties": {}},
        "annotations": {"title": "List calendars", **_RO},
    },
]

HANDLERS = {
    "list_events": lambda a: list_events(a),
    "search_events": lambda a: list_events(a, search=True),
    "get_event": get_event,
    "list_calendars": list_calendars,
}

# ---------------------------------------------------------------- JSON-RPC


def handle(msg):
    """Vrati odpoved (dict) nebo None pro notifikace."""
    method = msg.get("method")
    mid = msg.get("id")
    params = msg.get("params") or {}
    is_notification = "id" not in msg

    if is_notification:              # notifications/initialized, notifications/cancelled, ...
        return None

    def ok(result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    if method == "initialize":
        requested = params.get("protocolVersion")
        version = requested if requested in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
        return ok({
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
            "instructions": "Demo kalendar (jen cteni). V realnem vaultu sem patri Google Calendar MCP.",
        })
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name")
        handler = HANDLERS.get(name)
        if handler is None:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"Neznamy tool: {name}"}}
        try:
            result = handler(params.get("arguments") or {})
            return ok({"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                       "structuredContent": result, "isError": False})
        except Exception as e:  # chyba nastroje -> isError, ne chyba protokolu
            return ok({"content": [{"type": "text", "text": f"Chyba: {e}"}], "isError": True})
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}


def send(obj):
    sys.stdout.buffer.write(json.dumps(obj, ensure_ascii=False).encode("utf-8") + b"\n")
    sys.stdout.buffer.flush()


def main():
    for raw in sys.stdin.buffer:
        line = raw.decode("utf-8").strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}})
            continue
        batch = msg if isinstance(msg, list) else [msg]
        for m in batch:
            if not isinstance(m, dict):
                send({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}})
                continue
            resp = handle(m)
            if resp is not None:
                send(resp)


if __name__ == "__main__":
    main()
