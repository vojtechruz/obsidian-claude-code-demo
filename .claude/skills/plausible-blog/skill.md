---
name: plausible-blog
description: Načte statistiky návštěvnosti blogu ondrakodi.example z Plausible Analytics (Stats API v2) — návštěvníci, zobrazení, bounce rate, délka návštěvy, nejčtenější články, zdroje návštěv, země, zařízení, UTM kampaně, vývoj v čase, goals/custom eventy — a namapuje stránky na poznámky v Oblasti/Blog/Blog Articles. Use when the user asks about blog traffic or analytics — "statistiky blogu", "návštěvnost blogu", "kolik lidí čte blog", "nejčtenější články", "jak si vede článek X", "odkud chodí návštěvníci", "plausible", "blog analytics", "top posts", "how is my blog doing" — or wants traffic data to decide which articles to update or promote.
---

# Plausible statistiky blogu

Čte data z [Plausible](https://plausible.io) přes Stats API v2 (`POST /api/v2/query`). Skript `plausible_stats.py` je vedle tohoto souboru, používá jen standardní knihovnu Pythonu. Blog `ondrakodi.example` je statický web s Plausible skriptem v šabloně stránky.

> **Demo:** v demu běží nad fixtures v `demo_data/`: `site.json` jsou fiktivní denní čísla blogu (10/2024–1. 10. 2026, 12 článků + homepage, tagy) a `fake_api.py` nad nimi odpovídá na dotazy Stats API v2 stejným tvarem odpovědi. „Dnes“ je v demu 1. 10. 2026, takže `30d` = září 2026. Skript to ohlásí řádkem `[demo]` na stderr. Pro reálná data složku `demo_data/` smaž a vytvoř `~/.plausible/config.json` (viz Konfigurace).

## Konfigurace (jednorázově)

API klíč leží **mimo vault** v `~/.plausible/config.json`, aby se nedostal do synchronizace ani do gitu:

```json
{"api_key": "...", "site_id": "ondrakodi.example"}
```

- Klíč se vytváří v Plausible: *Account settings → API Keys → New API Key → Stats API*.
- `site_id` je doména webu přesně tak, jak je v Plausible dashboardu (URL `plausible.io/<site_id>`). Preview deploye mají v Plausible vlastní site, **ptej se na produkční**.
- Proměnné prostředí `PLAUSIBLE_API_KEY` / `PLAUSIBLE_SITE_ID` mají přednost před souborem.
- Když skript skončí hláškou „Chybi API klic“, požádej uživatele, ať soubor vytvoří sám. **Nikdy nechtěj klíč do chatu** a nezapisuj ho do vaultu.

## Příkazy

Spouštění z kořene vaultu: `python ".claude/skills/plausible-blog/plausible_stats.py" <příkaz>`.

| Příkaz | K čemu |
| --- | --- |
| `overview --period 30d` | Souhrn webu (návštěvníci, návštěvy, zobrazení, stránek/návštěva, bounce, délka) + srovnání s předchozím obdobím |
| `pages --period 30d --limit 20` | Nejčtenější stránky; články jako `[[wikilink]]` na poznámku v Blog Articles + datum publikace + změna |
| `pages --articles-only` | Jen články (bez homepage, tagů, archivu) |
| `page <slug\|/cesta/\|URL\|název poznámky>` | Detail jednoho článku: souhrn, zdroje návštěv, vývoj v čase (default 12mo) |
| `breakdown source` | Rozpad podle dimenze. Aliasy: `source`, `referrer`, `channel`, `country`, `city`, `device`, `browser`, `os`, `entry`, `exit`, `utm_source`, `utm_medium`, `utm_campaign`, `goal`, `page`, nebo plný název `visit:…` / `event:…` |
| `timeseries --period 12mo --interval month` | Vývoj návštěvnosti (`day` / `week` / `month`) |
| `goals` | Goals a custom eventy (např. `Outbound Link: Click`, `Copy Code`, `404`) |
| `summary START END` | Blok do Carpe Diem souhrnů (týden/měsíc/rok): zobrazení celkem + top 5 článků podle zobrazení. Volá ho `carpe-summary` (krok 2c) |
| `query '<json>'` | Libovolný dotaz Stats API v2 bez `site_id` (doplní se sám), pro nestandardní otázky |

Společné volby: `--period`, `--from YYYY-MM-DD --to YYYY-MM-DD`, `--json` (surová odpověď), `--no-compare`.

**Periody:** `7d`, `28d`, `30d`, `91d`, `365d` (N celých dní končících **včera**, protože dnešek je neúplný), `month` / `year` (od začátku měsíce/roku, srovnává se stejně dlouhý úsek předchozího měsíce/roku), `last-month`, `last-year`, `6mo` / `12mo` (celé měsíce), `YYYY-MM`, `YYYY`, `day`, `24h`, `all` (poslední tři bez srovnání).

## Návštěvnost v poznámkách článků

Poznámky v `Oblasti/Blog/Blog Articles/` mají ve frontmatteru `Path` (cesta článku na webu, např. `/spring-modulith-uvod/`) a `Date` (datum publikace) – podle nich skript mapuje stránky na poznámky. Volitelně můžou mít i `Views 6mo` (zobrazení za posledních 6 celých měsíců) a `AI Update Priority` z review článků. Tyhle hodnoty **nepíše tento skill** (udržují se ručně nebo samostatným synchronizačním skriptem). Když se uživatel ptá, který článek aktualizovat, čti nejdřív je. Dotaz na API dělej jen tehdy, když jsou zastaralé nebo když chybí.

## Postup

0. **Zkontroluj vyloučení vlastních návštěv** v prohlížeči (sekce níže), jednou za session, bez blokování zbytku.
1. **Pochop otázku** a vyber příkaz. Obecné „jak si vede blog“ → `overview` + `pages --articles-only --limit 10`. Otázka na konkrétní článek → `page`. Když uživatel článek nazve volně („ten o Testcontainers“), najdi poznámku v `Oblasti/Blog/Blog Articles/` a předej její název nebo slug.
2. **Spusť skript** a výstup (Markdown tabulky, české popisky) použij přímo. Čísla nepřepočítávej ručně. Pro vlastní výpočty (poměry, trendy přes víc dotazů) vezmi `--json`.
3. **Interpretuj**, ne jen opiš: co roste a co padá, které staré články pořád táhnou (sloupec *Publikováno*), odkud chodí návštěvnost. Hlídej rate limit (600 dotazů/hod) a nedělej zbytečné smyčky přes všechny články. Na celkový přehled stačí jeden `pages` dotaz s vyšším `--limit`.
4. **Propojení s vaultem:**
   - Články v tabulkách jsou `[[wikilinky]]` na poznámky v Blog Articles. Stránky bez poznámky (homepage, tagy, stránky mimo databázi) zůstávají jako `` `/cesta/` ``.
   - Hodí se to k rozhodování, co aktualizovat: články s vysokou návštěvností a `AI Review` callout se zastaralými informacemi jsou kandidáti na update. Navazující díly série (např. [[Spring Modulith serie]]) se vyplatí propagovat u článků, které táhnou.
5. **Ukládání do vaultu jen na požádání.** Report pak zapiš do `Oblasti/Blog/Statistiky/Plausible YYYY-MM.md` (nebo jiné místo, které uživatel řekne). Do poznámky dej období, výstupy skriptu a krátké shrnutí. Frontmatter poznámek v Blog Articles ani `.base` soubory needituj bez výslovného pokynu.

## Vyloučení vlastních návštěv (kontrola prohlížeče)

Uživatel si vylučuje vlastní návštěvy z Plausible flagem `localStorage.plausible_ignore = "true"`, který musí být
v každém prohlížeči zvlášť (kontroluje se jen prohlížeč připojený přes Claude in Chrome; ostatní zařízení si hlídá uživatel).
**V demu (fixtures, doména `.example`) kontrolu přeskoč.**
Flag zmizí, když se v prohlížeči smažou „Cookies a další data webů“, takže se tiše rozbije. Proto při každém spuštění
tohoto skillu **jednou za session** zkontroluj a případně obnov, pokud jsou k dispozici nástroje Claude in Chrome
(`mcp__claude-in-chrome__*`):

1. Načti nástroje jedním voláním ToolSearch:
   `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__tabs_close_mcp`
2. `navigate` na `https://ondrakodi.example/` (bez `tabId` si vytvoří vlastní záložku), pak `javascript_tool`:

   ```js
   const had = localStorage.getItem('plausible_ignore') === 'true';
   if (!had) localStorage.setItem('plausible_ignore', 'true');
   ({ had, now: localStorage.getItem('plausible_ignore'), browser: navigator.userAgentData?.brands.map(b => b.brand).join(', ') })
   ```

3. Záložku zavři přes `tabs_close_mcp`.
4. Do odpovědi dej jednu větu: „Vyloučení vlastních návštěv v prohlížeči: nastavené.“ nebo „… chybělo, nastavil jsem ho
   znovu.“ Když chybělo, dodej, že statistiky od posledního smazání dat prohlížeče mohou obsahovat vlastní návštěvy.

Kontrola nesmí zdržet čtení statistik: když rozšíření není připojené nebo nástroj selže, jednou větou to řekni a
pokračuj. Nespouštěj `plausible(...)` ručně, to by při chybějícím flagu odeslalo skutečnou událost. Jiná zařízení
(mobil, další prohlížeče) takhle ověřit nejdou, ta řeší uživatel sám.

## Poznámky

- `page` filtruje `event:page` na cestu s koncovým lomítkem i bez něj. Souhrnné metriky (návštěvy, bounce, délka) se pak týkají **návštěv, které danou stránku viděly**, ne jen té jedné stránky.
- Když Plausible vrátí varování (např. importovaná data nebo metrika, kterou nejde spočítat), skript ho připojí jako `> [!warning]` callout. Zmiň ho v odpovědi.
- Chyba 401 znamená neplatný klíč, chyba s `site` znamená špatné `site_id`. Obojí opraví uživatel v `~/.plausible/config.json`.
- Dokumentace API: https://plausible.io/docs/stats-api
