---
tags:
  - kubernetes
  - znalosti
kurz: Kubernetes pro vyvojare (online, kurzy.example)
---

# Kubernetes – Deploymenty a rollout

Modul 4 kurzu. Navazuje na [[Kubernetes - zakladni objekty]].

## Rolling update

- Vychozi strategie `RollingUpdate`: nove pody nabihaji, stare se postupne vypinaji.
- `maxSurge` – kolik podu muze byt **navic** nad `replicas` behem rolloutu (default 25 %).
- `maxUnavailable` – kolik jich muze **chybet** (default 25 %).
- Pro nase sluzby: `maxSurge: 1`, `maxUnavailable: 0` → nikdy mene kapacity, pomalejsi rollout.
- Alternativa `Recreate`: vsechno vypnout, pak zapnout – jen kdyz dve verze nesmi bezet soucasne (migrace schematu bez zpetne kompatibility).

## Probes

| Probe | Otazka | Kdyz selze |
|---|---|---|
| **startupProbe** | uz aplikace nastartovala? | do uspechu se ostatni probes nespousti; po limitu restart |
| **readinessProbe** | muze prijimat provoz? | pod se vyradi ze Service endpointu, **nerestartuje se** |
| **livenessProbe** | jeste zije? | **restart kontejneru** |

- Spring Boot Actuator: `/actuator/health/readiness` a `/actuator/health/liveness` (`management.endpoint.health.probes.enabled=true`).
- Chyba z praxe: liveness kontroluje databazi → kdyz spadne DB, Kubernetes restartuje vsechny pody dokola. Liveness ma kontrolovat jen aplikaci samotnou.

## Resources

- `requests` – co scheduler rezervuje (podle toho vybira node).
- `limits` – strop. Pres CPU limit → throttling, pres memory limit → **OOMKilled**.
- JVM v kontejneru: `-XX:MaxRAMPercentage=75` misto pevneho `-Xmx`, at heap respektuje limit.

## Rollout prikazy

```bash
kubectl rollout status deployment/orders
kubectl rollout history deployment/orders
kubectl rollout undo deployment/orders              # zpet na predchozi revizi
kubectl rollout undo deployment/orders --to-revision=3
kubectl rollout restart deployment/orders           # novy rollout bez zmeny image
```

## Horizontal Pod Autoscaler

- Skaluje `replicas` podle metriky (CPU, pamet, vlastni metriky).
- Potrebuje `requests` – procenta se pocitaji z nich.
- `kubectl autoscale deployment orders --cpu-percent=70 --min=2 --max=6`
