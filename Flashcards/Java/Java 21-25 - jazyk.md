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
> - Zdroje: JEPy na openjdk.org, tracker `Oblasti/Blog/Java features`.

## Pattern matching a records

Ve ktere verzi Javy je finalni pattern matching pro `switch` (JEP 441)?::Java 21
Record patterns (JEP 440) jsou finalni od Javy ==21==.
Co je record pattern?:::Destrukce recordu primo ve vzoru, napr. `if (o instanceof Point(int x, int y))`.
Jak se v Jave 22+ zapise nepouzita promenna nebo cast vzoru?::Podtrzitkem `_` (unnamed variables & patterns, JEP 456, finalni v Jave 22).

Co musi platit pro `switch` nad sealed interface, aby nepotreboval `default`?
?
Vsechny povolene podtypy (`permits`) musi byt pokryte vetvemi – kompilator kontroluje uplnost (exhaustiveness). Kdyz pozdeji pribude podtyp, kod prestane kompilovat, coz je zadouci.
+++

K cemu je v `switch` klicove slovo `when`?::Guard – dodatecna podminka vetve, napr. `case Order o when o.total() > 1000 ->`.
Primitive types in patterns (`instanceof int i`, `switch` nad `long`) jsou v Jave 25 stale ve stavu ==preview== (3. preview, JEP 507).

## Kolekce a streamy

Sequenced Collections (Java 21) pridavaji metody:::`getFirst()`, `getLast()`, `addFirst()`, `addLast()`, `removeFirst()`, `removeLast()` a `reversed()`.
Jak v Jave 21 ziskat posledni prvek `List` bez `list.get(list.size() - 1)`?::`list.getLast()`
Stream Gatherers (`Stream.gather(...)`) jsou finalni od Javy ==24== (JEP 485).

Co resi Stream Gatherers?
?
Vlastni mezilehle operace streamu (jako `collect` pro terminalni). Vestavene v `Gatherers`: `windowFixed`, `windowSliding`, `fold`, `scan`, `mapConcurrent`. Napr. `stream.gather(Gatherers.windowFixed(3))` vraci skupiny po trech.
+++

## Mene ceremonie

Compact source files a instance main methods (JEP 512) – co umoznuji?
?
Program bez deklarace tridy a s `void main()` bez `static` a `String[] args`. Finalni v Jave 25. Spolu s `IO.println(...)` idealni pro vyuku a skripty.
+++

Module import declarations:::`import module java.base;` naimportuje vsechny exportovane balicky modulu. Finalni v Jave 25 (JEP 511).
Flexible constructor bodies (JEP 513, Java 25) dovoluji psat prikazy ==pred== volanim `super(...)` nebo `this(...)`, napr. validaci argumentu.
Jak spustit program o vice zdrojovych souborech bez kompilace (Java 22+)?::`java Main.java` – launcher dohleda a zkompiluje i ostatni potrebne soubory (JEP 458).
Markdown v dokumentacnich komentarich (Java 23) se pise za::`///` misto `/** */` (JEP 467).
