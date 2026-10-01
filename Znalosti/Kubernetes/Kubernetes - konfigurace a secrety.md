---
tags:
  - kubernetes
  - znalosti
kurz: Kubernetes pro vyvojare (online, kurzy.example)
---

# Kubernetes – konfigurace a secrety

Modul 5 kurzu.

## ConfigMap

- Necitliva konfigurace jako key-value nebo cele soubory.
- Do podu dvema zpusoby:
  - **env promenne** (`envFrom: configMapRef`) – zmena se projevi az po restartu podu,
  - **volume** – soubory se aktualizuji samy (s par desitkami sekund zpozdeni), ale aplikace je musi znovu nacist.
- Spring Boot: `spring.config.import=optional:configtree:/etc/config/` nacte soubory z volume jako properties.

## Secret

- Stejne jako ConfigMap, ale pro hesla a tokeny.
- **Base64 neni sifrovani** – kdo ma pravo cist Secrets v namespace, vidi hesla. Dulezite je RBAC a sifrovani etcd.
- V praxi externi spravce (Vault, cloudovy secret manager) + operator, ktery Secret vytvori.
- Nikdy necommitovat Secret YAML do gitu; pokud uz, tak sifrovany (Sealed Secrets, SOPS).

## Priklad

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: orders-config
data:
  SPRING_PROFILES_ACTIVE: prod
  ORDERS_BATCH_SIZE: "200"
---
apiVersion: v1
kind: Secret
metadata:
  name: orders-db
type: Opaque
stringData:
  SPRING_DATASOURCE_PASSWORD: zmenit-me
```

```yaml
# v Deploymentu
envFrom:
  - configMapRef:
      name: orders-config
  - secretRef:
      name: orders-db
```

## Tipy

- Zmena ConfigMap neudela rollout. Trik: hash obsahu ConfigMap do anotace podu (Helm `checksum/config`), pak zmena = novy rollout.
- `kubectl create secret generic orders-db --from-literal=...` je rychle na zkouseni, ale do produkce patri deklarativne.
