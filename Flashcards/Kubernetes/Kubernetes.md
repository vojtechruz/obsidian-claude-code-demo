---
tags:
  - flashcards/Kubernetes
---

> [!info] Konvence karticek (plugin Spaced Repetition)
> - **Slozka = balicek**: soubory v `Flashcards/Kubernetes/` patri do balicku „Kubernetes“, tag `#flashcards/Kubernetes`.
> - Jednosmerna karticka: otazka a odpoved oddelene **dvema dvojteckami**, obousmerna **tremi dvojteckami**.
> - Viceradkova: otazka, `?` na samostatnem radku, odpoved, ukonceni `+++`.
> - Doplnovacka (cloze): zvyrazneni textu dvema rovnitky z obou stran.
> - Podklady: `Znalosti/Kubernetes` (poznamky z kurzu Kubernetes pro vyvojare).

Kde Kubernetes uklada stav clusteru?::V `etcd` (distribuovane key-value uloziste).
Ktera komponenta rozhoduje, na jaky node pujde novy pod?::`kube-scheduler`
Komponenta na kazdem nodu, ktera spousti a hlida pody, se jmenuje ==kubelet==.
Deployment:::Objekt pro bezstavove aplikace – drzi pozadovany pocet replik pres ReplicaSet a umi rolling update a rollback.
StatefulSet:::Objekt pro stavove aplikace – kazdy pod ma stabilni jmeno a vlastni PersistentVolume (databaze, Kafka).
DaemonSet:::Zajisti jeden pod na kazdem nodu (logovani, monitoring).
Jak Service najde sve pody?::Pres label selector – vybere pody s odpovidajicimi labely.

Jaky je rozdil mezi readiness a liveness probe?
?
- **Readiness** selze → pod se vyradi z endpointu Service, nedostava provoz, ale bezi dal.
- **Liveness** selze → kubelet kontejner restartuje.
Liveness nema kontrolovat zavislosti (DB), jinak vypadek DB restartuje vsechny pody.
+++

Co znamena stav `CrashLoopBackOff` a jak zacit ladit?::Kontejner opakovane pada po startu; `kubectl logs <pod> --previous` a `kubectl describe pod <pod>`.
Co se stane, kdyz kontejner prekroci memory limit?::Je zabit (OOMKilled) a restartovan.
Co se stane, kdyz kontejner prekroci CPU limit?::Je throttlovany (zpomaleny), nezabije se.
Parametr rolling updatu, ktery urcuje, kolik podu muze byt navic nad pozadovanym poctem: ==maxSurge==.
Jak vratit Deployment na predchozi verzi?::`kubectl rollout undo deployment/<nazev>`
Jsou Secrets v Kubernetes sifrovane?::Ve vychozim stavu ne – jen base64. Ochrana je RBAC a sifrovani etcd at rest.

Jak dostat konfiguraci z ConfigMap do podu a jaky je rozdil?
?
1. **env promenne** (`envFrom`) – zmena se projevi az po restartu podu.
2. **volume** – soubory se aktualizuji samy, aplikace je musi znovu nacist.
+++

Prikaz pro presmerovani lokalniho portu 8080 na Service `orders` (port 80)::`kubectl port-forward svc/orders 8080:80`
