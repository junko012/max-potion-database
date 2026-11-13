#!/usr/bin/env python3
"""Comprueba (y opcionalmente actualiza) que la documentación coincida con pokemon.db.

Uso:  python3 scripts/check_docs.py [database/pokemon.db]            solo verifica (código de salida 1 si hay desfases)
      python3 scripts/check_docs.py [database/pokemon.db] --write-stats  reescribe las tablas de estadísticas

Verifica: (1) toda tabla de la DB tiene sección `## Tabla` en docs/SCHEMA_REFERENCE.md y todas sus columnas figuran;
(2) toda tabla se menciona como `Tabla` en README.md; (3) las estadísticas de README.md y docs/POKEMON_DB_REFERENCE.md
(bloques entre marcadores) coinciden con el número real de filas; (4) toda clave de Metadata figura en SCHEMA_REFERENCE.md.
"""
import pathlib, re, sqlite3, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PURPOSE = {
    "Species": "Species and forms: base stats, growth, genus, egg groups",
    "SpeciesTypes": "Typing of each species (slot 1 / 2)",
    "SpeciesAbilities": "Normal and hidden abilities per species",
    "SpeciesFlavorText": "Pokédex entries per species, language and game",
    "Abilities": "Ability names and descriptions",
    "Moves": "Move metadata (type, power, accuracy, PP, effect)",
    "Learnsets": "Moves each species can learn, per game and method",
    "MachineMoves": "Move taught by each TM / TR / HM per game",
    "Items": "Item metadata (category, cost, fling)",
    "ItemGameCodes": "Which items exist in each game, save id and pouch",
    "ItemDescriptions": "Item descriptions in 9 languages, with source",
    "ItemNames": "Official item names PKHeX.Core does not provide",
    "HiddenItems": "Items the bag must not offer in a game",
    "EvolutionChains": "Species-to-species evolution edges",
    "EvolutionConditions": "Requirements of each evolution (level, item, trade...)",
    "FormEvolutionChains": "Evolution edges that involve regional / alternate forms",
    "FormEvolutionConditions": "Requirements of each form evolution",
    "SpeciesGameAvailability": "Which species can be created in each game",
    "FormGameAvailability": "Forms that cannot be built / have their own encounter",
    "Games": "Game identifiers (one per version pair)",
    "TypeEffectiveness": "Attack / defense type multipliers",
    "Metadata": "Database version and per-dataset provenance",
}
S0, S1 = "<!-- STATS:START -->", "<!-- STATS:END -->"

def stats_table(counts):
    lines = ["| Table | Records | Purpose |", "| ----- | ------: | ------- |"]
    for t in sorted(counts):
        lines.append(f"| `{t}` | {counts[t]:,} | {PURPOSE.get(t, '')} |")
    lines.append(f"| **Total ({len(counts)} tables)** | **{sum(counts.values()):,}** | |")
    return "\n".join(lines)

def stats_block(counts):
    w = max(len(t) for t in counts)
    return "```text\n" + "\n".join(f"{t:<{w}}  {n:>9,}" for t, n in sorted(counts.items())) + "\n```"

def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    db = pathlib.Path(args[0]) if args else ROOT / "database/pokemon.db"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    tables = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY 1")]
    counts = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    ref = (ROOT / "docs/POKEMON_DB_REFERENCE.md").read_text(encoding="utf-8")
    schema = (ROOT / "docs/SCHEMA_REFERENCE.md").read_text(encoding="utf-8")
    new_readme = re.sub(re.escape(S0) + r".*?" + re.escape(S1), S0 + "\n" + stats_table(counts) + "\n" + S1, readme, flags=re.S)
    new_ref = re.sub(re.escape(S0) + r".*?" + re.escape(S1), S0 + "\n" + stats_block(counts) + "\n" + S1, ref, flags=re.S)

    if "--write-stats" in argv:
        (ROOT / "README.md").write_text(new_readme, encoding="utf-8")
        (ROOT / "docs/POKEMON_DB_REFERENCE.md").write_text(new_ref, encoding="utf-8")
        print("estadísticas actualizadas"); return 0

    errors = []
    if S0 not in readme or S0 not in ref: errors.append("faltan los marcadores STATS en README.md o POKEMON_DB_REFERENCE.md")
    if new_readme != readme: errors.append("README.md: estadísticas desfasadas (corre con --write-stats)")
    if new_ref != ref: errors.append("docs/POKEMON_DB_REFERENCE.md: estadísticas desfasadas (corre con --write-stats)")
    sections = {p.split("\n", 1)[0].strip(): p for p in re.split(r"\n## ", schema)[1:]}
    readme_body = re.sub(re.escape(S0) + r".*?" + re.escape(S1), "", readme, flags=re.S)
    for t in tables:
        if t not in sections: errors.append(f"SCHEMA_REFERENCE.md: falta la sección '## {t}'"); continue
        for (_, col, *_r) in con.execute(f'PRAGMA table_info("{t}")'):
            if not re.search(r"\|\s*" + col + r"\s*\|", sections[t]): errors.append(f"SCHEMA_REFERENCE.md: '{t}' no documenta la columna {col}")
        if f"`{t}`" not in readme_body: errors.append(f"README.md: la tabla `{t}` no se menciona en 'Database Contents'")
    for (k,) in con.execute("SELECT Key FROM Metadata"):
        if k not in schema: errors.append(f"SCHEMA_REFERENCE.md: la clave Metadata '{k}' no está documentada")
    if errors:
        print("DOCS DESFASADOS:"); [print("  -", e) for e in errors]; return 1
    print(f"OK  docs al día con {len(tables)} tablas"); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
