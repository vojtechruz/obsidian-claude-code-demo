---
tags:
  - uceni
cssclasses:
  - wide
---

# Uceni

## Quick Info

Learning tracker: co se chci naucit, co se prave ucim a z ceho. **Fronta a rozpracovana temata jsou tady, hotove znalosti ve `Znalosti/`.**

- **Temata** (`Oblasti/Osobni rust/Temata/`): jedna poznamka na tema, zaroven tracker i misto pro vypisky. Vlastnosti `priorita` (vysoka / stredni / nizka), `kategorie`, `zdroje`, `cil`, `zacato`, `odlozeno`, volitelne `v_praci`, `blog`. Prazdna poznamka s radkem "proc" = polozka fronty; obsah vznika az pri studiu.
- **Zadna vlastnost stav** - stav se odvozuje: *fronta* = v `Temata/` bez `zacato`; *rozpracovano* = ma `zacato` (**max 2 najednou**); *odlozeno* = ma `odlozeno` (datum + radek, kde jsem skoncil); *hotovo* = ma `dokonceno` a lezi ve `Znalosti/<obor>/`.
- **Hotove tema se presune** z `Temata/` do `Znalosti/<obor>/` (napr. [[Prednaseni - prace s publikem]]). Male rozsireni existujicich vypisku se misto presunu vlije jako sekce do te poznamky; takove tema ma v prvnim radku tela `Rozsiruje [[...]]` (napr. [[Kubernetes - networking a Helm]]).
- **Zdroje** (`Oblasti/Osobni rust/Zdroje/`): jen kurzy a platformy, ktere se konzumuji pres vic sezeni (`typ`, `platforma`, `koupeno`, `zacato`, `dokonceno`, `url`, u predplatnych `plati_do`). Knihy zustavaji v `Media/` a tema na ne odkazuje primo. Clanky, videa a dokumentace patri do tematu do sekce `## Zdroje`, s jednim radkem proc.
- **AI obsah** (zkopirovane odpovedi z chatu) patri do sbaleneho calloutu `> [!ai]- AI material (nezpracovano)`; vlastni vypisky mimo nej. Po zpracovani callout smazat. Priklad: [[GraalVM native image]].

**Postup u tematu:** *Start* - zkontrolovat WIP limit, doplnit `zacato` a `cil` (jedna veta: kdy je hotovo), vybrat `zdroje` a dat zdroji `zacato`. *Behem* - vypisky do poznamky, nejasnosti do `## Otevrene otazky`, Big Rock v [[Aktualni plan|tydennim planu]], napady na clanek pres `blog-idea`. *Konec* - splneny cil, `zrevidovano: true`, `dokonceno`, presun do `Znalosti/<obor>/`; u zdroje `dokonceno`.

---

## Rozpracovano

![[System/Bases/Uceni.base#Rozpracovano]]

---

## Fronta

![[System/Bases/Uceni.base#Fronta]]

---

## Zdroje - rozpracovane

![[System/Bases/Zdroje.base#Rozpracovano]]

## Zdroje - koupene a nevyuzite

![[System/Bases/Zdroje.base#Koupeno nevyuzito]]

---

## Podle kategorie

![[System/Bases/Uceni.base#Podle kategorie]]

## Prehledy

- Vsechna temata: [[System/Bases/Uceni.base|Uceni.base]] (pohledy Hotovo, Odlozeno, V praci) - vsechny zdroje: [[System/Bases/Zdroje.base|Zdroje.base]]
- Karticky k opakovani: `Flashcards/Java`, `Flashcards/Kubernetes`
