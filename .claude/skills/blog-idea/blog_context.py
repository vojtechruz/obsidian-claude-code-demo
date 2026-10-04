#!/usr/bin/env python3
"""
Context loader for the `blog-idea` skill.

Reads the blog databases straight from the vault (no API, no dependencies
beyond the standard library) and prints a JSON context bundle used to review a
single new blog post idea:

  * existing articles  -> Oblasti/Blog/Blog Articles/*.md   (overlap, series fit)
  * existing ideas     -> Oblasti/Blog/Blog Ideas/*.md      (duplicate detection)
  * learning list      -> Oblasti/Osobni rust/Temata/*.md (open learning topics, learning alignment, optional)
  * tag vocabulary     -> tags actually used in the two databases

Usage:
    python .claude/skills/blog-idea/blog_context.py "Idea title" [--full-ideas]

Options:
    --full-ideas   also dump every idea title with its priority/tags
    --limit N      how many duplicate candidates per database (default 8)

Everything comes from notes in the vault; no blog source repository is needed.
The vault root is derived from this file's location; override with the
OBSIDIAN_VAULT environment variable.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

VAULT = Path(os.environ.get("OBSIDIAN_VAULT") or Path(__file__).resolve().parents[3])

BLOG_DIR = VAULT / "Oblasti" / "Blog"
IDEAS_DIR = BLOG_DIR / "Blog Ideas"
ARTICLES_DIR = BLOG_DIR / "Blog Articles"
LEARNING_DIR = VAULT / "Oblasti" / "Osobni rust" / "Temata"  # open learning topics; state derived from zacato/odlozeno/dokonceno

IDEA_CALLOUT = "AI Feedback"

STOPWORDS = {
    "a", "an", "and", "the", "in", "on", "of", "for", "to", "with", "without",
    "vs", "versus", "your", "you", "how", "what", "why", "using", "use", "is",
    "are", "it", "its", "at", "by", "or", "from", "into", "as", "new", "guide",
    "tutorial", "intro", "introduction", "part", "review",
}


# --------------------------------------------------------------------------- #
# frontmatter parsing (deliberately dependency-free)
# --------------------------------------------------------------------------- #

def split_note(text):
    """Return (frontmatter_dict, body) for a markdown note."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    return parse_frontmatter(lines[1:end]), "\n".join(lines[end + 1:])


def _clean(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def parse_frontmatter(lines):
    data = {}
    key = None
    for raw in lines:
        if not raw.strip():
            continue
        list_item = re.match(r"^\s*-\s+(.*)$", raw)
        if list_item and key is not None and isinstance(data.get(key), list):
            data[key].append(_clean(list_item.group(1)))
            continue
        m = re.match(r"^([A-Za-z][\w \-]*):\s*(.*)$", raw)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value in ("", "|", ">"):
            data[key] = []
        elif value == "[]":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            data[key] = [_clean(v) for v in value[1:-1].split(",") if v.strip()]
        else:
            data[key] = _clean(value)
    return data


def as_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    return [str(value)]


def load_dir(path):
    notes = []
    if not path.is_dir():
        return notes
    for f in sorted(path.glob("*.md")):
        try:
            fm, body = split_note(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        notes.append({
            "title": f.stem,
            "path": str(f.relative_to(VAULT)).replace("\\", "/"),
            "fm": fm,
            "body": body,
        })
    return notes


def strip_callout(body):
    """Drop the `> [!note]+ # AI Feedback` block from an idea body."""
    out, skipping = [], False
    for line in body.splitlines():
        if re.match(r"^>\s*\[!\w+\][+-]?\s*#?\s*" + IDEA_CALLOUT, line, re.I):
            skipping = True
            continue
        if skipping:
            if line.startswith(">") or not line.strip():
                continue
            skipping = False
        out.append(line)
    return "\n".join(out).strip()


# --------------------------------------------------------------------------- #
# fuzzy title matching
# --------------------------------------------------------------------------- #

def tokens(text):
    words = re.split(r"[^a-z0-9+#]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def score(query_tokens, text):
    other = tokens(text)
    if not query_tokens or not other:
        return 0.0
    overlap = len(query_tokens & other)
    return round(overlap / len(query_tokens), 2)


def rank(query, notes, limit, mapper):
    qt = tokens(query)
    scored = []
    for n in notes:
        s = max(score(qt, n["title"]), score(qt, " ".join(as_list(n["fm"].get("Topics")))))
        if s >= 0.34:
            item = mapper(n)
            item["match"] = s
            scored.append(item)
    scored.sort(key=lambda x: (-x["match"], x["title"]))
    return scored[:limit]


# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("title", help="title / topic of the new idea")
    ap.add_argument("--full-ideas", action="store_true")
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args()

    # Windows consoles often default to a legacy code page — the vault is full of non-ASCII.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    articles = load_dir(ARTICLES_DIR)
    ideas = [n for n in load_dir(IDEAS_DIR) if n["fm"].get("base")]
    learning = load_dir(LEARNING_DIR)

    missing = [str(p) for p in (ARTICLES_DIR, IDEAS_DIR) if not p.is_dir()]
    if missing:
        print(json.dumps({"error": "missing blog folders", "paths": missing}), flush=True)
        return 1

    tag_counts = {}
    for n in ideas:
        for t in as_list(n["fm"].get("Tags")):
            if "http" not in t and len(t) <= 25:
                tag_counts[t] = tag_counts.get(t, 0) + 1
    for n in articles:
        for t in as_list(n["fm"].get("Topics")):
            if "http" not in t and len(t) <= 25:
                tag_counts[t] = tag_counts.get(t, 0) + 1

    def article_row(n):
        return {
            "title": n["title"],
            "topics": as_list(n["fm"].get("Topics")),
            "date": str(n["fm"].get("Date", "")),
            "series": n["fm"].get("Series") or "",
            "draft_status": n["fm"].get("Draft Status") or "",
            "url": n["fm"].get("URL") or "",
        }

    def article_candidate(n):
        row = article_row(n)
        row["excerpt"] = (n["fm"].get("Excerpt") or "")[:400]
        return row

    def idea_candidate(n):
        return {
            "title": n["title"],
            "path": n["path"],
            "priority": n["fm"].get("Priority") or "",
            "tags": as_list(n["fm"].get("Tags")),
            "star": n["fm"].get("Star") in (True, "true", "True"),
            "reviewed": IDEA_CALLOUT.lower() in n["body"].lower(),
            "body_preview": strip_callout(n["body"])[:500],
        }

    slug = re.sub(r"[\\/:*?\"<>|]", "-", args.title).strip()
    exact = IDEAS_DIR / f"{slug}.md"

    out = {
        "vault": str(VAULT),
        "query": args.title,
        "target_path": f"Oblasti/Blog/Blog Ideas/{slug}.md",
        "target_exists": exact.is_file(),
        "counts": {
            "articles": len(articles),
            "ideas": len(ideas),
            "learning_items": len(learning),
        },
        "duplicate_candidates": {
            "ideas": rank(args.title, ideas, args.limit, idea_candidate),
            "articles": rank(args.title, articles, args.limit, article_candidate),
        },
        "tag_vocabulary": dict(sorted(tag_counts.items(), key=lambda kv: -kv[1])),
        "series": sorted({n["fm"].get("Series") for n in articles if n["fm"].get("Series")}),
        "learning_items": [
            {
                "title": n["title"],
                "priority": n["fm"].get("priorita") or "",
                "status": "rozpracovano" if n["fm"].get("zacato") else "chci",
                "tags": [t for t in (n["fm"].get("kategorie"),) if t],
            }
            for n in learning
            if not n["fm"].get("odlozeno") and not n["fm"].get("dokonceno")
        ],
        "articles": [article_row(n) for n in articles],
    }

    if args.full_ideas:
        out["ideas"] = [
            {
                "title": n["title"],
                "priority": n["fm"].get("Priority") or "",
                "tags": as_list(n["fm"].get("Tags")),
                "star": n["fm"].get("Star") in (True, "true", "True"),
            }
            for n in ideas
        ]

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
