# Data Sources

The database is generated from publicly available Pokémon information.

## Primary Sources

### PokeAPI

Used for:

* Species (stats, genus, egg groups, habitat, colour, shape)
* Species flavor text (Pokédex entries, English and Spanish)
* Moves
* Abilities
* Items
* Evolution chains
* Type effectiveness

Also used for item descriptions (`item_flavor_text`, `item_prose`) in 9 languages and for the move taught by each
TM/HM/TR per game (`machines`).

https://pokeapi.co

## PKHeX Research

Used for validation and interoperability with Pokémon save editing ecosystems, and as the source of:

* game-by-game species and form availability (`SpeciesGameAvailability`, `FormGameAvailability`), checked with
  PKHeX.Core's legality analysis
* form data and form evolution trees (`FormEvolutionChains`, `FormEvolutionConditions`)
* the Generation 1 Special stat (`Species.BaseSpecialGen1`)
* item ids per game and pouch (`ItemGameCodes`) and the move ids used by `MachineMoves`

https://github.com/kwsch/PKHeX

## Item Names Research

`ItemNames` holds official names for Legends: Z-A items that PKHeX.Core does not name. They were taken from community
wikis (Bulbapedia, WikiDex, Poképédia) and are stored with their source URL and a confidence level (`high` when two
sources agree). They are not confirmed against in-game captures.

## Item Description Research

Item descriptions that PokeAPI does not provide (mostly Legends: Arceus, Legends: Z-A, Scarlet/Violet picnic and
crafting items, Pokémon Colosseum/XD key items) were gathered from community references (Serebii, Bulbapedia, and
a few from GameGuides) with AI assistance and validated by script. They are English only, are stored with their
source URL, and are **not** confirmed against in-game captures. Mega Stone descriptions in non-English languages are
generated templates. Both are marked in `ItemDescriptions.Source` (`research`, `template`).

## Community Research

Used to validate evolution conditions, learnsets and gameplay-related information.

## External Competitive Resource

movesets_all_combined.json

This file is intentionally distributed outside the SQLite database because:

* it changes frequently
* it is optional
* it represents competitive recommendations rather than canonical game data

## Attribution

Pokémon and related intellectual property belong to:

* Nintendo
* Game Freak
* The Pokémon Company

This repository does not claim ownership of Pokémon content.

