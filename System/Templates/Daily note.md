<%*
/*
 * Navigace ve stejném formátu jako .claude/skills/denik-souhrn/link_denik.py (--all),
 * až na jednu odchylku: odkaz na "zítřek" se sem dá VŽDY (spočítaný datem, ne podle
 * existence souboru) - takže nezůstane prázdný, dokud zítřejší poznámka nevznikne.
 * Bude to zpočátku nevyřešený (červený) odkaz, který se sám "rozsvítí", jakmile
 * tu poznámku založíš. Odkaz na včerejšek naopak bere nejbližší EXISTUJÍCÍ
 * předchozí poznámku (přeskočí díry), stejně jako link_denik.py.
 * Případné rozjetí mezi tímhle a skriptem si škript při přeběhnutí (--all) sám opraví.
 */
const stem = tp.file.title; // např. "2026-07-11"
const m = moment(stem, "YYYY-MM-DD", true);
const weekStem = `${m.isoWeekYear()}-W${String(m.isoWeek()).padStart(2, "0")}`;
const monthStem = m.format("YYYY-MM");
const nextStem = m.clone().add(1, "day").format("YYYY-MM-DD");

const dayRe = /^\d{4}-\d{2}-\d{2}$/;
const days = tp.app.vault.getMarkdownFiles()
    .filter(f => f.path.startsWith("Denik/") && dayRe.test(f.basename) && f.basename !== stem)
    .map(f => f.basename)
    .sort();

let prev = null;
for (const d of days) {
    if (d < stem) prev = d;
}

const link = (t) => `[[${t}]]`;
const parts = [];
if (prev) parts.push(`← ${link(prev)}`);
parts.push(`${link(nextStem)} →`);
const top = parts.join("  ·  ");
const up = `↑ ${link(weekStem)} · ${link(monthStem)}`;

tR += `${top}   ·   ${up}`;
%>

- 