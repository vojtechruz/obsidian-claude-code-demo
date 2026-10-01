---
name: garmin-aktivita
description: Stáhne data aktivity z Garmin Connect (vzdálenost, čas, tempo, tep, převýšení, kalorie, úseky, volitelně GPX) a doplní je do poznámky závodu / sportovní akce nebo denní poznámky ve vaultu. Use when the user shares a Garmin Connect activity link or ID (connect.garmin.com/.../activity/<id>), says "doplň výsledky z Garminu", "garmin aktivita", "stáhni aktivitu z garminu", "jak jsem běžel podle garminu", "poslední aktivity z garminu", or asks for pace/heart-rate/distance of a run, race or workout recorded on their Garmin watch.
---

# Garmin aktivita

Integrace s Garmin Connect přes knihovnu `garminconnect` (neoficiální API). Skripty jsou vedle tohoto souboru; tokeny leží **mimo vault** v `~/.garminconnect`.

> **Demo:** v demu běží nad fixtures v `demo_data/` (fiktivní aktivity 10/2025–9/2026, stejná data jako `carpe-summary/demo_data`; úseky po km mají závody a aktivity od 1. 9. 2026, GPX jen závody) a knihovnu `garminconnect` nepotřebuje. Skript to ohlásí řádkem `[demo]` na stderr. Pro reálná data složku `demo_data/` smaž, nainstaluj `pip install garminconnect` a jednou ručně spusť `garmin_login.py`.

## Skripty

| Skript | K čemu |
| --- | --- |
| `garmin_login.py` | **Jednorázové** přihlášení (heslo + MFA). Interaktivní — **uživatel ho spouští sám v terminálu**, Claude ho nespouští (Bash nemá stdin). |
| `garmin_activity.py <id\|url>` | Vypíše Markdown blok `## 📊 Výsledek z Garminu` (souhrn + tabulka úseků). |
| `garmin_activity.py <id> --gpx "<složka>"` | Navíc stáhne `garmin-<id>.gpx` do složky. |
| `garmin_activity.py <id> --json` | Surová data (summary + splity) pro nestandardní dotazy. |
| `garmin_activity.py --recent N` | Tabulka posledních N aktivit (datum, název, typ, km, čas, tep, ID). |

Spouštění: `python ".claude/skills/garmin-aktivita/garmin_activity.py" 20104559832` z kořene vaultu.

## Postup

1. **ID aktivity** — z URL (`.../activity/<id>`) nebo od uživatele. Když uživatel ID nezná („ten dnešní běh"), použij `--recent 10` a vyber podle data/typu; při nejasnosti nabídni výběr.
2. **Spusť** `garmin_activity.py <id>`. Pokud skript skončí hláškou „Nejsi přihlášen" / „Přihlášení z tokenů selhalo", požádej uživatele, aby ve svém terminálu spustil `garmin_login.py`, a počkej — **nikdy nechtěj heslo do chatu**.
3. **Najdi cílovou poznámku**:
   - Závod / sportovní akce → `Oblasti/Kondice a Zdravi/<Název závodu YYYY>.md` (poznámky s tagem `zavod`; index je [[Sportovní akce]]). Blok vlož **za** sekci `## 📸 Fotografie a zážitky` a před `## 🔗 Odkazy` (pořadí sekcí po závodě viz skill `zpracovani-zavodu`); u poznámky ještě před závodem ho dej na konec. Do frontmatteru přidej `garmin: <url>`.
   - Běžný trénink → denní poznámka `Carpe Diem/YYYY/YYYY-MM/YYYY-MM-DD.md`: **jen jeden bullet** ve stylu deníku (`- Beh 9 km za 45:31, tempo 5:03, tep 144`), žádný velký blok — denní poznámky jsou ploché seznamy.
   - Pokud poznámka pro závod neexistuje, zeptej se, jestli ji založit (šablona = existující závodní poznámka, např. [[Brdska dvacitka 2025]]).
4. **Vlož blok** tak, jak ho skript vypsal (jednotky a formát jsou už české). Nepřepisuj ručně čísla — když je něco divné (např. 0 km u překážkového závodu, kde hodinky pauzovaly), řekni to a nech surová data přes `--json`.
5. **GPX** stahuj jen když o něj uživatel stojí; ukládej do `Oblasti/Kondice a Zdravi/Attachments/` a odkaž `[[garmin-<id>.gpx]]` z poznámky.
6. Krátce shrň klíčová čísla v odpovědi (vzdálenost, čas, tempo, tep) a odkaž poznámku wikilinkem.

## Poznámky

- Tempo se počítá z `averageSpeed` (m/s) → min/km; u kola/plavání dává skript tempo také, ale v odpovědi použij raději km/h nebo min/100 m.
- U překážkových závodů (OCR, např. [[Bahenni liska 2026]]) je „čas v pohybu" často výrazně kratší než celkový čas — uveď obojí.
- **Rozdělené aktivity:** hodinky občas závod rozseknou na dvě aktivity (např. po omylem zmáčknutém Stop na překážce). Ověř přes `--recent` / datum, jestli na den závodu není víc aktivit těsně za sebou; pokud ano, stáhni obě (`--json`) a do poznámky dej **sloučené hodnoty** (součet vzdálenosti, času, převýšení, kalorií; tep vážený podle trvání; max = max) + odkazy na obě části. Pokud existuje oficiální čipový čas, uveď ho jako směrodatný.
- Knihovna občas přestane fungovat po změně přihlašování na straně Garminu → `pip install -U garminconnect` a znovu `garmin_login.py` (jen reálný režim).
- Google Calendar ani Sportovní akce index skript nemění — index [[Sportovní akce]] aktualizuj ručně (status ✅ Dokončeno) jako součást kroku 3 u závodů.
