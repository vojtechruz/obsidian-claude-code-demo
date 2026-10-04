# CLAUDE.md

This file guides Claude Code when working in this repository.

## What this is

This is an **Obsidian vault** (a personal knowledge base of Markdown notes), not a software project. There is no build, test, lint, or dependency tooling. Work here means creating, editing, organizing, and linking Markdown (`.md`) notes. Content is bilingual — mostly Czech, some English.

The vault is a plain **git repository** prepared for a workshop (JOpenSpace). There is no sync service behind it: open the folder as a vault in Obsidian and work with it like any other repo.

## Demo vault

This is a **fictional demo vault**. It belongs to the persona **Ondřej „Ondra“ Kratochvíl** — a Java developer and tech lead at the fictional company Lumera Labs, living in Prague with his partner Lucie and the cat Bublina. He runs, does OCR races and bouldering, plays board games with friends, co-organizes the fictional meetup Java Pivo Praha and writes the blog `ondrakodi.example`.

All people, companies, races, results, dates and domains are invented (domains only `*.example`). Inside the vault, "today" is **2026-10-01**. The skills in `.claude/skills/` are real skills adapted to this vault; skills that would call external services run over fixtures in their `demo_data/` folder, and the Google Calendar is replaced by the local `demo-calendar` MCP server (`.mcp.json`).

Human-facing workshop docs (map, plugins, skills overview, scenarios, reset/troubleshooting) live in `Workshop/`. Treat them as documentation, not content: skills should not summarize, file or process notes from `Workshop/`.

## Layout

The vault follows a **PARA-style** organization (`Projekty`, `Oblasti`, `Znalosti`, `Archiv`) alongside a few special-purpose folders:

- `Denik/` — the journal: daily notes as `YYYY/YYYY-MM/YYYY-MM-DD.md` (e.g. `Denik/2026/2026-09/2026-09-26.md`), weekly summaries and weekly plans in `YYYY/Weekly/`, monthly/yearly folder notes. See **Denik journal** below.
- `Projekty/` — **Projects**: active efforts with a goal and an end (PARA "Projects"). One folder per project with a note of the same name (template `System/Templates/Projekt.md`, tag `Projekt`, `oblast`, `status`, `start_date`, `due_date`).
- `Oblasti/` — **Areas**: ongoing responsibilities to maintain over time (PARA "Areas"). One folder per area with a folder note of the same name (template `System/Templates/Oblast.md`, tag `Oblast`). Areas: Prace, Lucie, Rodina a Pratele, Kondice a Zdravi, Osobni rust, Blog, IT Komunita, Cestovani, Domov, Administrativa, Finance, Radost, Vzpominky.
- `Znalosti/` — **Resources/Knowledge**: reference material by topic (e.g. `Znalosti/Kubernetes/`). Each topic is a subfolder, often with its own `Attachments/`. `Znalosti/` holds only **acquired** knowledge (výpisky); the to-learn queue lives in `Oblasti/Osobni rust/Temata/` — see *Learning* below.
- `Archiv/` — **Archive**: inactive notes from the other three PARA buckets. Mirrors the live structure: archived projects go to `Archiv/Projekty/<name>/`, archived area notes to `Archiv/<Oblast>/` (e.g. `Archiv/Prace/`, `Archiv/Radost/`, `Archiv/Domov/`), archived tasks to `Archiv/Tasks/`. Attachments live next to the notes in `Archiv/<Oblast>/Attachments/` — don't create a flat `Archiv/Attachments/`.
- `Lide/` — **People**: one note per person (e.g. `Lide/Lucie.md`).
- `Media/` — media notes (books, films, series, music, games, theatre…), one note per title, `Media.base` table view (Czech `Category` values: Film, Seriál, Kniha, Hudba, Hra, Dokument, Divadlo, Umění, Zdroj; `Genre`, `Consumed`, `Rating` = ČSFD/Databáze knih score, `Link`, optional `Doporucil: [[Person]]`).
- `Flashcards/` — spaced-repetition decks for the Spaced Repetition plugin. **The folder is the deck** (`Flashcards/Git/` → deck "Git"); files are tagged `#flashcards/<deck>`. Card formats: `Question::Answer` (one-way), `Question:::Answer` (bidirectional), multiline (`?` on its own line), and `==cloze==`. See the info callout at the top of any deck file for the full convention.
- `Tasks/` — tasks managed by the TaskNotes plugin. Each task is a note with YAML frontmatter (`tags: [task]`, `status`, `priority` (`dnes`/`tyden`/`mesic`/`pozdeji`/`on-ice`), `due`, `scheduled`, `projects`, `oblast`, etc.). Don't restructure these by hand — the plugin owns their schema.
- `System/` — infrastructure: `System/Bases/` (Bases table views: `Oblasti.base`, `Projekty.base`, `Lide.base`, `Darky.base`, `Napady na darky.base`, plus one `.base` per area in `System/Bases/Oblasti/` and per project in `System/Bases/Projekty/`, embedded by the area/project notes), `System/Templates/` (Templater templates; `Oblast.base` / `Projekt.base` are the templates for those per-area/per-project bases), `System/TaskNotes/Views/*.base` (TaskNotes saved views).
- `__INBOX/` — default location for newly created notes; a staging area before notes are filed elsewhere.
- `__INBOX/Attachments/` — pasted images and other attachments (configured attachment folder is `./Attachments` relative to the note).
- `.obsidian/` — Obsidian app configuration (plugins, hotkeys, appearance, workspace). Do not edit unless explicitly asked.
- `.trash/` — Obsidian's local trash (deleted notes). Don't treat as active content.

## Plugins that affect content

Community plugins are enabled that give special meaning to certain notes — respect their conventions when editing:

- **Spaced Repetition** — reads `#flashcards`-tagged notes under `Flashcards/` as cards (see folder note above).
- **TaskNotes** — each task is a frontmatter-driven note under `Tasks/`; `.base` files are its views.
- **Templater** / **QuickAdd** — create daily notes, areas and projects from `System/Templates/`.
- **Folder Notes** — a note with the same name as its folder is that folder's note (e.g. `Oblasti/Blog/Blog.md`); renaming the folder renames the note.
- **Paste Image Rename** — auto-renames pasted images.

## Markdown conventions (Obsidian flavor)

- **Internal links:** `[[Note Name]]` (links by note title, not path). Clicking a link to a non-existent note creates it.
- **Embeds:** `![[Note Name]]` or `![[image.png]]` embeds the target inline.
- **External links:** `[Text](url)`; images `![alt](url)`.
- **Emphasis:** `**bold**`, `*italic*`, `~~strikethrough~~`, `==highlight==`.
- Notes use `-` bulleted lists heavily and often have no top-level `# H1` title (the filename is the title).

## Working guidelines

- New notes default to `__INBOX/` unless the user specifies another folder.
- Daily notes belong in `Denik/YYYY/YYYY-MM/` using the `YYYY-MM-DD.md` filename.
- Preserve the existing language of a note (Czech or English) when editing. Czech notes are written without diacritics in file and folder names.
- Link related notes with `[[...]]` rather than duplicating content.
- `alwaysUpdateLinks` is on in Obsidian, but this only applies inside the app — if you rename or move a note via the filesystem/git, update `[[links]]` to it manually.
- `.gitignore` excludes JetBrains IDE files (`.idea/`, `*.iml`) and Obsidian workspace state.
- Commit only when explicitly asked.
- **Archiving notes:** When the user says "archivuj" (archive), move the note to the matching subfolder of `Archiv/` (project → `Archiv/Projekty/`, area note → `Archiv/<Oblast>/`, task → `Archiv/Tasks/`) AND add the `archived` tag to the note's frontmatter (`tags: [archived, ...]`).
- **Races (závody):** race notes live in `Oblasti/Kondice a Zdravi/<Název YYYY>.md` (tag `zavod`, index `Sportovní akce`). After a race, the skill `zpracovani-zavodu` restructures the note: post-race info on top (Přehled → Oficiální výsledky → Fotografie a zážitky → Garmin → Odkazy), everything that mattered only before the start under a single `# 🗂️ Před závodem` H1 at the bottom.
- **Learning (učení):** hub `Oblasti/Osobni rust/Uceni.md`, bases `System/Bases/Uceni.base` + `Zdroje.base`. One note per topic in `Oblasti/Osobni rust/Temata/` is both the notes (výpisky) and the tracker. There is **no `stav` property** — state is derived: queued = in `Temata/` without `zacato`; in progress = has `zacato` (max 2 at once); postponed = has `odlozeno` (date + a line where it stopped); done = has `dokonceno` and is **moved to `Znalosti/<obor>/`** (`Znalosti/` never holds a to-learn queue). Properties: `priorita` (`vysoka`/`stredni`/`nizka`), `kategorie`, `zdroje`, `cil`, `zacato`, `odlozeno`, `dokonceno`, `v_praci`, `blog` (link to a Blog Idea). A topic that extends existing výpisky starts its body with `Rozsiruje [[...]]` and is merged into that note as a section on completion instead of moving. `Oblasti/Osobni rust/Zdroje/` holds only courses and platforms (`typ`, `platforma`, `koupeno`, `zacato`, `dokonceno`, `url`, `plati_do`); books stay in `Media/` and topics link them directly; articles and videos are plain links in the topic's `## Zdroje` section. Pasted AI answers go into a collapsed `> [!ai]- AI material (nezpracovano)` callout, own notes outside it. The `blog-idea` skill reads open topics from `Temata/` for learning alignment.
- **Board games (deskovky):** always belong to the **Rodina a Pratele** area. The game catalog lives in `Oblasti/Rodina a Pratele/Deskovky/` (one note per game + `Deskovky.base` table view); anything boardgame-related that needs an area/context maps to Rodina a Pratele. In game notes, the `Language` property uses plain `CZ` / `EN` values (no flag emoji).

## Reminders (dates, deadlines, expiries)

Obsidian reminds nothing by itself, so any date that matters must become one of these:

- **No action needed** (pure info, e.g. a warranty ends, insurance cover starts) → **Google Calendar** all-day event with a notification and an Obsidian link to the source note. Create events only after the user confirms. (In the demo the calendar is the read-only `demo-calendar` MCP server — propose the event instead of creating it.)
- **Action needed** (renew, replace, book, extend) → **TaskNote** in `Tasks/` with `due` = the real deadline, `scheduled` = when to start dealing with it (due minus lead time: ~2 weeks for a few clicks, ~1 month when booking is needed, 2–3 months for offices or comparing contracts), `priority: pozdeji`, `status: To Do`. Yearly items use TaskNotes `recurrence`. Link task ↔ note both ways. Don't duplicate actionable items into the calendar by hand — the weekly plan (`tydenni-plan`) surfaces them once `scheduled` falls in the planned week or `due` is within 30 days.
- **Imported or scanned material** may carry inline reminder dates (e.g. `2027-04-23` next to text) or hide expiry dates in scanned documents. Find them all, flag expired items in the note, and convert them by the rules above.

## Journal (Denik)

Three layers, each with its own skill; the scripts under `.claude/skills/denik-souhrn/` own the navigation blocks, MOC and stamps — never hand-edit those parts.

- **Daily notes** `Denik/YYYY/YYYY-MM/YYYY-MM-DD.md` — flat `-` bullets of what happened. Templater inserts the nav line (`← … → · ↑ week · month`).
- **Weekly summary** `Denik/YYYY/Weekly/YYYY-Www.md` (skill `denik-souhrn`, ISO week) — bullets regrouped by life role + `## AI shrnutí`. Frontmatter property **`denik_src`** is a per-day content hash written by `check_late_edits.py --stamp`; `denik-souhrn` uses it to detect bullets added to daily notes *after* the summary was written (typical: Sunday evening, after planning) and merges them in. Script-owned — don't edit or remove it.
- **Weekly plan** `Denik/YYYY/Weekly/YYYY-Www-plan.md` (skill `tydenni-plan`) — forward-looking only (Big Rocks — max 3 measured priorities planned into free evenings first; Po–Ne calendar; fixed appointments; deadlines; Small Rocks — unmeasured gap-fillers; projects; waiting-for); opened daily, so keep it lean. The current plan carries alias **`Aktualni plan`** — exactly one plan has it; the skill moves it when a new plan is written. Google Calendar is read-only for this skill.
- **Weekly review** `Denik/YYYY/Weekly/YYYY-Www-review.md` (written by `tydenni-plan` when planning week Www+1) — how week Www's plan went (Big Rocks ✅/🔁/❌, planned vs done, `## Poučení`); read once, its lessons feed the next plan. `*-plan.md` and `*-review.md` are ignored by the Denik scripts (no nav block, not in the MOC).
- Monthly/yearly folder notes and the MOC `Denik/Denik.md` are generated from the summaries (`build_moc.py`).

## Where to create skills

Skills live in `.claude/skills/<name>/skill.md` (in this vault) or in the user-global
`~/.claude/skills/`. When asked to create a skill, decide by scope:

- **Vault-specific → create it in the vault**, at `.claude/skills/<name>/skill.md`, without
  asking. A skill is vault-specific if it reads or writes notes here, references vault
  paths (`Denik/`, `Oblasti/`, `Tasks/`…), or encodes conventions from this file.
  Existing examples: `denik-souhrn`, `denik-dotazy`, `tydenni-plan`, `navrh-darku`. Keeping them in
  the vault means they are versioned together with the notes they operate on.
- **Not vault-specific → ask explicitly where to create it** (vault vs. global) before
  writing anything. Don't default to one silently.

**Never create the same skill in both places.** A stale global copy shadows the vault one
and silently produces worse output.

Skills must work on Windows, macOS and Linux. Helper scripts are Python 3 (stdlib where
possible), never PowerShell or Bash-only. They find the vault from their own location
(`Path(__file__).resolve().parents[3]`), never from a hardcoded absolute path. Run them with
`python` on Windows and `python3` elsewhere. Scripts that call an external service support a
demo mode: with a `demo_data/` folder next to the script (or `DEMO_MODE=1`) they read
fixtures instead of the network.

**Running skill scripts:** the working directory is already the vault root. Run a script as a single plain command, e.g. `python .claude/skills/verifikace-vaultu/verify_vault.py`, with no `cd`, no `&&` chains, no pipes and no redirection to temp files. Read the output directly. `.claude/settings.json` pre-approves exactly this form (`python …` / `python3 …` in Bash and PowerShell), so plain commands run without a permission prompt. Compound commands would stop and ask.

Skill format: a single `skill.md` with YAML frontmatter (`name`, `description`) — the
description must state *when* to use the skill, since that's what triggers it. Supporting
scripts live next to it in the same folder. `manifest.json` / `README.md` are the old
format; don't create new ones.
