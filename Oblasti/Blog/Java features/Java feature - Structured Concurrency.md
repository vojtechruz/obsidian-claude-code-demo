---
base: "[[Java features - přehled.base]]"
tags:
  - java
Clanky: []
Napady:
  - "[[Structured Concurrency in Java 25]]"
Pokryto do:
Finalni verze: []
Sleduje se: Structured Concurrency (JEP 499, Java 24)
Problem:
---

Strukturovana konkurence - skupina subtasku jako jedna jednotka prace (StructuredTaskScope). Stavi na [[Java feature - Virtual Threads]].

| JEP | Java | Typ | V článku |
| --- | --- | --- | --- |
| [428](https://openjdk.org/jeps/428) Structured Concurrency | 19 | incubator | — |
| [437](https://openjdk.org/jeps/437) Structured Concurrency | 20 | incubator 2 | — |
| [453](https://openjdk.org/jeps/453) Structured Concurrency | 21 | preview | — |
| [462](https://openjdk.org/jeps/462) Structured Concurrency | 22 | preview 2 | — |
| [480](https://openjdk.org/jeps/480) Structured Concurrency | 23 | preview 3 | — |
| [499](https://openjdk.org/jeps/499) Structured Concurrency | 24 | preview 4 | — |

- dlouhy preview, API se v Jave 25 vyrazne meni (Joiner, `StructuredTaskScope.open()`) - s clankem pockat aspon na 25

## Zdroje

- https://openjdk.org/jeps/499
