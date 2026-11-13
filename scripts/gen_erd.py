#!/usr/bin/env python3
"""Regenera docs/ERD.png (y docs/ERD.dot) desde el esquema REAL de pokemon.db. Requiere Graphviz (`dot`).

Uso:  python3 scripts/gen_erd.py [database/pokemon.db] [docs/ERD.png]
Las columnas y las claves primarias salen de la base; las relaciones lógicas (la DB casi no declara FOREIGN KEY)
están en RELATIONS: si añades una tabla, añádela también aquí para que aparezca conectada.
"""
import html, pathlib, shutil, sqlite3, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUPS = {   # tabla -> (color de cabecera)
    "Species": "#DCE9FB", "SpeciesTypes": "#DCE9FB", "SpeciesAbilities": "#DCE9FB", "SpeciesFlavorText": "#DCE9FB",
    "Moves": "#FDE7C8", "Learnsets": "#FDE7C8", "MachineMoves": "#FDE7C8",
    "Items": "#DDF1DC", "ItemGameCodes": "#DDF1DC", "ItemDescriptions": "#DDF1DC", "ItemNames": "#DDF1DC", "HiddenItems": "#DDF1DC",
    "EvolutionChains": "#EBDDF5", "EvolutionConditions": "#EBDDF5", "FormEvolutionChains": "#EBDDF5", "FormEvolutionConditions": "#EBDDF5",
    "SpeciesGameAvailability": "#F8D9D9", "FormGameAvailability": "#F8D9D9",
    "Abilities": "#E6E6E6", "Games": "#E6E6E6", "TypeEffectiveness": "#E6E6E6", "Metadata": "#E6E6E6",
}
# (origen, destino, etiqueta, discontinua)  — origen 1 : N destino
RELATIONS = [
    ("Species", "SpeciesTypes", "SpeciesId", False), ("Species", "SpeciesAbilities", "SpeciesId", False),
    ("Species", "SpeciesFlavorText", "SpeciesId", False), ("Species", "Learnsets", "SpeciesId", False),
    ("Species", "SpeciesGameAvailability", "SpeciesId", False), ("Species", "FormGameAvailability", "SpeciesId", False),
    ("Species", "EvolutionChains", "From/ToSpeciesId", False), ("Species", "FormEvolutionChains", "From/ToSpeciesId", False),
    ("EvolutionChains", "EvolutionConditions", "EvolutionId", False), ("FormEvolutionChains", "FormEvolutionConditions", "EvolutionId", False),
    ("Moves", "Learnsets", "MoveId", False), ("Moves", "MachineMoves", "MoveId", False),
    ("Games", "Learnsets", "GameId", False), ("Games", "MachineMoves", "GameId", False), ("Games", "ItemGameCodes", "GameId", False),
    ("Games", "HiddenItems", "GameId", False), ("Games", "SpeciesGameAvailability", "GameId", False), ("Games", "FormGameAvailability", "GameId", False),
    ("Items", "ItemGameCodes", "ItemId", False), ("Items", "ItemDescriptions", "ItemId", False), ("Items", "ItemNames", "ItemId", False),
    ("Items", "MachineMoves", "ItemId", False), ("Items", "HiddenItems", "ItemId", False),
    ("Abilities", "SpeciesAbilities", "AbilityName = Name", True),
    ("TypeEffectiveness", "SpeciesTypes", "TypeName = type", True), ("TypeEffectiveness", "Moves", "TypeName = type", True),
]

def main(argv):
    db = pathlib.Path(argv[1]) if len(argv) > 1 else ROOT / "database/pokemon.db"
    png = pathlib.Path(argv[2]) if len(argv) > 2 else ROOT / "docs/ERD.png"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    tables = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY 1")]
    missing = [t for t in tables if t not in GROUPS]
    if missing: print("AVISO: tablas sin grupo/color en gen_erd.py:", ", ".join(missing))
    out = ['digraph ERD {', 'rankdir=LR; nodesep=0.35; ranksep=1.1; bgcolor="white"; pad=0.3;',
           'node [shape=plain, fontname="DejaVu Sans", fontsize=10]; edge [fontname="DejaVu Sans", fontsize=8, color="#555555", arrowsize=0.7];']
    for t in tables:
        n = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        rows = "".join(
            f'<TR><TD ALIGN="LEFT" PORT="{html.escape(c[1])}">{"<B>PK</B> " if c[5] else "      "}{html.escape(c[1])}'
            f' <FONT COLOR="#888888">{html.escape(c[2].split()[0] if c[2] else "")}</FONT></TD></TR>'
            for c in con.execute(f'PRAGMA table_info("{t}")'))
        out.append(f'"{t}" [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">'
                   f'<TR><TD BGCOLOR="{GROUPS.get(t, "#E6E6E6")}"><B>{t}</B><BR/><FONT POINT-SIZE="8" COLOR="#555555">{n:,} rows</FONT></TD></TR>{rows}</TABLE>>];')
    for a, b, label, dashed in RELATIONS:
        if a in tables and b in tables:
            out.append(f'"{a}" -> "{b}" [label="{label}", taillabel="1", headlabel="N"{", style=dashed" if dashed else ""}];')
    out.append("}")
    dot = png.with_suffix(".dot"); dot.write_text("\n".join(out), encoding="utf-8")
    if not shutil.which("dot"):
        print("Graphviz (dot) no encontrado: solo se escribió", dot); return 0
    subprocess.run(["dot", "-Tpng", "-Gdpi=110", str(dot), "-o", str(png)], check=True)
    print("OK ", png, f"({len(tables)} tablas)")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
