---
name: vysledky-zavodu
description: Stáhne oficiální výsledky závodu z časomíry sport-base.eu (OCR a trailové závody s touto časomírou) — najde uživatele/Radka ve výsledkovce, vypíše čas, pořadí, ztrátu a kategorii, a doplní je do poznámky závodu ve vaultu. Use when the user shares a sport-base.eu results link, asks "scrapni výsledky", "najdi mě ve výsledcích", "jak jsme dopadli v závodě", "oficiální výsledky Brdské dvacítky / Bahenní lišky", or wants race results added to a race note under Oblasti/Kondice a Zdravi.
---

# Výsledky závodu (sport-base.eu)

Skript `sportbase_results.py` vedle tohoto souboru čte veřejné API `https://sport-base.eu/api/public` (bez přihlášení).

> **Demo:** v demu běží nad fixtures v `demo_data/` (fiktivní výsledkovky, slugy `brdska-dvacitka-2025`, `vltavsky-pulmaraton-2026`, `bahenni-liska-2026`, `brdska-dvacitka-2026`), síť nevolá a hlásí to řádkem `[demo]` na stderr. Pro reálná data složku `demo_data/` smaž; přístup není potřeba, API je veřejné.

```
python ".claude/skills/vysledky-zavodu/sportbase_results.py" <slug|URL>                    # tratě + kategorie
python ".claude/skills/vysledky-zavodu/sportbase_results.py" <slug|URL> --find "Kratoch"   # najít závodníka (bez diakritiky)
python ".claude/skills/vysledky-zavodu/sportbase_results.py" <slug|URL> --track 20K --top 10
```

## Postup

1. Ze zadané URL vezmi slug (`/competitions/<slug>/results`). Nejdřív spusť bez parametrů — ukáže tratě (20K / 10K / RACE / …) a kategorie.
2. Hledej `--find "Kratoch|Simek"` (regex; najde Kratochvíl i Kratochvílová, jednotlivce i dvojice/týmy, kde je člen). Uživatel = „Kratochvíl Ondřej", Radek = „Šimek Radek" (závodí spolu na trailech a OCR).
3. **Nenajde-li je:** ověř kategorii v poznámce závodu. U OCR závodů bývá kategorie **FUN neměřená** (ve výsledcích vůbec není, např. FUN vlna [[Bahenni liska 2026]]) — pak je jediný zdroj času Garmin (skill `garmin-aktivita`). Napiš to do poznámky, ať se to příště nehledá znovu.
4. Do poznámky závodu (`Oblasti/Kondice a Zdravi/<závod>.md`) doplň sekci `## 🏆 Oficiální výsledky` — tabulku pro oba (Ondra + Radek, pokud běžel; čas, pořadí absolutně i v kategorii, ztráta na vítěze) + odkaz na výsledkovku + kontext tratě (počet finisherů, vítěz, medián). Sekci dej hned za `## 📍 Přehled` (pořadí sekcí po závodě viz skill `zpracovani-zavodu`), případně před `## 📊 Výsledek z Garminu`.
5. Když se oficiální čas liší od Garminu, uveď oficiální jako směrodatný a rozdíl krátce vysvětli (pauzy, rozdělená aktivita, start čipu vs. hodinek).

## Poznámky

- Pole API: `trackPosition` (absolutní pořadí v trati), `timeMs`, `trackLossTimeMs` (ztráta na vítěze trati), `categoryRanks[].rank`, `categoryLosses[]`, `members[]` u dvojic/týmů, `disqualification`.
- Jiné časomíry (vlastní weby pořadatelů, PDF listiny) tento skript neumí — tam se stahuje PDF/HTML ručně (viz skill `zpracovani-zavodu`).
- Index [[Sportovní akce]] a status závodu skript nemění — aktualizuj ručně.
