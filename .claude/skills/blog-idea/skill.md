---
name: blog-idea
description: Capture a new blog post idea as a note in the vault's Blog Ideas database and immediately run the full AI review on it (overlap, gap value, series fit, angle, learning alignment, blog fit, audience impact, time sensitivity, AI Suggested Priority, AI Expected Effort). Use when the user wants to record an article/blog idea — "pridej blog ideu", "novy napad na clanek", "zapis blog ideu a udelej review", "add a blog idea", "new blog post idea" — or drops a link, selection or topic that should become an idea note. Creates the note in Oblasti/Blog/Blog Ideas with the correct Blog Ideas.base frontmatter and writes the AI Feedback callout.
---

# New blog idea + AI review

Adds **one** idea to the blog idea database of the blog `ondrakodi.example` and reviews it
right away. Every idea gets the same review structure and vocabulary, so a re-review simply
replaces the callout and older and newer notes stay interchangeable.

The whole workflow is filesystem-only: everything it needs lives in the vault — no API
tokens, no blog source repository.

## Data in the vault

```
Oblasti/Blog/Blog Ideas/                 1 note = 1 idea (database view: Blog Ideas.base in the same folder)
Oblasti/Blog/Blog Ideas/Attachments/     images belonging to idea notes
Oblasti/Blog/Blog Articles/              1 note = 1 published article (context for the review)
Oblasti/Blog/Java features/              Java feature topics (JEP chains) — see the `java-features` skill
Oblasti/Osobni rust/Learning Tracker/    learning list (learning alignment signal, optional)
```

### Blog Ideas — note format

Idea note frontmatter (exactly these keys, in this order):

```yaml
---
base: "[[Blog Ideas.base]]"
Star: false
Tags:
  - Java
Priority: Medium
AI Expected Effort: Low
AI Suggested Priority: High
---
```

- `base` — membership in the database; `blog_context.py` and the Base filter on it. Notes
  without it (e.g. a folder note) are ignored.
- `Star` — author's "must write" flag. **Always `false` on a new idea** unless the user
  explicitly stars it.
- `Tags` — topic tags in English (`Java`, `Spring`, `IDEA`, `Security`, `AI`, `Test`,
  `Career`, `Book`, …).
- `Priority` — the *author's* priority: `Very High` / `High` / `Medium` / `Low` /
  `Very Low` / `On Ice`. Never invent it; see step 4.
- `AI Suggested Priority` — same vocabulary, written by this skill.
- `AI Expected Effort` — `Low` / `Medium` / `High`, written by this skill.

Body: the author's notes and source links, optional private remarks in `%%...%%`, and at the
end the `> [!note]+ # AI Feedback` callout (step 6). Ideas that have not been reviewed yet
simply have no callout and no `AI …` keys.

### Blog Ideas.base

`Oblasti/Blog/Blog Ideas/Blog Ideas.base` — one table over all notes whose `base` points to it:

```yaml
filters:
  and:
    - note["base"] == link("Blog Ideas.base")
properties:
  file.name:
    displayName: Name
views:
  - type: table
    name: Table View
    order:
      - file.name
      - Star
      - Tags
      - Priority
      - AI Expected Effort
      - AI Suggested Priority
```

### Blog Articles — note format

One note per published post, title = post title. The skill reads only the frontmatter:

```yaml
---
base: "[[Blog Articles.base]]"
Topics:
  - Spring
Series: Spring Modulith
Date: 2026-05-28
Draft Status: Published
URL: https://ondrakodi.example/spring-modulith-intro/
Excerpt: One-sentence teaser of the post.
Views 6mo: 840
---
```

`Series`, `Excerpt` and `Views 6mo` are optional (`Views 6mo` is used by `java-features`).

### Learning Tracker (optional)

`Oblasti/Osobni rust/Learning Tracker/*.md`, one note per thing to learn, frontmatter
`Category` (only `Development` items are used), `Priority`, `status` (`Done` items are skipped)
and `Tags`. If the folder does not exist, learning alignment is just `none`.

**Blog content is in English** — the note body and the whole review are written in English
even when the user asks in Czech. Reply to the user in the language they used.

## Steps

### 1. Parse the request

Extract from the user's message (and from `<editor_selection>` / `<browser_selection>` /
`<linked_note>` context if present):

- **Title** — a concrete, article-like note title. If the user gave only a URL or a vague
  phrase, derive a clean title (fetch the page with WebFetch if needed) and tell them what
  you chose.
- **Sources** — every URL, quote or note the user provided. These become the note body.
- **Tags** and **Priority** — only if the user stated them.

### 2. Load the blog context

```
python .claude/skills/blog-idea/blog_context.py "<idea title>"
```

Returns JSON: `counts`, `target_path`, `target_exists`, `duplicate_candidates.ideas`,
`duplicate_candidates.articles` (fuzzy title/topic matches, with excerpts and body
previews), `tag_vocabulary`, `series`, `learning_items` (open Development items) and
`articles` (all published posts with topics, date, series, URL).

Add `--full-ideas` when you need every idea title (e.g. the user asks how the new idea sits
against the whole backlog).

### 3. Duplicate check — before writing anything

- `target_exists: true` or a `duplicate_candidates.ideas` entry that is clearly the same
  idea → **do not create a second note.** Tell the user which note exists and offer to
  (a) merge the new sources into it and re-run the review, or (b) create it under a
  different, sharper title. Wait for the answer.
- A `duplicate_candidates.articles` entry that already covers the topic → still create the
  idea if the user wants it, but the review must name that post under **Overlap**.

### 4. Create the note

Path: `Oblasti/Blog/Blog Ideas/<Title>.md`.
Sanitize the filename: replace `\ / : * ? " < > |` with `-`, keep spaces and normal
punctuation (use `Book Review - X`, not `Book Review: X`).

Write the note **first**, before the review, so the capture survives even if the review is
interrupted:

```markdown
---
base: "[[Blog Ideas.base]]"
Star: false
Tags:
  - <tag>
Priority: <author priority>
---

<user's notes, one bullet or paragraph per thought>

<every source as a markdown link on its own line>
```

- **Tags** — reuse the existing vocabulary from `tag_vocabulary`. Only coin a new tag when
  nothing fits, and say so in the final report. Empty list (`Tags: []`) if genuinely nothing
  fits.
- **Priority** — if the user did not state one, use `Medium` and flag in the report that
  this is a placeholder the author should confirm; it is *their* priority, not the AI's.
- Keep the user's own wording and links; do not pad the body with generated prose.
- Author's private remarks belong in `%%...%%` comments, the way existing notes do it.

### 4b. Java feature ideas — link the tracker

If the idea is about a **Java language or API feature** (anything that shipped as a JEP), check
`Oblasti/Blog/Java features/` (Grep the folder for the feature name):

- **Matching topic exists** → add the idea to its `Napady:` list (`  - "[[<idea title>]]"`). That is
  the only cross-note edit this skill makes; the opposite direction is covered by backlinks, so do
  **not** edit the idea note to point at the topic.
- **No topic** → say so in the final report and offer the `java-features` skill to create one.
  Don't create topics here.
- Use the topic's table in the review: which version made the feature final, what is still in
  preview (`Sleduje se`), and whether an existing article already covers part of it (`Clanky`,
  `Pokryto do`). That is better grounded than a web search for "when did X ship".

### 5. Review the idea

Analyse the idea against `articles` (existing coverage), `duplicate_candidates`,
`learning_items` and the tag vocabulary.

**Run a web search** to verify current relevance — never rely on training data alone. Check
when the feature/version shipped, whether it is still new, whether there is recent
community discussion, and whether the window has already passed. For Java features prefer the
tracker data from step 4b (versions there are verified against openjdk.org).

Produce exactly this structure (no title heading — the callout supplies it):

```
**Reviewed:** YYYY-MM-DD HH:MM UTC

**Overlap:** [none / partial — existing post: "Title"]
**Gap value:** [High / Medium / Low] — [one sentence why]
**Series fit:** [none / fits "Series Name"]
**Suggested angle:** [working title or "keep as-is"]

**Learning alignment**
[matching learning item(s) with priority + status, or "none"]

**Blog fit**
[2–4 sentences — how it sits in the existing post history, which posts it synergises with]

**Audience impact**
[2–4 sentences — reach, usefulness, search/sharing potential, who the reader is]

**Time sensitivity:** [Evergreen / Fades slowly / Time-sensitive / Expires soon]
[one sentence — reason + how long the window is and whether it is still open]

**AI Suggested Priority:** [Very High / High / Medium / Low / Very Low / On Ice]
[2–4 sentences — starred?, author priority, gap, overlap, learning alignment, time pressure]

**AI Expected Effort:** [Low / Medium / High]
[2–4 sentences — topic breadth, demos/code needed, series reuse, depth of the sources]

**Concerns:** [bullet list or "none"]
```

Definitions to keep the vocabulary consistent with past reviews:

- **Time sensitivity** — `Evergreen` = just as valuable in 5 years; `Fades slowly` = new
  language/framework features, best when fresh but useful for years; `Time-sensitive` =
  tied to a recent release or trend, value window in months; `Expires soon` = conference
  writeups, news reactions, loses most value within weeks.
- **AI Suggested Priority** — `On Ice` for ideas that are interesting but not ready or
  relevant yet. Bump `Time-sensitive` / `Expires soon` ideas up.
- Use the real current UTC time in the `**Reviewed:**` line (`date -u`).

### 6. Write the feedback into the note

Append the review as an Obsidian callout — every line prefixed with `> `, blank lines as
a bare `>`:

```markdown
> [!note]+ # AI Feedback
> **Reviewed:** 2026-09-30 18:12 UTC
>
> **Overlap:** partial — existing post: "Getting started with Spring Modulith"
> ...
```

- The callout goes at the **end of the note body**, after the sources.
- If a `# AI Feedback` callout already exists (re-review of an existing idea),
  **replace it** — never stack two.
- Then set the two frontmatter keys in the note you just created:
  `AI Expected Effort` and `AI Suggested Priority` (add them below `Priority`).
- Touch nothing else — no other note, no `.base` file, no reordering of existing keys.

### 7. Report

Tell the user (in their language):

- the note path as a wikilink, e.g. `[[Oblasti/Blog/Blog Ideas/Structured Concurrency in Java 25.md]]`
- one line summary: `[AI Suggested Priority] [AI Expected Effort] — Title`
- overlap verdict and the suggested angle
- anything they should confirm: placeholder `Priority`, a newly coined tag, a near-duplicate
  idea note, or a topic already covered by an existing post
- for a Java feature: which tracker topic the idea was linked to, or that no topic exists yet

Never commit to git — offer it only if the user asks.

## Related

- Java feature topics, JEP chains and outdated articles: skill `java-features` ([[Java features]]).
- Re-reviewing an existing idea uses the same steps 2, 5 and 6 on the existing note — the
  callout is replaced, the author's `Priority` and `Star` are left alone.
