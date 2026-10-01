# Jak funguje deník

Deník je složka `Denik/` a pár skills kolem ní (`denik-souhrn`, `denik-dotazy`, `tydenni-plan`). Nejde o plugin, je to jen konvence: denní poznámky a souhrny nad nimi.

## Proč deník

Cílem je **pamatovat si vlastní život**, ne psát hezké texty. Zápis zabere minutu denně a po roce se dá zeptat:

- „Kdy jsem naposledy viděl babičku?“
- „Kolikrát jsem byl letos lézt?“
- „Co se dělo, když jsem dostal povýšení?“
- „Co dát Mámě, abych neopakoval loňský dárek?“

Práci s textem dělá AI. Člověk jen sype odrážky a souhrny, třídění a hledání obstarají skills.

## Tři vrstvy

```
den      →   týden            →   měsíc         →   rok
odrážky      přeskupené podle     hlavní            milníky
co se        životních rolí       výsledky
stalo        + AI shrnutí
```

| Vrstva | Soubor | Kdo píše | Úroveň detailu |
| --- | --- | --- | --- |
| **Den** | `Denik/2026/2026-09/2026-09-26.md` | člověk: ploché odrážky, klidně jedno slovo | všechno, co stálo za zmínku |
| **Týden** | `Denik/2026/Weekly/2026-W37.md` | skill `denik-souhrn` | každá událost, přeskupená do kategorií (Práce, Lucie, Rodina a přátelé, Kondice a zdraví, Osobní růst, Radost, Domácnost, Administrativa, Memories) |
| **Měsíc** | `Denik/2026/2026-08/2026-08.md` | `denik-souhrn` (z týdnů) | výsledky, ne kroky k nim |
| **Rok** | `Denik/2025/2025.md` | `denik-souhrn` (z měsíců) | milníky |

Čím širší období, tím méně detailu. Na konci každého souhrnu skill napíše, **co vynechal, sloučil nebo přesunul**, takže je hned vidět, co se v souhrnu ztratilo.

Rozcestník přes všechny roky a měsíce je poznámka [[Denik]] (MOC), kterou generuje skript.

## Plánování navazuje

Souhrn se dívá dozadu, **plán týdne** dopředu (skill `tydenni-plan`):

- `2026-W40-plan.md` obsahuje Big Rocks (nejvýš 3 priority), kalendář Po–Ne, deadliny a projekty. Aktuální plán má alias `Aktualni plan`.
- `2026-W39-review.md` vyhodnocuje, jak plán dopadl (✅ / 🔁 / ❌), a obsahuje sekci *Poučení*, kterou čte další plán.

Cyklus tedy vypadá takhle: **píšu den → souhrn týdne → review → plán dalšího týdne**.

## Co dělají skripty (a proč ne AI)

Mechanické části obstarávají deterministické skripty v `.claude/skills/denik-souhrn/`, aby se nerozbily:

| Skript | Co dělá |
| --- | --- |
| `link_denik.py` | navigační řádek `← včera · zítra → · ↑ týden · měsíc` v každé poznámce |
| `check_late_edits.py` | Do souhrnu uloží otisk (hash) každého dne (`denik_src`). Když člověk v neděli večer dopíše odrážku do čtvrtka, příští běh to pozná a doplní ji do souhrnu. |
| `garmin_days.py` | řádek `⌚ Garmin` (kroky, aktivity) do dnů a souhrnů; v demu z fixtures |
| `build_moc.py` | rozcestník [[Denik]] |
| `check_gaps.py` | hlídá, kterým týdnům a měsícům chybí souhrn |

Značka `- xjs week` v denní poznámce jen zaznamenává, že ten den vznikl souhrn.

## Kde začít

1. Otevři libovolnou denní poznámku, třeba `2026-04-17` (Lisabon), a projdi se šipkami.
2. Porovnej ji s týdnem [[2026-W16]], měsícem [[2026-04]] a rokem [[2025]].
3. Pak pusť scénáře 1 a 2 z [[Scenare]]: vygeneruj souhrn W39 a zeptej se deníku na něco.
