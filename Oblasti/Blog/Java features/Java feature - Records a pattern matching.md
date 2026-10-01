---
base: "[[Java features - přehled.base]]"
tags:
  - java
Clanky:
  - "[[Records a pattern matching v Jave 21]]"
Napady: []
Pokryto do: 21
Finalni verze:
  - 16
  - 21
  - 22
Sleduje se: Primitive Types in Patterns, instanceof, and switch (JEP 488, Java 24)
Problem:
---

Records, pattern matching pro `instanceof` a `switch`, record patterns a navazujici rozsireni. Sealed tridy (JEP 409, Java 17) clanek zminuje, ale samostatne se nesleduji.

| JEP | Java | Typ | V článku |
| --- | --- | --- | --- |
| [305](https://openjdk.org/jeps/305) Pattern Matching for instanceof | 14 | preview | ✅ |
| [359](https://openjdk.org/jeps/359) Records | 14 | preview | ✅ |
| [375](https://openjdk.org/jeps/375) Pattern Matching for instanceof | 15 | preview 2 | ✅ |
| [384](https://openjdk.org/jeps/384) Records | 15 | preview 2 | ✅ |
| [394](https://openjdk.org/jeps/394) Pattern Matching for instanceof | 16 | **final** | ✅ |
| [395](https://openjdk.org/jeps/395) Records | 16 | **final** | ✅ |
| [406](https://openjdk.org/jeps/406) Pattern Matching for switch | 17 | preview | ✅ |
| [420](https://openjdk.org/jeps/420) Pattern Matching for switch | 18 | preview 2 | ✅ |
| [405](https://openjdk.org/jeps/405) Record Patterns | 19 | preview | ✅ |
| [427](https://openjdk.org/jeps/427) Pattern Matching for switch | 19 | preview 3 | ✅ |
| [432](https://openjdk.org/jeps/432) Record Patterns | 20 | preview 2 | ✅ |
| [433](https://openjdk.org/jeps/433) Pattern Matching for switch | 20 | preview 4 | ✅ |
| [440](https://openjdk.org/jeps/440) Record Patterns | 21 | **final** | ✅ |
| [441](https://openjdk.org/jeps/441) Pattern Matching for switch | 21 | **final** | ✅ |
| [443](https://openjdk.org/jeps/443) Unnamed Patterns and Variables | 21 | preview | ✅ |
| [456](https://openjdk.org/jeps/456) Unnamed Variables & Patterns | 22 | **final** | ⚠️ |
| [455](https://openjdk.org/jeps/455) Primitive Types in Patterns, instanceof, and switch | 23 | preview | 👀 |
| [488](https://openjdk.org/jeps/488) Primitive Types in Patterns, instanceof, and switch | 24 | preview 2 | 👀 |

- clanek uvadi `_` jako preview featuru - od Javy 22 final (JEP 456): staci banner / jedna veta
- primitive types in patterns jen sledovat, clanek az to bude final

## Zdroje

- https://openjdk.org/jeps/440
- https://openjdk.org/jeps/441
- https://openjdk.org/jeps/456
