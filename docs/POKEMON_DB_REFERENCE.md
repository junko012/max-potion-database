# Pokemon.db Reference

## Introduction

Pokemon.db is a normalized SQLite database designed to provide a complete offline Pokémon knowledge repository.

The database is intended for:

* Desktop applications
* PKHeX plugins
* Web APIs
* Research projects
* Data analysis
* AI systems
* Pokémon companion applications

The database is fully self-contained except for:

```text
movesets_all_combined.json
```

which is intentionally maintained as an external resource.

---

# Database Characteristics

## Engine

SQLite 3

## Encoding

UTF-8

## Design Goals

* Fast local queries
* Minimal duplication
* Stable species identifiers
* Game-specific learnsets
* Explicit evolution conditions
* Portable across platforms

---

# Entity Relationships

## Species

Central entity representing a Pokémon species.

Related tables:

```text
Species
├── SpeciesTypes
├── SpeciesAbilities
├── Learnsets
└── EvolutionChains
```

---

## Moves

Represents learnable Pokémon moves.

Referenced by:

```text
Learnsets
```

---

## Abilities

Represents Pokémon abilities.

Referenced by:

```text
SpeciesAbilities
```

---

## Games

Represents a supported game version.

Referenced by:

```text
Learnsets
```

---

## Evolution System

Evolution data is normalized into two tables:

```text
EvolutionChains
EvolutionConditions
```

Example:

```text
Bulbasaur
 └─(Level 16)
    Ivysaur
      └─(Level 32)
         Venusaur
```

EvolutionChains stores:

```text
from species
to species
```

EvolutionConditions stores:

```text
minimum level
held item
time of day
trade requirements
special conditions
```

---

# Learnset Model

Learnsets are stored per game.

Primary key:

```text
SpeciesId
FormId
GameId
MoveId
LearnMethod
```

This allows the same move to be learned differently in different games.

Examples:

```text
Level Up
TM
Tutor
Egg
Evolution
Event
```

---

# Type Effectiveness

The TypeEffectiveness table stores battle multipliers.

Examples:

```text
Fire -> Grass = 2.0
Electric -> Ground = 0.0
Water -> Fire = 2.0
```

---

# Metadata Table

Stores database metadata.

Example entries:

```text
SchemaVersion
DataVersion
BuildDate
Generator
ItemDescriptionsVersion
MachineMovesVersion
```

Per-feature hotfixes add their own `<Feature>Version` / `<Feature>Source` keys (see `docs/SCHEMA_REFERENCE.md`).

---

# Item Descriptions and Machine Moves

* `Items.Description` is the legacy English text (many items are empty).
* `ItemDescriptions(ItemId, Lang, Text, Source, SourceUrl, Verified)` holds per-language text. Read the requested language,
  then `en`, then `Items.Description`; ignore `Verified = 0` rows.
* `MachineMoves(GameId, Kind, Number, ItemId, MoveId)` gives the move of each TM/HM/TR **per game**; TM numbers are not
  stable across games.
* Texts marked `template` or `research` are not official game text (see `Source`).

---

# Common Queries

## Species Lookup

```sql
SELECT *
FROM Species
WHERE Name='pikachu';
```

## Species Types

```sql
SELECT TypeName
FROM SpeciesTypes
WHERE SpeciesId=25;
```

## Species Abilities

```sql
SELECT *
FROM SpeciesAbilities
WHERE SpeciesId=25;
```

## Learnset

```sql
SELECT *
FROM Learnsets
WHERE SpeciesId=25;
```

## Evolution Chain

```sql
SELECT *
FROM EvolutionChains
WHERE FromSpeciesId=25;
```

## Move Information

```sql
SELECT *
FROM Moves
WHERE MoveId=85;
```

---

# External Resources

## movesets_all_combined.json

Contains curated movesets.

This resource is not included in SQLite because:

* large size
* different update cycle
* optional consumption
* competitive metadata

Applications should load it independently.

---

# Versioning

Version information should be stored in:

```text
Metadata
```

Recommended keys:

```text
SchemaVersion
DataVersion
BuilderVersion
```

---

# Compatibility

Compatible with:

* .NET
* Java
* Python
* Go
* Rust
* NodeJS
* C++
* SQLiteStudio
* DB Browser for SQLite

---

# Release Statistics

Version 1.0.0

```text
Species                1350
Moves                   937
Abilities               371
Items                  1200
Learnsets           681289
Evolution Chains        484
Evolution Conditions   3294
Type Effectiveness      128
```

