---
base: "[[Blog Ideas.base]]"
Star: false
Tags:
  - Java
Priority: Medium
AI Expected Effort: Low
AI Suggested Priority: Medium
---

- ScopedValue je od Javy 25 final - kdy nahradit ThreadLocal (request context, tenant id)
- jak to hraje s virtual threads a structured concurrency
- co Spring (zatim) pouziva pod kapotou

> [!note]+ # AI Feedback
> **Reviewed:** 2026-09-14 08:20 UTC
>
> **Overlap:** none
> **Gap value:** High — final since Java 25 and still rarely covered in Czech; ThreadLocal pitfalls with virtual threads are a real pain point.
> **Series fit:** none
> **Suggested angle:** "ThreadLocal je mrtvy, at zije ScopedValue"
>
> **Learning alignment**
> Java 25 - novinky jazyka (Medium, To Do)
>
> **Blog fit**
> Completes the Loom trio with "Virtual Threads v praxi" and the Structured Concurrency idea.
>
> **Audience impact**
> Mostly framework-minded developers and tech leads; smaller audience than virtual threads but a clear search intent ("ThreadLocal virtual threads").
>
> **Time sensitivity:** Fades slowly
> Freshly final, useful for years; best published while Java 25 adoption grows.
>
> **AI Suggested Priority:** Medium
> Good gap and alignment, but a narrower audience. Write it right after the Structured Concurrency post to reuse the demo.
>
> **AI Expected Effort:** Low
> Small API surface, one before/after example, can share the demo project with the Structured Concurrency post.
>
> **Concerns:** none
