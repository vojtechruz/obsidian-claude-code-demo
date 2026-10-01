#!/usr/bin/env python3
"""Verifikace vaultu: broken links + orphaned attachments.

Run from vault root:  python .claude/skills/verifikace-vaultu/verify_vault.py
Output: report to stdout (sections BROKEN LINKS / ORPHANED ATTACHMENTS).
"""
import os
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VAULT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
EXCLUDE_DIRS = {'.obsidian', '.claude', '.claudian', '.git', '.idea', '.trash', 'node_modules'}
NOTE_EXTS = {'.md', '.base', '.canvas'}

WIKILINK_RE = re.compile(r'!?\[\[([^\]\[]+?)\]\]')
# Only a short alphanumeric suffix counts as a file extension - note names often end with
# a date or an abbreviation ("Schuzka s Adamem 21.11.", "Vymena pneumatik 4.10.")
EXT_RE = re.compile(r'^\.[A-Za-z0-9]{1,6}$')
MDLINK_RE = re.compile(r'\]\(([^)\s]+)\)')
EXTERNAL_PREFIXES = ('http://', 'https://', 'mailto:', 'obsidian://', 'file://', 'ftp://', 'data:', 'tel:', '#')


def walk_files():
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for f in files:
            yield os.path.relpath(os.path.join(root, f), VAULT).replace('\\', '/')


def main():
    all_files = list(walk_files())

    # Indexes (case-insensitive, Obsidian resolves links by basename)
    by_basename = {}          # 'name.ext' -> [paths]
    md_by_stem = {}           # 'name' (no ext) -> [paths] for notes
    by_relpath = {}           # full relative path lowercased -> path
    for p in all_files:
        base = os.path.basename(p).lower()
        by_basename.setdefault(base, []).append(p)
        by_relpath[p.lower()] = p
        stem, ext = os.path.splitext(base)
        if ext in NOTE_EXTS:
            md_by_stem.setdefault(stem, []).append(p)

    referenced = set()        # lowercased basenames that are linked from somewhere
    broken = []               # (source, target)

    def resolve(target):
        """Return True if target resolves; record referenced basename."""
        t = target.strip().strip('/')
        if not t:
            return True
        tl = t.lower()
        base = os.path.basename(tl)
        stem, ext = os.path.splitext(base)
        if not EXT_RE.match(ext):
            stem, ext = base, ''
        # Full-path match first (Obsidian accepts path links), then basename
        if tl in by_relpath or (tl + '.md') in by_relpath:
            referenced.add(os.path.basename(tl if tl in by_relpath else tl + '.md'))
            return True
        if ext and base in by_basename:
            referenced.add(base)
            return True
        if not ext and stem in md_by_stem:
            referenced.add(stem + '.md')
            return True
        # Note name that exists with .base/.canvas ext
        if not ext and (base + '.md') in by_basename:
            referenced.add(base + '.md')
            return True
        return False

    for p in all_files:
        if os.path.splitext(p)[1].lower() not in NOTE_EXTS:
            continue
        if p == 'CLAUDE.md' or p.startswith('System/Templates/'):  # docs and templates with example/placeholder links
            continue
        try:
            text = open(os.path.join(VAULT, p), encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        # Wikilinks: [[target]], [[target|alias]], [[target#heading]]
        # In markdown tables the alias pipe is escaped: [[target\|alias]]
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).replace('\|', '|').split('|')[0].split('#')[0]
            if '<%' in target or '${' in target or target.startswith('^'):  # template placeholders / regex artifacts
                continue
            if not resolve(target):
                broken.append((p, target))
        # Markdown links to local files: [text](path)
        for m in MDLINK_RE.finditer(text):
            raw = m.group(1)
            if raw.startswith(EXTERNAL_PREFIXES) or '://' in raw:
                continue
            target = urllib.parse.unquote(raw.split('#')[0])
            if not target:
                continue
            # Resolve relative to the note's folder, then vault root
            cand = os.path.normpath(os.path.join(os.path.dirname(p), target)).replace('\\', '/')
            if cand.lower() in by_relpath:
                referenced.add(os.path.basename(cand).lower())
                continue
            if not resolve(target):
                broken.append((p, raw))

    orphans = []
    for p in all_files:
        ext = os.path.splitext(p)[1].lower()
        if ext in NOTE_EXTS or ext in {'.json', '.js', '.css', '.py', '.sh', '.iml', '.gitignore', '.gitattributes'}:
            continue
        if os.path.basename(p).startswith('.'):  # service dotfiles
            continue
        if os.path.basename(p).lower() not in referenced:
            orphans.append(p)

    print(f'=== BROKEN LINKS ({len(broken)}) ===')
    for src, target in sorted(broken):
        print(f'{src}\t->\t{target}')
    print()
    print(f'=== ORPHANED ATTACHMENTS ({len(orphans)}) ===')
    for p in sorted(orphans):
        size = os.path.getsize(os.path.join(VAULT, p))
        print(f'{p}\t{size // 1024} KB')
    print()
    print(f'Checked {len(all_files)} files.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
