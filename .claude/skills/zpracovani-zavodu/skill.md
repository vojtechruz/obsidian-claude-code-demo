---
name: zpracovani-zavodu
description: Zpracuje závod nebo sportovní akci po doběhnutí. Doplní oficiální výsledky a Garmin, přestaví poznámku závodu (nahoře to, co je důležité po závodě, informace platné jen před závodem pod jeden H1 „Před závodem“), aktualizuje index Sportovní akce a denní poznámku. Use when the user says they finished a race — „doběhl jsem X“, „dokončili jsme závod“, „máme za sebou Brdskou dvacítku / Bahenní lišku / půlmaraton“, „zpracuj závod“, „uklid poznámku závodu po závodě“ — or asks to restructure a completed race note in Oblasti/Kondice a Zdravi.
---

# Zpracování závodu po doběhnutí

Závodní poznámky jsou v `Oblasti/Kondice a Zdravi/<Název závodu YYYY>.md` (tag `zavod`), index je [[Sportovní akce]]. Před závodem je poznámka plná logistiky (registrace, parkování, výbava, pravidla, checklist). Po závodě ji uživatel otevírá kvůli výsledku a vzpomínkám, proto se přestavuje. Vzor hotové poznámky: [[Brdska dvacitka 2025]], [[Bahenni liska 2026]].

Traily a OCR běží uživatel (Ondra) často **s Radkem** ([[Radek Simek]]), výsledky se pak hledají pro oba; [[Lucie]] občas jezdí fandit.

> **Demo:** `vysledky-zavodu` a `garmin-aktivita` běží nad fixtures. Pro nezpracovanou [[Brdska dvacitka 2026]] (so 26. 9. 2026): výsledky `sportbase_results.py brdska-dvacitka-2026 --find "Kratoch|Simek"`, Garmin `garmin_activity.py --recent 10` → aktivita `20104559832`.

## Postup

1. **Najdi poznámku závodu** podle data a názvu. Pokud neexistuje, zeptej se, jestli ji založit.
2. **Garmin:** skill `garmin-aktivita` (`--recent` podle data, pak detail aktivity). Pozor na rozdělené aktivity (hodinky omylem stopnuté na překážce). Divné hodnoty (např. převýšení z barometru) nepřepisuj, jen je v odpovědi zmiň.
3. **Oficiální výsledky:** podle časomíry:
   - **sport-base.eu** (trailové a OCR závody, v demu všechny čtyři závody z indexu): skill `vysledky-zavodu`.
   - **chiptiming.cz** (některé OCR série): `https://www.chiptiming.cz/results/<závod>/<trať>`. Stačí `curl -sL` s prohlížečovým User-Agentem. Stránka obsahuje celou výsledkovku v jedné HTML tabulce, sloupce: Pořadí, Jméno, Kat (pohlaví), Věk, Tým, Start číslo, Čip, Start čas, Pistol čas, Čas v cíli, Handicap, Průběžný čas, Celkový čas, Status, Ztráta. Jména jsou bez diakritiky (`Ondrej Kratochvil`, `Radek Simek`).
     - Kategorii poznáš podle **Pistol času** (výstřelu vlny): Elite startuje první, FUN má vlastní vlnu, ostatní jsou Open.
     - Status `running` **neznamená DNF**. Časomíra nezaznamenala cíl a „čas“ běží dál od výstřelu vlny. Rozliš: FUN vlna = neměří se; bez `Start čas` = skoro jistě DNS (startovní rám chytí >99 % lidí); se `Start čas` a bez cíle = skutečné DNF nebo nepřečtený čip.
     - Exporty „Excel“ z webu jsou po kategoriích (muži Open, ženy Open, týmy). Použij je jako kontrolu webu.
   - **Jiné weby časomír** a **PDF listiny**: HTML stáhnout, PDF přes `pdftotext -layout` + grep na jméno nebo startovní číslo.
   - **FUN kategorie** (u OCR) se často neměří. Jediný čas je z Garminu, napiš to do výsledků.
4. **Sekce `## 🏆 Oficiální výsledky`:** tabulka pro oba (číslo, čas, pořadí celkově, v kategorii, podle pohlaví, věková kategorie), pod ní vítěz, medián a počet lidí v cíli. Co jsi dopočítal sám (např. věková kategorie podle věku), výslovně označ jako dopočítané.
5. **Kompletní výsledky jako příloha**, pokud o ně uživatel stojí: `Attachments/<Název závodu YYYY> - výsledky.md` (všichni v cíli podle času bez ohledu na kategorii, u členů týmů jejich individuální čas, sekce „Kdo nedoběhl“), případně totéž jako `.xlsx`. Vzor: [[Brdska dvacitka 2025 - výsledky]].
6. **Přestav poznámku** (nic nemaž, jen přesouvej; po přestavbě zkontroluj, že se neztratil žádný řádek):

   ```
   ---  frontmatter: status: completed, garmin: <url>, vysledky: <url>
   # Název závodu
   Jedna věta: co, kdy, s kým, oficiální čas.
   ## 📍 Přehled         tabulka: datum (+vlna), místo, kategorie/trať, startovní čísla, čas + pořadí, status
   ## 🏆 Oficiální výsledky
   ## 📸 Fotografie a zážitky   (zážitky, poučení na příště, odkazy na fotky/videa)
   ## 📊 Výsledek z Garminu
   ## 🔗 Odkazy           jen co dává smysl po závodě: výsledky, Garmin, stránka závodu, video, příloha s výsledky
   ---
   # 🗂️ Před závodem      jeden H1, dá se v Obsidianu sbalit
   (registrace, harmonogram, parkování/doprava, výbava, pravidla, podmínky/VOP, checklist, přílohy od pořadatele, motivace…)
   ```

   Když poznámka žádné předzávodní info nemá, H1 „Před závodem“ nezakládej.
7. **Index [[Sportovní akce]]:** přesuň závod na začátek sekce „Absolvované závody“ (je na konci poznámky, nejnovější nahoře), status `✅ Dokončeno · <čas> · [Garmin](…) · [výsledky](…)`, v tabulce Timeline `✅ Hotovo` a aktualizuj řádky „Nejbližší“ a „Příprava“.
8. **Denní poznámka** dne závodu: jeden bullet (`- [[Brdska dvacitka 2026]] s Radkem, 20,4 km, oficialne 1:58:12, 39./162`). Pokud tam uživatel už svůj bullet o závodu má, **nepřidávej druhý**, jen k jeho řádku připiš čas a odkaz.
9. **Odpověď:** krátce čas, pořadí, Garmin (vzdálenost, čas v pohybu, tep) a co jsi kam zapsal. Pořadí podávej věcně a srovnej s minulým ročníkem nebo cílem z poznámky (např. Brdská dvacítka 2025 → 2026: −8:28).
