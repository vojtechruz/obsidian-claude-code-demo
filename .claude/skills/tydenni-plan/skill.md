---
name: tydenni-plan
description: Naplánuje uživateli příští (nebo aktuální) týden a zapíše plán jako samostatnou poznámku v Carpe Diem/YYYY/Weekly/YYYY-Www-plan.md; vyhodnocení minulého týdne zapíše zvlášť do YYYY-Www-review.md. Use when the user asks to plan the week, "naplánuj týden", "naplánuj mi příští týden", "týdenní plán", "plán na týden", "dashboard týdne", "weekly plan", "plan my week", nebo v neděli/pátek chce udělat týdenní review + plán. Sbírá tasky (TaskNotes), projekty, lidi (svátky/narozeniny), kalendář (MCP `demo-calendar`, jen čtení) a denní poznámky; vyhodnotí, jak se naplnil plán minulého týdne, a výsledek promítne do nového plánu (Big Rocks, kalendář Po–Ne, deadliny, Small Rocks, projekty). Po odsouhlasení zapíše naplánovaným taskům `scheduled:`.
---

# Týdenní plán

Vytvoří plán na jeden ISO týden jako **vlastní poznámku** (`YYYY-Www-plan.md`) a přitom
**vyhodnotí plán minulého týdne** do **samostatné poznámky** (`YYYY-Www-review.md`). Oddělené
jsou záměrně: plán se otevírá denně a má být stručný; review se čte jednou. Vyhodnocení není
jen report – jeho závěry (co se nestihlo, co se opakovaně odsouvá, kolik toho reálně zvládneš)
se **promítnou do nového plánu**.

Jazyk plánu: **čeština**. Styl: stručný, věcný, žádná omáčka (stejně jako `carpe-summary`).

**Big Rocks / Small Rocks.** Tasky týdne se dělí na dva druhy a plán s nimi pracuje odlišně:
- **Big Rocks** (max 3) – větší věci, které definují týden. Plánují se **první** a dostávají
  volné večery/bloky; drobnost nikdy nesmí zabrat slot velkého kamene. Plnění se měří – jsou
  jádrem vyhodnocení.
- **Small Rocks** – drobnosti, které vyplňují mezery kolem velkých kamenů (čekání, mezičasy,
  přetížené večery). Neměří se (aby nemotivovaly plnit drobnosti místo velkých věcí) – co se
  stihne navíc, objeví se ve vyhodnocení jako „hotovo navíc“.

## Zdroje

| Zdroj | Co z něj | Přístup |
| --- | --- | --- |
| `Tasks/*.md` (TaskNotes) | status, priority (`dnes`/`tyden`/`mesic`/`pozdeji`/`on-ice`), `due`, `scheduled`, `projects`, `completedDate` | skript |
| `Projekty/<X>/<X>.md` | `due_date`, `status`, sekce `## Nejbližší kroky` | skript |
| `Lide/*.md` | `svatek`, `narozeniny`, `vyroci_*` (formát `D. M.` nebo `YYYY-MM-DD`). Kdo má vyplněné `umrti` (příp. `zemrel`/`zemrela`), ten se přeskakuje celý. | skript |
| `Carpe Diem/YYYY/YYYY-MM/YYYY-MM-DD.md` | denní poznámky minulého týdne (retrospektiva) | skript |
| `Carpe Diem/YYYY/Weekly/YYYY-Www-plan.md` | předchozí plán – tasky z Top 3 a Kalendáře (co bylo naplánováno) | skript |
| `Carpe Diem/YYYY/Weekly/YYYY-Www-review.md` | poslední vyhodnocení – `## Poučení` k přenesení | skript |
| Kalendář – MCP server `demo-calendar` (**jen čtení**) | události Po–Ne | `mcp__demo-calendar__list_events` |
| `Oblasti/Kondice a Zdravi/Sportovní akce.md` | nadcházející závody + sekce „Pořadatelé“ (jen pro krok 2b) | ručně / skill `zavody-terminy` |

Kalendář: v demo vaultu ho poskytuje lokální MCP server **`demo-calendar`**
(`.claude/mcp/demo-calendar/server.py`, data v `events.json`, registrovaný v `.mcp.json`).
Napodobuje Google Calendar MCP – stejné názvy toolů i parametrů. **V reálném vaultu sem patří
Google Calendar MCP** (např. claude.ai konektor Google Calendar, tool
`mcp__claude_ai_Google_Calendar__list_events`); postup se nemění, jen prefix toolu.

Používej **jen `list_events`** na primárním kalendáři. Nikdy nevytvářej, neměň ani nemaž
události (demo server to ani neumí). Časy z výstupu skriptu (sekce „Kalendář dotaz“) předej
jako `startTime`/`endTime`, `timeZone: Europe/Prague`, `orderBy: startTime`. Celodenní události
mají `start.date` (a `end.date` exkluzivně), časované `start.dateTime`.

## Postup

1. **Urči týden.** Spusť
   ```
   python .claude/skills/tydenni-plan/collect.py            # auto
   python .claude/skills/tydenni-plan/collect.py 2026-W42   # explicitně
   ```
   Auto = **příští** ISO týden, pokud je dnes Pá–Ne, jinak aktuální. Pokud uživatel řekl
   „tento týden“ / „příští týden“ / konkrétní číslo, předej ho explicitně. **Řekni uživateli
   rozsah** („Plánuju W42: Po 12.10. – Ne 18.10.“), ať chytne off-by-one. Když plán pro ten týden
   už existuje (skript to hlásí), zeptej se, zda přepsat, nebo jen aktualizovat.

2. **Načti kalendář** přes `list_events` (`demo-calendar`) s časy ze skriptu. Když MCP selže
   (server neběží / není schválený), pokračuj bez něj a do plánu napiš, že kalendář nebyl dostupný.

2b. **Kontrola závodů (jen občas).** Spusť skill `zavody-terminy` (období = příštích 6 měsíců)
   pouze když platí aspoň jedno:
   - plánovaný týden je **první plán v kalendářním měsíci** (žádný `*-plan.md` pro dřívější
     týden téhož měsíce neexistuje), nebo
   - v `Sportovní akce.md` (sekce Nadcházející závody) není žádný závod
     s datem dál než 6 týdnů od konce plánovaného týdne.
   Jinak krok přeskoč a nic nehlásej. Výsledek kontroly patří do diskuse v kroku 7 (jedna až
   tři věty: nové termíny, kolize s kalendářem); závod k registraci nabídni jako Small Rock
   „Registrovat na X“. Do poznámky plánu se kvůli tomu nic nepřidává. Když weby neodpovídají,
   nezdržuj plánování – napiš to jednou větou a pokračuj.

3. **Vyhodnoť minulý týden** (sekce skriptu „Předchozí plán“, „dokončené tasky“, „propadlo“,
   denní poznámky):
   - Big Rocks z minulého plánu: ✅ splněno / 🔁 rozpracováno / ❌ nesplněno + jedna věta proč
     (z denních poznámek, stavu tasků; pokud není jasné, zeptej se).
   - Naplánované tasky: kolik z kolika hotovo; vypiš nesplněné.
   - Co bylo hotovo navíc (dokončené tasky mimo plán).
   - **Poučení** – 1–3 body, které mění příští plán: např. „plán měl 9 tasků, hotovo 4 →
     plánovat max 5“, „X se odsouvá třetí týden → buď zaplánovat na pevný den, nebo přesunout
     do Someday“, „pátky s deskovkami nepočítat jako pracovní večer“. Poučení z posledního
     review (skript ho cituje v sekci „Poučení z posledního vyhodnocení“) přenes dál, pokud
     stále platí; co už neplatí, vynech.
   - Když předchozí plán neexistuje (první běh), udělej vyhodnocení jen z tasků a denních
     poznámek a poučení odvoď z toho, co propadlo.
   - **Zapiš vyhodnocení jako samostatnou poznámku** `Carpe Diem/YYYY/Weekly/YYYY-Www-review.md`
     pro **minulý** týden (cesta je ve výstupu skriptu, šablona níže). Do plánu jde jen odkaz
     na ni. Když review už existuje, nepřepisuj ho bez dotazu. Zapiš ho hned (nečekej na
     odsouhlasení plánu) – je to záznam minulosti, ne návrh.

4. **Sestav kalendář Po–Ne.** Pro každý den: události z kalendáře (s časem), svátky/narozeniny
   a **jen tasky, které mají `scheduled:` přesně v ten den** (TaskNotes je zdroj pravdy; task
   bez `scheduled` do kalendáře nepatří – due samo o sobě nestačí, to žije v sekci Deadliny).
   Kalendář v plánu tak vždy odpovídá TaskNotes kalendáři. Tasky se **statusem
   `Scheduled`** (rezervovaný pevný termín – sekce „Pevné termíny“ ve výstupu skriptu) jsou
   fixní body jako události z kalendáře – nepřesouvej je a nepočítej je do kapacity; do plánu
   patří i ty mimo tento týden (sekce „Pevné termíny“ pod Čekám na). Označ **přetížené dny**
   (večerní akce + více tasků) a **volné dny** – tam patří větší věci.

5. **Navrhni Big Rocks (max 3).** Vyber z: po termínu → due tento týden → priorita
   `dnes`/`tyden` → projekty s blízkým deadlinem (do 30 dní) bez naplánovaného kroku. Zohledni
   poučení z kroku 3 (kapacita) a kalendář (kolik je reálně volných večerů) – big rocks se
   plánují první, do volných večerů. Big rock může být i něco, co není task (např. „odpočinout
   po dovolené“) – pak to napiš bez odkazu.

6. **Rozlož tasky do dnů.** Nejdřív big rocks na volné večery/bloky, pak deadliny a věci
   vázané na událost ke správnému dni (meetup Java Pivo Praha → připravit slajdy den předem). Zbylé
   drobnosti jsou **Small Rocks** – zásobník na vyplnění mezer, nedávají se do konkrétních dnů.
   **Nepřeplňuj** – radši méně a splnit. Do kalendáře plánu se tasky dostanou **až po zápisu
   `scheduled:`** (krok 9) – dokud uživatel den neodsouhlasí, patří návrh jen do diskuse, ne
   do tabulky.

7. **Ukaž návrh uživateli a diskutuj** (v próze, ne formulářem): big rocks, rozložení do dnů,
   co navrhuješ odložit/zrušit, co urgovat u Waiting. Uprav podle odpovědi.

8. **Zapiš plán** do `Carpe Diem/YYYY/Weekly/YYYY-Www-plan.md` (šablona níže). Cesta a odkazy
   pro nav jsou ve výstupu skriptu. Složka `Weekly/` už existuje. **Předchozí plán nikdy
   nepřepisuj** (kromě předání aliasu, viz níže) – vyhodnocení jde do review poznámky.
   Plán obsahuje **jen budoucnost**.

8b. **Předej alias `Aktualni plan`.** Nový plán dostane ve frontmatteru `aliases: [Aktualni plan]`,
   aby šel najít v quick switcheru a aby `[[Aktualni plan]]` vždy vedl na běžný týden. Skript
   vypíše, které starší plány alias drží (řádek „Alias `Aktualni plan` drží“) – z každého z nich
   alias **odeber** (smaž položku ze seznamu `aliases`; když je seznam prázdný, smaž celý klíč).
   Nic jiného ve starém plánu neměň. Alias smí mít v jednu chvíli právě jeden plán.

9. **Zapiš `scheduled:` do tasků** – pouze u tasků, které uživatel v kroku 7 odsouhlasil na
   konkrétní den, a **pouze po explicitním potvrzení** („zapiš to do tasků?“). Měň jen řádek
   `scheduled:` (formát `YYYY-MM-DD`), nic jiného ve frontmatteru. Nepřidávej `due`, neměň
   `status` ani `priority` (tohle uživatel řídí v TaskNotes). Skript nic nezapisuje – edituj
   soubory přímo.

10. **Nabídni**, ne dělej: `carpe-summary` pro souhrn minulého týdne (pokud chybí), `navrh-darku`
    pro blízké narozeniny/svátky, `process-inbox`, `zavody-terminy` (když krok 2b neběžel a
    uživatel se ptá na závody).
    Když se souhrn minulého týdne generuje v neděli jako součást plánování a uživatel pak do
    nedělní denní poznámky ještě něco dopíše, nic se neztratí: `carpe-summary` má krok 1b
    (`check_late_edits.py`), který při příštím běhu pozdější změny denních poznámek odhalí a
    doplní. Není potřeba to řešit tady.

## Šablona plánu

```markdown
---
tags:
  - tydenni-plan
aliases:
  - Aktualni plan
cssclasses:
  - wide
week: 2026-W42
start: 2026-10-12
end: 2026-10-18
---

# Plán týdne 2026-W42 (Po 12.10. – Ne 18.10. 2026)

Vyhodnocení minulého týdne: [[2026-W41-review]] · předchozí plán: [[2026-W41-plan]] · souhrn týdne: [[2026-W42]] · měsíc: [[2026-10]]

## Big Rocks
1. [[Task]] – proč teď
2. …
3. Odpočinout před půlmaratonem (není task → bez odkazu)

## Kalendář
| Den | Kalendář | Tasky (scheduled) | Pozn. |
| --- | --- | --- | --- |
| Po 12.10. | 9:30 Sprint planning | [[Task]] | |
| Út 13.10. | 7:30 Zubař | — | |
| St 14.10. | 18:00 Lucie – vernisáž | | večer pryč |
| Čt 15.10. | 18:30 Java Pivo Praha | — | večer pryč |
| Pá 16.10. | 19:00 Deskovky u Novotných | [[Task]] | večer pryč |
| So 17.10. | 10:00 Výměna pneumatik | | brzy spát |
| Ne 18.10. | 9:00 Podzimní půlmaraton | | celé dopoledne; plán W43 |

## Pevné termíny (Scheduled)
- Út 27.10. 17:00 – [[Task]] (rezervace; patří sem i termíny za horizontem týdne)

## Deadliny
### Po termínu
- [[Task]] (due 2026-09-20, 22 d) → návrh: přeplánovat na Po / zrušit

### Tento týden
- [[Task]] – due Pá 16.10.

### Projekty do 30 dní
- [[JOpenSpace 2026]] – 23.10. (zbývá 11 d) – další krok: …

## Small Rocks
- [[Task]]
- [[Task]]

## Projekty
| Projekt | Deadline | Zbývá | Otevřené | Tento týden |
| --- | --- | --- | --- | --- |
| [[Podzimni pulmaraton 2026]] | 18.10. | 6 d | 2 | vyzvednout startovní číslo |
| [[Rekonstrukce koupelny]] | — | — | 4 | ⚠️ 35 d bez pohybu – rozhodnout |

## Čekám na
| Task | Od koho | Čeká | Akce |
| --- | --- | --- | --- |
| [[Task]] | Zuzana | 12 d | urgovat Út |
```

Pořadí sekcí je záměrné (denní čtení shora, aktivní nahoře, pasivní dole):
Big Rocks → Kalendář → Pevné termíny → Deadliny → Small Rocks → Projekty → Čekám na.

## Šablona vyhodnocení (`YYYY-Www-review.md`, hodnotí minulý týden)

```markdown
---
tags:
  - tydenni-review
week: 2026-W41
start: 2026-10-05
end: 2026-10-11
---

# Vyhodnocení týdne 2026-W41 (Po 5.10. – Ne 11.10. 2026)

Plán týdne: [[2026-W41-plan]] · souhrn: [[2026-W41]] · další plán: [[2026-W42-plan]]

## Big Rocks
- ✅ [[Task]] – …
- 🔁 [[Task]] – rozpracováno, proč
- ❌ [[Task]] – proč

## Naplánované tasky
- **Hotovo 4/7:** [[Task]], [[Task]], …
- **Nesplněno:** [[Task A]] → přesunuto na Po, [[Task B]] → Someday
- **Hotovo navíc:** [[Task D]], [[Task E]]

## Poučení
- …
- …
```

Pravidla pro poznámky:
- Odkazuj tasky a projekty **wikilinkem na název souboru** (`[[Nazev tasku]]`). Skript příště
  vyhodnocuje plnění podle odkazů v sekcích **Big Rocks** a **Kalendář** plánu – tasky v „Čekám
  na“, „Projekty“ a „Small Rocks“ se nepočítají jako naplánované. Big rock, který není task,
  piš bez odkazu.
- Nadpisy `## Big Rocks` a `## Kalendář` (plán) a `## Poučení` (review) ponech doslovně –
  skript je hledá.
- V tabulce Kalendář je ve sloupci Tasky jen to, co má `scheduled:` v ten den (po odsouhlasení
  zapsané do tasků). Jednorázové ne-taskové akce (popřát, souhrn W+1) piš do sloupce Pozn.
- **TaskNotes vykresluje `[[task]]` jako inline widget** (kolečko, priorita, Due/Scheduled).
  Text pokračující za widgetem na stejném řádku dělá ošklivé mezery, proto: task link je vždy
  **poslední věc na řádku** (komentář piš před něj, např. „zrušit dřív, než se ozvou →
  [[Task]]“), víc tasků = víc odrážek, v buňce tabulky odděluj tasky `<br>`. **Neopakuj za
  linkem due/scheduled** – widget je ukazuje sám.
- Vynech prázdné podsekce (např. „Po termínu“, když nic není).
- Soubory `*-plan.md` a `*-review.md` nesplňují vzory `verify_carpe.py` / `build_moc.py` /
  `link_carpe.py`, takže do souhrnů a MOC nezasahují – **nepřidávej jim navigační blok se
  šipkami** a nepouštěj na ně `link_carpe.py`.

## Co skill nedělá

- Nepíše do kalendáře (demo ani Google Calendar).
- Nemění status/prioritu tasků, nevytváří nové tasky (pokud to uživatel výslovně nechce – pak
  přes TaskNotes konvenci: frontmatter `tags: [task]`, `status: To Do`, `priority`, `due`/`scheduled`,
  `projects`, `oblast`, `dateCreated`).
- Nepřepisuje předchozí plány, review ani týdenní souhrny (jediná výjimka: odebrání aliasu `Aktualni plan`).
