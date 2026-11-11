#!/usr/bin/env python3
"""Fija la versión de pokemon.db: Metadata.SchemaVersion / DataVersion / BuildDate y PRAGMA user_version.

Uso:  python scripts/set_version.py <db> <schema> <AAAA.MM.R>
Ej.:  python scripts/set_version.py database/pokemon.db 1 2026.11.0   ->  versión completa 1.2026.11.0
"""
import re, sqlite3, sys, datetime

def main(argv):
    if len(argv) != 4:
        print(__doc__); return 2
    db, schema, data = argv[1], argv[2], argv[3]
    if not schema.isdigit() or int(schema) < 1:
        print("schema debe ser un entero >= 1"); return 2
    if not re.fullmatch(r"20\d\d\.(0[1-9]|1[0-2])\.\d+", data):
        print("data debe tener la forma AAAA.MM.R (R = revisión del mes, empieza en 0), p. ej. 2026.11.0"); return 2
    con = sqlite3.connect(db)
    with con:
        for k, v in (("SchemaVersion", schema), ("DataVersion", data),
                     ("BuildDate", datetime.date.today().isoformat())):
            con.execute("INSERT INTO Metadata(Key, Value) VALUES(?, ?) "
                        "ON CONFLICT(Key) DO UPDATE SET Value = excluded.Value", (k, v))
    con.execute(f"PRAGMA user_version = {int(schema)}")
    con.close()
    print(f"OK  versión {schema}.{data}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
