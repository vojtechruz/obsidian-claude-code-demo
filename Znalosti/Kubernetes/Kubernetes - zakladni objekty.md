---
tags:
  - kubernetes
  - znalosti
kurz: Kubernetes pro vyvojare (online, kurzy.example)
---

# Kubernetes – zakladni objekty

Poznamky z online kurzu **Kubernetes pro vyvojare** (fiktivni, kurzy.example), ktery jsem zacal 19. 1. 2026. Modul 1–3. Karticky k opakovani: `Flashcards/Kubernetes`.

## Architektura v kostce

- **Control plane:** `kube-apiserver` (vse jde pres nej), `etcd` (stav clusteru, key-value), `kube-scheduler` (kam s podem), `kube-controller-manager` (smycky, ktere dotahuji skutecny stav k pozadovanemu).
- **Node:** `kubelet` (spousti pody na nodu), `kube-proxy` (sitova pravidla pro Service), container runtime (containerd).
- Vsechno je **deklarativni**: popisu pozadovany stav v YAML, controller ho dotahuje.

## Objekty

| Objekt | K cemu | Poznamka |
|---|---|---|
| **Pod** | nejmensi jednotka, 1+ kontejneru se sdilenou siti a volumes | sam o sobe se nerestartuje po smazani – nikdy nepouzivat holy pod |
| **ReplicaSet** | drzi N kopii podu | primo nepouzivat, ridi ho Deployment |
| **Deployment** | bezstavove aplikace, rolling update, rollback | nase Spring Boot sluzby |
| **StatefulSet** | stabilni identita a disk pro kazdy pod | databaze, Kafka |
| **DaemonSet** | jeden pod na kazdem nodu | logovani, monitoring |
| **Job / CronJob** | jednorazova / planovana uloha | noci reporty |
| **Service** | stabilni adresa pro sadu podu (label selector) | ClusterIP, NodePort, LoadBalancer |
| **Ingress** | HTTP routing zvenku na Services | potrebuje ingress controller |
| **ConfigMap / Secret** | konfigurace mimo image | viz [[Kubernetes - konfigurace a secrety]] |
| **Namespace** | logicke oddeleni (tymy, prostredi) | |

## Labels a selectors

- Labely jsou key-value na objektech (`app: orders`, `tier: backend`).
- Service a Deployment hledaji pody **pres selector** – kdyz label nesedi, Service nema endpointy a nic nefunguje. Nejcastejsi chyba v kurzu (u me 2×).

## Minimalni Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orders
  template:
    metadata:
      labels:
        app: orders
    spec:
      containers:
        - name: orders
          image: registry.example/orders:1.4.2
          ports:
            - containerPort: 8080
```

Dalsi: [[Kubernetes - Deploymenty a rollout]], [[Kubernetes - kubectl tahak]].
