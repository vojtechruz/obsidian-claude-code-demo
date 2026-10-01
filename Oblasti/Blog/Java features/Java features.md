---
tags:
  - java
cssclasses:
  - wide
---

> [!info]- Jak tracker funguje
> - 1 poznamka `Java feature - <Tema>` = 1 tema = retezec JEPu (preview → final). Rucne se vyplnuje `Clanky`, `Napady`, `Pokryto do` (do ktere verze Javy clanek popisuje) a `Problem`; `Finalni verze` a `Sleduje se` odpovidaji tabulce.
> - Sloupec **V článku**: ✅ clanek to popisuje · ⚠️ final/zasadni JEP po clanku (dluh) · 👀 preview po clanku (jen sledovat) · — tema nema clanek.
> - Kazdy JEP ma prave jedno rozhodnuti: tabulka jednoho tematu, [[Java features - ignorované]], nebo `## Nerozhodnuté JEPy` nize.
> - Kontrola 2x rocne po vydani Javy (brezen, zari) - skill `java-features`: `jeps.py release N`, `check`, `articles`.
> - Pohled **K aktualizaci** ukazuje temata se zastaralym clankem serazena podle `Views 6mo`.

![[Java features - přehled.base]]

## Zdroje k roztřídění

### Stable Values
- https://openjdk.org/jeps/502 - lazy inicializace konstant, v Jave 25 jako preview

### Project Leyden (AOT)
- https://openjdk.org/jeps/483
- https://openjdk.org/jeps/514
- https://openjdk.org/jeps/515

### JFR profilovani
- https://openjdk.org/jeps/509 - CPU-time profiling na Linuxu

## Nerozhodnuté JEPy

| JEP | Název | Java | Skupina |
| --- | --- | --- | --- |
| [477](https://openjdk.org/jeps/477) | Implicitly Declared Classes and Instance Main Methods (Third Preview) | 23 | Compact Source Files |
| [482](https://openjdk.org/jeps/482) | Flexible Constructor Bodies (Second Preview) | 23 | Flexible Constructor Bodies |
| [492](https://openjdk.org/jeps/492) | Flexible Constructor Bodies (Third Preview) | 24 | Flexible Constructor Bodies |
| [495](https://openjdk.org/jeps/495) | Simple Source Files and Instance Main Methods (Fourth Preview) | 24 | Compact Source Files |

## Kontroly verzí

- Java 23 (2025-10-12): 12 JEPů – 5 do témat, 5 do ignore, 0 nových témat (zalozeni trackeru, 6 temat zalozeno zpetne), 2 odlozeno; zastaralo: Records a pattern matching (JEP 456 z Javy 22)
- Java 24 (2025-10-12): 24 JEPů – 6 do témat, 16 do ignore, 0 nových témat, 2 odlozeno; zastaralo: Virtual Threads
- Java 25: rozpracovano – zatim jen 2 JEPy do ignore, zbytek ceka na `jeps.py release 25`
