---
base: "[[Blog Ideas.base]]"
Star: true
Tags:
  - Java
Priority: High
AI Expected Effort: Medium
AI Suggested Priority: High
---

- StructuredTaskScope po prepracovani API v Jave 25 (Joiner, open() misto konstruktoru)
- srovnani s CompletableFuture na realnem prikladu - paralelni volani tri sluzeb v objednavce
- navaznost na [[Virtual Threads v praxi]]
%%idealne jako talk na Java Pivo Praha a pak clanek%%

https://openjdk.org/jeps/505

> [!note]+ # AI Feedback
> **Reviewed:** 2026-09-12 19:40 UTC
>
> **Overlap:** partial — existing post: "Virtual Threads v praxi"
> **Gap value:** High — no post covers structured concurrency, and the Java 25 API redesign makes most existing tutorials outdated.
> **Series fit:** none
> **Suggested angle:** "Structured Concurrency v Jave 25: konec CompletableFuture spaget?"
>
> **Learning alignment**
> none
>
> **Blog fit**
> Natural follow-up to "Virtual Threads v praxi", which is still the most-read Java post. Together with the planned Scoped Values idea it could form a small Loom mini-series.
>
> **Audience impact**
> Java developers running Spring Boot services with fan-out calls are the core readership. The topic is actively discussed after each preview round, so search and sharing potential is good.
>
> **Time sensitivity:** Fades slowly
> Still in preview (fifth preview in Java 25, another one in 26), so the article needs a banner until it goes final, but the concepts stay valid.
>
> **AI Suggested Priority:** High
> Starred by the author, author priority High, strong gap and synergy with the most-read Java post. Preview status is the only reason not to go Very High.
>
> **AI Expected Effort:** Medium
> Needs a runnable demo and a comparison with CompletableFuture; virtual threads background can be reused from the existing post.
>
> **Concerns:**
> - API may still change before final — keep code samples minimal and pin the Java version.
