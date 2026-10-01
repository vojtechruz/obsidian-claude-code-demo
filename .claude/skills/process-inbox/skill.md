---
name: process-inbox
description: Zpracuje a roztřídí __INBOX — přesune podcasty z _Clippings do _Podcasts, smaže duplicitní clippings, navrhne co s actionable položkami (blog ideas, tasky, nákupy, místa do Kam, atd.) a čistou konzumaci obsahu (články, videa bez další akce) roztřídí do _Articles / _Videos. Use when the user asks to process/clean/sort the inbox or clippings — "zpracuj inbox", "process inbox", "ukliď inbox", "roztřiď clippings", "projdi inbox", "inbox cleanup".
---

# Process Inbox

Zpracování `__INBOX/` ve třech krocích: (1) podcasty pryč z clippings, (2) smazat duplicity, (3) navrhnout akce pro zbytek — včetně toho, co je jen ke čtení/shlédnutí. Kroky 1–2 proveď rovnou; krok 3 je **jen návrh** — nic nepřesouvej ani nevytvářej bez odsouhlasení uživatelem.

Cíl: `_Clippings` je **fronta netříděného**. Po zpracování v něm nemá nic zůstat ležet — vše je buď převedeno na akci (a smazáno), nebo roztříděno do `_Podcasts` / `_Articles` / `_Videos`.

## Struktura inboxu

- `__INBOX/_Clippings/` — web clippings čekající na roztřídění (Obsidian Web Clipper; frontmatter `title`, `source`, `description`, `created`, tag `clippings`). Plugin Read It Later sem ukládá taky.
- `__INBOX/_Podcasts/` — podcastové epizody k poslechu (cíl kroku 1)
- `__INBOX/_Articles/` — články ke čtení, čistá konzumace bez další akce (eseje, názorové texty, konferenční reporty, recenze…)
- `__INBOX/_Videos/` — videa ke shlédnutí, čistá konzumace bez další akce (dokumenty, záznamy konferencí…)
- `__INBOX/*.md` — volné poznámky čekající na zařazení
- `__INBOX/Attachments/` — přílohy, neřešit

## Krok 1 — Podcasty do _Podcasts

Projdi `__INBOX/_Clippings/*.md` a přesuň do `__INBOX/_Podcasts/` soubory, které **jsou záznamem podcastové epizody**:

- název obsahuje `Podcast`, `Episode`, vzor `S5E19` apod., NEBO
- `source` URL je podcastová (`infoq.com/podcasts/`, `podcasts.apple.com`, `spotify.com/episode`, `buzzsprout`, …), NEBO
- description se identifikuje jako podcast ("this podcast is…")

**Pozor na falešné pozitivy:** konferenční reporty a blogposty, které podcast jen *zmiňují* (např. "we also recorded a podcast about it"), a video dokumenty (dokument o historii Javy na YouTube) podcasty NEJSOU — při pochybnosti otevři soubor a rozhodni podle `source` a obsahu, ne podle grep matche.

Články a videa se v kroku 1 **nepřesouvají** — viz krok 3.

## Krok 2 — Duplicitní clippings

Kandidáti: dvojice `Název.md` + `Název 1.md` (vzniká opakovaným clipnutím). **Nikdy nemaž jen podle názvu** — vždy porovnej:

1. `source` URL (ignoruj utm parametry) — musí být stejná stránka
2. tělo poznámky (`diff`) — rozdíl smí být jen ve frontmatter `created`/`published` a v doplněných komentářích

Pravá duplicita → smaž novější kopii (tu se suffixem). Různý obsah → **ponechat obě** a přejmenovat tak, aby se lišily popisně (např. dva různé LinkedIn posty téhož autora → doplnit téma do názvu). Typický případ: `Post by <autor> on LinkedIn.md` a `... 1.md` vypadají jako duplicita, ale jsou to dva různé posty téhož autora (např. Testcontainers vs. Kafka retry) → přejmenovat podle tématu.

Duplicity kontroluj i napříč `_Clippings` ↔ `_Articles` / `_Videos` / `_Podcasts` (stejná `source` URL).

## Krok 3 — Návrh akcí

Projdi zbylé položky v `__INBOX/*.md` a `__INBOX/_Clippings/*.md` (stačí title + description + rychlý pohled do obsahu) a roztřiď je do kategorií. Výstup prezentuj jako přehled seskupený podle navrhované akce, u každé položky 1 řádek se zdůvodněním. **Čekej na potvrzení, pak proveď jen odsouhlasené.**

Cílové destinace:

| Kategorie | Akce |
|---|---|
| **Nápad na článek** (téma, o kterém by mohl psát; série Spring Modulith, testování, Java/Spring novinky) | **nejdřív zkontrolovat existující ideje v `Oblasti/Blog/Blog Ideas/`** — pokud se položka vztahuje k už existující idei, přilinkovat ji tam jako zdroj/podklad místo vytváření nové; jen jinak vytvořit novou přes skill `blog-idea` |
| **Úkol** (něco udělat, vyzkoušet, ověřit, zařídit) | vytvořit task v `Tasks/` — TaskNotes frontmatter: `status: To Do`, `priority` (dnes/tyden/mesic/pozdeji), `tags: [task]`, případně `oblast` |
| **Nákup** (věc ke koupi someday) | nová poznámka v `Oblasti/Domov/Nakupy/` — frontmatter `Priority`, `Description`, `Link`, `Category`, `Can be present` (deskovky → `Deskovky Wishlist` v `Oblasti/Rodina a Pratele/Deskovky/`; věc, která se hodí jako dárek, zvaž i jako nápad v `Napady na darky`) |
| **Místo / akce k navštívení** | přidat do `__INBOX/Kam.md` do odpovídající sekce |
| **Referenční materiál k tématu** (běh, lezení, deskovky, vaření, …) | přesunout do příslušné složky v `Znalosti/` či `Oblasti/` |
| **Článek ke čtení, žádná další akce** | přesunout do `__INBOX/_Articles/` |
| **Video ke shlédnutí, žádná další akce** | přesunout do `__INBOX/_Videos/` |
| **Mrtvé / už nerelevantní** | navrhnout smazání |

Pro tohoto uživatele typicky: Spring / Java / testování / Kafka clippings jsou často **podklad pro blog** (píše sérii o Spring Modulith — viz projekt `Spring Modulith serie`); kurzy a certifikace bývají **tasky nebo Osobní růst**; konferenční reporty, eseje a dokumenty jsou typicky **`_Articles` / `_Videos`** (nebo smazat).

### Články a videa — typ obsahu nerozhoduje

`_Articles` a `_Videos` jsou jen pro **čistou konzumaci** — zajímavé, ale nic se z toho nemá dělat. **Formát (YouTube URL, blogpost) sám o sobě o zařazení nerozhoduje:** video tutoriál, tech talk nebo webinář o konkrétní technologii je velmi často **podklad pro blog ideu** (nebo task „vyzkoušet X“), ne položka do `_Videos`. Stejně tak technický článek o nástroji/featuře, ke které existuje blog idea.

- Jasná konzumace (dokument, esej, názorový text, konferenční report, recenze hry, sbírka talků bez konkrétního tématu) → `_Articles` / `_Videos`.
- Tutoriál / tech talk / technický článek → nejdřív porovnat s `Oblasti/Blog/Blog Ideas/` a tasky.
- **Při nejasnosti se zeptej** — uveď položku, obě možnosti (např. „`_Videos`, nebo zdroj k idei *Testcontainers v praxi*?“) a nech rozhodnout uživatele. Nehádej.
- Posty na X/LinkedIn bez obsahu v clippingu (jen embed) — obsah nevidíš, vždy se zeptej.

## Vždy porovnat s existujícími blog ideas

Při každém zpracování inboxu **aktivně projdi zbývající clippings proti existujícím idejím** v `Oblasti/Blog/Blog Ideas/` (stačí porovnat názvy + témata). Clipping, který pasuje k existující idei, do ní přidej jako zdroj — markdown odkaz s krátkou anotací pod komentář `%%from _Clippings%%` (zavedená konvence v idea poznámkách) — a clipping smaž. To platí i pro položky, které by jinak šly do `_Articles` / `_Videos`. Teprve když téma žádné idei neodpovídá, zvaž novou ideu přes `blog-idea`.

Stejnou kontrolu občas proveď i nad obsahem `_Articles` a `_Videos` (mezitím mohly vzniknout nové ideje) — shody navrhni uživateli.

## Zpracované položky se mažou

Jakmile je clipping zpracován (vytvořen task, blog idea, položka v Nákupech, přesunut obsah do reference…), **clipping se smaže** — nezůstává ležet. Před smazáním přenes do cílové poznámky vše podstatné: **přímou URL ze `source`/`URL` frontmatteru** a stručnou podstatu obsahu. V cílové poznámce nikdy neodkazuj wikilinkem na clipping (po smazání by byl rozbitý) — vždy použij původní URL.

Totéž platí pro `_Articles` / `_Videos` / `_Podcasts`: po přečtení/shlédnutí/poslechu se položka maže; pokud z ní něco vzešlo (poznatek do `Znalosti/`, blog idea), nejdřív přenést URL a podstatu.

## Reportování

Na konci shrň: kolik podcastů přesunuto, kolik duplicit smazáno (a kterých), návrhová tabulka pro krok 3 (včetně navržených přesunů do `_Articles` / `_Videos` a samostatného seznamu **nejasných položek s otázkou**). Po odsouhlasení proveď schválené akce a vypiš, co se kam přesunulo/vytvořilo.
