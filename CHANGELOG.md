# Changelog

## Unreleased (documentation and versioning)

### Documentation

* README, `SCHEMA_REFERENCE.md`, `POKEMON_DB_REFERENCE.md` and `DATA_SOURCES.md` now cover all 22 tables. Previously undocumented or incomplete: `SpeciesFlavorText` (no documentation at all), `FormEvolutionConditions` (columns), `Species` (`GenusEs`, `GenusEn`, `EggGroup1`, `EggGroup2`, `BaseSpecialGen1`), `FormGameAvailability` (the `own_encounter` status) and the full list of `Metadata` keys
* Statistics tables corrected (they listed 8 tables with outdated counts, e.g. 1,200 items vs 2,515 and 128 type-effectiveness rows vs 120)
* `ERD.png` regenerated from the real schema (all 22 tables, row counts, logical relationships); source in `scripts/gen_erd.py`
* New `scripts/check_docs.py` (run by CI) fails when a table, column or `Metadata` key is missing from the docs or the statistics are stale

### Versioning

* Release versions are now `S.AAAA.MM.R` (tag `db-v...`); `Metadata.SchemaVersion` / `DataVersion` and `PRAGMA user_version` must agree (`scripts/set_version.py`, `scripts/validate_db.py`). See `VERSIONING.md` and `RELEASING.md`

## Unreleased (HiddenItems)

### Database (items the bag should not offer)

* New table `HiddenItems` (12 rows: `GameId`, `ItemId`, `Reason`): TM/HM/TR rows of `ItemGameCodes` with no move in `MachineMoves` — Red/Green and Yellow `TM51`–`TM55`, Scarlet/Violet `TM00`, Legends: Z-A `TM161`. `ItemGameCodes` is not modified
* The Bag does not offer hidden items for adding, but still shows one if the loaded save already contains it
* `Metadata.HiddenItemsVersion`. Applied with `hotfixes/fix_hidden_items` (`create_tables.py`, `load_data.py`; optional `data/manual_hidden.csv`)

## Unreleased (ItemNames)

### Database (item names missing in PKHeX)

* New table `ItemNames` (585 rows, 65 items, all 9 languages each): official names in 9 languages (`en`, `es`, `fr`, `de`, `it`, `ja`, `ko`, `zh-Hans`, `zh-Hant`) for the 65 Legends: Z-A items that PKHeX.Core 25.11.07 does not name (19 Mega Stones, Hyperspace Berries, butters, Hoennian Salt, etc.). Columns: `Source` (`research-wiki`), `SourceUrl`, `Confidence` (`high` = two wikis agree, `medium` = one source, `low`) and `Verified` (0 for `low`, hidden by the app)
* Names come from Bulbapedia, WikiDex and Poképédia (not confirmed against in-game captures). Confidence `high` where two sources agree (144 rows), `medium` otherwise
* The app uses `ItemNames` only when PKHeX returns no name for an item (language row, otherwise English row of the table)
* `Items`, `ItemGameCodes` and `ItemDescriptions` are unchanged
* `Metadata.ItemNamesVersion` / `ItemNamesSource`
* Applied with `hotfixes/fix_item_names` (`create_tables.py`, `validate_names.py`, `load_data.py`)

## Unreleased (ItemDescriptions / MachineMoves)

### Database (item descriptions and machine moves)

* New table `ItemDescriptions` (12 738 rows): item description per language (`en`, `es`, `fr`, `de`, `it`, `ja`, `ko`, `zh-Hans`, `zh-Hant`, PKHeX codes), with `Source` (`legacy` = previous `Items.Description`, `pokeapi-flavor`, `pokeapi-prose`, `template`, `research`), `SourceUrl` and `Verified`. 2 042 of 2 116 items found in game pouches (TM/HM/TR excluded) have a verified description; 9 have none (Strange Ball, Carbink Jewel, Safe Key: no source; Guidebook, Pokédex, Secret Medicine, Data ROM, Red/Green Canari Plush: text differs per game/level, not supported by the schema) — see `hotfixes/item_descriptions/research_review.md`
* New table `MachineMoves` (2 026 rows): the move taught by each TM/HM/TR **per game** (`GameId`, `Kind`, `Number` → `ItemId`, `MoveId`). The same TM number teaches different moves in different games (e.g. TM101 in Scarlet/Violet vs Legends: Z-A). Covers TM101–TM229 (Scarlet/Violet), TR00–TR99 (Sword/Shield), TM108–TM160 (Legends: Z-A / Mega Dimension) and every older game; move ids match PKHeX.Core
* `Items`, `ItemGameCodes` and `Games` are unchanged; `Items.Description` (English) stays as a fallback
* 12 `ItemGameCodes` rows have no move in any source and were left untouched: Red/Green and Yellow `TM51`–`TM55`, Scarlet/Violet `TM00`, Legends: Z-A `TM161`
* `Metadata.ItemDescriptionsVersion` / `ItemDescriptionsSource` / `MachineMovesVersion` / `MachineMovesSource`
* Sources: PokeAPI (`item_flavor_text`, `item_prose`, `machines`), generated templates for the 45 new Z-A Mega Stones in the non-English languages, and community references (Serebii, Bulbapedia) gathered with AI assistance and validated by script (English only, not confirmed against in-game captures)
* Applied with `hotfixes/fix_item_descriptions` (`create_tables.py` + `load_data.py`); data built with `hotfixes/item_descriptions` (`extract.py`, `gen_templates.py`, `validate_research.py`)
* Database size: 51.4 MB → 53.4 MB

## Unreleased (FormDataVersion 2026.10, SpeciesAvailabilityVersion 2026.10)

### Database (form availability)

* New table `FormGameAvailability` (273 rows: 234 `uncreatable` + 39 `own_encounter`) + `Metadata.FormAvailabilityVersion` / `FormAvailabilitySource`. Applied with `hotfixes/fix_form_availability`.

### Database (species availability)

* New table `SpeciesGameAvailability` (4507 rows): per species and game, only for the games that cut their Pokédex (Let's Go, Sword/Shield, Legends: Arceus, Scarlet/Violet, Legends: Z-A). `Status`: `native`, `present_illegal`, `transfer_only`, `dlc`, `uncreatable`. The "Create Pokémon" picker hides `uncreatable` species (e.g. Unown/Arceus in Z-A)
* `Metadata.SpeciesAvailabilityVersion` / `SpeciesAvailabilitySource`
* SpeciesAvailabilityVersion 2026.10.1: 43 species moved from `present_illegal` to `native` (37 Legends: Arceus, 5 Sword/Shield, 1 Scarlet/Violet) after improving `BuildPokemon`. Remaining `present_illegal`: Hoopa/Volcanion (Z-A), Yanmega and Dudunsparce (Scarlet/Violet)
* SpeciesAvailabilityVersion 2026.10.2: Yanmega and Dudunsparce (Scarlet/Violet) moved from `present_illegal` to `native` (level probe now regenerates the moveset per level). Remaining `present_illegal`: Hoopa/Volcanion (Z-A) only
* SpeciesAvailabilityVersion 2026.10.3: 17 Legends: Arceus species whose base form does not exist in the game (16 Hisui-form species + Giratina) moved to `uncreatable`; FormAvailabilityVersion 2026.10.1 adds `own_encounter` rows for Giratina Origin (487:1) and White-Striped Basculin (550:2)
* SpeciesAvailabilityVersion 2026.10.4 / FormAvailabilityVersion 2026.10.2: Legends: Z-A base Zygarde moved to `uncreatable`; Zygarde form 2 added as `own_encounter`
* Applied with `hotfixes/fix_species_availability` (`create_tables.py` + `load_data.py`)

### Database

* New tables `FormEvolutionChains` (54 edges) and `FormEvolutionConditions` (340 rows): evolutions that involve a form, same structure as `EvolutionChains` / `EvolutionConditions`
* `Species` form rows (`SpeciesId > 10000`): `EggGroup1` / `EggGroup2` filled for 132 forms (were NULL), from PKHeX.Core
* `Species` corrections from PKHeX.Core per-form data: `GenderRate` of Meowstic-F, Indeedee-F, Basculegion-F, Oinkologne-F (always female), Ursaluna-Bloodmoon (always male) and Greninja-Battle-Bond/Ash (male); `Height` / `Weight` of Ursaluna-Bloodmoon
* `Metadata.FormDataVersion`
* Applied with `hotfixes/fix_form_data` (`create_tables.py` + `load_data.py`)

## v1.0.0

Initial public release.

### Database

* Species imported
* Species types imported
* Species abilities imported
* Moves imported
* Abilities imported
* Items imported
* Type effectiveness imported
* Learnsets imported
* Evolution chains imported
* Evolution conditions imported

### Statistics

* Species: 1350
* Moves: 937
* Abilities: 371
* Items: 1200
* Learnsets: 681289
* Evolution Chains: 484
* Evolution Conditions: 3294
* Type Effectiveness: 128

### Build System

* Exxeguttor.DataBuilder-v06

### External Resources

* movesets_all_combined.json

