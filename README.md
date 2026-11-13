# Max Potion Database

A portable SQLite Pokémon database built for [Max Potion](https://github.com/junko012/max-potion), a Pokémon save file editor, and open to any third-party application.

## Overview

Max Potion Database is a consolidated Pokémon knowledge base generated from multiple public data sources and normalized into a single SQLite database.

The project was created to provide a fast, offline, language-independent data layer for:

* Desktop applications
* Web APIs
* AI systems
* Research projects
* Companion applications
* PKHeX integrations
* Data analysis tools

The database is distributed as a single SQLite file:

```text
pokemon.db
```

and can be consumed from any platform that supports SQLite.

---

## Release Information

Each release is tagged `db-vS.AAAA.MM.R` (for example `db-v1.2026.11.0`) and publishes
`pokemon.db`, `pokemon.db.gz` and `pokemon.db.sha256` in the
[Releases](https://github.com/junko012/max-potion-database/releases) page.

| Part | Meaning |
|------|---------|
| `S` | **Schema** version. Only changes when existing queries could break. |
| `AAAA.MM.R` | Data version: year, month and revision within the month. |

Within the same schema, updates are additive only (new rows, tables or nullable columns), so an
application written for schema `S` keeps working with every later release of that schema.
The version is stored in the `Metadata` table (`SchemaVersion`, `DataVersion`) and in `PRAGMA user_version`.
See [VERSIONING.md](VERSIONING.md) for the full contract and [RELEASING.md](RELEASING.md) for the release steps.

Database File:

```text
pokemon.db   (~52 MB, ~16 MB compressed)
```

---

## Dataset Statistics

Row counts of every table in `pokemon.db` (kept in sync by `scripts/check_docs.py --write-stats`).

<!-- STATS:START -->
| Table | Records | Purpose |
| ----- | ------: | ------- |
| `Abilities` | 371 | Ability names and descriptions |
| `EvolutionChains` | 484 | Species-to-species evolution edges |
| `EvolutionConditions` | 3,294 | Requirements of each evolution (level, item, trade...) |
| `FormEvolutionChains` | 54 | Evolution edges that involve regional / alternate forms |
| `FormEvolutionConditions` | 340 | Requirements of each form evolution |
| `FormGameAvailability` | 276 | Forms that cannot be built / have their own encounter |
| `Games` | 24 | Game identifiers (one per version pair) |
| `HiddenItems` | 12 | Items the bag must not offer in a game |
| `ItemDescriptions` | 12,738 | Item descriptions in 9 languages, with source |
| `ItemGameCodes` | 9,801 | Which items exist in each game, save id and pouch |
| `ItemNames` | 585 | Official item names PKHeX.Core does not provide |
| `Items` | 2,515 | Item metadata (category, cost, fling) |
| `Learnsets` | 681,289 | Moves each species can learn, per game and method |
| `MachineMoves` | 2,026 | Move taught by each TM / TR / HM per game |
| `Metadata` | 23 | Database version and per-dataset provenance |
| `Moves` | 937 | Move metadata (type, power, accuracy, PP, effect) |
| `Species` | 1,350 | Species and forms: base stats, growth, genus, egg groups |
| `SpeciesAbilities` | 2,926 | Normal and hidden abilities per species |
| `SpeciesFlavorText` | 20,314 | Pokédex entries per species, language and game |
| `SpeciesGameAvailability` | 4,507 | Which species can be created in each game |
| `SpeciesTypes` | 2,115 | Typing of each species (slot 1 / 2) |
| `TypeEffectiveness` | 120 | Attack / defense type multipliers |
| **Total (22 tables)** | **746,101** | |
<!-- STATS:END -->

---

## Repository Structure

```text
max-potion-database
│
├── database
│   └── pokemon.db
│
├── resources
│   └── movesets_all_combined.json
│
├── scripts
│   ├── set_version.py
│   ├── validate_db.py
│   ├── check_docs.py
│   └── gen_erd.py
│
├── docs
│   ├── SCHEMA_REFERENCE.md
│   ├── POKEMON_DB_REFERENCE.md
│   ├── DATA_SOURCES.md
│   └── ERD.png
│
├── CHANGELOG.md
├── CONTRIBUTING.md
├── ROADMAP.md
├── VERSIONING.md
├── RELEASING.md
├── LICENCE
└── README.md
```

---

## Database Contents

### Species

Table: `Species`

Stores Pokémon species metadata and base stats.

Includes:

* Physical characteristics
* Growth rate
* Capture rate
* Base experience
* Gender rate
* Base battle statistics
* Genus (English / Spanish), habitat, colour, shape and egg groups
* The single Gen 1 Special stat (`BaseSpecialGen1`)
* Alternate and regional forms as extra rows (`SpeciesId > 10000`)

---

### Species Types

Table: `SpeciesTypes`

Stores primary and secondary typings.

Example:

```text
Bulbasaur
├─ Grass
└─ Poison
```

---

### Species Abilities

Table: `SpeciesAbilities`

Stores normal and hidden abilities.

---

### Moves

Table: `Moves`

Stores move metadata.

Includes:

* Type
* Power
* Accuracy
* PP
* Priority
* Target
* Effect descriptions

---

### Abilities

Table: `Abilities`

Stores ability metadata and descriptions.

---

### Items

Table: `Items`

Stores item metadata.

Includes:

* Category
* Cost
* Fling data
* Descriptions (legacy English; see `ItemDescriptions` for localized text)

---

### ItemDescriptions

Table: `ItemDescriptions`

Item descriptions per language (9 languages) with source and verification status.

---

### MachineMoves

Table: `MachineMoves`

The move taught by each TM/HM/TR in each game.

---

### Type Effectiveness

Table: `TypeEffectiveness`

Stores battle effectiveness multipliers.

Example:

```text
Fire → Grass = 2.0
Electric → Ground = 0.0
Water → Fire = 2.0
```

---

### Games

Table: `Games`

Stores supported game identifiers.

Examples:

```text
redgreen
yellow
emerald
platinum
blackwhite
scarletviolet
```

---

### Learnsets

Table: `Learnsets`

Stores move acquisition information per game.

Supports:

* Level-up moves
* TM/HM moves
* Tutor moves
* Egg moves
* Event moves
* Evolution moves

Row count: see [Dataset Statistics](#dataset-statistics).

---

### Evolution Chains

Table: `EvolutionChains`

Stores evolutionary relationships.

Example:

```text
Bulbasaur
 └─ Ivysaur
     └─ Venusaur
```

---

### Evolution Conditions

Table: `EvolutionConditions`

Stores evolution requirements.

Examples:

```text
Level
Item
Trade
Friendship
Time of Day
Known Move
Location
Weather
```

---

### Form Evolution Chains and Conditions

Tables: `FormEvolutionChains`, `FormEvolutionConditions`

Evolution edges that involve a **form** (Alolan, Galarian, Hisuian and Paldean forms, Burmy cloaks,
Meowstic, ...). `EvolutionChains` keeps one edge per species and cannot tell "Slowbro of Galar" from
"Slowbro"; these tables can. Same structure and condition vocabulary as the species tables.

---

### Species Flavor Text

Table: `SpeciesFlavorText`

Pokédex entries, one row per species, language and game version (English and Spanish). Forms have no
entries of their own: use the base species.

---

### Species Game Availability

Table: `SpeciesGameAvailability`

Which species can be created in each game that restricts its Pokédex (Let's Go, Sword/Shield,
Legends: Arceus, Scarlet/Violet, Legends: Z-A). Each row has a `Status`: `native`, `present_illegal`,
`transfer_only`, `dlc` or `uncreatable`.

---

### Form Game Availability

Table: `FormGameAvailability`

Per-game exceptions for forms: `uncreatable` (no legal build) and `own_encounter` (hidden from the form
selector but obtainable through its own legal encounter).

---

### Item Game Codes

Table: `ItemGameCodes`

Which items exist in each game, their raw id inside the save file and the bag pouch they belong to.

---

### Item Names

Table: `ItemNames`

Official item names in 9 languages for objects that PKHeX.Core does not name (Legends: Z-A), with source,
source URL and a confidence level.

---

### Hidden Items

Table: `HiddenItems`

Items an editor should not offer in a given game (for example TMs that exist in the item table but teach no move).

---

### Metadata

Table: `Metadata`

Database version (`SchemaVersion`, `DataVersion`, `BuildDate`, `Generator`) and one `<Dataset>Version` /
`<Dataset>Source` pair per dataset that was added or revised after the first build.

---

## External Resources

The following resource is intentionally distributed outside the SQLite database:

```text
movesets_all_combined.json
```

Reason:

* Large file size
* Independent update cycle
* Competitive data changes frequently
* Optional consumption by client applications

Applications may load this resource separately when advanced moveset recommendations are required.

---

## Design Goals

* Portable
* Offline-first
* SQLite-native
* Language independent
* Fast local queries
* Easy integration
* Stable identifiers
* Minimal duplication

---

## Generation

This database is generated using:

```text
Exxeguttor.DataBuilder
```

which transforms and normalizes Pokémon data into a relational SQLite structure.

---

## Documentation

Additional documentation can be found in:

```text
docs/
```

Including:

* SCHEMA_REFERENCE.md (every table and column)
* POKEMON_DB_REFERENCE.md
* DATA_SOURCES.md
* ERD.png (all tables; regenerate with `python3 scripts/gen_erd.py`)

Run `python3 scripts/check_docs.py` to verify that the documentation covers every table, column and
Metadata key of the database.

---

## Intended Usage

This database may be used in:

* Personal projects
* Open source software
* Commercial software
* Research projects
* Educational tools
* AI systems

subject to the terms of the MIT License.

---

## Legal Notice

Pokémon and all related names, characters, species, moves, abilities,
items, games, trademarks, and intellectual property are owned by Nintendo,
Game Freak, and The Pokémon Company.

Max Potion Database is an independent project and is not affiliated
with, endorsed by, or sponsored by Nintendo, Game Freak, The Pokémon Company,
or the PKHeX project.

---

## License

MIT License

See the LICENCE file for details.

