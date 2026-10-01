---
name: zavody-terminy
description: Zkontroluje weby pořadatelů běžeckých, trailových a OCR závodů, na které uživatel chodí (seznam je v sekci „Pořadatelé“ v Oblasti/Kondice a Zdravi/Sportovní akce.md, např. Spartan Race, Gladiator Race, Brdská dvacítka, Vltavský půlmaraton), najde nově vypsané termíny, porovná je s indexem Sportovní akce a s kalendářem a řekne, na co se dá registrovat a co koliduje. Use when the user asks "jsou už vypsané závody", "jaké závody jsou na jaro/podzim", "zkontroluj termíny závodů", "kdy je Brdská dvacítka / Vltavský půlmaraton / Spartan 2027", "na co se registrovat", "race calendar check", or when the tydenni-plan skill triggers its monthly race check. Neregistruje, nic neplatí – jen hlásí termíny a nabídne zápis do indexu.
---

# Termíny závodů

Najde nově vypsané termíny závodů sérií, na které uživatel chodí (sám nebo s Radkem), a nabídne je k registraci nebo
k zápisu do plánu. **Nic neregistruje, nic neplatí a nepíše do kalendáře.**

Jazyk výstupu: **čeština**, stručně.

## Zdroje

| Zdroj | Co z něj |
| --- | --- |
| `Oblasti/Kondice a Zdravi/Sportovní akce.md`, sekce `## Pořadatelé` | tabulka sérií: web, obvyklé závody, obvyklý termín, kdy vypisují – **jediný zdroj pravdy**, neopisuj ji do skillu |
| tamtéž, sekce `## Nadcházející závody` / `## Potenciální závody` / `## Timeline` | co už máme registrované nebo evidované jako kandidáta |
| `Oblasti/Kondice a Zdravi/<Název YYYY>.md` (tag `zavod`) | poznámky jednotlivých závodů |
| Kalendář – MCP server `demo-calendar` (**jen čtení**, `mcp__demo-calendar__list_events` / `search_events` na kalendáři `primary`; v reálném nasazení Google Calendar MCP se stejnými nástroji) | kolize s dovolenou, meetupy, rodinnými akcemi |
| weby pořadatelů | `WebFetch`; když web neodpovídá (některé weby vrací `ECONNREFUSED`), použij záložní URL z tabulky nebo `WebSearch` s názvem série a rokem. Fiktivní závody demo vaultu mají web na doméně `*.example` – ten nezkoušej, rovnou použij odhad ze sloupce „Obvyklý termín“ |

## Postup

1. **Načti tabulku Pořadatelé** a index. Urči **období zájmu**: default = od dneška do konce
   příštího půlroku; uživatel může říct jinak („jaro 2027“, „únor až duben“).

2. **Projdi weby** ze sloupce „Web / kalendář“ – všechny `WebFetch` volej **paralelně**. Z každého
   vytáhni: název závodu, datum, místo, zda je otevřená registrace. Zajímají nás jen závody
   v období zájmu. Pokud web neodpovídá, zkus záložní URL; když ani ta, napiš „web nedostupný“
   a odhadni termín ze sloupce „Obvyklý termín“ (označ jako **odhad**).

3. **Porovnej** s indexem: co už je zapsané, vynech. Ke každému novému termínu zjisti kolize:
   - kalendář v ten den/víkend (dovolená, Java Pivo Praha, JOpenSpace, návštěvy v Hradci, rodinné akce),
   - jiné závody v indexu (dva závody za sebou = upozornit),
   - **odhadované** termíny ze sloupce „Obvyklý termín“ pro závody, které ještě vypsané nejsou
     (např. Brdská dvacítka = poslední sobota v září) – ať se na ten víkend neplánuje pobyt.

4. **Vypiš výsledek** jako tabulku: Závod · Datum · Místo · Registrace · Kolize · Doporučení
   (registrovat / počkat / nejde). Zvlášť uveď „ještě nevypsané, ale obvykle“ s odhadem.
   Uveď zdroje (URL). Když nic nového není, řekni to jednou větou – žádná tabulka.

5. **Nabídni, ne dělej:**
   - zápis nového termínu do `Sportovní akce.md` (sekce „Potenciální závody“ se
     `Status: 💡 Zvažuji` + řádek v Timeline; po registraci přesunout do „Nadcházející závody“) –
     po souhlasu zapiš,
   - založení poznámky závodu `Oblasti/Kondice a Zdravi/<Název YYYY>.md` (tag `zavod`, sekce
     `# 🗂️ Před závodem` s checklistem `[[Checklist - Zavod OCR]]`) – jen když se uživatel
     registroval,
   - task `Registrovat na <závod>` (TaskNotes: `tags: [task]`, `status: To Do`,
     `priority: pozdeji`, `due` = konec early-bird nebo 4 týdny před závodem, `scheduled` =
     due minus 1 týden, `oblast: [[Oblasti/Kondice a Zdravi/Kondice a Zdravi|Kondice a Zdravi]]`),
   - a **nikdy** registraci samotnou.

6. Když přibyla nová série nebo se změnil web, navrhni úpravu tabulky Pořadatelé (po souhlasu
   uprav – tabulka je v poznámce, ne tady).

## Volání z `tydenni-plan`

`tydenni-plan` spouští tento skill v kroku 2b jen **jednou měsíčně** (první plán v měsíci)
nebo když index Sportovní akce nemá žádný závod dál než 6 týdnů od plánovaného týdne. V tom
případě běž s obdobím zájmu = příštích 6 měsíců, výsledek dej **stručně** do diskuse plánu
(krok 7) a nový závod k registraci nabídni jako Small Rock „Registrovat na X“. Do poznámky
plánu se nic dalšího nepíše.

## Co skill nedělá

- Neregistruje na závody, neplatí, nevyplňuje formuláře.
- Nepíše do kalendáře (událost závodu se přidává až po registraci, ručně nebo na výzvu).
- Nemění existující poznámky závodů (to dělá `zpracovani-zavodu` / `vysledky-zavodu`).
