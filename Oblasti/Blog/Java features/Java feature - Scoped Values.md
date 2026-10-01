---
base: "[[Java features - přehled.base]]"
tags:
  - java
Clanky: []
Napady:
  - "[[Scoped Values misto ThreadLocal]]"
Pokryto do:
Finalni verze: []
Sleduje se: Scoped Values (JEP 487, Java 24)
Problem:
---

Nemenna data sdilena v ramci vlakna a jeho potomku - nahrada `ThreadLocal`. Souvisi s [[Java feature - Structured Concurrency]].

| JEP | Java | Typ | V článku |
| --- | --- | --- | --- |
| [429](https://openjdk.org/jeps/429) Scoped Values | 20 | incubator | — |
| [446](https://openjdk.org/jeps/446) Scoped Values | 21 | preview | — |
| [464](https://openjdk.org/jeps/464) Scoped Values | 22 | preview 2 | — |
| [481](https://openjdk.org/jeps/481) Scoped Values | 23 | preview 3 | — |
| [487](https://openjdk.org/jeps/487) Scoped Values | 24 | preview 4 | — |

- `orElse(null)` uz neni povolene od 4. preview

## Zdroje

- https://openjdk.org/jeps/487
