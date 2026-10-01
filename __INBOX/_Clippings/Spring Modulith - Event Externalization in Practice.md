---
title: "Spring Modulith - Event Externalization in Practice"
source: "https://spring.io/blog/"
author: ""
published:
created: 2026-09-02
description: >-
  How to publish application module events to Kafka with Spring Modulith event externalization, the event publication registry and retries.
tags:
  - "clippings"
---
## Highlights

- Event publication registry uklada udalosti do tabulky v te same transakci jako business data.
- `@Externalized("orders.created")` na udalosti = posle se do Kafky.
- Nedokoncene publikace se pri startu daji znovu odeslat.

Podklad k dilu 4 serie (produkcni zkusenosti).
