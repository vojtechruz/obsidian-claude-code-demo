# Mapa vaultu

Vault je uspořádaný podle **PARA** (Projects, Areas, Resources, Archive) a má k tomu několik speciálních složek.

```
Denik/                 deník (viz Denik Denik)
  2025/2025-10/2025-10-01.md      denní poznámka (ploché odrážky)
  2025/2025-10/2025-10.md         měsíční souhrn
  2025/2025.md                    roční souhrn
  2026/Weekly/2026-W37.md         týdenní souhrn (+ denik_src hash)
  2026/Weekly/2026-W40-plan.md    plán týdne (alias „Aktualni plan“)
  2026/Weekly/2026-W39-review.md  vyhodnocení týdne
  Denik.md                   MOC – rozcestník (generuje build_moc.py)
Projekty/                   aktivní projekty s cílem a koncem (JOpenSpace 2026, Rekonstrukce koupelny…)
Oblasti/                    dlouhodobé oblasti
  Prace/  Lucie/  Rodina a Pratele/  Kondice a Zdravi/  Osobni rust/  Blog/
  IT Komunita/  Cestovani/  Domov/  Administrativa/  Finance/  Radost/  Vzpominky/
  Osobni rust/Uceni.md       learning tracker (hub s pohledy), Temata/ (fronta a rozpracované), Zdroje/ (kurzy, platformy)
Znalosti/                   referenční materiál – jen nabyté znalosti (Kubernetes, Vareni, Lezeni, Prednaseni)
Archiv/                     hotové projekty a archivované tasky
Lide/                       jedna poznámka na člověka (narozeniny, svátky, info k dárkům)
Tasks/                      TaskNotes tasky
Media/                      knihy, filmy, seriály, hry (+ Media.base)
Flashcards/                 balíčky kartiček
__INBOX/                    nové poznámky, _Clippings, _Articles, _Podcasts, _Videos, Kam.md
System/                     Bases, šablony, TaskNotes pohledy
Workshop/                   tahle dokumentace
.claude/skills/             Claude Code skills
.claude/mcp/demo-calendar/  falešný kalendář (MCP server)
CLAUDE.md                   konvence vaultu pro Claude Code
```

Jak funguje deník: [[Jak funguje denik]].

## Kde co najdeš pro scénáře

| Hledáš | Poznámka |
| --- | --- |
| Persona | [[Lide]] – Ondra, partnerka [[Lucie]], rodina v Hradci, kamarádi Radek, Hana a Filip, kočka [[Bublina]] |
| Rok v kostce | [[Denik]] (MOC), [[2025]], měsíce [[2026-04]] (Lisabon a povýšení), [[2026-08]] (Dolomity) |
| Aktuální týden | [[2026-W40-plan]], [[2026-W39-review]] |
| Závody | [[Sportovní akce]]; před závodem [[Oblasti/Kondice a Zdravi/Podzimni pulmaraton 2026\|Podzimni pulmaraton 2026]]; doběhnutý a nezpracovaný [[Brdska dvacitka 2026]]; zpracovaný [[Brdska dvacitka 2025]] |
| Dárky | `Oblasti/Rodina a Pratele/Darky/`, `Napady na darky/` |
| Blog | `Oblasti/Blog/Blog Articles/`, `Blog Ideas/`, [[Java features]] |
| Učení | [[Uceni]] (fronta, rozpracované, zdroje); rozpracovaná témata [[Spring AI]] a [[Anglictina - mluveni]], odložené [[Kubernetes - networking a Helm]], hotové [[Prednaseni - prace s publikem]] ve `Znalosti/` |
| Tasky | `Tasks/`. Pohledy otevřeš z příkazového panelu přes „TaskNotes“ |

## Konvence

- Poznámky jsou **česky bez diakritiky** (tak je píše i autor originálu) a mají konce řádků CRLF.
- Odkazy se píšou dvojitými hranatými závorkami kolem názvu poznámky. U nejednoznačných jmen se používá cesta (`Lucie` je osoba i oblast).
- Rozpracované věci mají datum v `scheduled` (kdy začít) a `due` (deadline).
- Podrobné konvence jsou v `CLAUDE.md`.
