# Pokemon.db Schema Reference

Every table of `pokemon.db`, with its columns, keys and meaning. Row counts are in the README
(*Dataset Statistics*); the diagram is `ERD.png`. `python3 scripts/check_docs.py` fails if a table, a column
or a `Metadata` key is missing here.

| Group | Tables |
| ----- | ------ |
| Species | `Species`, `SpeciesTypes`, `SpeciesAbilities`, `SpeciesFlavorText` |
| Moves | `Moves`, `Learnsets`, `MachineMoves` |
| Items | `Items`, `ItemGameCodes`, `ItemDescriptions`, `ItemNames`, `HiddenItems` |
| Evolution | `EvolutionChains`, `EvolutionConditions`, `FormEvolutionChains`, `FormEvolutionConditions` |
| Availability | `SpeciesGameAvailability`, `FormGameAvailability` |
| Reference | `Abilities`, `Games`, `TypeEffectiveness`, `Metadata` |

## Species

Stores Pokémon species metadata and base stats.

| Column         | Type                |
| -------------- | ------------------- |
| SpeciesId      | INTEGER PRIMARY KEY |
| Name           | TEXT                |
| Height         | REAL                |
| Weight         | REAL                |
| GrowthRate     | TEXT                |
| CaptureRate    | INTEGER             |
| BaseExperience | INTEGER             |
| GenderRate     | INTEGER             |
| Habitat        | TEXT                |
| Color          | TEXT                |
| Shape          | TEXT                |
| BaseHP         | INTEGER             |
| BaseAttack     | INTEGER             |
| BaseDefense    | INTEGER             |
| BaseSpAttack   | INTEGER             |
| BaseSpDefense  | INTEGER             |
| BaseSpeed      | INTEGER             |
| GenusEs        | TEXT                |
| GenusEn        | TEXT                |
| EggGroup1      | TEXT                |
| EggGroup2      | TEXT                |
| BaseSpecialGen1 | INTEGER            |

Rows with `SpeciesId > 10000` are alternate / regional **forms** (325 rows). Forms have no genus or habitat of
their own (`GenusEs`, `GenusEn`, `Habitat` are `NULL`: use the base species) and some have no egg group.
`GenusEs` is `NULL` for 127 base species. `EggGroup2` is `NULL` when the species has a single egg group.
`BaseSpecialGen1` is the single **Special** stat of Generation 1 (only the 151 Gen 1 species have it; in
Gen 2+ Special is split into `BaseSpAttack` / `BaseSpDefense`).

---

## SpeciesTypes

Stores Pokémon typing.

| Column    | Type    |
| --------- | ------- |
| SpeciesId | INTEGER |
| Slot      | INTEGER |
| TypeName  | TEXT    |

Primary Key:

```text
(SpeciesId, Slot)
```

---

## SpeciesAbilities

Stores Pokémon abilities.

| Column      | Type    |
| ----------- | ------- |
| SpeciesId   | INTEGER |
| AbilityName | TEXT    |
| IsHidden    | INTEGER |

Primary Key:

```text
(SpeciesId, AbilityName)
```

---

## SpeciesFlavorText

Pokédex entries, one row per species, language and game version.

| Column    | Type                                                          |
| --------- | ------------------------------------------------------------- |
| SpeciesId | INTEGER (→ `Species`, base species ≤ 1025)                    |
| Lang      | TEXT (`en`, `es`)                                             |
| Game      | TEXT (version slug: `red`, `crystal`, `alpha-sapphire`, `moon`, `lets-go-pikachu`, `shield`, ...) |
| Text      | TEXT                                                          |

Primary Key:

```text
(SpeciesId, Lang, Game)
```

Currently 20,314 rows over 35 game slugs: `en` covers 1,025 species and `es` 898. Forms have no entries (use the
base species). The slugs are PokeAPI version names, not `Games.GameCode` values; an app maps its game to
the slug (version pairs such as Red/Blue have one row per version). Source: PokeAPI species flavor text.

```sql
SELECT Text FROM SpeciesFlavorText WHERE SpeciesId = 25 AND Lang = 'en' AND Game = 'yellow';
```

---

## Moves

Stores move metadata.

| Column      | Type                |
| ----------- | ------------------- |
| MoveId      | INTEGER PRIMARY KEY |
| Name        | TEXT                |
| TypeName    | TEXT                |
| DamageClass | TEXT                |
| Power       | INTEGER             |
| Accuracy    | INTEGER             |
| PP          | INTEGER             |
| Priority    | INTEGER             |
| EffectText  | TEXT                |
| Target      | TEXT                |
| Generation  | TEXT                |

---

## Abilities

Stores ability metadata.

| Column          | Type                |
| --------------- | ------------------- |
| AbilityId       | INTEGER PRIMARY KEY |
| Name            | TEXT                |
| Description     | TEXT                |
| LongDescription | TEXT                |
| Generation      | TEXT                |
| IsMainSeries    | INTEGER             |

---

## Items

Stores item metadata.

| Column      | Type                |
| ----------- | ------------------- |
| ItemId      | INTEGER PRIMARY KEY |
| Name        | TEXT                |
| Description | TEXT                |
| Category    | TEXT                |
| Cost        | INTEGER             |
| FlingPower  | INTEGER             |
| FlingEffect | TEXT                |

`Description` is the legacy English text (empty for ~1 700 items). Localized descriptions live in
`ItemDescriptions`; use it first and fall back to this column.

---

## ItemGameCodes

Which items exist in each game, their id inside the save and the pouch they belong to.

| Column            | Type                                        |
| ----------------- | ------------------------------------------- |
| ItemId            | INTEGER (→ `Items`)                         |
| GameId            | INTEGER (→ `Games`)                         |
| RawItemId         | INTEGER (item index in the save/PKHeX)      |
| PouchCategory     | TEXT                                        |
| UserPouchCategory | TEXT                                        |

Primary key `(GameId, RawItemId)`; unique `(ItemId, GameId)`.

---

## ItemDescriptions

Item description per language. Added by `hotfixes/fix_item_descriptions`. TM/HM/TR items have no row here: their
text is built from `MachineMoves`.

| Column    | Type                                                         |
| --------- | ------------------------------------------------------------ |
| ItemId    | INTEGER (→ `Items`)                                          |
| Lang      | TEXT (`en`, `es`, `fr`, `de`, `it`, `ja`, `ko`, `zh-Hans`, `zh-Hant`) |
| Text      | TEXT                                                         |
| Source    | TEXT (`legacy`, `pokeapi-flavor`, `pokeapi-prose`, `template`, `research`) |
| SourceUrl | TEXT (nullable; set for `research`)                          |
| Verified  | INTEGER (1 = show, 0 = pending approval)                     |

Primary key `(ItemId, Lang)`. Index: `IX_ItemDescriptions_Lang (Lang)`.

Precedence when several texts exist for the same `(ItemId, Lang)`: English — verified research > legacy >
PokeAPI > template > unverified research; other languages — verified research > PokeAPI > template > unverified
research. Readers should look up the requested language and fall back to `en`, then to `Items.Description`.
Rows with `Verified = 0` must not be shown. `Source = 'template'` and `'research'` are not official game text.

```sql
SELECT COALESCE(l.Text, e.Text, i.Description) AS Description
FROM   Items i
LEFT JOIN ItemDescriptions l ON l.ItemId = i.ItemId AND l.Lang = 'es' AND l.Verified = 1
LEFT JOIN ItemDescriptions e ON e.ItemId = i.ItemId AND e.Lang = 'en' AND e.Verified = 1
WHERE  i.ItemId = 17;
```

---

## HiddenItems

Items the Bag must not offer in a given game (derived by `hotfixes/fix_hidden_items`).

| Column | Type | Notes |
|---|---|---|
| GameId | INTEGER | FK → `Games.GameId` |
| ItemId | INTEGER | FK → `Items.ItemId` |
| Reason | TEXT | `machine_without_move` or `manual` |

PK (`GameId`, `ItemId`). Read with `PokemonDatabase.GetHiddenItemIds(gameId)`; an item already present in the save is still shown.

## ItemNames

Official item names for objects PKHeX.Core does not name (65 Legends: Z-A items). Added by `hotfixes/fix_item_names`.

| Column | Type | Notes |
|---|---|---|
| ItemId | INTEGER | FK → `Items.ItemId` |
| Lang | TEXT | PKHeX code: `en`, `es`, `fr`, `de`, `it`, `ja`, `ko`, `zh-Hans`, `zh-Hant` |
| Name | TEXT | Name as shown in-game (per wiki source) |
| Source | TEXT | `research-wiki` |
| SourceUrl | TEXT | Page the name was taken from |
| Confidence | TEXT | `high` / `medium` / `low` |
| Verified | INTEGER | 0 = hidden by the app |

PK (`ItemId`, `Lang`); index `IX_ItemNames_Lang`. Read with `PokemonDatabase.GetItemNames` only when PKHeX has no name.

## MachineMoves

The move taught by each TM/HM/TR in each game. The key includes the game because numbering changes between games.

| Column | Type                                           |
| ------ | ---------------------------------------------- |
| GameId | INTEGER (→ `Games`)                            |
| Kind   | TEXT (`TM`, `TR`, `HM`)                        |
| Number | INTEGER (number inside that game)              |
| ItemId | INTEGER (→ `Items`)                            |
| MoveId | INTEGER (PKHeX move id, = `Moves.MoveId`)      |

Primary key `(GameId, Kind, Number)`. Index: `IX_MachineMoves_Item (GameId, ItemId)`.

```sql
SELECT m.Name FROM MachineMoves mm JOIN Moves m ON m.MoveId = mm.MoveId
WHERE  mm.GameId = 12 AND mm.Kind = 'TM' AND mm.Number = 108;   -- Legends: Z-A TM108
```

---

## TypeEffectiveness

Stores battle effectiveness multipliers.

| Column      | Type |
| ----------- | ---- |
| AttackType  | TEXT |
| DefenseType | TEXT |
| Multiplier  | REAL |

Only matchups that are **not neutral** are stored (`Multiplier` is `2.0`, `0.5` or `0.0`); a missing
`(AttackType, DefenseType)` pair means `1.0`. Type names are lowercase (`fire`, `water`, ...), as in
`SpeciesTypes.TypeName` and `Moves.TypeName`.

Primary Key:

```text
(AttackType, DefenseType)
```

---

## Games

Stores game identifiers.

| Column   | Type                |
| -------- | ------------------- |
| GameId   | INTEGER PRIMARY KEY |
| GameCode | TEXT UNIQUE         |

Examples:

```text
redgreen
yellow
crystal
emerald
platinum
blackwhite
scarletviolet
```

---

## Learnsets

Stores move acquisition data.

| Column      | Type    |
| ----------- | ------- |
| SpeciesId   | INTEGER |
| FormId      | INTEGER |
| GameId      | INTEGER |
| MoveId      | INTEGER |
| LearnMethod | TEXT    |
| LearnLevel  | INTEGER |
| LearnItem   | TEXT    |

Primary Key:

```text
SpeciesId
FormId
GameId
MoveId
LearnMethod
```

Indexes:

```text
IX_Learnsets_Species
IX_Learnsets_Move
```

---

## EvolutionChains

Stores evolution relationships.

| Column        | Type                              |
| ------------- | --------------------------------- |
| EvolutionId   | INTEGER PRIMARY KEY AUTOINCREMENT |
| FromSpeciesId | INTEGER                           |
| ToSpeciesId   | INTEGER                           |

Example:

```text
1 -> 2
2 -> 3
```

---

## EvolutionConditions

Stores evolution requirements.

| Column         | Type                              |
| -------------- | --------------------------------- |
| ConditionId    | INTEGER PRIMARY KEY AUTOINCREMENT |
| EvolutionId    | INTEGER                           |
| ConditionType  | TEXT                              |
| ConditionValue | TEXT                              |

Examples:

```text
min_level = 16
item = thunder-stone
trigger = trade
time_of_day = night
```

---

## FormEvolutionChains

Stores evolution relationships that involve a **form** (regional forms, Burmy cloaks, Meowstic
female, Basculin White-Striped...). Same columns as `EvolutionChains`; the difference is that
`FromSpeciesId` / `ToSpeciesId` may be a form row of `Species` (`SpeciesId > 10000`, e.g.
`10161 meowth-galar`). A side with no own form row keeps its base id (e.g. `863 perrserker`).
`EvolutionChains` is not modified: it keeps one edge per species and merges the conditions of
every form (it cannot tell "Slowbro of Galar" from "Slowbro"); this table can.

| Column        | Type                              |
| ------------- | --------------------------------- |
| EvolutionId   | INTEGER PRIMARY KEY AUTOINCREMENT |
| FromSpeciesId | INTEGER                           |
| ToSpeciesId   | INTEGER                           |

Example:

```text
10164 slowpoke-galar -> 10165 slowbro-galar   (item = galarica-cuff)
10164 slowpoke-galar -> 10172 slowking-galar  (item = galarica-wreath)
```

Source: `PKHeX.Core` evolution trees (USUM, SWSH, LA, SV, ZA). An edge can appear more than once when
the condition differs between games (Qwilfish of Hisui -> Overqwil: use Barb Barrage 20 times in
Legends: Arceus, know Barb Barrage in Scarlet/Violet).

---

## FormEvolutionConditions

Same structure and `ConditionType` vocabulary as `EvolutionConditions` (EAV, one row per condition),
keyed by `FormEvolutionChains.EvolutionId`.

| Column         | Type                              |
| -------------- | --------------------------------- |
| ConditionId    | INTEGER PRIMARY KEY AUTOINCREMENT |
| EvolutionId    | INTEGER (→ `FormEvolutionChains`) |
| ConditionType  | TEXT                              |
| ConditionValue | TEXT                              |

Index: `IX_FormEvolutionConditions_Evolution (EvolutionId)`. Keys not present in `EvolutionConditions`:
`min_critical_hits`, `min_coins`, `nature` (`amped` / `low-key`), `min_move_count`.

---

## SpeciesGameAvailability

Which species can be created in each game. Same convention as `ItemGameCodes` (`SpeciesId` → `Species`,
`GameId` → `Games`, one `Games` row per version pair). Rows exist **only** for the games that cut their
Pokédex: `letsgopikachueevee` (13), `swordshield` (20), `legendsarceus` (11), `scarletviolet` (18),
`legendsza` (12). A game with no rows (Gen 1-7, BD/SP) restricts nothing.

| Column         | Type                              |
| -------------- | --------------------------------- |
| AvailabilityId | INTEGER PRIMARY KEY AUTOINCREMENT |
| SpeciesId      | INTEGER (base species, ≤ 1025)    |
| GameId         | INTEGER                           |
| Status         | TEXT                              |
| Reason         | TEXT                              |

Unique: `(SpeciesId, GameId)`. Index: `IX_SpeciesGameAvailability_Game (GameId, Status)`.

`Status` values:

| Status            | Meaning                                                                                       | Picker  |
| ----------------- | --------------------------------------------------------------------------------------------- | ------- |
| `native`          | In the game's PKHeX table and `BuildPokemon` produces a legal Pokémon                         | shown   |
| `present_illegal` | In the game's table, but `BuildPokemon` finds no legal build (builder limitation)             | shown   |
| `transfer_only`   | Not in the game's table but legal (arrives through HOME, e.g. Sandshrew in Z-A)               | shown   |
| `dlc`             | Not in PKHeX.Core 25.11.07's table but in the game's Pokédex (`restricted_dex_availability`)  | shown   |
| `uncreatable`     | Does not exist in the game and no legal build exists                                          | hidden  |

Source: PKHeX.Core 25.11.07 (`IsPresentInGame` + `LegalityAnalysis` over `BuildPokemon`, 4 attempts).
For the version pairs, a species is `native` if it is for either version. Metadata keys:
`SpeciesAvailabilityVersion`, `SpeciesAvailabilitySource`.

```sql
SELECT s.Name FROM SpeciesGameAvailability a JOIN Species s ON s.SpeciesId = a.SpeciesId
WHERE  a.GameId = 12 AND a.Status = 'uncreatable';
```

---

## FormGameAvailability

Per-game exceptions for forms (`SpeciesId` → `Species`, `GameId` → `Games`). 276 rows over 12 games, in two kinds:

* `uncreatable` (234 rows: `legendsza` 70, `scarletviolet` 93, `legendsarceus` 38, `swordshield` 33): forms that
  `PokemonService.BuildPokemon` cannot leave legal in that game. A listed form is hidden from the form selector only
  if switching to it also breaks the Pokémon's origin (e.g. Zygarde 10%/50% and Ash-Greninja in Z-A).
* `own_encounter` (42 rows, spread over Gen 4–9 games): the form is hidden from the form selector (changing to it
  would break the origin) but has its own legal encounter, so it is offered when **creating** a Pokémon.

Fallback when the table is missing: `Assets/uncreatable_forms.json`.

| Column             | Type                              |
| ------------------ | --------------------------------- |
| FormAvailabilityId | INTEGER PRIMARY KEY AUTOINCREMENT |
| SpeciesId          | INTEGER                           |
| FormId             | INTEGER                           |
| GameId             | INTEGER                           |
| Status             | TEXT (`uncreatable`, `own_encounter`) |
| Reason             | TEXT                              |

Unique: `(SpeciesId, FormId, GameId)`. Index: `IX_FormGameAvailability_Game (GameId, Status)`.
Metadata keys: `FormAvailabilityVersion`, `FormAvailabilitySource`.

---

## Metadata

Stores database version and provenance.

| Column | Type             |
| ------ | ---------------- |
| Key    | TEXT PRIMARY KEY |
| Value  | TEXT             |

Keys present in the current release:

| Key | Meaning |
| --- | ------- |
| `SchemaVersion` | Schema version `S` (integer). The compatibility contract; see `VERSIONING.md`. Mirrored in `PRAGMA user_version`. |
| `DataVersion` | Data version `AAAA.MM.R` (year, month, revision within the month). |
| `BuildDate` | Date the file was stamped (`YYYY-MM-DD`). |
| `Generator` | Tool that produced the original build (`Exxeguttor.DataBuilder.v06`). |
| `MigrationDate`, `MigrationSource` | Date and origin of the first migration from the app's JSON assets. |
| `MovesPopulated`, `AbilitiesPopulated`, `ItemsPopulated` | Row counts recorded at the first build (not updated afterwards; see the README for current counts). |
| `FormDataVersion` | Version of the form data (forms as `Species` rows > 10000 and `FormEvolution*`). |
| `SpeciesAvailabilityVersion`, `SpeciesAvailabilitySource` | `SpeciesGameAvailability` dataset. |
| `FormAvailabilityVersion`, `FormAvailabilitySource` | `FormGameAvailability` dataset. |
| `Gen1SpecialVersion`, `Gen1SpecialSource` | `Species.BaseSpecialGen1` (Gen 1 Special stat). |
| `ItemDescriptionsVersion`, `ItemDescriptionsSource` | `ItemDescriptions` dataset. |
| `MachineMovesVersion`, `MachineMovesSource` | `MachineMoves` dataset. |
| `ItemNamesVersion`, `ItemNamesSource` | `ItemNames` dataset. |
| `HiddenItemsVersion` | `HiddenItems` dataset. |

Each dataset added after the first build carries its own `<Dataset>Version` / `<Dataset>Source` pair.

---

# Entity Relationship Summary

```text
Species
├── SpeciesTypes
├── SpeciesAbilities       (AbilityName -> Abilities.Name, by name)
├── SpeciesFlavorText
├── Learnsets
└── EvolutionChains

Moves
└── Learnsets

Games
└── Learnsets

EvolutionChains
└── EvolutionConditions

FormEvolutionChains   (FromSpeciesId / ToSpeciesId -> Species, incl. form rows > 10000)
└── FormEvolutionConditions

SpeciesGameAvailability   (SpeciesId -> Species, GameId -> Games)
FormGameAvailability      (SpeciesId -> Species, GameId -> Games)

Items
├── ItemGameCodes         (ItemId -> Items, GameId -> Games)
├── ItemDescriptions      (ItemId -> Items)
├── ItemNames             (ItemId -> Items)
├── HiddenItems           (ItemId -> Items, GameId -> Games)
└── MachineMoves          (ItemId -> Items, GameId -> Games; MoveId = PKHeX move id)

TypeEffectiveness         (type names are shared by SpeciesTypes.TypeName and Moves.TypeName, by name)
Abilities                 (referenced by SpeciesAbilities.AbilityName, by name)
Metadata                  (standalone)
```

---

# Schema Version

```text
SchemaVersion: 1   (full release version: see VERSIONING.md, e.g. 1.2026.11.0)
```

Within one schema version the database only grows (new rows, tables or nullable columns); a change that can break
existing queries raises `SchemaVersion`.

# Database Engine

```text
SQLite 3
```

