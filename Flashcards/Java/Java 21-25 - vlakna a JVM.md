---
tags:
  - flashcards/Java
---

> [!info] Konvence karticek (plugin Spaced Repetition)
> - **Slozka = balicek**: soubory v `Flashcards/Java/` patri do balicku „Java“, kazdy soubor ma tag `#flashcards/Java`.
> - Jednosmerna karticka: otazka a odpoved na jednom radku oddelene **dvema dvojteckami**.
> - Obousmerna karticka: oddelene **tremi dvojteckami** (zkousi se oba smery).
> - Viceradkova karticka: otazka, na samostatnem radku `?`, odpoved, ukonceni `+++`.
> - Doplnovacka (cloze): zvyrazneni textu dvema rovnitky z obou stran – zvyrazneny text se skryje.

## Virtual threads

Virtual threads jsou finalni od Javy ==21== (JEP 444).
Jak vytvorit executor, ktery pro kazdou ulohu spusti novy virtual thread?::`Executors.newVirtualThreadPerTaskExecutor()`

Co je „pinning“ virtualniho vlakna a co se zmenilo v Jave 24?
?
Virtual thread se nemuze odpojit od carrier (platform) vlakna, typicky pri blokovani uvnitr `synchronized`. Carrier je pak blokovany. Od Javy 24 (JEP 491) se virtual thread v `synchronized` uz nepinuje – neni nutne prepisovat na `ReentrantLock`.
+++

Proc virtual threads nepoolovat?::Jsou levne a urcene na jednu ulohu; pool omezuje jejich pocet. Na omezeni soubeznosti (napr. spojeni do DB) pouzit `Semaphore`.
Scoped Values:::Nemenna hodnota sdilena v ramci vymezeneho rozsahu volani a podrizenych vlaken – nahrada `ThreadLocal`. Finalni v Jave 25 (JEP 506).

Proc jsou Scoped Values lepsi nez `ThreadLocal` s virtual threads?
?
Jsou nemenne, plati jen po dobu `ScopedValue.where(KEY, v).run(...)` (nic se nezapomene uklidit) a dedi se do podrizenych vlaken ve structured concurrency bez kopirovani. `ThreadLocal` u milionu virtual threads zabira pamet a je mutovatelny.
+++

Structured Concurrency (`StructuredTaskScope`) je v Jave 25 ve stavu ==preview== (5. preview, JEP 505).

## JVM a GC

Ktery GC ma od Javy 23 generacni rezim jako vychozi (a v 24 negeneracni rezim odstranen)?::ZGC
Compact Object Headers (JEP 519, Java 25):::Hlavicka objektu zmensena z 12 na 8 bajtu na 64bit JVM; zapina se `-XX:+UseCompactObjectHeaders`, setri pamet a zlepsuje lokalitu.
Co prinasi AOT cache (JEP 483 v Jave 24, rozsireni v 25)?::Rychlejsi start: tridy nactene a slinkovane z trenovaciho behu se ulozi do cache a pouziji pri dalsim startu (`-XX:AOTCache`).
Security Manager je od Javy ==24== trvale vypnuty (JEP 486).
Ktere verze Javy jsou LTS v rade 21–25?::Java 21 (zari 2023) a Java 25 (zari 2025).
