---
tags:
  - kubernetes
  - znalosti
  - tahak
---

# Kubernetes – kubectl tahak

Prikazy, ktere jsem v kurzu a pak v praci pouzival nejcasteji.

## Kontext a namespace

```bash
kubectl config get-contexts
kubectl config use-context staging
kubectl config set-context --current --namespace=orders   # vychozi namespace
```

## Prohlizeni

```bash
kubectl get pods -o wide                 # na jakem nodu, IP
kubectl get pods -l app=orders           # podle labelu
kubectl get all
kubectl describe pod orders-7c9f-xk2lp   # udalosti dole = proc pod nestartuje
kubectl get events --sort-by=.lastTimestamp
kubectl top pods                         # spotreba (potrebuje metrics-server)
```

## Logy a ladeni

```bash
kubectl logs orders-7c9f-xk2lp
kubectl logs -f deployment/orders            # stream z jednoho podu deploymentu
kubectl logs orders-7c9f-xk2lp --previous    # logy z predchoziho (spadleho) kontejneru
kubectl exec -it orders-7c9f-xk2lp -- sh
kubectl port-forward svc/orders 8080:80      # lokalne na Service
kubectl debug -it orders-7c9f-xk2lp --image=busybox --target=orders
```

## Zmeny

```bash
kubectl apply -f k8s/                    # deklarativne cela slozka
kubectl diff -f k8s/                     # co by se zmenilo
kubectl scale deployment/orders --replicas=5
kubectl set image deployment/orders orders=registry.example/orders:1.4.3
kubectl delete pod orders-7c9f-xk2lp     # Deployment ho nahradi
```

## Stavy podu, ktere stoji za to znat

| Stav | Obvykle znamena |
|---|---|
| `Pending` | scheduler nenasel node (malo zdroju, nodeSelector) |
| `ImagePullBackOff` | spatny nazev image nebo chybi pristup do registry |
| `CrashLoopBackOff` | aplikace pada po startu → `logs --previous` |
| `OOMKilled` | prekrocen memory limit |
| `Running`, ale 0/1 Ready | readiness probe selhava |
