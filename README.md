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

| Table                | Records |
| -------------------- | ------: |
| Species              |    1350 |
| Moves                |     937 |
| Abilities            |     371 |
| Items                |    1200 |
| Learnsets            |  681289 |
| Evolution Chains     |     484 |
| Evolution Conditions |    3294 |
| Type Effectiveness   |     128 |

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
│   └── validate_db.py
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

Stores Pokémon species metadata and base stats.

Includes:

* Physical characteristics
* Growth rate
* Capture rate
* Base experience
* Gender rate
* Base battle statistics

---

### Species Types

Stores primary and secondary typings.

Example:

```text
Bulbasaur
├─ Grass
└─ Poison
```

---

### Species Abilities

Stores normal and hidden abilities.

---

### Moves

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

Stores ability metadata and descriptions.

---

### Items

Stores item metadata.

Includes:

* Category
* Cost
* Fling data
* Descriptions (legacy English; see `ItemDescriptions` for localized text)

---

### ItemDescriptions

Item descriptions per language (9 languages) with source and verification status.

---

### MachineMoves

The move taught by each TM/HM/TR in each game.

---

### Type Effectiveness

Stores battle effectiveness multipliers.

Example:

```text
Fire → Grass = 2.0
Electric → Ground = 0.0
Water → Fire = 2.0
```

---

### Games

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

Stores move acquisition information per game.

Supports:

* Level-up moves
* TM/HM moves
* Tutor moves
* Egg moves
* Event moves
* Evolution moves

Current records:

```text
681,289
```

---

### Evolution Chains

Stores evolutionary relationships.

Example:

```text
Bulbasaur
 └─ Ivysaur
     └─ Venusaur
```

---

### Evolution Conditions

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

* SCHEMA_REFERENCE.md
* POKEMON_DB_REFERENCE.md
* DATA_SOURCES.md
* ERD.png

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

