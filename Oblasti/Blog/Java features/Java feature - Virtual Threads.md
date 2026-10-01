---
base: "[[Java features - přehled.base]]"
tags:
  - java
Clanky:
  - "[[Virtual Threads v praxi]]"
Napady: []
Pokryto do: 21
Finalni verze:
  - 21
  - 24
Sleduje se:
Problem:
---

Lehka vlakna z projektu Loom. Navazuji na ne [[Java feature - Structured Concurrency]] a [[Java feature - Scoped Values]].

| JEP | Java | Typ | V článku |
| --- | --- | --- | --- |
| [425](https://openjdk.org/jeps/425) Virtual Threads | 19 | preview | ✅ |
| [436](https://openjdk.org/jeps/436) Virtual Threads | 20 | preview 2 | ✅ |
| [444](https://openjdk.org/jeps/444) Virtual Threads | 21 | **final** | ✅ |
| [491](https://openjdk.org/jeps/491) Synchronize Virtual Threads without Pinning | 24 | **final** | ⚠️ |

- clanek popisuje pinning u `synchronized` jako hlavni past - od Javy 24 (JEP 491) uz `synchronized` vlakno nepinuje
- navrh: update sekce o pinningu + banner "plati pro Javu 21-23", zbytek clanku plati

## Zdroje

- https://openjdk.org/jeps/444
- https://openjdk.org/jeps/491
