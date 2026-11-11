# Versioning of `pokemon.db`

Full version: **`S.AAAA.MM.R`**, e.g. `1.2026.11.0`. Release tag: `db-v1.2026.11.0`.

| Part | Meaning | When it changes |
|---|---|---|
| `S` | **Schema** (integer) | Only for changes that can break existing queries: dropping or renaming a table or column, changing what a column means or its type. |
| `AAAA.MM` | Data month | Every data update. |
| `R` | Revision within the month | Starts at 0; +1 for each extra release in the same month. |

The version lives in three places that must agree (`scripts/validate_db.py` checks it):
`Metadata.SchemaVersion`, `Metadata.DataVersion` (`AAAA.MM.R`) and `PRAGMA user_version` (= `S`).
Set all of them with `python scripts/set_version.py database/pokemon.db <S> <AAAA.MM.R>`.

## Compatibility contract (for apps using this database)

1. The **schema number is the only contract.** An app declares the schema it understands (`RequiredSchema`)
   and, optionally, the oldest data version it accepts.
2. Within one schema, changes are **additive only**: new rows, new tables, new nullable columns.
   Existing tables, columns and their meaning do not change. Any app written for schema `S` keeps working
   with every later release of schema `S`.
3. If `schema_in_db > RequiredSchema` the app must be updated; if `schema_in_db < RequiredSchema` the database
   must be updated. Apps should check this at startup and fail with a clear message, not with a SQL error.
4. A schema bump is announced in `CHANGELOG.md` with a migration note, and released together with the
   Max Potion version that requires it.
