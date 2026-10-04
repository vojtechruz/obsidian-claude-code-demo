# Scénáře k vyzkoušení

Každý scénář jde pustit samostatně. Po vyzkoušení vrať vault do výchozího stavu, viz [[Reset a reseni problemu]].

> „Dnes“ je ve vaultu **čtvrtek 1. 10. 2026**. Když skill pracuje s dneškem, začni prompt třeba „Předstírej, že je 1. 10. 2026.“

## 1. Týdenní souhrn deníku ⭐
Jak deník funguje, vysvětluje [[Jak funguje denik]].

**Prompt:** `Udělej týdenní souhrn 2026-W39`

- **Co se stane:** `denik-souhrn` přečte denní poznámky 21.–27. 9. a roztřídí je do kategorií (Práce, Lucie, Rodina a přátelé, Kondice a zdraví…). Nahoru napíše AI shrnutí, doplní řádek z Garminu a blogové statistiky a do neděle zapíše značku `xjs week`.
- **Kam se podívat:** nová poznámka `Denik/2026/Weekly/2026-W39.md` a závěrečný report skillu, tedy co vynechal, co sloučil a co přesunul.
- **Pokračování:**
  - `Udělej souhrn W38 a W40` a pak `měsíční souhrn září 2026`. Měsíc se skládá z týdnů.
  - Pak `aktualizuj MOC`, výsledek je v `Denik/Denik.md`.
  - Pro porovnání se podívej na hotové měsíce, třeba `2026-04` (Lisabon a povýšení), a na rok `2025`.

## 2. Otázky na deník
**Prompty:**
- `Kdy jsem naposledy hrál Wingspan?`
- `Kolikrát jsem byl lézt od ledna a jak se zlepšuju?`
- `Co jsem dělal v Lisabonu?`
- `Jak dopadly moje půlmaratony?`

`denik-dotazy` odpovídá s daty a odkazy na denní poznámky a souhrny.

## 3. Plán týdne ⭐
**Prompt:** `Naplánuj mi týden 2026-W41` (týden uveď výslovně, protože skript bere dnešní datum ze systému).

- **Co se stane:** `tydenni-plan` porovná plán W40 (`2026-W40-plan.md`) s tím, co se opravdu stalo, a zapíše `2026-W40-review.md`. Převezme poučení z W39 review. Pak sesbírá tasky, projekty, narozeniny a kalendář z demo MCP (zubař, Luciina vernisáž, pneumatiky, půlmaraton) a navrhne nejvýš 3 Big Rocks na volné večery.
- **Zajímavost:** v sobotu 17. 10. je výměna pneumatik a zároveň výdej startovních balíčků na půlmaraton. Ukaž, jestli si toho všimne.
- **Kam se podívat:** `Denik/2026/Weekly/` a alias `Aktualni plan`, který se přesune na nový plán.
- **Poznámka:** jednou za měsíc plán spouští i kontrolu termínů závodů (`zavody-terminy`), která potřebuje web. Offline ji skill přeskočí.

## 4. Zpracování závodu ⭐
**Prompt:** `Doběhl jsem Brdskou dvacítku 2026, zpracuj závod`

- **Co se stane:**
  - Stáhne oficiální výsledky: Ondra 39./162 za 1:58:12, Radek 31.
  - Stáhne data z Garminu: tempo, tep a úseky po km.
  - Přestaví `Oblasti/Kondice a Zdravi/Brdska dvacitka 2026.md`: nahoru přehled, výsledky a zážitky, dolů jeden nadpis „Před závodem“.
  - Aktualizuje `Sportovní akce` (absolvované závody, timeline) a doplní čas do denní poznámky 26. 9.
- **Pro srovnání:** `Brdska dvacitka 2025.md` je už zpracovaná. Je vidět i meziroční zlepšení o 8:28.

## 5. Dárek
**Prompt:** `Co dát Mámě k narozeninám?` nebo `Vymysli dárek pro Lucii k Vánocům`

`navrh-darku` projde historii dárků (`Oblasti/Rodina a Pratele/Darky/`), nápady a „Info k dárkům“ v poznámce člověka a navrhne něco, co se neopakuje.

## 6. Inbox
**Prompt:** `Zpracuj inbox`

- **Co se stane:** `process-inbox` přesune podcasty, najde duplicitu (`... 1.md`) i duplicitu napříč složkami (report z JOpenSpace) a navrhne:
  - tutoriál k Testcontainers připojit k existujícímu nápadu na článek,
  - recenzi deskovky Heat dát do wishlistu,
  - tip na kavárnu do `Kam`,
  - CKAD jako task.
- **Pozor:** skill se na akce ptá, nic neudělá sám.

## 7. Blog
- `Přidej blog ideu: Testcontainers v CI pipeline` – `blog-idea` založí nápad, najde podobný nápad i článek a napíše AI review.
- `Jak si vede blog za září? Které články aktualizovat?` – `plausible-blog`.
- `Vyšla Java 25, projdi JEPy` – `java-features` stáhne JEPy z openjdk.org, část z nich ještě není roztříděná. Potřebuje síť.

## 8. Údržba
- `Zkontroluj vault` – `verifikace-vaultu`. Očekávané nálezy jsou odkazy na souhrny, které ještě neexistují (`2026-W38`, `2026-09`, `2026`). Ty vzniknou ve scénáři 1.
- `Jsou už vypsané závody na jaro?` – `zavody-terminy`. Čte skutečné weby pořadatelů, takže potřebuje síť.

## 9. Učení
Learning tracker nemá vlastní skill, řídí se konvencemi v `CLAUDE.md` a pohledy v [[Uceni]]. Stav tématu se neukládá, odvozuje se ze složky a dat `zacato` / `odlozeno` / `dokonceno`.
- `Co se teď učím a co mám ve frontě?` – Claude přečte `Oblasti/Osobni rust/Temata/`, rozliší rozpracované (mají `zacato`), odložené a frontu a připomene WIP limit 2 (rozpracované jsou už dvě: Spring AI a Anglictina).
- `Chci se začít učit Kafka exactly-once` – podle postupu v [[Uceni]] má Claude ohlídat WIP limit, doplnit `zacato` a `cil`, navrhnout zdroje a napsat Big Rock do týdenního plánu.
- `Dokončil jsem Spring AI, uzavři to` – Claude doplní `dokonceno`, zeptá se na revizi výpisků a přesune poznámku do `Znalosti/Spring/`; blog idea [[Spring AI - prvni kroky s RAG]] zůstane propojená.
- `Vyplatí se mi obnovit předplatné kurzy.example?` – pohled „Koupeno nevyužito“ v [[Uceni]] a task [[Rozhodnout o obnove predplatneho kurzy.example]].

## Vlastní nápady na experimenty
- Napiš si vlastní denní poznámku na 1. 10. 2026 a nech ji zařadit do souhrnu.
- Přidej do poznámky z minulého týdne odrážku, kterou souhrn nemá, a spusť souhrn znovu. `denik_src` pozdní úpravu odhalí a skill ji doplní.
- Napiš vlastní skill: třeba „co vařit tento týden“ podle receptů ve `Znalosti/Vareni`.
