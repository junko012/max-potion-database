# Especificación: `movesets_consolidado.json`

Este documento describe la estructura del archivo `movesets_consolidado.json`, que combina movesets de Pokémon de 3 fuentes originales (Smogon, Pokémon Showdown y Randbats) en un único JSON, organizado en forma de árbol. El objetivo es que cualquier desarrollador (o instancia de Claude) que necesite escribir código para leer este archivo entienda exactamente qué esperar en cada nivel, sin tener que inspeccionar el archivo manualmente.

## 1. Estructura general (4 niveles)

```
{
  "<NombrePokemon>": {
    "<Fuente>": {
      "<Generacion>": <nodo_datos>
    }
  }
}
```

- **Nivel 1 — Pokémon**: clave = nombre exacto del Pokémon (string), tal como aparece en Pokémon Showdown (ej. `"Charizard"`, `"Charizard-Mega-X"`, `"Tornadus-Therian"`). Las formas alternativas (Mega, regional, etc.) son claves independientes, no están anidadas dentro del Pokémon base.
- **Nivel 2 — Fuente**: una de exactamente 4 strings literales (case-sensitive):
  - `"Smogon"`
  - `"Showdown"`
  - `"Showdown Most Used"`
  - `"Randbats"`
- **Nivel 3 — Generación**: string con el formato `"gen1"` a `"gen9"`.
- **Nivel 4 — Nodo `datos`**: aquí es donde cambia la forma según la fuente (ver sección 3). **Toda la complejidad de parseo vive en este nivel.**

### Regla importante: ausencia de datos
Si un Pokémon no tiene información para una fuente o generación determinada, **esa clave simplemente no existe** (no aparece como `null`, `{}` ni `[]`). Tu código debe usar acceso seguro (`?.` en JS/TS, `.get()` en Python, etc.) en cada nivel, nunca asumir que una rama existe.

```js
const data = movesets["Pikachu"]?.["Randbats"]?.["gen9"]; // puede ser undefined
```

## 2. Mapa rápido de fuentes

| Fuente | Origen | Qué representa |
|---|---|---|
| `Smogon` | Smogon Strategy Dex | Sets de análisis competitivo, escritos/curados por la comunidad. Puede contener **alternativas** (slashes "X/Y") representadas como arrays anidados. |
| `Showdown` | Pokémon Showdown teambuilder ("dex") | Misma idea que Smogon pero **ya resuelto**: cada campo es siempre un valor único, nunca un array de alternativas. |
| `Showdown Most Used` | Pokémon Showdown usage stats ("stats") | Sets derivados de estadísticas de uso real en batallas. Solo trae un set llamado `"Showdown Usage"`. |
| `Randbats` | Random Battles | Sets usados en el formato Random Battle. Estructura distinta: usa `level`, y desde gen2 en adelante usa `roles` (varios sub-sets por rol). |

## 3. Forma del nodo `datos` por fuente

### 3.1 `Smogon`
Diccionario de `nombreDelSet → detalles`. **Único caso donde los campos pueden ser string o array de alternativas** — tu parser debe checkear el tipo en cada campo.

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

Campos posibles dentro de cada set: `moves` (array; cada elemento puede ser un string o, si hay alternativas, un array de strings), `ability`, `item`, `nature` (string o array de alternativas), `evs`, `ivs`, `teratypes` (string o array, solo aparece desde gen9). No todos los campos están siempre presentes.

**Cómo resolver alternativas**: si un campo es un array donde se esperaba un string (`nature`, `item`, `ability`) o un elemento de `moves` es a su vez un array, significa "elige una opción de esta lista". Para mostrar un set "jugable" en la UI puedes tomar la primera opción por defecto, o dejar que el usuario elija.

### 3.2 `Showdown`
Misma forma que `Smogon`, pero **sin alternativas** (siempre valores únicos, listo para usar directo).

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
Diccionario con **una sola clave fija**: `"Showdown Usage"`. Incluye `level` (no aparece en Smogon/Showdown).

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

Como solo hay un set por generación, si tu app espera "una lista de sets" para mostrar, aquí siempre tendrá longitud 1.

### 3.4 `Randbats` — la fuente con más variación
Aquí la forma cambia según la generación:

**Gen 1**: estructura plana, sin `roles`.
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
Nota: en gen1, `moves` puede tener más de 4 elementos — son **todos los movimientos posibles** que el set aleatorio puede elegir, no necesariamente las 4 que se usan en una partida específica.

**Gen 2 a Gen 9**: estructura con `roles` (uno o más sub-sets nombrados).
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

Puntos clave de `Randbats`:
- `abilities` e `items` a nivel raíz son la **unión** de todas las habilidades/ítems posibles entre todos los roles (útil para filtros rápidos sin entrar a `roles`).
- El detalle real de un set jugable (los 4-5 movimientos que efectivamente se usan) está **dentro de cada rol**, en `roles.<nombreRol>.moves`.
- `teraTypes` (con "T" mayúscula aquí, a diferencia de `teratypes` en Smogon) es siempre un array, nunca un string suelto.
- En `evs`/`ivs`, las claves no listadas no tienen un valor fijo universal: representan estadísticas que el generador de equipos no restringe explícitamente. Para efectos prácticos, puedes asumir 0 para `evs` y 31 para `ivs` en las claves ausentes, salvo que tu app necesite la exactitud completa del generador de Showdown.

## 4. Claves de estadísticas (evs/ivs)
Siempre en minúsculas y abreviadas: `hp`, `atk`, `def`, `spa`, `spd`, `spe`. No siempre aparecen las 6; solo las que el set restringe explícitamente.

## 5. Pseudocódigo de carga recomendado

```ts
type Fuente = "Smogon" | "Showdown" | "Showdown Most Used" | "Randbats";

function getSets(movesets: any, pokemon: string, fuente: Fuente, gen: number) {
  const genKey = `gen${gen}`;
  const nodo = movesets?.[pokemon]?.[fuente]?.[genKey];
  if (!nodo) return null;

  switch (fuente) {
    case "Smogon":
    case "Showdown":
      // nodo = { nombreSet: { moves, ability, item, nature, evs, ivs, teratypes } }
      return Object.entries(nodo).map(([setName, set]) => ({ setName, ...resolveAlternatives(set) }));

    case "Showdown Most Used":
      // nodo = { "Showdown Usage": { level, moves, ... } }
      return nodo["Showdown Usage"];

    case "Randbats":
      if (nodo.roles) {
        // gen2-9: iterar roles
        return Object.entries(nodo.roles).map(([roleName, role]) => ({ roleName, level: nodo.level, ...role }));
      }
      // gen1: plano
      return [{ level: nodo.level, moves: nodo.moves, evs: nodo.evs, ivs: nodo.ivs }];
  }
}

// Solo necesario para fuente "Smogon": resuelve campos que pueden venir como array de alternativas
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

Adapta el pseudocódigo al lenguaje real de tu app (el patrón — switch por fuente, acceso seguro por nivel, resolución de alternativas solo en Smogon — se mantiene igual en cualquier stack).

## 6. Resumen de decisiones de diseño (contexto)
- Se eligió estructura de árbol (`Pokémon → Fuente → Generación → datos`) en vez de lista plana porque las 3 primeras dimensiones tienen cardinalidad fija y conocida (864 Pokémon, 4 fuentes, 9 generaciones), permitiendo acceso directo por clave sin iterar/filtrar arrays, y porque la complejidad real de los datos vive únicamente en el nodo final.
- Los nombres de fuente están en formato "humano" (`"Showdown Most Used"` en vez de `showdown_usage`) por preferencia del usuario al consumir el JSON directamente.
- No se rellenan claves vacías; la ausencia de una rama significa "sin datos para esa combinación", no "datos vacíos".
