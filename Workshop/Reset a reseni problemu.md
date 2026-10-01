# Reset a řešení problémů

## Vrátit vault do výchozího stavu

Skills vault mění: píšou souhrny, přestavují poznámku závodu, zakládají plán. Po vyzkoušení vrátíš vše do stavu z repa:

```bash
git status                 # co se změnilo
git checkout -- .          # vrátit změněné soubory
git clean -fd              # smazat nově vytvořené soubory a složky
```

Jen jeden soubor: `git checkout -- "Oblasti/Kondice a Zdravi/Brdska dvacitka 2026.md"`.

> Obsidian během resetu klidně nech otevřený. Soubory si znovu načte sám.

## Co jde na internet

| Co | Kam |
| --- | --- |
| `zavody-terminy` | weby pořadatelů závodů |
| `java-features` | openjdk.org (seznam JEPů) |
| Claude Code | Anthropic API |

Všechno ostatní běží lokálně nad fixtures v `demo_data/` a nad demo kalendářem.

## Co je předem povolené

`.claude/settings.json` povoluje bez ptaní `python`/`python3` v Bash i PowerShellu (skripty skills) a nástroje demo kalendáře. Projektové nastavení začne platit, až při prvním spuštění `claude` potvrdíš důvěru ke složce. Zápis souborů a ostatní příkazy se schvalují normálně. Po workshopu nebo na vlastním vaultu si oprávnění nastav podle sebe.

## Problémy

**Skill se nespustil.**
- Claude vybírá skill podle `description` v `skill.md`. Zkus formulaci z [[Scenare]], nebo ho zavolej výslovně: `/tydenni-plan 2026-W41`.
- Ověř, že `claude` běží z kořene repa (`.claude/skills/` musí být vidět).

**Kalendář nefunguje / „demo-calendar“ chybí.**
- `claude mcp list` nebo `/mcp`: server se zapíná sám přes `enableAllProjectMcpServers` v `.claude/settings.json`. Když ho tvoje globální nastavení přebije, schval ho ručně.
- Nemáš příkaz `python` (Linux, macOS): v `.mcp.json` ho přepiš na `python3`.
- Ruční test: `echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python .claude/mcp/demo-calendar/server.py`

**Skript hlásí chybu kvůli `python`.** Skripty potřebují Python 3.8+ a stačí jim standardní knihovna. Na Linuxu a macOS piš `python3`.

**Plán týdne plánuje špatný týden.** Skripty berou „dnes“ ze systému. Týden zadej výslovně (`2026-W41`), nebo napiš „předstírej, že je 1. 10. 2026“.

**Skill chce přihlášení ke Garminu nebo Plausible.** Nejspíš chybí složka `demo_data/` vedle skriptu. Obnov ji přes `git checkout -- .claude/skills`.

**Rozbité odkazy na `2026`, `2026-09`, `2026-W38`.** To je v pořádku: jsou to souhrny, které ještě nevznikly (viz [[Scenare]], scénář 1).

## Přepnutí na skutečná data

Smaž `demo_data/` u daného skillu a nastav přístup podle jeho `skill.md`:
- **Garmin:** `pip install garminconnect`, pak jednorázově `garmin_login.py`.
- **Plausible:** API klíč a site ID.
- **Kalendář:** napoj Google Calendar MCP a v `tydenni-plan/skill.md` změň prefix toolů.
