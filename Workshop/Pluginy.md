# Pluginy

Pluginy jsou součástí repa (`.obsidian/plugins/`). Po otevření vaultu stačí kliknout na *Trust author and enable plugins*.

## Core (vestavěné)

| Plugin | K čemu tu je | Kde to vidět |
| --- | --- | --- |
| **Bases** | Tabulkové a kartové pohledy nad poznámkami podle frontmatteru, bez psaní kódu. | `System/Bases/*.base`, vložené v poznámkách oblastí a projektů, `Media/Media.base`, `Deskovky.base`, `Lide/Lide.md` |
| **Daily notes** + **Templates** | Denní poznámka v `Carpe Diem/YYYY/YYYY-MM/`. | kalendářová ikona, šablona `System/Templates/Daily note.md` |
| **Properties** | Frontmatter jako formulář. | libovolný task nebo osoba |

## Komunitní

| Plugin | K čemu tu je | Kde to vidět |
| --- | --- | --- |
| **TaskNotes** | Task je samostatná poznámka s frontmatterem (`status`, `priority`, `scheduled`, `due`, `recurrence`). Nabízí pohledy kanban, kalendář, agenda a seznam. | `Tasks/`, `System/TaskNotes/Views/`, příkazový panel „TaskNotes: Open …“ |
| **Templater** | Šablony se skriptem. Denní poznámka si sama vygeneruje navigaci ← → ↑. | `System/Templates/Daily note.md` |
| **QuickAdd** | Rychlé založení oblasti nebo projektu včetně jejich `.base` pohledu. | příkazy „QuickAdd: Add Area / Add Project“ |
| **Folder Notes** | Poznámka se jménem složky slouží jako její „index“, třeba `Workshop/Workshop.md`. | klik na složku |
| **Spaced Repetition** | Kartičky: `Otázka::Odpověď`, `Otázka:::Odpověď`, `==cloze==`. Balíček = tag `#flashcards/<balíček>`. | `Flashcards/`, ikona kartiček vpravo |
| **Omnisearch** | Fulltextové hledání s tolerancí překlepů. | příkazový panel → „Omnisearch: Vault search“ |
| **Tag Wrangler** | Hromadné přejmenování a sloučení tagů. | panel tagů, pravé tlačítko |
| **Read It Later** | Uloží URL ze schránky jako poznámku do `__INBOX/_Clippings`. | příkazový panel → „Read It Later“ |
| **Paste Image Rename** | Vloženým obrázkům dá smysluplná jména. | vložení obrázku |
| **Heading Level Indent** | Odsazení obsahu podle úrovně nadpisu, kvůli čitelnosti. | dlouhé poznámky závodů |
| **Settings Search** | Hledání v nastavení. | Nastavení |
| **Claudian** (realclaudian) | Chat s Claude Code přímo v Obsidianu (postranní panel). | ikona v postranním panelu |

## Konvence, které pluginy využívají

- **Priority tasků:** `dnes` → `tyden` → `mesic` → `pozdeji` → `on-ice`. Pohled „⚡ Dnes“ ukazuje jen `dnes`.
- **Oblasti a projekty** mají frontmatter `tags: [Oblast]` nebo `[Projekt]` a `status`. Tasky na ně odkazují přes `oblast` a `projects`.
- **Lidé:** `narozeniny`, `svatek`, `darky: ano|historie`. Z toho žijí `Lide.base`, `tydenni-plan` i `navrh-darku`.
