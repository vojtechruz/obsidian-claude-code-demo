---
priorita: stredni
kategorie: Java
---

- proc: startup Spring Boot sluzeb v Kubernetes je 8 s, native image slibuje pod sekundu
- co chci zjistit: reflexe a hints, build cas, kolik z nasich knihoven to zvladne

> [!ai]- AI material (nezpracovano)
> **GraalVM Native Image - shrnuti z chatu**
> - AOT kompilace celeho programu do nativniho binarky; zadny JIT, closed-world assumption
> - Reflexe, proxy a resources je nutne deklarovat (reachability metadata), Spring Boot 3+ to generuje pres AOT engine
> - Plusy: start v desitkach ms, nizka pamet. Minusy: dlouhy build, peak throughput nizsi nez JIT, slozitejsi debugging
> - Typicky vhodne pro serverless a CLI, mene pro dlouho bezici sluzby s vysokou zatezi
