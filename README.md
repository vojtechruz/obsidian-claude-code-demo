# Obsidian + Claude Code – demo vault (JOpenSpace 2026)

Ukázkový Obsidian vault s **vymyšlenou personou** Ondrou Kratochvílem, Java vývojářem z Prahy. Strukturu, pluginy a Claude Code skills přebírá z reálného osobního vaultu. Obsah je celý fiktivní: lidé, firma, závody, deník, tasky, dárky, blog i statistiky. Jakákoli shoda se skutečností je náhodná.

Jádrem je **deník** (složka `Denik/`): každý den pár odrážek, ze kterých AI skládá týdenní, měsíční a roční souhrny, a nad celým rokem se dá ptát „kdy jsem naposledy…“. Podrobněji v [Deník Denik](Workshop/Jak%20funguje%20denik.md).

Externí služby (Garmin, Plausible, časomíra, Google Calendar) nahrazují lokální fixtures a demo MCP server, takže si vault můžeš naklonovat a zkoušet bez jakýchkoli účtů.

## Rychlý start

Potřebuješ [Obsidian](https://obsidian.md), [Claude Code](https://claude.com/claude-code) a Python 3.8+ (stačí standardní knihovna).

```bash
git clone https://github.com/vojtechruz/obsidian-claude-code-demo.git obsidian-demo
cd obsidian-demo
claude          # potvrď „trust this folder“ – pak platí .claude/settings.json (demo kalendář + skripty skills bez ptaní)
```

V Obsidianu: *Open folder as vault* → `obsidian-demo` → *Trust author and enable plugins*.

Na Linuxu a macOS bez příkazu `python` přepiš v `.mcp.json` `python` na `python3`.

Pak zkus třeba:

```
Udělej týdenní souhrn 2026-W39
Doběhl jsem Brdskou dvacítku 2026, zpracuj závod
Naplánuj mi týden 2026-W41
Co dát Mámě k narozeninám?
```

> „Dnes“ je ve vaultu **1. 10. 2026**. Deník končí 30. 9., kalendář a fixtures pokrývají září až listopad 2026.

Po zkoušení vrátíš vault do původního stavu: `git checkout -- . && git clean -fd`

## Dokumentace

Je ve složce [`Workshop/`](Workshop/Workshop.md) a dá se číst i přímo v Obsidianu:

| Soubor | Obsah |
| --- | --- |
| [Jak funguje deník](Workshop/Jak%20funguje%20denik.md) | k čemu deník je, tři vrstvy (den → týden → měsíc → rok), plán a review týdne, skripty |
| [Mapa vaultu](Workshop/Mapa%20vaultu.md) | struktura složek (PARA, deník…), kde co najdeš, konvence |
| [Pluginy](Workshop/Pluginy.md) | co dělají TaskNotes, Bases, Templater, QuickAdd, Spaced Repetition… a kde je uvidíš |
| [Skills](Workshop/Skills.md) | 13 skills: co dělají, jak je spustit, co čtou a píšou, jak spolupracují |
| [Scénáře](Workshop/Scenare.md) | prompty k vyzkoušení krok za krokem a co sledovat |
| [Reset a řešení problémů](Workshop/Reset%20a%20reseni%20problemu.md) | návrat do výchozího stavu, co jde na internet, časté potíže, přechod na skutečná data |

Konvence vaultu pro Claude Code jsou v [`CLAUDE.md`](CLAUDE.md).

## Licence

Obsah a skripty: MIT. Pluginy v `.obsidian/plugins/` mají licence svých autorů.
