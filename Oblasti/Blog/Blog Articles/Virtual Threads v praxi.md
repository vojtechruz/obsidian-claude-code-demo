---
base: "[[Blog Articles.base]]"
Topics:
  - Java
Date: 2025-11-20
Draft Status: Published
Path: /virtual-threads-v-praxi/
URL: https://ondrakodi.example/virtual-threads-v-praxi/
Excerpt: Virtual threads z Javy 21 na realne Spring Boot sluzbe - kdy pomuzou, co je pinning a na co si dat pozor.
Views 6mo: 3602
---

## Osnova

- platform vs. virtual threads, jak funguje carrier thread
- zapnuti ve Spring Boot (spring.threads.virtual.enabled)
- pinning u synchronized a jak ho najit pres JFR
- benchmark: blokujici REST klient pred a po
- vznikl z prednasky na [[Java Pivo Praha]]
