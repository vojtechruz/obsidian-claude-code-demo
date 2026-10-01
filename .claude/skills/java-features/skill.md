---
name: java-features
description: Spravuje Java features tracker ve vaultu (Oblasti/Blog/Java features/) – po vydání nové Javy stáhne její JEPy z openjdk.org, roztřídí je do témat nebo do ignore listu, aktualizuje řetězce preview → final a ukáže, které blogové články tím zastaraly. Use when the user says a new Java version is out or asks to process one ("vyšla Java 28", "projdi JEPy Javy N", "zkontroluj novou Javu", "java release check"), wants to triage JEPs ("roztřiď JEPy", "zařaď JEP 5xx"), asks which Java articles need updating ("které Java články zastaraly", "co aktualizovat na blogu z Javy"), wants to create a Java feature topic, or asks to check the tracker's consistency.
---

# Java features tracker

Tracker hlídá dvě věci: **které Java featury stojí za naučení / článek** na blogu
`ondrakodi.example` a **které existující články zastaraly**, protože po nich přišel další JEP
(preview → final, rozšíření, stažení). Data o JEPech se stahují živě z veřejného openjdk.org,
všechno ostatní je v poznámkách vaultu.

## Data

```
Oblasti/Blog/Java features/Java features.md    MOC a zároveň folder note: legenda, vložená Base, „Zdroje k roztřídění“,
                                               „Nerozhodnuté JEPy“, „Kontroly verzí“
Oblasti/Blog/Java features/Java features - přehled.base   přehled témat (vzorce: stav, zastaralé N×, poslední final, Views 6mo)
Oblasti/Blog/Java features/Java feature - <Téma>.md   1 poznámka = 1 téma (řetězec JEPů)
Oblasti/Blog/Java features/Java features - ignorované.md   JEPy rozhodnuté jako „teď ne“, po verzích
Oblasti/Blog/Blog Articles/                    poznámky článků (formát viz skill `blog-idea`) – NEEDITOVAT
Oblasti/Blog/Blog Ideas/                       nápady na články (formát viz skill `blog-idea`)
```

**Pravidlo:** každý JEP má právě jedno rozhodnutí – je v tabulce **jednoho** tématu, v ignore
listu, nebo vědomě odložený v tabulce `## Nerozhodnuté JEPy` v MOC
(`| JEP | Název | Java | Skupina |`). Návaznosti mezi tématy se řeší odkazem v textu, ne duplicitním řádkem.

### MOC `Java features.md`

```markdown
---
tags:
  - java
cssclasses:
  - wide
---

> [!info]- Jak tracker funguje
> (legenda: co se vyplňuje ručně, význam ✅ ⚠️ 👀 —, kontrola 2× ročně po vydání Javy – březen, září)

![[Java features - přehled.base]]

## Zdroje k roztřídění

### <Téma bez vlastní poznámky>
- odkazy

## Nerozhodnuté JEPy

| JEP | Název | Java | Skupina |
| --- | --- | --- | --- |
| [390](https://openjdk.org/jeps/390) | Warnings for Value-Based Classes | 16 | Valhalla |

## Kontroly verzí

- Java 25 (2025-09-20): 18 JEPů – 6 do témat, 11 do ignore, 1 nové téma; zastaralo: Virtual Threads
```

Skript čte jen tabulku pod `## Nerozhodnuté JEPy` (sloupce JEP s odkazem, Název, Java).

### Poznámka tématu

```markdown
---
base: "[[Java features - přehled.base]]"
tags:
  - java
Clanky:
  - "[[<poznámka v Blog Articles>]]"
Napady:
  - "[[<poznámka v Blog Ideas>]]"
Pokryto do: 15
Finalni verze:
  - 16
  - 21
Sleduje se: Primitive Types in Patterns (JEP 532, Java 27)
Problem:
---

<jedna věta, co téma pokrývá; odkazy na související témata>

| JEP | Java | Typ | V článku |
| --- | --- | --- | --- |
| [305](https://openjdk.org/jeps/305) Pattern Matching for instanceof | 14 | preview | ✅ |
| [394](https://openjdk.org/jeps/394) Pattern Matching for instanceof | 16 | **final** | ⚠️ |

- poznámky, návrh aktualizace článku

## Zdroje

- odkazy
```

- Klíče frontmatteru přesně v tomto pořadí; prázdné hodnoty nech prázdné (`Clanky: []`,
  `Pokryto do:`), Base s nimi počítá.
- `Clanky` musí odkazovat na existující poznámku v `Oblasti/Blog/Blog Articles/` (hlídá `check`).
- `Pokryto do` = verze Javy, kterou článek popisuje (ověř v textu / výňatku článku nebo v AI
  review v poznámce článku; když to nejde, zeptej se uživatele).
- `Finalni verze` = **přesně** verze řádků s typem `**final**` v tabulce (hlídá `check`).
- `Sleduje se` = poslední preview/incubator JEP řetězce, který ještě není final
  (`Název (JEP N, Java V)`); když řetězec dojde do final, vyprázdni.
- `Problem` = co se verzemi vyjádřit nedá (článek o stažené featuře, věcná chyba).
- Sloupec **Typ**: `preview`, `preview 2`…, `incubator N`, `experimental`, `**final**`,
  `⛔ **stažen**`.
- Sloupec **V článku**: `✅` článek to popisuje · `⚠️` final/zásadní JEP po článku (dluh) ·
  `👀` preview po článku (jen sledovat) · `—` téma nemá článek.
- Řádky řaď podle verze Javy, v rámci verze podle čísla JEPu. Skript řádek pozná podle tvaru
  `| [N](url) Název | Java | Typ | V článku |`.

### Ignore list

Sekce `## Java N` (vzestupně), v každé tabulka `| JEP | Název | Důvod |` řazená podle čísla
(`| [304](https://openjdk.org/jeps/304) | Garbage Collector Interface | GC |`).
Důvod je nepovinný – krátce (`GC`, `port`, `odstranění`, `security`, `interní JDK`,
`incubator`), delší jen tam, kde by rozhodnutí za rok překvapilo. Ignore = **teď ne**: když
ignorovaný řetězec dojde do final, nabídni ho znovu.

### Base `Java features - přehled.base`

Filtr `note["base"] == link("Java features - přehled.base")`. Vzorce:
`zastarale` = počet `Finalni verze` větších než `Pokryto do` (jen u témat s článkem),
`posledni_final` = max z `Finalni verze`, `views` = součet `Views 6mo` odkázaných článků,
`stav` = `⛔ problém` / `💡 bez článku` / `📝 bez článku, nápad existuje` / `⚠️ zastaralé N×` /
`✅ aktuální`. Pohledy **Přehled** (všechna témata) a **K aktualizaci** (`zastarale > 0` nebo
vyplněný `Problem`, řazeno podle `views`).

### Návštěvnost článků

`Views 6mo` je číselná vlastnost ve frontmatteru poznámky článku (zobrazení za posledních 6
měsíců). Skript ji jen čte; když chybí, bere se 0 a pořadí v `articles` je pak jen orientační.

## Skript

```
python .claude/skills/java-features/jeps.py release N [--details]   # JEPy verze N + klasifikace
python .claude/skills/java-features/jeps.py jep N [N ...]           # detail JEPu (status, release, summary, related)
python .claude/skills/java-features/jeps.py check                   # konzistence trackeru
python .claude/skills/java-features/jeps.py articles                # zastaralé články / problémy podle Views 6mo
```

Klasifikace: `topic` / `ignored` / `pending` (už rozhodnuto nebo odloženo), `suggest_pending`
(stejný řetězec jako odložený JEP – odlož taky, nebo nabídni rozhodnout celý řetězec), `suggest_topic` (stejný řetězec jako řádek
tématu – podle názvu bez „(Second Preview)“ nebo přes `related` JEPy ze stránky JEPu),
`suggest_ignore` (řetězec už ignorovaný; pole `note`, pokud je teď final), `untriaged`.
`--details` stáhne stránku každého JEPu (pomalejší, ale zachytí přejmenované řetězce, např.
Unnamed Classes → Compact Source Files). Stránka verze existuje už během vývoje, seznam je
uzavřený od Rampdown Phase One (červen / prosinec). openjdk.org při rychlém dotazování vrací
403 – skript proto stahuje sekvenčně s pauzou a při chybě čeká a zkouší znovu.

## Workflow A – nová verze Javy

1. `release N --details`. Pokud stránka ještě nemá JEPy nebo verze není GA, řekni to (seznam
   se může do rampdownu měnit).
2. Předlož uživateli tabulku k potvrzení – **nic nezapisuj před potvrzením**:
   - `suggest_topic` → „přidat do <téma>“ (+ co se změní: `Finalni verze`, `Sleduje se`,
     zastarání článku).
   - `suggest_ignore` → „ignore“; když je řetězec teď final, výslovně se zeptej, jestli ho
     znovu zvážit.
   - `untriaged` → tvůj návrh: existující téma / nové téma / ignore, s jednou větou proč
     (summary z `--details`). Jazykové a API featury spíš téma, GC / porty / security /
     interní JDK / odstranění spíš ignore. Zohledni Blog Ideas a články (`Grep` v
     `Oblasti/Blog/Blog Ideas` a `Blog Articles`).
3. Po potvrzení zapiš: řádky do témat, nová témata (šablona výše; přesuň do nich odpovídající
   odkazy ze sekce „Zdroje k roztřídění“ v MOC a nápady z `Blog Ideas` do `Napady`), řádky do
   ignore listu.
4. `check` – oprav, co hlásí.
5. `articles` – vypiš dotčené články (které nově zastaraly) seřazené podle `Views 6mo` a
   ke každému navrhni typ aktualizace: banner (preview → final beze změn) / update sekce /
   navazující článek / přepis. Samotné přepsání článku je mimo tento skill.
6. Když uživatel část rozhodnutí odloží, zapiš ty JEPy do `## Nerozhodnuté JEPy` v MOC
   (se skupinou = název featury). Při každé kontrole nabídni odložené skupiny znovu jen tehdy,
   když se v nich něco pohnulo (nový JEP řetězce, přechod do final).
7. Do MOC, sekce `## Kontroly verzí`, přidej řádek
   `- Java N (YYYY-MM-DD): X JEPů – a do témat, b do ignore, c nových témat; zastaralo: …`.

## Workflow B – roztřídění odložených JEPů

Stejné jako A, jen zdrojem je tabulka `## Nerozhodnuté JEPy` v MOC (nebo seznam JEPů, který
uživatel zadá – `jep N [N ...]` pro detaily). Předkládej po skupinách (např. po verzích nebo
po oblastech), ať to uživatel zvládne potvrdit. Rozhodnuté řádky z tabulky odlož odstraň.

## Workflow C – co aktualizovat na blogu

`articles` → seznam témat se zastaralými články / problémem, seřazený podle návštěvnosti.
Stejná data ukazuje pohled **K aktualizaci** v `Java features - přehled.base`.

## Pravidla

- Poznámky v `Blog Articles` ani `Blog Ideas` needituj – propojení drží pole `Clanky` /
  `Napady` v tématu (opačný směr ukazují backlinky).
- Nová témata zakládej zápisem souboru; **přejmenování / přesun** poznámky dělej v Obsidianu
  (nebo přes `obsidian move`), ne přes souborový systém – jinak zůstanou duchové v indexu –
  a pak oprav `[[odkazy]]`.
- Poznámka `Java features.md` je **folder note** složky – plugin Folder Notes synchronizuje název
  složky s názvem poznámky. Při přejmenování proto přejmenuj složku, ne poznámku.
- `.base` needituj bez výslovného pokynu (Obsidian ho přeformátovává; vlastnosti z
  frontmatteru mají v `properties:` prefix `note.`).
- Větší změny zapiš do dnešní denní poznámky pod `- obsidian cleanup`.
- Nikdy necommituj bez výslovného pokynu.
