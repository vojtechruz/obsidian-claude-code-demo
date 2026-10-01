---
name: navrh-darku
description: Navrhne dárky pro konkrétního člověka na základě uložených nápadů a celé historie darování. Use when the user asks what to give someone, for gift suggestions, "co dát Mámě", "navrhni dárek pro Tátu", "napady na darek pro Lucii", "co koupit k narozeninám", "gift ideas for X", or wants to pick a gift for Vánoce/Narozeniny/Svátek/Valentýn/Výročí. Reads Oblasti/Rodina a Pratele/Darky (historie) and Napady na darky (nápady), avoids repeating what was already given, and grounds suggestions in real patterns from past gifts.
---

# Návrh dárků pro osobu

Doporučí, co dát konkrétnímu člověku. Kombinuje **uložené nápady** (explicitní přání)
s **historií darování** (co už dostal, co obvykle dostává, co dává on).

## Data ve vaultu

```
Oblasti/Rodina a Pratele/
  Darky/                    1 poznámka = 1 dárek   tags: [darek]
                            typ: dano|dostano, rok, prilezitost, osoba, darek
  Napady na darky/          1 poznámka = 1 nápad   tags: [darek-napad]
                            osoba, cena, odkaz, tělo = popis
Lide/<Jméno>.md             poznámka o člověku
                            sekce "## Info k dárkům" = velikosti, preference,
                            co má/nemá rád, alergie (trvalá fakta, ne konkrétní tipy)
```

Frontmatter v `Lide/<Jméno>.md`, ze kterého skript počítá blížící se příležitosti:
`darky: ano|historie` (chybí = nedáváte si), `darky_prilezitosti: [Narozeniny, Vanoce, …]`
(prázdné = všechny), `narozeniny` / `svatek` / `vyroci_prvni_rande` ve tvaru `D. M.` nebo
`YYYY-MM-DD`, volitelně `vyroci_svatby` (jen evidence). Jméno osoby = název souboru
v `Lide/` a musí sedět s wikilinkem v `osoba:` u dárků a nápadů.

**Trvalá fakta o člověku patří do `Lide/<Jméno>.md` → `## Info k dárkům`**, ne do nápadů.
Nápad = konkrétní věc k darování; Info k dárkům = co o něm platí dlouhodobě.

Příležitosti: `Vanoce`, `Narozeniny`, `Svatek`, `Valentyn`, `Vyroci`, `Advent`.

`Advent` = adventní kalendář, **jen u Lucie** (dáváte si ho navzájem, termín 1. 12.).
U ostatních lidí ho nenavrhuj. (Technicky: platí jen pro toho, kdo má `Advent`
v `darky_prilezitosti`.)

## Kontext o lidech

Fakta, která nejsou vidět z dat, ale ovlivňují návrhy:

- **Mama a Tata dostávají dárky každý zvlášť** (jiné narozeniny, jiné zájmy). Historie
  každého z nich se posuzuje samostatně — **nevyřazuj nápad jen proto, že totéž (nebo něco
  podobného) už dostal ten druhý**. Společný dárek pro oba navrhni jen na výslovné přání.
- **U Lucie znamená `Vyroci` výročí vztahu (14. 2.).** Padá na Valentýna, proto Lucie nemá
  `Valentyn` v `darky_prilezitosti` — dárek se eviduje jednou, jako `Vyroci`.
- **Advent je vzájemný** — kalendář dáváš i dostáváš, takže se u něj v datech objevují
  oba záznamy (`dano` i `dostano`) na stejný rok. Není to duplicita.

## Postup

### 1. Načti data

```
python .claude/skills/navrh-darku/gift_data.py "<jméno>"
```

Vrátí JSON: `osoba`, `poznamka_o_osobe`, **`o_osobe`**, **`nadchazejici`**,
`info_k_darkum`, `statistiky`, `napady[]`, `dane[]`, `dostane[]`.

**Nejdřív zkontroluj `o_osobe` — než začneš cokoli navrhovat:**

- **`darky: "historie"`** → s tímhle člověkem si už dárky nedáváte. **Nenavrhuj nic.**
  Řekni to a uveď důvod z `info_k_darkum` (např. že zemřel/a). Historii můžeš ukázat,
  když se na ni zeptá.
- **`darky` chybí** → nedáváte si dárky (výchozí stav). Zeptej se, jestli to má platit
  dál, nebo jestli chce člověka aktivovat.
- **`darky_prilezitosti`** → seznam příležitostí, na které si dárky **skutečně dáváte**.
  Když uživatel chce dárek na příležitost, která tam není, **upozorni na to** a odkaž na
  dohodu v `info_k_darkum` (např. Radek — od 2025 jen k narozeninám, bez Vánoc). Nenavrhuj přes to.

`nadchazejici` má spočítané, co se u té osoby blíží (jen povolené příležitosti), takže
datumovou matematiku neřeš sám.

**Plánování napříč lidmi:**

```
python .claude/skills/navrh-darku/gift_data.py --nadchazejici 90
```

Vrátí, co se u všech aktivních lidí blíží v příštích N dnech (default 90) — použij, když
se uživatel ptá obecně („co mě čeká", „na koho nezapomenout").
Jméno stačí částečné a bez diakritiky (`babi` → `Babicka Vera`). Bez argumentu nebo s
`--lide` vypíše seznam všech osob — použij, když si nejsi jistý jménem nebo je zadání
nejednoznačné (skript sám vrátí `kandidati`).

**Zadání od uživatele má přednost před vším ostatním** — před motivy z historie i před
mezerami. Vytěž z jeho zprávy:

- **Příležitost** (Vánoce, narozeniny…). Když ji neuvede, odvoď ji z toho, co se blíží;
  neptej se zbytečně.
- **Rozpočet** — když ho neuvede, drž se cenové hladiny obvyklé pro danou příležitost.
- **Vyloučení a omezení** („nechci alkohol ani doutníky", „něco praktického", „ne poukazy",
  „chci zážitek"). Tohle je **tvrdý filtr**: takový návrh nedávej vůbec — ani jako
  alternativu, ani „pro úplnost". I když jde o nejsilnější motiv v historii.
- **Směr** („něco na vaření", „k tomu novému bytu") — ber jako prioritu, i když v historii
  oporu nemá.

Když vyloučení odřízne dominantní motiv, **jednou větou to pojmenuj** („alkohol a doutníky
jsou u něj nejsilnější linie, ale vynechávám je") a pak už se k nim nevracej. Zbytek analýzy
udělej **na zúženém vzorku** — hledej motivy a mezery jen mezi tím, co po filtru zbylo.

Pokud po odfiltrování zbyde příliš málo, řekni to na rovinu a nabídni nejbližší dostupné
směry — nedoplňuj vatu.

**Jednorázové vs. trvalé:** „letos nechci alkohol" je jednorázové zadání, nikam se nezapisuje.
„Přestal pít, alkohol už nikdy" je trvalý fakt → nabídni zápis do `## Info k dárkům` (krok 6).

### 2. Analyzuj historii (tohle je jádro skillu)

**Nejdřív si přečti `info_k_darkum`** — trvalá fakta (velikosti, preference, alergie,
zážitky vs. věci) mají **přednost před vzorci z historie**. Když si odporují, řiď se
`info_k_darkum` a rozpor zmiň. Konkrétně:

- **Velikosti** — bez uvedené velikosti nedoporučuj oblečení/boty jako jistotu; buď to
  označ jako riziko, nebo navrhni poukaz.
- **Preference typu daru** („preferuje zážitky") — přebíjí i silný věcný motiv v historii.
- **Alergie / co nemá rád** — tvrdý filtr, takový návrh vůbec nedávej.

Pak projdi `dane[]` a `dostane[]` a hledej:

- **Opakování** — je některý nápad podezřele blízko něčemu, co už jsi dal? Explicitně to označ.
  Pozor i na varianty téhož (další kus stejné kolekce, stejná značka, stejný typ zážitku).
- **Motivy** — co se v darech opakuje (čaj, knihy, zážitky, zahrada, deskovky…). Skutečné
  motivy z dat, ne domněnky.
- **Zážitek vs. věc** — u některých lidí jasně převažuje jedno; drž se toho, co funguje.
- **Cenová hladina podle příležitosti** — z historie je vidět, že Vánoce bývají dražší než
  Svátek. Odhadni obvyklou částku pro danou příležitost (v datech jsou často ceny v závorce).
- **Co ten člověk dává tobě** (`dostane[]`) — vypovídá o jeho vkusu a o tom, co považuje
  za dobrý dárek. Užitečné hlavně u lidí, kde je málo nápadů.
- **Mezera** — co dlouho nedostal, i když to sedí k motivům.

### 3. Novinky z webu

Vault obsahuje jen historii — konkrétní koupitelné novinky v něm nejsou. Dohledej je
webem, ale **jen navázané na motivy zjištěné v kroku 2**.

**Takhle ano** — hledej podle motivu, značky nebo kategorie z historie:
`sypaný čaj dárková sada`, `zahradní nářadí dárková sada`, `kurz keramiky Hradec Králové`, `wellness pobyt pro dva`

**Takhle ne** — obecné žebříčky vrací SEO balast a zředí datově podložené návrhy:
~~`dárky pro maminku 2026`~~, ~~`TOP 20 vánočních dárků`~~

Pravidla:

- 2–4 dotazy odvozené z **nejsilnějších motivů** + příležitosti + cenové hladiny.
- Preferuj **české e-shopy** (nakupuje se v Kč) a konkrétní produkty, ne články typu „30 tipů".
- **Nikdy si produkt nevymýšlej.** Uveď jen to, co reálně vyšlo z výsledků, vždy s odkazem.
- Cenu ber jako orientační — označ ji jako *k ověření*, ceny i dostupnost se mění.
- Profiltruj přes historii i `info_k_darkum` stejně jako vlastní návrhy (žádné opakování,
  žádné alergeny).
- Vyber **3 nejlepší**. Když z hledání nic pořádného nevyleze, radši napiš, že nic
  relevantního nenašlo, než abys dodával vatu.

Krok přeskoč, když si uživatel řekne o rychlý přehled nebo práci bez webu.

### 4. Výstup

Nejdřív krátký **profil** (2–3 věty): co tenhle člověk dostává, v jaké cenové hladině,
zážitky vs. věci. Ať je vidět, že návrhy stojí na datech.

Pak tři sekce:

**A) Z uložených nápadů** — seřazené, u každého:
- proč zrovna teď (sedí k příležitosti / motivu / rozpočtu)
- cena a odkaz, pokud jsou
- ⚠️ pokud připomíná něco už darovaného, napiš to natvrdo (rok + co to bylo)

**B) Nové návrhy** — 3–5 kusů, každý **navázaný na konkrétní data**
(„navazuje na *X* z roku 2019", „doplňuje motiv Y"). Žádné generické tipy typu
„poukaz do drogerie" bez opory v historii.

**C) Novinky z webu** — 3 kusy z kroku 3, u každého:
- **odkaz** a orientační cena (*k ověření*)
- **na jaký motiv z historie navazuje** — bez toho návrh nepatří do výstupu
- ⚠️ pokud jde o novinku, kterou nemáš jak ověřit (dostupnost, kvalita), napiš to

Na konec jedna věta: **co bys vybral a proč**.

### 5. Nabídni uložení

Když uživatel některý nový návrh schválí, nabídni založení nápadu:

`Oblasti/Rodina a Pratele/Napady na darky/<Název>.md`

```yaml
---
tags:
  - darek-napad
osoba:
  - "[[<Jméno>]]"
cena: "<pokud známá>"
odkaz: "<pokud známý>"
---

<krátký popis, proč to sedí>
```

Když naopak uživatel nápad **daroval**, zaznamenej to do historie:

`Oblasti/Rodina a Pratele/Darky/<rok> - <Jméno> - <Prilezitost> (dano).md`

```yaml
---
tags:
  - darek
typ: dano
rok: <rok>
prilezitost: <Vanoce|Narozeniny|Svatek|Valentyn|Vyroci>
osoba:
  - "[[<Jméno>]]"
darek: <co to bylo>
---
```

a zvaž smazání odpovídajícího nápadu (zeptej se).

### 6. Zachyť nová trvalá fakta

Když během rozhovoru vyplyne **trvalý fakt** o té osobě (velikost, alergie, „ta nesnáší
parfémy", „radši zážitky"), nabídni jeho zapsání do `Lide/<Jméno>.md` → `## Info k dárkům`.
Vyplatí se to — příště z toho těží každý návrh. Jednorázové věci („letos chce konkrétně X")
tam nepatří, z toho udělej nápad.

## Pravidla

- **Prázdný `darek` = ještě nevybráno.** Pro aktuální rok jsou v evidenci předpřipravené
  záznamy pro každou příležitost. Prázdný záznam neznamená, že se dárek nedával — znamená,
  že se teprve vybírá. Neuváděj ho jako darovanou věc a neber ho jako „mezeru" v historii.
- **Nikdy netvrď, že něco bylo darováno, aniž to je v datech** — a naopak nedoporuč něco,
  co už v `dane[]` je, bez upozornění.
- U lidí, kde jsou jen dané dárky a žádné dostané (typicky děti — např. Kryštof),
  se o `dostane[]` neopírej — prostě tam nic není.
- Ceny v datech jsou v Kč, obvykle v závorce na konci textu.
- Odpovídej česky.
