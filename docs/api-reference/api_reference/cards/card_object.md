# The Card Object

Complete reference for the card object structure in the Pokémon TCG API.

## Attributes

### Basic Information

#### `id` (string)
Unique identifier for the card.

**Example**: `"swsh4-25"`

#### `name` (string)
The name of the card.

**Example**: `"Charizard"`

#### `supertype` (string)
The supertype of the card.

**Possible Values**: 
- `Pokémon`
- `Energy`
- `Trainer`

#### `subtypes` (list of strings)
A list of subtypes for the card.

**Examples**: 
- `["Basic", "EX"]`
- `["Stage 2"]`
- `["Item"]`
- `["MEGA"]`
- `["V", "VMAX"]`

#### `level` (string)
The level of the card. Only pertains to older sets and Pokémon supertype cards.

**Example**: `"42"`

---

### Pokémon-Specific Attributes

#### `hp` (string)
The hit points of the card.

**Example**: `"170"`

#### `types` (list of strings)
The energy types for a card.

**Possible Values**: 
- `Fire`
- `Water`
- `Grass`
- `Lightning`
- `Psychic`
- `Fighting`
- `Darkness`
- `Metal`
- `Fairy`
- `Dragon`
- `Colorless`

**Example**: `["Fire"]`

#### `evolvesFrom` (string)
Which Pokémon this card evolves from.

**Example**: `"Charmeleon"`

#### `evolvesTo` (list of strings)
Which Pokémon this card evolves to. Can be multiple (e.g., Eevee).

**Example**: `["M Charizard-EX"]` or `["Vaporeon", "Jolteon", "Flareon"]`

#### `rules` (list of strings)
Any rules associated with the card.

**Examples**:
- VMAX rules
- Mega rules
- EX rules
- Trainer rules

**Example**: 
```json
["Pokémon-EX rule: When a Pokémon-EX has been Knocked Out, your opponent takes 2 Prize cards."]
```

---

### Abilities and Traits

#### `ancientTrait` (object)
The ancient trait for a given card (if applicable).

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The name of the ancient trait |
| `text` | string | The text value of the ancient trait |

**Example**:
```json
{
  "name": "Θ Stop",
  "text": "Prevent all effects of your opponent's Pokémon's Abilities done to this Pokémon."
}
```

#### `abilities` (list of objects)
One or more abilities for a given card.

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The name of the ability |
| `text` | string | The text value of the ability |
| `type` | string | The type (e.g., "Ability", "Pokémon-Power") |

**Example**:
```json
[
  {
    "name": "Battle Sense",
    "text": "Once during your turn, you may look at the top 3 cards of your deck and put 1 of them into your hand. Discard the other cards.",
    "type": "Ability"
  }
]
```

---

### Attacks

#### `attacks` (list of objects)
One or more attacks for a given card.

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `cost` | list of strings | The cost represented by energy types |
| `name` | string | The name of the attack |
| `text` | string | The text/description of the attack |
| `damage` | string | The damage amount |
| `convertedEnergyCost` | integer | Total cost (e.g., 2 fire energy = 2) |

**Example**:
```json
[
  {
    "name": "Royal Blaze",
    "cost": ["Fire", "Fire"],
    "convertedEnergyCost": 2,
    "damage": "100+",
    "text": "This attack does 50 more damage for each Leon card in your discard pile."
  }
]
```

---

### Weaknesses, Resistances, and Retreat

#### `weaknesses` (list of objects)
One or more weaknesses for a given card.

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `type` | string | The type of weakness (e.g., Fire, Water) |
| `value` | string | The value of the weakness |

**Example**:
```json
[
  {
    "type": "Water",
    "value": "×2"
  }
]
```

#### `resistances` (list of objects)
One or more resistances for a given card.

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `type` | string | The type of resistance |
| `value` | string | The value of the resistance |

**Example**:
```json
[
  {
    "type": "Fighting",
    "value": "-30"
  }
]
```

#### `retreatCost` (list of strings)
A list of costs to retreat the card to your bench. Each cost is an energy type.

**Example**: `["Colorless", "Colorless", "Colorless"]`

#### `convertedRetreatCost` (integer)
The count of energy types in the retreatCost field.

**Example**: `3` (for three energy retreat)

---

### Set Information

#### `set` (object)
The set details embedded into the card. See the [Set Object](../sets/set_object.md) for complete details.

**Example**:
```json
{
  "id": "swsh4",
  "name": "Vivid Voltage",
  "series": "Sword & Shield",
  "printedTotal": 185,
  "total": 203,
  "legalities": {...},
  "ptcgoCode": "VIV",
  "releaseDate": "2020/11/13",
  "updatedAt": "2020/11/13 09:00:00",
  "images": {...}
}
```

#### `number` (string)
The number of the card in the set.

**Example**: `"25"`

---

### Card Metadata

#### `artist` (string)
The artist of the card.

**Example**: `"Kouki Saitou"`

#### `rarity` (string)
The rarity of the card.

**Possible Values**:
- `Common`
- `Uncommon`
- `Rare`
- `Rare Holo`
- `Rare Holo EX`
- `Rare Holo GX`
- `Rare Holo V`
- `Rare Holo VMAX`
- `Rare Rainbow`
- `Rare Secret`
- `Amazing Rare`
- And more...

#### `flavorText` (string)
The flavor text of the card (usually italicized text at the bottom).

**Example**: `"It is said to be the world's largest Pokémon. It is said to breath fire that is hot enough to melt anything."`

#### `nationalPokedexNumbers` (list of integers)
The national pokédex numbers associated with any Pokémon featured on the card.

**Example**: `[6]` (for Charizard)

For TAG TEAM cards: `[25, 133]` (Pikachu & Eevee)

---

### Legalities

#### `legalities` (object)
The legalities for a given card. A legality will NOT be present if it's not legal. If Legal or Banned, it will be specified.

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `standard` | string | Legal, Banned, or not present |
| `expanded` | string | Legal, Banned, or not present |
| `unlimited` | string | Legal, Banned, or not present |

**Example**:
```json
{
  "unlimited": "Legal",
  "standard": "Legal",
  "expanded": "Legal"
}
```

**Note**: If a format is missing, the card is not legal for that format (different from being banned).

#### `regulationMark` (string)
A letter symbol on each card that identifies tournament legality. Introduced in Sword & Shield series.

**Example**: `"D"`, `"E"`, `"F"`

---

### Images

#### `images` (object)
The images for a card.

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `small` | string | Lower-res image URL |
| `large` | string | Higher-res image URL |

**Example**:
```json
{
  "small": "https://images.pokemontcg.io/swsh4/25.png",
  "large": "https://images.pokemontcg.io/swsh4/25_hires.png"
}
```

**Image Formats**:
- Small: Suitable for thumbnails and lists
- Large: High-resolution for detailed viewing

---

### Pricing Information

#### `tcgplayer` (object)
TCGPlayer information for a given card. **ALL PRICES ARE IN US DOLLARS.**

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `url` | string | URL to TCGPlayer store page |
| `updatedAt` | string | Date price was last updated (YYYY/MM/DD) |
| `prices` | object | Hash of price types |

**Price Types**: `normal`, `holofoil`, `reverseHolofoil`, `1stEditionHolofoil`, `1stEditionNormal`

**Each price type contains**:
| Field | Type | Description |
|-------|------|-------------|
| `low` | decimal | Low price |
| `mid` | decimal | Mid price |
| `high` | decimal | High price |
| `market` | decimal | Market value (best representation) |
| `directLow` | decimal | Direct low price |

**Example**:
```json
{
  "url": "https://prices.pokemontcg.io/tcgplayer/swsh4-25",
  "updatedAt": "2021/08/04",
  "prices": {
    "normal": {
      "low": 1.73,
      "mid": 3.54,
      "high": 12.99,
      "market": 2.82,
      "directLow": 3.93
    },
    "reverseHolofoil": {
      "low": 2.00,
      "mid": 4.00,
      "high": 15.00,
      "market": 3.50
    }
  }
}
```

#### `cardmarket` (object)
Cardmarket information for a given card. **ALL PRICES ARE IN EUROS.**

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `url` | string | URL to Cardmarket store page |
| `updatedAt` | string | Date price was last updated (YYYY/MM/DD) |
| `prices` | object | Hash of price types |

**Price Fields**:
| Field | Description |
|-------|-------------|
| `averageSellPrice` | Average sell price for non-foils |
| `lowPrice` | Lowest market price for non-foils |
| `trendPrice` | Trend price for non-foils |
| `germanProLow` | Lowest from German pro sellers |
| `suggestedPrice` | Suggested price for pro users |
| `reverseHoloSell` | Average sell price for reverse holos |
| `reverseHoloLow` | Lowest price for reverse holos |
| `reverseHoloTrend` | Trend price for reverse holos |
| `lowPriceExPlus` | Lowest price for EX+ condition |
| `avg1` | Average sale price over last day |
| `avg7` | Average sale price over last 7 days |
| `avg30` | Average sale price over last 30 days |
| `reverseHoloAvg1` | Reverse holo avg over last day |
| `reverseHoloAvg7` | Reverse holo avg over last 7 days |
| `reverseHoloAvg30` | Reverse holo avg over last 30 days |

---

## Sample JSON

Complete example of a card object:

```json
{
  "id": "swsh4-25",
  "name": "Charizard",
  "supertype": "Pokémon",
  "subtypes": ["Stage 2"],
  "hp": "170",
  "types": ["Fire"],
  "evolvesFrom": "Charmeleon",
  "abilities": [
    {
      "name": "Battle Sense",
      "text": "Once during your turn, you may look at the top 3 cards of your deck and put 1 of them into your hand. Discard the other cards.",
      "type": "Ability"
    }
  ],
  "attacks": [
    {
      "name": "Royal Blaze",
      "cost": ["Fire", "Fire"],
      "convertedEnergyCost": 2,
      "damage": "100+",
      "text": "This attack does 50 more damage for each Leon card in your discard pile."
    }
  ],
  "weaknesses": [
    {
      "type": "Water",
      "value": "×2"
    }
  ],
  "retreatCost": ["Colorless", "Colorless", "Colorless"],
  "convertedRetreatCost": 3,
  "set": {
    "id": "swsh4",
    "name": "Vivid Voltage",
    "series": "Sword & Shield",
    "printedTotal": 185,
    "total": 203,
    "legalities": {
      "unlimited": "Legal"
    },
    "ptcgoCode": "VIV",
    "releaseDate": "2020/11/13",
    "updatedAt": "2020/11/13 09:00:00",
    "images": {
      "symbol": "https://images.pokemontcg.io/swsh4/symbol.png",
      "logo": "https://images.pokemontcg.io/swsh4/logo.png"
    }
  },
  "number": "25",
  "artist": "Kouki Saitou",
  "rarity": "Rare Holo",
  "flavorText": "It spits fire that is hot enough to melt boulders. It may cause forest fires by blowing flames.",
  "nationalPokedexNumbers": [6],
  "legalities": {
    "unlimited": "Legal",
    "standard": "Legal",
    "expanded": "Legal"
  },
  "images": {
    "small": "https://images.pokemontcg.io/swsh4/25.png",
    "large": "https://images.pokemontcg.io/swsh4/25_hires.png"
  },
  "tcgplayer": {
    "url": "https://prices.pokemontcg.io/tcgplayer/swsh4-25",
    "updatedAt": "2021/08/04",
    "prices": {
      "normal": {
        "low": 1.73,
        "mid": 3.54,
        "high": 12.99,
        "market": 2.82,
        "directLow": 3.93
      },
      "reverseHolofoil": {
        "low": 2.00,
        "mid": 4.00,
        "high": 15.00,
        "market": 3.50
      }
    }
  }
}
```

## See Also

- [Get a Card](get_card.md) - Fetch a single card by ID
- [Search Cards](search_cards.md) - Search for cards with queries
- [Set Object](../sets/set_object.md) - Set object structure
