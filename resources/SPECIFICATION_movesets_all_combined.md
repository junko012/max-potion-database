# Specification: `movesets_consolidated.json`

This document describes the structure of `movesets_all_combined.json`, a file that combines Pokémon movesets from 3 original sources (Smogon, Pokémon Showdown, and Randbats) into a single JSON, organized as a tree. The goal is for any developer (or Claude instance) who needs to write code to read this file to know exactly what to expect at each level, without having to manually inspect the file.

## 1. Overall structure (4 levels)

```
{
  "<PokemonName>": {
    "<Source>": {
      "<Generation>": <data_node>
    }
  }
}
```

- **Level 1 — Pokemon**: key = exact Pokémon name (string), as it appears in Pokémon Showdown (e.g. `"Charizard"`, `"Charizard-Mega-X"`, `"Tornadus-Therian"`). Alternate forms (Mega, regional, etc.) are independent keys, not nested under the base Pokémon.
- **Level 2 — Source**: one of exactly 4 literal strings (case-sensitive):
  - `"Smogon"`
  - `"Showdown"`
  - `"Showdown Most Used"`
  - `"Randbats"`
- **Level 3 — Generation**: string formatted as `"gen1"` through `"gen9"`.
- **Level 4 — `data` node**: this is where the shape changes depending on the source (see section 3). **All parsing complexity lives at this level.**

### Important rule: absence of data
If a Pokémon has no information for a given source or generation, **that key simply does not exist** (it is never represented as `null`, `{}`, or `[]`). Your code must use safe access (`?.` in JS/TS, `.get()` in Python, etc.) at every level, and should never assume a branch exists.

```js
const data = movesets["Pikachu"]?.["Randbats"]?.["gen9"]; // may be undefined
```

## 2. Quick source overview

| Source | Origin | What it represents |
|---|---|---|
| `Smogon` | Smogon Strategy Dex | Competitive analysis sets, written/curated by the community. May contain **alternatives** (slashes "X/Y") represented as nested arrays. |
| `Showdown` | Pokémon Showdown teambuilder ("dex") | Same idea as Smogon but **already resolved**: every field is always a single value, never an array of alternatives. |
| `Showdown Most Used` | Pokémon Showdown usage stats ("stats") | Sets derived from real battle usage statistics. Only contains one set, named `"Showdown Usage"`. |
| `Randbats` | Random Battles | Sets used in the Random Battle format. Different structure: uses `level`, and from gen2 onward uses `roles` (several named sub-sets). |

## 3. Shape of the `data` node per source

### 3.1 `Smogon`
Dictionary of `setName → details`. **The only case where fields can be either a string or an array of alternatives** — your parser must check the type of each field.

```json
"Smogon": {
  "gen6": {
    "Dragon Dance": {
      "moves": ["Dragon Dance", "Flare Blitz", "Dragon Claw", "Roost"],
      "item": "Charizardite X",
      "nature": ["Jolly", "Adamant"],
      "evs": { "atk": 252, "def": 4, "spe": 252 },
      "ability": "Tough Claws",
      "teratypes": ["Fire", "Ghost"]
    }
  }
}
```

Possible fields inside each set: `moves` (array; each element can be a string, or an array of strings if there are alternatives), `ability`, `item`, `nature` (string or array of alternatives), `evs`, `ivs`, `teratypes` (string or array, only present from gen9 onward). Not every field is always present.

**How to resolve alternatives**: if a field is an array where a string was expected (`nature`, `item`, `ability`), or an element of `moves` is itself an array, it means "pick one option from this list." To render a "playable" set in the UI you can default to the first option, or let the user choose.

### 3.2 `Showdown`
Same shape as `Smogon`, but **without alternatives** (always single values, ready to use directly).

```json
"Showdown": {
  "gen4": {
    "Defensive Nasty Plot": {
      "moves": ["Nasty Plot", "Air Slash", "Roost", "Thunder Wave"],
      "ability": "Serene Grace",
      "item": "Leftovers",
      "nature": "Bold",
      "evs": { "hp": 252, "def": 192, "spe": 64 }
    },
    "All-Out Attacker": {
      "moves": ["Air Slash", "Aura Sphere", "Fire Blast", "Thunder Wave"],
      "ability": "Serene Grace",
      "item": "Lum Berry",
      "nature": "Timid",
      "evs": { "spa": 252, "spd": 4, "spe": 252 }
    }
  }
}
```

### 3.3 `Showdown Most Used`
Dictionary with **a single fixed key**: `"Showdown Usage"`. Includes `level` (which doesn't appear in Smogon/Showdown).

```json
"Showdown Most Used": {
  "gen1": {
    "Showdown Usage": {
      "level": 100,
      "moves": ["Body Slam", "Rest", "Reflect", "Earthquake"],
      "ability": "...",
      "item": "...",
      "nature": "...",
      "evs": { ... },
      "hpType": "...",
      "shiny": false
    }
  }
}
```

Since there's only one set per generation, if your app expects "a list of sets" for display purposes, here it will always have length 1.

### 3.4 `Randbats` — the source with the most variation
Here the shape changes depending on the generation:

**Gen 1**: flat structure, no `roles`.
```json
"Randbats": {
  "gen1": {
    "level": 84,
    "moves": ["Counter", "Psychic", "Reflect", "Seismic Toss", "Substitute", "Thunder Wave"],
    "evs": { "atk": 0 },
    "ivs": { "atk": 2 }
  }
}
```
Note: in gen1, `moves` can have more than 4 elements — these are **all the possible moves** the random set generator can choose from, not necessarily the 4 actually used in a specific battle.

**Gen 2 through Gen 9**: structure with `roles` (one or more named sub-sets).
```json
"Randbats": {
  "gen9": {
    "level": 90,
    "abilities": ["Aroma Veil"],
    "items": ["Leftovers"],
    "evs": { "atk": 0 },
    "roles": {
      "Bulky Setup": {
        "abilities": ["Aroma Veil"],
        "items": ["Leftovers"],
        "teraTypes": ["Poison", "Steel"],
        "moves": ["Alluring Voice", "Calm Mind", "Psychic", "Psyshock", "Recover"],
        "evs": { "atk": 0 },
        "ivs": { "atk": 0 }
      },
      "Tera Blast user": { "...": "..." }
    }
  }
}
```

Key points for `Randbats`:
- `abilities` and `items` at the root level are the **union** of all possible abilities/items across all roles (useful for quick filtering without drilling into `roles`).
- The actual playable set detail (the 4-5 moves actually used) lives **inside each role**, at `roles.<roleName>.moves`.
- `teraTypes` (note the capital "T" here, unlike `teratypes` in Smogon) is always an array, never a bare string.
- For `evs`/`ivs`, keys that aren't listed don't have one universal fixed value: they represent stats the team generator doesn't explicitly constrain. For practical purposes you can assume 0 for `evs` and 31 for `ivs` on absent keys, unless your app needs full fidelity with Showdown's generator logic.

## 4. Stat keys (evs/ivs)
Always lowercase and abbreviated: `hp`, `atk`, `def`, `spa`, `spd`, `spe`. Not all 6 always appear; only the ones a given set explicitly constrains.

## 5. Recommended loading pseudocode

```ts
type Source = "Smogon" | "Showdown" | "Showdown Most Used" | "Randbats";

function getSets(movesets: any, pokemon: string, source: Source, gen: number) {
  const genKey = `gen${gen}`;
  const node = movesets?.[pokemon]?.[source]?.[genKey];
  if (!node) return null;

  switch (source) {
    case "Smogon":
    case "Showdown":
      // node = { setName: { moves, ability, item, nature, evs, ivs, teratypes } }
      return Object.entries(node).map(([setName, set]) => ({ setName, ...resolveAlternatives(set) }));

    case "Showdown Most Used":
      // node = { "Showdown Usage": { level, moves, ... } }
      return node["Showdown Usage"];

    case "Randbats":
      if (node.roles) {
        // gen2-9: iterate roles
        return Object.entries(node.roles).map(([roleName, role]) => ({ roleName, level: node.level, ...role }));
      }
      // gen1: flat
      return [{ level: node.level, moves: node.moves, evs: node.evs, ivs: node.ivs }];
  }
}

// Only needed for the "Smogon" source: resolves fields that may come as an array of alternatives
function resolveAlternatives(set: any) {
  const pickFirst = (v: any) => (Array.isArray(v) ? v[0] : v);
  return {
    ...set,
    item: pickFirst(set.item),
    ability: pickFirst(set.ability),
    nature: pickFirst(set.nature),
    teratypes: pickFirst(set.teratypes),
    moves: set.moves?.map((m: any) => (Array.isArray(m) ? m[0] : m)),
  };
}
```

Adapt this pseudocode to your app's actual language (the pattern — switch by source, safe access at every level, alternative-resolution only for Smogon — stays the same regardless of stack).

## 6. Design decisions (context)
- A tree structure (`Pokemon → Source → Generation → data`) was chosen over a flat list because the first three dimensions have a fixed, known cardinality (864 Pokémon, 4 sources, 9 generations), allowing direct key access without iterating/filtering arrays, and because all the real data complexity lives only in the final node.
- Source names use a "human-readable" format (`"Showdown Most Used"` instead of `showdown_usage`) per the data owner's preference when consuming the JSON directly.
- Empty keys are never filled in; the absence of a branch means "no data for that combination," not "empty data."
