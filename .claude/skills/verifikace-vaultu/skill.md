---
name: verifikace-vaultu
description: Zkontroluje integritu Obsidian vaultu - najde broken links (odkazy na neexistující poznámky či přílohy), orphaned attachments (přílohy, na které nevede žádný odkaz) a zvaliduje deník (chybějící souhrny, špatně zařazené poznámky, rozbité navigační bloky). Use when the user asks to verify/check the vault, "zverifikuj vault", "zkontroluj vault", "najdi broken links", "rozbité odkazy", "osiřelé přílohy", "orphaned attachments", "úklid příloh", "zkontroluj denik", or after larger migrations/reorganizations to validate nothing broke.
---

# Verifikace vaultu

Kontrola integrity vaultu: broken links, orphaned attachments a validace deníku.

## Postup

1. Spusť všechny tři kontroly z kořene vaultu (výstup první může být dlouhý — ulož ho do souboru):

   ```bash
   python .claude/skills/verifikace-vaultu/verify_vault.py > /tmp/vault_report.txt
   python .claude/skills/denik-souhrn/check_gaps.py
   python .claude/skills/verifikace-vaultu/verify_denik.py
   ```

   - `verify_vault.py` — broken links + orphaned attachments (celý vault)
   - `check_gaps.py` — chybějící týdenní/měsíční/roční souhrny deníku (žije ve skillu denik-souhrn, nevytvářej duplikát)
   - `verify_denik.py` — struktura deníku: špatně zařazené poznámky (MISPLACED), duplikáty (DUPLICATE), neplatná data/týdny (INVALID), budoucí data (FUTURE), rozbité navigační bloky (NAV), souhrny bez `## AI shrnutí` (NO-AI, jen informativní)

2. Projdi reporty (`=== BROKEN LINKS ===` a `=== ORPHANED ATTACHMENTS ===` z prvního, sekce z dalších dvou).

3. **Broken links** — u každého posuď příčinu, než navrhneš opravu:
   - **Překlep / přejmenovaný soubor** → oprav odkaz (najdi nejbližší existující název).
   - **Odkaz na budoucí poznámku** — v Obsidianu je legitimní odkazovat na dosud nevytvořenou poznámku (kliknutím se vytvoří). Nahlaš, ale neopravuj bez ptaní.
   - **Pozůstatek po smazaném souboru** → navrhni odkaz odstranit nebo obsah dohledat v `.trash/` či git historii.

4. **Orphaned attachments** — přílohy bez jediného odkazu:
   - Zkontroluj kontext (složku, název) — může jít o přílohu čekající na zpracování (např. `__INBOX/`).
   - Navrhni: smazat / přesunout do `.trash` / nechat. **Nikdy nemaž bez explicitního potvrzení uživatele.**

4b. **Denik nálezy:**
   - **Chybějící souhrny** (check_gaps) → nabídni dogenerování skillem denik-souhrn. Pozor: díra v týdnu se může propagovat do měsíce/roku (měsíční souhrn postavený z neúplných týdnů přijde o události chybějícího týdne) — u dogenerovaného týdne zkontroluj klíčové položky i v nadřazeném měsíci a roce.
   - **NAV problémy** → `link_denik.py --all` opraví chybějící bloky; **stale řádky NAD H1 souhrnu** skript neopravuje, smaž je ručně a pak spusť link_denik.
   - **MISPLACED/DUPLICATE/INVALID/FUTURE** → navrhni přesun/opravu, proveď až po potvrzení.
   - **NO-AI** je informativní (staré souhrny předcházejí konvenci) — backfill jen na výslovné přání.
   - Odkazy na budoucí období ([[2026]], aktuální týden/měsíc) v broken links jsou očekávané — vzniknou přirozeně.

5. Prezentuj výsledek stručně: počty, seskupené podle složky/typu problému, s konkrétními návrhy oprav. U velkých počtů ukaž top problémy a nabídni hromadné řešení.

## Poznámky k implementaci

- Skript řeší odkazy stylem Obsidianu: wikilinky podle basename (case-insensitive), `[[cesta/Poznamka]]`, `[[Poznamka#nadpis|alias]]`, embedy `![[...]]`, markdown odkazy `[text](relativni%20cesta)` i reference v `.base` souborech (`cover: "[[...]]"` ve frontmatteru poznámek zachytí wikilink regex).
- Ignoruje: `.obsidian`, `.claude`, `.claudian`, `.git`, `.idea`, `.trash`, skryté složky.
- Za přílohy považuje vše kromě `.md`, `.base`, `.canvas` (a servisních `.json/.js/.css/.py/.sh`).
- False positives: odkazy na nadpisy v téže poznámce (`[[#sekce]]`) skript přeskakuje, ale neověřuje existenci nadpisů; externí URL v markdown odkazech se ignorují.
