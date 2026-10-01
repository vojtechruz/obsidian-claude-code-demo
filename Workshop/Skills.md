# Skills

Claude Code skills žijí v `.claude/skills/<jméno>/`. Každý skill tvoří soubor `skill.md` a případně Python skripty vedle něj (jen standardní knihovna). Claude skill spustí sám, když tvoje věta odpovídá popisu (`description`) ve frontmatteru. Spustit ho jde i výslovně: `/carpe-summary`.

| Skill | Co dělá | Řekni třeba | Čte | Píše | Síť |
| --- | --- | --- | --- | --- | --- |
| `carpe-summary` | Týdenní, měsíční a roční souhrn deníku: přeskupí odrážky podle životních rolí, přidá AI shrnutí a řádky z Garminu a blogu. Udržuje MOC a navigaci. | „Udělej týdenní souhrn 2026-W39“, „aktualizuj MOC“ | `Carpe Diem/`, Garmin a Plausible fixtures | souhrn, `xjs` značku do denní poznámky, `carpe_src` | ne |
| `carpe-diem-query` | Odpovídá na otázky nad deníkem: kdy naposledy, jak často, co se dělo. | „Kdy jsem naposledy hrál Wingspan?“ | `Carpe Diem/` | nic | ne |
| `tydenni-plan` | Vyhodnotí minulý týden a naplánuje další: Big Rocks, kalendář Po–Ne, deadliny, projekty. | „Naplánuj mi týden 2026-W41“ | `Tasks/`, `Projekty/`, `Lide/`, deník, kalendář (MCP) | `YYYY-Www-plan.md`, `-review.md`, `scheduled` u tasků | ne |
| `navrh-darku` | Navrhne dárek podle historie a nápadů, nic nezopakuje. | „Co dát Mámě k narozeninám?“ | `Lide/`, `Darky/`, `Napady na darky/` | nic, nebo nápad na požádání | ne |
| `zpracovani-zavodu` | Po závodě přestaví poznámku závodu: výsledky, Garmin, zážitky nahoře, „Před závodem“ dole. Aktualizuje index a denní poznámku. | „Doběhl jsem Brdskou dvacítku 2026, zpracuj závod“ | poznámka závodu, `Sportovní akce` | poznámku závodu, index, denní poznámku | ne |
| `vysledky-zavodu` | Najde tě ve výsledkovce časomíry (čas, pořadí, kategorie, ztráta). | „Najdi mě a Radka ve výsledcích Brdské dvacítky 2026“ | časomíra (fixtures) | blok výsledků | ne |
| `garmin-aktivita` | Data aktivity z Garminu: tempo, tep, převýšení, úseky po km. | „Poslední aktivity z Garminu“ | Garmin (fixtures) | blok Garmin | ne |
| `zavody-terminy` | Zkontroluje weby pořadatelů, najde nově vypsané termíny a kolize s kalendářem. | „Jsou už vypsané závody na jaro?“ | weby pořadatelů, `Sportovní akce`, kalendář | nic, zápis do indexu na požádání | **ano** |
| `plausible-blog` | Návštěvnost blogu: nejčtenější články, zdroje, vývoj v čase. Stránky mapuje na poznámky článků. | „Jak si vede blog za září?“ | Plausible (fixtures), `Blog Articles/` | nic | ne |
| `blog-idea` | Zapíše nápad na článek a hned na něj udělá AI review: duplicity, série, priorita, náročnost. | „Přidej blog ideu: Testcontainers v CI pipeline“ | `Blog Ideas/`, `Blog Articles/`, Learning Tracker | novou poznámku nápadu | ne |
| `java-features` | Po vydání Javy stáhne JEPy, roztřídí je do témat a ukáže zastaralé články. | „Vyšla Java 25, projdi JEPy“ | openjdk.org, `Java features/` | témata, ignore list, MOC | **ano** |
| `process-inbox` | Roztřídí `__INBOX`: podcasty, duplicity, články a videa. U položek, které něco vyžadují, navrhne další krok. | „Zpracuj inbox“ | `__INBOX/` | přesuny, mazání duplicit, nové tasky a nápady (po schválení) | ne |
| `verifikace-vaultu` | Rozbité odkazy, osiřelé přílohy, integrita deníku. | „Zkontroluj vault“ | celý vault | nic | ne |

## Jak to spolu souvisí

- **Závod:** `zpracovani-zavodu` volá `vysledky-zavodu` a `garmin-aktivita` a výsledek zapíše do poznámky závodu, do indexu i do denní poznámky.
- **Týden:** `carpe-summary` (co se stalo) a `tydenni-plan` (co bude) jsou dvě poloviny téhož cyklu. Plán čte poučení z minulého review a review hodnotí minulý plán.
- **Blog:** `blog-idea` kontroluje duplicity proti článkům i nápadům. `java-features` a `plausible-blog` plní u článků `Views 6mo`, podle kterého se rozhoduje, co aktualizovat.

## Anatomie skillu

```
.claude/skills/navrh-darku/
├── skill.md        # frontmatter (name, description = kdy se spustí) + postup pro Clauda
└── gift_data.py    # deterministická práce s daty (parsování, výpočty) – výstup JSON
```

Osvědčený vzor: **skript dělá deterministickou část** (najde poznámky, spočítá data, vytáhne frontmatter) **a model dělá úsudek** (co z toho plyne, jak to napsat). Skript se dá otestovat a model nemusí číst stovky souborů.

Vlastní skill si přidáš tak, že vytvoříš složku s `skill.md`. Popis v `description` musí říkat, **kdy** se má skill použít, podle toho ho Claude vybírá.
