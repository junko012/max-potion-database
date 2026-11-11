#!/usr/bin/env python3
"""Valida pokemon.db antes de publicarla.

Uso:  python scripts/validate_db.py <db> [--tag db-v1.2026.11.0]
Comprueba: integridad SQLite, tablas obligatorias, Metadata (SchemaVersion, DataVersion con formato AAAA.MM.R),
PRAGMA user_version == SchemaVersion y, con --tag, que el tag coincida con la versión declarada.
"""
import re, sqlite3, sys

REQUIRED = ["Metadata", "Species", "Moves", "Abilities", "Items", "ItemNames", "ItemDescriptions",
            "ItemGameCodes", "Games", "Learnsets", "MachineMoves", "HiddenItems", "TypeEffectiveness",
            "SpeciesTypes", "SpeciesAbilities", "EvolutionChains"]

def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    db = argv[1]
    tag = argv[argv.index("--tag") + 1] if "--tag" in argv else None
    errors = []
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)

    r = con.execute("PRAGMA integrity_check").fetchall()
    if r != [("ok",)]:
        errors.append(f"integrity_check: {r[:3]}")
    fk = con.execute("PRAGMA foreign_key_check").fetchall()
    if fk:
        errors.append(f"foreign_key_check: {len(fk)} filas huérfanas (p. ej. {fk[0]})")

    tables = {t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for t in REQUIRED:
        if t not in tables:
            errors.append(f"falta la tabla {t}")
        elif con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] == 0:
            errors.append(f"la tabla {t} está vacía")

    meta = dict(con.execute("SELECT Key, Value FROM Metadata").fetchall()) if "Metadata" in tables else {}
    schema = meta.get("SchemaVersion", "")
    data = meta.get("DataVersion", "")
    if not schema.isdigit():
        errors.append(f"Metadata.SchemaVersion inválido: {schema!r}")
    if not re.fullmatch(r"20\d\d\.(0[1-9]|1[0-2])(\.\d+)?", data):
        errors.append(f"Metadata.DataVersion inválido (esperado AAAA.MM.R): {data!r}")
    uv = con.execute("PRAGMA user_version").fetchone()[0]
    if schema.isdigit() and uv != int(schema):
        errors.append(f"PRAGMA user_version ({uv}) != SchemaVersion ({schema}); usa scripts/set_version.py")

    full = None
    if schema.isdigit() and data:
        parts = data.split(".")
        full = f"{schema}.{parts[0]}.{parts[1]}.{parts[2] if len(parts) > 2 else 0}"
    if tag:
        if full is None or tag != f"db-v{full}":
            errors.append(f"el tag {tag} no coincide con la versión declarada (db-v{full})")

    con.close()
    if errors:
        print("FALLÓ:"); [print("  -", e) for e in errors]; return 1
    print(f"OK  versión {full}  ({len(tables)} tablas)")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
