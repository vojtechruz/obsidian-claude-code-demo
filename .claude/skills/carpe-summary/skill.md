---
name: carpe-summary
description: Aggregate daily journal notes into a weekly, monthly, or yearly summary for the Carpe Diem vault, and maintain the journal's MOC. Use when the user asks to summarize a week/month/year, merge daily notes, create a weekly summary, "udelej tydenni souhrn", "shrnuti tydne/mesice/roku", or similar — and also when they ask to refresh/rebuild the Carpe Diem MOC, rozcestnik or folder note ("aktualizuj MOC", "pregeneruj rozcestnik", "rebuild carpe diem index"). Regroups bullets into role-based Czech categories (Práce, Lucie, Rodina a přátelé, Kondice a zdraví, Osobní růst, Radost, Domácnost, Administrativa, Memories) with an AI summary on top. Detail falls as the period widens (week = every event, month = outcomes, year = milestones), and every run ends with a report of what was omitted, merged or moved. Daily notes are preserved. Uses Folder Notes plugin.
---

# Weekly / Monthly / Yearly summary

Aggregates the user's daily notes into a period summary. Output is an **open bulleted list regrouped by category**, with a short **AI summary at the top**. Original daily notes are always **kept**.

## Vault layout (dates use ISO week, week starts Monday; uses Folder Notes plugin)

```
Carpe Diem/
  Carpe Diem.md              <- MOC / rozcestník (folder note of the whole journal, generated)
  2026/
    2026.md                  <- yearly folder note for 2026
    2026-06/                 <- month folder (YYYY-MM)
      2026-06.md             <- monthly folder note (Folder Notes plugin)
      2026-06-29.md          <- daily note (source)
    Weekly/
      2026-W27.md            <- weekly summary
```

- **Daily notes:** `Carpe Diem/YYYY/YYYY-MM/YYYY-MM-DD.md`
- **Weekly:** `Carpe Diem/YYYY/Weekly/YYYY-Www.md` (ISO week; year = the year the week's Thursday falls in, per ISO 8601)
- **Monthly (Folder Notes):** `Carpe Diem/YYYY/YYYY-MM/YYYY-MM.md` (folder note inside `YYYY-MM/` folder)
- **Yearly (Folder Notes):** `Carpe Diem/YYYY/YYYY.md` (folder note inside `YYYY/` folder)
- **MOC (Folder Notes):** `Carpe Diem/Carpe Diem.md` — the journal's entry point, **fully generated** from the summaries (see step 8). Never hand-edit its generated part.

## Steps

1. **Determine period and range.**
   - Default period is **week**. Accept an argument like `week`, `month`, `year`, optionally with an identifier (`2026-W27`, `2026-06`, `2026`).
   - If no identifier is given, default to the **most recently completed period** (for `week`: the previous Monday–Sunday relative to today; for `month`/`year`: the last full one). If today is mid-week and the user clearly means the current in-progress week, use that instead.
   - Compute the exact date range with the Bash tool so week boundaries and ISO week numbers are correct, e.g.:
     - `date -d "2026-06-29" +%V` → ISO week number; `date -d "2026-06-29" +%G` → ISO week-year.
     - For "previous complete week": `date -d "last monday -7 days" +%F` (start) through `+6 days` (Sunday end).
   - **State the resolved range back to the user** (e.g. "Týden 27: Po 29.6. – Ne 5.7. 2026") before writing, so they can catch an off-by-one.

1b. **Late-edit check of the previous week (always for `week`, cheap).** Summaries are typically
   written on Sunday afternoon as part of planning the next week (`tydenni-plan`), and the user
   often adds more bullets to that Sunday's daily note afterwards. Those would otherwise be lost
   for good (they never reach the month/year either). Run:
   ```
   python .claude/skills/carpe-summary/check_late_edits.py
   ```
   Each weekly summary carries a frontmatter property `carpe_src` (list of `YYYY-MM-DD=hash`)
   with a content hash per source day (nav block, blank lines, `xjs` bullets and the `⌚ Garmin:` line are ignored, so
   `link_carpe.py` and `garmin_days.py` don't trigger it). Never hand-edit that property; the script owns it. The script lists days whose content changed since the stamp
   (`CHANGED`/`NEW`); for summaries without a stamp (`NOSTAMP`, older notes) it falls back to
   file mtimes and always flags the Sunday.
   - For every flagged day: read the daily note, compare against the week's summary and **add
     the missing bullets** to the right category (apply the same filters as step 2 — drop `xjs`,
     keep everything else). Update `## AI shrnutí` only if something significant was added.
   - If the **monthly summary** containing that week already exists, add the item there too
     (and to the yearly, if it exists and the item is year-worthy).
   - Then re-stamp: `python .claude/skills/carpe-summary/check_late_edits.py --stamp YYYY-Www`.
   - Tell the user what was merged (or that nothing changed).

2. **Collect source material.**
   - **Week** → read every daily note whose date falls in the range, in chronological order.
   - **Month** → read that month's **weekly summaries** (`Carpe Diem/YYYY/Weekly/`) if they exist; otherwise fall back to the daily notes for the month.
   - **Year** → read that year's **monthly summaries**; otherwise fall back to weekly, then daily.
   - Use Glob to find the files. If none exist for the range, tell the user and stop — do not invent content.
   - **Exclude meta-bullets that refer to writing this very report:** any `xjs week`, `xjs month`, `xjs year` item marks that the aggregation report itself was done (see step 6b). It belongs only in the daily note — **never carry it into a weekly/monthly/yearly summary.** Drop it silently.
   - **`pocket wipe` only propagates up one level:** include it in the **weekly** summary, but **drop it from monthly and yearly** summaries. (When building a month/year, ignore any `pocket wipe` bullets found in the source daily/weekly notes.)
   - **Routine noise also only propagates up one level — keep in weekly, drop from monthly and yearly.** A month/year is a retrospective, so leave out what will read as filler later. Drop:
     - **Rutinní pochůzky a spotřební nákupy** — stříhání a péče o vzhled (`nechal jsem se ostříhat`, `objednáno se k holiči`), nákup potravin (`velký nákup`, `objednán a převzat košík`), krmivo a potřeby pro kočku (`granule pro Bublinu`), běžné doplňování zásob (drogerie).
     - **Drobné jednorázovky bez trvalého výsledku** — instalace či vyzkoušení běžné aplikace, sociální mikro-interakce (odpověď na gratulaci na LinkedInu), tisk/sken/vyplnění formuláře jako mezikrok k něčemu, co už je uvedené (`vytištěna startovka na závod`, `vyplněn formulář k pasu`), uplatnění drobných kreditů a voucherů (audioknihy, slevové kódy), drobný úkon, který je podkrokem větší položky (`objednán termín u veterináře` — samotné očkování Bubliny zůstává).

     **Ponech výsledek, zahoď kroky, které k němu vedly.** Pokud větší položka událost už pokrývá, její administrativní mezikroky nepotřebují vlastní odrážku.

     **Nemaž jen proto, že je položka malá — v týdnu.** V týdenním souhrnu jednorázové nákupy s trvalou hodnotou (běžecké boty, čelovka, hodinky, vybavení, nábytek) a skutečné poprvé / jednorázové zážitky **zůstávají**. Od měsíce výš platí škála z kroku 2d: zůstávají jen **větší** nákupy a vybavení, které něco mění (monitor, fotoaparát, hodinky, nábytek); drobné vybavení (masážní válec, ponožky, imbusy, magnézium) a drobné poprvé jdou ven a do reportu. Roční souhrn nechá jen to, co dává smysl po celém roce.

2b. **Garmin — kroky a aktivity (always).** The user wears a Garmin watch; every period gets its
   steps and activities (type + duration, plus distance for distance sports — no pace or HR here) from
   `garmin_days.py`:
   ```
   python .claude/skills/carpe-summary/garmin_days.py START END --write     # week: writes a line into each daily note + prints the period line
   python .claude/skills/carpe-summary/garmin_days.py START END --summary   # month / year: period line only
   ```
   - **Week:** run with `--write`. It appends (or refreshes — idempotent) one bullet at the end of
     each daily note in the range: `- ⌚ Garmin: 11 575 kroků · Posilovna 45 min · Běh 23 min (2,9 km)`.
     Days without data are skipped; missing daily notes are **not** created (the script just reports
     them). Do this **before** stamping (5c) — the hash ignores the line anyway.
   - **V demu běží nad fixtures v `demo_data/`** (`daily_steps.json`, `activities.json` ve tvaru
     odpovědí Garmin Connect API, fiktivní data 2025-10-01 – 2026-09-30, generuje je
     `demo_data/_generate.py`); stačí stdlib, nic se nevolá po síti. Pro reálná data složku
     `demo_data/` smaž, nainstaluj `pip install garminconnect` a jednou se přihlas přes
     `python .claude/skills/garmin-aktivita/garmin_login.py` (tokeny se uloží do `~/.garminconnect`).
     Vynutit demo jde i proměnnou `DEMO_MODE=1`.
   - **Every level (week/month/year):** put the printed period line as the **last bullet of
     `## Kondice a zdraví`** (create the category if it is otherwise empty):
     `- ⌚ Garmin: 62 340 kroků (Ø 8 906/den, 10k+ 3/7) · Běh 3× 1:45 h (18,2 km) · Posilovna 2× 1:30 h`.
     For month/year compute it directly from the API for the whole range (`--summary`) — don't sum
     the weekly lines by hand.
   - The `⌚ Garmin:` bullets in daily notes are **data, not events**: never regroup or paraphrase
     them into other categories, and don't carry a day's Garmin line into the weekly summary — the
     period line replaces them. Real sport bullets the user wrote themselves (`beh s Radkem 14 km`)
     stay as they are.
   - If the script fails on auth, tell the user to run `garmin_login.py` in their own terminal and
     continue without Garmin data (mention it in the report); never ask for the password.

2c. **Blog — zobrazení z Plausible (always, week/month/year).** Total pageviews of the blog
   and the top 5 articles by pageviews for the period, from the `plausible-blog` skill
   (API key in `~/.plausible/config.json`):
   ```
   python .claude/skills/plausible-blog/plausible_stats.py summary START END
   ```
   - It prints a ready block. Put it as the **last bullet of `## Práce`** (the blog is Práce),
     unchanged; create the category if it is otherwise empty:
     ```
     - 📈 Blog: 5 432 zobrazení
         - [[Spring Modulith v praxi]] 325
         - [[Virtual Threads bez magie]] 210
     ```
     Total = the whole site (homepage, tags… included); the top list = articles only (pages that
     have a note in `Oblasti/Blog/Blog Articles/`), linked to that note.
   - For month/year query the whole range directly. Don't sum the weekly blocks by hand.
   - Empty output means there's no data for the period (e.g. before Plausible was set up). Leave the block out.
   - This is **data, not an event**: never regroup or paraphrase it, and don't count its child
     bullets towards the "3+ bullets → subcategory" rule.
   - If the script fails (missing/invalid API key, network), continue without it and mention it in
     the report; never ask for the key in chat.

2d. **Detail scale — detail falls as the period widens.** Each level *summarises* the one below, it doesn't copy it; the detail stays one click away via the `↓` links and project notes. Limits (agreed 10/2026):

   | Level | AI shrnutí | Bullets | Nesting | Links | Total |
   |---|---|---|---|---|---|
   | **Day** | – | everything, as written | any | any | no limit |
   | **Week** | 3–5 sentences | every event, 1–2 lines, numbers OK | max 1 level | inline, freely | ~60 lines |
   | **Month** | 2–3 sentences | max ~6 per category, result not steps, 1 line each | grouping only, no detail under it | 1 main link per topic (project, race, trip) | ~40–50 lines |
   | **Year** | 3–5 sentences | max ~5 per category, milestones only | none | hub notes only | ~40–50 lines |

   - **Week:** keep every event, but drop technical internals (PR numbers, config, test lists, file names, script fixes) — the project note has them. One topic with many days of work = one bullet with a few short sub-bullets.
   - **Week → month:** drop intermediate steps (zaplaceno, zarezervováno, vyzvednuto, odesláno), partial amounts, dates of individual sessions, technical detail. A topic collapses into its outcome: `Java Pivo Praha — 1. meetup, 34 lidí`, not 15 sub-bullets. Small sport/purchase lists collapse to one line (`Běh 5×, bouldering 3×` — the Garmin line has the numbers).
   - **Month → year:** only what still matters after a year — milestones, races, trips, certifications, big purchases, project starts/ends.
   - **Test per bullet:** month = *"Will I care about this in a year?"*; year = *"Would I mention it when telling someone about my year?"*
   - Data blocks (`⌚ Garmin:`, `📈 Blog:`), `## Hlavní události` and the inbox line don't count towards the limits and keep their own format.

3. **Regroup bullets by category.** Keep the meaning of what you carry up, in the user's wording where possible, but compress to the detail level of step 2d — at week level close to a reorganization, at month/year a real summary. Everything you leave out or merge goes into the report (step 9). **Categories = the user's life roles** — the point of the log is to record what worthwhile thing the user did/contributed in each role. Categorise experiences by **which role the user was in** (i.e. who they were with), not by activity type. In this order:
   - **Práce** — the professional. Job, career, team, meetings, office, conferences, courses, certifications, **blog**, and **IT community / teaching** (meetups like Java Pivo Praha, mentoring, talks) — plus **all technical self-development** (programming, dev tooling, building Claude skills). All work and technical growth lives here.
   - **Lucie** — Activities and topics related to Lucie (partner): time together, trips, meals, cinema, theatre, things bought/arranged for her, anniversaries, relationship admin. Anything "s Lucií" is Lucie — a joint errand, meal, trip, cinema — because the point is *which relationship the user was in*. **Exception: sport/fitness and anything medical always go to Kondice a zdraví, even done with Lucie** — a joint run or bike ride is Kondice, not Lucie.
   - **Rodina a přátelé** — own family (máma, táta, babička, sister Alena with Martin and Kryštof) and friends (Radek, Hana a Filip…). Includes **deskovky** (board games) and social hangouts, meals, and trips with them. **Exception: a sport/fitness activity with friends goes to Kondice a zdraví, not here** — e.g. a race or a long run with Radek.
   - **Kondice a zdraví** — body & health: sport, running, cycling, bouldering, races, fitness **and** medical (doctors, dentist, checkups, meds, **vaccinations**). **Sport/fitness and medical always land here regardless of who the user was with** — a bike ride with Lucie, an OCR race with friends, a checkup: all Kondice a zdraví, never Lucie or Rodina a přátelé.
   - **Osobní růst** — **non-technical** personal development: non-tech reading, non-IT courses, languages, habits/systems (GTD…), personal growth. Technical learning belongs to **Práce**, not here.
   - **Radost** — hobbies & mental wellbeing: things done purely for enjoyment or to feel good. Personal hobbies (film photography, vinyl collection), films and series watched solo, cooking for fun, gaming, relaxation / mental self-care. Boundary: **Osobní růst** = *improving myself*; **Radost** = *enjoying myself / feeling well*. (Medical stays in **Kondice a zdraví**.) A solo hobby is Radost; a hobby that's really social — e.g. board games with friends — stays **Rodina a přátelé**.
   - **Domácnost** — Home & apartment (furniture, renovation, cleaning, organising), the cat, auto, possessions & purchases, shopping, errands, chores.
   - **Administrativa** — Documents, taxes, insurance, financial records, admin (passport, STK…). Includes `pocket wipe` (read-later list) — but only in weekly summaries, per the propagation rule above.
   - **Memories** — Digitalization, photo archiving, personal archives, diary entries, document scanning.
   - **No separate seasonal categories.** Recurring seasonal themes are **subcategories** inside their role (see below), never top-level: **Výročí → Lucie**, **Vánoce → Lucie / Rodina a přátelé**, **Dovolená → by companion**, **Závody → Kondice a zdraví**.
   - Omit any category that ends up empty. Category order: **Práce, Lucie, Rodina a přátelé, Kondice a zdraví, Osobní růst, Radost, Domácnost, Administrativa, Memories**.
   - Merge obvious duplicates/continuations across days into one bullet where it reads better, but keep distinct events separate.
   - **No links to tasks (all levels: week, month, year).** Daily notes often link TaskNotes (notes in `Tasks/` or `Archiv/Tasks/`, e.g. `([[Vratit router]])`, `→ [[Opravit mrtve odkazy na blogu]]`, `task [[Research bezeckych bot]]`). Drop those links when carrying a bullet into a summary. Keep the fact itself in plain words if it matters (`router vrátit poštou`), and remove leftover glue such as empty `()`, `→`, `task`/`tasky`. A bullet whose whole content is "vytvořen task X" is a mezikrok → drop it. Links to projects, areas, people, races, media and reference notes **stay**. If unsure whether a link is a task, check whether the note exists under `Tasks/` or `Archiv/Tasks/`.
   - **Links go inline, into the text itself.** Where it makes sense, the words that name the thing become the link, using an alias when the note title doesn't fit the sentence: `S Lucií do [[Lisabon 2026|Lisabonu]] — Alfama, Belém, Sintra`, `S Radkem na [[Bahenni liska 2026|Bahenní lišce]] — 8 km, 25 překážek`, `[[JOpenSpace 2026 - Prezentace - osnova|Osnova prezentace]] (…)`. **Don't** append the link after the text, in parentheses or behind a dash or arrow: `JOpenSpace 2026 ([[JOpenSpace 2026]])`, `… – [[Preventivka 2026]]`, `→ [[Java Pivo Praha - 2026-09 sraz]]`. The alias doesn't have to be the full note name, just the natural words of the sentence (and with diacritics: `[[Vinylova sbirka|Vinylová sbírka]]`). Rewrite the bullet slightly if needed so that some word carries the link; keep a parenthetical link only when nothing in the sentence names the target (e.g. `([[Vltavsky pulmaraton 2026 - vysledky|výsledky]])`). Daily notes often have the appended style, so convert it when carrying bullets up. The generated `📈 Blog:` block and the nav block are exceptions and stay as they are.
   - **Group repeated items into a subcategory.** When a role has **3+ bullets of the same theme** (e.g. deskovky, kino, dovolená, konference, nákupy oblečení), collect them under a **parent bullet** (the theme name) with the items as **indented child bullets**. Fewer than 3 → leave them as flat bullets. Subcategories are emergent (whatever repeats), not a fixed list. This applies mainly to **weekly** summaries. In **monthly/yearly** summaries, merge repeated items into **one line** instead (`Běh 12× (neděle s Radkem), bouldering 4×`, `Kino — Duna 2, Perfect Days, …`, `deskovky — Wingspan ×3 s Hanou a Filipem, Root ×2 s Radkem`). Keep a parent bullet with children there only when each child is a distinct significant event that would otherwise need its own bullet. Example (week):
     ```
     - deskovky
         - s Hanou a Filipem [[Wingspan]] ×2
         - s Radkem [[Root]]
         - s Lucií [[Patchwork]]
     ```
   - **Within each category, order bullets by importance — most important first, least important last.** Weigh milestones, big purchases, and meaningful events over routine chores; grouped subcategory clusters (hobbies/routine) usually sit lower. Order items inside a subcategory by importance too. (Category order itself stays fixed per the list above.)

4. **Write the AI summary** at the very top under an `## AI shrnutí` heading, in **Czech**. Cover the period's highlights and themes within the sentence budget of step 2d (week 3–5, month 2–3, year 3–5) — it is the shortest view of the period, not a list of everything. Keep it **very terse and plain**: no flowery phrasing, no adjectives-for-effect, no scene-setting ("ve znamení…", "spousta…"). Short, factual, matter-of-fact sentences. Prefer density over prose; think shorthand notes, not a narrative.

4b. **Add a `## Hlavní události` section** right after the AI summary (before the categories) — **required for yearly and monthly** summaries, **skipped for weekly**. A short bulleted list of the period's **major life events** — deaths, births, wedding/engagement, moving, job change, big trips, health milestones, and similar turning points. Pull them from across the categories; it's a highlight reel, not a new category (the events also stay in their normal category). Keep it to a handful of genuinely significant items (a month usually has 3–7, a year 2–6). A quiet month with nothing notable may omit the section entirely.

   **These two sections feed the MOC.** `## AI shrnutí` and `## Hlavní události` are what `build_moc.py` (step 8) lifts into `Carpe Diem/Carpe Diem.md`, so keep their headings spelled exactly like this, keep the AI summary a **single paragraph** (the generator takes the first paragraph only), and keep events as flat `- ` bullets (no nesting — nested lines are dropped).

5. **Assemble and write the note** to the correct path (create the `Weekly/` folder if needed).

5a. **For weekly/monthly summaries: add inbox stats.** Before writing, calculate the inbox/clippings flow for the period using:
   ```
   python .claude/skills/carpe-summary/inbox_stats.py YYYY-MM-DD (start date)
   python .claude/skills/carpe-summary/inbox_stats.py YYYY-MM-DD (end date)
   ```
   Then add a single line at the very end of the note body, after all categories:
   ```
   ---
   Inbox flow (week/month): START→END (delta) | Clippings: START→END (delta)
   ```
   Example: `Inbox flow (week): 48→41 (-7) | Clippings: 12→15 (+3)`
   - Shows net processing/accumulation during the period
   - Skip this for yearly summaries (too much time spans)
   - Skip if the user doesn't ask for tracking

5b. **Structure** (with optional inbox stats for weekly/monthly):

```markdown
# 2026-W27 (Po 29.6. – Ne 5.7. 2026)

## AI shrnutí
<2–5 vět>

## Práce
- ...
- 📈 Blog: 5 432 zobrazení
    - [[Spring Modulith v praxi]] 325
    - ...

## Lucie
- ...

## Rodina a přátelé
- <important standalone bullet>
- deskovky
    - ...
    - ...
    - ...

## Kondice a zdraví
- ...
- ⌚ Garmin: 62 340 kroků (Ø 8 906/den, 10k+ 3/7) · Běh 3× 1:45 h (18,2 km) · Posilovna 2× 1:30 h

## Osobní růst
- ...

## Radost
- ...

## Domácnost
- ...

---
Inbox flow (week): 48→41 (-7) | Clippings: 12→15 (+3)
```

   Adjust the H1 for month (`# 2026-06 (červen 2026)`) and year (`# 2026`). For a **month**, keep the inbox stats line; for a **year**, omit it. For a **year**, put `## Hlavní události` between the AI summary and the first category (per step 4b):

```markdown
# 2026

## AI shrnutí
<terse>

## Hlavní události
- <major life event>
- ...

## Práce
- ...
```

6. **Keep the daily notes** — never delete or move source notes. The summary is purely additive.

6a. **Add inbox/clippings stats to daily notes (optional).** Use the git-based `inbox_stats.py` script to log how many files flowed through `__INBOX/` and `__INBOX/_Clippings/` on each day in the period:
   ```
   python .claude/skills/carpe-summary/inbox_stats.py YYYY-MM-DD
   ```
   This returns a line like: `Inbox: 12→10 (-2) | Clippings: 5→3 (-2)`
   - Start count → End count (delta)
   - Uses git history, so it works for any past date
   - Optional: add this stat line to the daily note (e.g., at the end after all bullets) for productivity tracking
   - Only do this if the user specifically asks for it or if it's part of your workflow

5c. **Stamp the new weekly summary.** Right after writing a **week** summary run:
   ```
   python .claude/skills/carpe-summary/check_late_edits.py --stamp YYYY-Www
   ```
   This writes the `carpe_src` hash stamp into the summary's frontmatter (creating the
   frontmatter block if the note has none) that step 1b uses next time to detect bullets added
   to the daily notes after the summary was written. Weekly summaries therefore start with a
   `---` frontmatter block followed by the H1 — that is expected, keep it.
   Re-run it whenever you later edit a summary because of merged late edits.

6b. **Mark today's daily note with the `xjs` meta-bullet.** (`xjs` is just the marker's name; it means "souhrn vygenerován".) Add a single line to **today's daily note** to log that this summary was generated:
   - **For a week summary:** add `- xjs week` to today's note
   - **For a month summary:** add `- xjs month` to today's note
   - **For a year summary:** add `- xjs year` to today's note
   
   This marker:
   - Lives **only in the day's note where the summary was generated** (not in all days of the period)
   - Serves as a record: "on this day I created a summary for [period]"
   - Is automatically filtered out (per step 2) when the daily note is read as source for a higher-level summary
   - Should be added as a **new bullet at the end of today's existing bullets**
   
   Use the Edit tool to append the line to today's daily note.

7. **Rebuild navigation links.** After marking the daily notes, run:
   ```
   python .claude/skills/carpe-summary/link_carpe.py --all
   ```
   This (re)builds the prev/next + up/down navigation block on every daily note and every summary. It links the new summary into its neighbours and parents, and **backfills the up-links into its child notes** — e.g. finishing a week adds the `↑ week` link to that week's days; finishing a month adds `↑ month` to its weeks. Idempotent and fast (~1 s over the whole archive).
   - The block is the arrow line(s) (`←`/`→` prev/next, `↑` up to week/month/year, `↓` down to children) placed at the **top of a daily note** and **directly under the H1 of a summary**. It carries no comment markers — the script finds it by the leading arrow. **Never hand-edit or duplicate it**; just re-run the script.
   - Scope options: `--all` (whole archive, the safe default) or explicit file paths for a targeted refresh.

8. **Rebuild the MOC.** After the links, run:
   ```
   python .claude/skills/carpe-summary/build_moc.py
   ```
   This regenerates `Carpe Diem/Carpe Diem.md`, the journal's rozcestník:
   - **`# Carpe Diem` and nothing else above the first `## `** — the note deliberately has **no intro prose**; it opens straight into the rozcestník. That zone is hand-editable and preserved verbatim, so don't "helpfully" write an explanation into it, and don't reintroduce one in `DEFAULT_INTRO`.
   - **`## Rychlý rozcestník`** — one line per year (newest first), on it just the month links (`01`…`12`) and nothing else, then a `---` rule. Year lines follow each other with **no blank line between them** (the vault has Obsidian's *strict line breaks* off, so each line wraps on its own);
   - below the rule the same archive again, **reverse chronological with detail decreasing with age**:
     - **current (in-progress) year** — one `###` block per month, newest first, each with its week links (or day links for a month that has no weekly summaries yet) and that month's `## Hlavní události`;
     - **last 3 closed years** (`RECENT_YEARS` in the script) — `## [[YYYY]]` section with the year's AI summary, its `Hlavní události` and month links;
     - **older years** — collapsible bullet per year with just its `Hlavní události`.

   Year links are **bold** (`**[[2025]]**`). That only looks right because of the `bold-links` CSS snippet: AnuPpuccin colours `.cm-strong` in Live Preview and that rule outranks the link colour, so without the snippet a bold link renders in plain text colour while a link in a heading gets the accent colour. **If bold links ever look like plain text, the snippet is missing or disabled** — check `.obsidian/snippets/bold-links.css` and `enabledCssSnippets` in `.obsidian/appearance.json`; don't "fix" it by stripping the bold from the generator.

   Everything below the first `## ` heading is generated; the zone above it is hand-editable and preserved across runs. The script is idempotent, derives everything from the summaries, and **holds no information of its own** — so run it after *any* summary is written or edited (a new week changes nothing there, a new month or year changes a whole section). Never hand-edit the generated part; fix the source summary and re-run.
   - Links to a year note are emitted only if that note exists, so an in-progress year without `YYYY.md` shows as plain text instead of an unresolved link.
   - **If the note is open in Obsidian, its editor buffer can overwrite the freshly written file.** After running, verify the output (`--print` renders the expected content without writing); if the note on disk differs, close the tab and re-run.

9. **Report** to the user which file was written, the range it covers and its length (lines). Then always add a short **"Co jsem vynechal / sloučil"** section, so the user can spot anything that should have stayed:
   - **Vynecháno** — dropped items, grouped by reason (rutina, mezikroky, technické detaily, task odkazy, mimo období…), each item named briefly (`ostříhání`, `vyzvednutí balíku`, `PR #130 detaily`), not just counted.
   - **Sloučeno** — what was merged into one bullet (`5 běhů → „Běh 5×"`, `JOpenSpace příprava 8 bodů → 1 řádek`).
   - **Přesunuto** — items placed in a different category than the source had (with the reason).
   - Keep it compact (a few lines per group). If nothing was dropped, say so. Offer to put any item back.

10. **Completeness check (always after batch/backfill work, cheap enough to run every time).** Run:
   ```
   python .claude/skills/carpe-summary/check_gaps.py
   ```
   Lists every week/month/year that has daily notes but no summary note (current in-progress period excluded). Batch backfills can silently skip a week — this check is what catches that. If gaps are reported, tell the user and offer to generate them.

   For a deeper structural check (misplaced notes, duplicates, broken nav blocks), the `verifikace-vaultu` skill runs `verify_carpe.py` on top of this.

## MOC-only refresh

If the user just wants the rozcestník updated (no new summary), skip steps 1–6 and run only steps 7 and 8. If the MOC looks stale or wrong, the cause is almost always a source summary missing its `## AI shrnutí` / `## Hlavní události` section (older notes predate the convention) — fix or add it there, then re-run. Older summaries may be **backfilled** with those two sections on request, but never rewrite their content otherwise (see *Historical categories*).

## Known people (for consistent categorisation)

Use these to place recurring names in the right role (people notes live in `Lide/`):

- **Lucie** — partner → **Lucie**.
- **Own family** (→ Rodina a přátelé): máma (Jana) and táta (Petr) in Hradec Králové (chalupa in Orlické hory); **babička Věra**; sister **Alena** (Brno) with husband **Martin** and son **Kryštof**.
- **Friends** (→ Rodina a přátelé): **Radek** (Šimek), **Hana a Filip** (Novotní — deskovky every other Friday).
- **Work** (→ Práce): **Adam** (Beneš, CTO, 1:1 every other Monday), **Zuzana** (Dvořáková, QA lead), junior **Šimon**.
- **Ivo** — bouldering coach → **Kondice a zdraví**.
- **Bublina** — the cat, not a person; vet visits and cat supplies → **Domácnost**.
- Recurring activities: **Java Pivo Praha** (meetup the user co-organises), talks, blog, conferences (Czech Java Days, JOpenSpace) → **Práce**; **deskovky** (board games) → **Rodina a přátelé**; running/bouldering/cycling/races (Brdská dvacítka, Vltavský půlmaraton, Bahenní liška) → **Kondice a zdraví** (always, even with Lucie or friends); film photography, vinyls, solo films/series → **Radost**.

## Historical categories (older notes — read-only mapping)

The role categories above are the **current** system. If the vault holds **older aggregation notes with different category names** (e.g. imported from an earlier journaling system), a straddling period will mix both. **Never rewrite historical notes.** But when you *read* an old summary as source for a new aggregation, map its old headings into the current roles so the output is consistent, for example:

- Sociální / Socializing → **Rodina a přátelé**; any meetup/community part → **Práce**
- Community, Blog, Škola → **Práce**
- Sport / Zdraví → **Kondice a zdraví**
- Byt / Bydlení / Majetek → **Domácnost**; Finance / Úkoly → **Administrativa**
- Kino / Divadlo / Koncerty → by companion (**Lucie** if with her, **Rodina a přátelé** with others, **Radost** solo)
- Dárky → by recipient (**Lucie** for her, **Rodina a přátelé** for family)

## Notes

- **Garmin line format:** steps with thin-space thousands (`11 575 kroků`), `10k+ N/M` = days with ≥ 10 000 steps out of days with data (fixed goal, not Garmin's adaptive one), activities as `Typ 45 min` / `Typ 1:33 h`, distance sports with `(2,9 km)` (swimming in metres); in period lines `Typ N× total (km)`. Keep the `⌚ Garmin:` prefix exactly — scripts key on it.
- **Blog block format:** `📈 Blog: N zobrazení` + up to 5 indented `[[Article]] N` bullets, thin-space thousands. Keep the `📈 Blog:` prefix exactly — it marks the generated data block.
- Write output in **Czech**, preserving the user's wording and casual style. Don't "correct" or formalize their phrasing.
- **Neuváděj částky u dárků** (daných ani dostaných) — piš `poukaz na kurz keramiky`, ne `poukaz 1500 Kč na kurz keramiky`. U darů na charitu a u smluv (pojištění, předplatné) částky naopak **ponech** — tam nesou informaci.
- If the user asks for a month or year but the underlying weekly/monthly summaries don't exist yet, offer to build them bottom-up (weeks → month → year) or fall back to aggregating daily notes directly.
