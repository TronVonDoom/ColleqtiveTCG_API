# The Set Object

Complete reference for the set object structure in the Pokémon TCG API.

## Attributes

### `id` (string)
Unique identifier for the set.

**Format**: Usually lowercase abbreviation

**Examples**: 
- `"base1"` - Base Set
- `"swsh1"` - Sword & Shield Base
- `"xy1"` - XY Base
- `"sm1"` - Sun & Moon Base

### `name` (string)
The name of the set.

**Examples**:
- `"Base"`
- `"Sword & Shield"`
- `"Vivid Voltage"`
- `"Champion's Path"`

### `series` (string)
The series the set belongs to.

**Examples**:
- `"Base"`
- `"Sword & Shield"`
- `"Sun & Moon"`
- `"XY"`
- `"Black & White"`
- `"Diamond & Pearl"`

### `printedTotal` (integer)
The number printed on cards representing the set total. This does NOT include secret rares.

**Example**: `202` (for a set with 202 regular cards)

### `total` (integer)
The actual total number of cards in the set, including secret rares, alternate art, and other special cards.

**Example**: `216` (includes 202 regular + 14 secret rares)

**Note**: `total` is always >= `printedTotal`

### `legalities` (object)
The legalities of the set. If a format is not present, the set is not legal for that format.

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `standard` | string | "Legal" if legal in Standard |
| `expanded` | string | "Legal" if legal in Expanded |
| `unlimited` | string | "Legal" if legal in Unlimited |

**Example**:
```json
{
  "unlimited": "Legal",
  "standard": "Legal",
  "expanded": "Legal"
}
```

**Note**: Missing legality means not legal (different from banned)

### `ptcgoCode` (string)
The code the Pokémon Trading Card Game Online uses to identify a set.

**Examples**:
- `"BS"` - Base Set
- `"SSH"` - Sword & Shield
- `"VIV"` - Vivid Voltage
- `"CPA"` - Champion's Path

**Note**: This is useful for PTCGO/PTCGL deck imports

### `releaseDate` (string)
The date the set was released in the USA.

**Format**: `YYYY/MM/DD`

**Examples**:
- `"1999/01/09"` - Base Set
- `"2020/02/07"` - Sword & Shield
- `"2020/11/13"` - Vivid Voltage

### `updatedAt` (string)
The date and time the set was last updated in the API.

**Format**: `YYYY/MM/DD HH:MM:SS`

**Example**: `"2020/08/14 09:35:00"`

### `images` (object)
Images associated with the set.

**Structure**:
| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | URL to the set symbol image |
| `logo` | string | URL to the set logo image |

**Example**:
```json
{
  "symbol": "https://images.pokemontcg.io/swsh1/symbol.png",
  "logo": "https://images.pokemontcg.io/swsh1/logo.png"
}
```

**Image Uses**:
- **Symbol**: Small icon for displaying on cards or in lists
- **Logo**: Larger branded logo for set pages

## Sample JSON

Complete example of a set object:

```json
{
  "id": "swsh1",
  "name": "Sword & Shield",
  "series": "Sword & Shield",
  "printedTotal": 202,
  "total": 216,
  "legalities": {
    "unlimited": "Legal",
    "standard": "Legal",
    "expanded": "Legal"
  },
  "ptcgoCode": "SSH",
  "releaseDate": "2020/02/07",
  "updatedAt": "2020/08/14 09:35:00",
  "images": {
    "symbol": "https://images.pokemontcg.io/swsh1/symbol.png",
    "logo": "https://images.pokemontcg.io/swsh1/logo.png"
  }
}
```

## Common Set IDs

### Modern Sets

**Sword & Shield Series**:
- `swsh1` - Sword & Shield Base
- `swsh2` - Rebel Clash
- `swsh3` - Darkness Ablaze
- `swsh4` - Vivid Voltage
- `swsh5` - Battle Styles
- `swsh6` - Chilling Reign
- `swsh7` - Evolving Skies
- `swsh8` - Fusion Strike
- `swsh9` - Brilliant Stars
- `swsh10` - Astral Radiance
- `swsh11` - Lost Origin
- `swsh12` - Silver Tempest

**Sun & Moon Series**:
- `sm1` - Sun & Moon Base
- `sm2` - Guardians Rising
- `sm3` - Burning Shadows
- `sm4` - Crimson Invasion
- `sm5` - Ultra Prism
- `sm6` - Forbidden Light
- `sm7` - Celestial Storm
- `sm8` - Lost Thunder
- `sm9` - Team Up
- `sm10` - Unbroken Bonds
- `sm11` - Unified Minds
- `sm12` - Cosmic Eclipse

**XY Series**:
- `xy1` - XY Base
- `xy2` - Flashfire
- `xy3` - Furious Fists
- `xy4` - Phantom Forces
- `xy5` - Primal Clash
- `xy6` - Roaring Skies
- `xy7` - Ancient Origins
- `xy8` - BREAKthrough
- `xy9` - BREAKpoint
- `xy10` - Fates Collide
- `xy11` - Steam Siege
- `xy12` - Evolutions

### Classic Sets

**Original Series**:
- `base1` - Base Set
- `base2` - Jungle
- `base3` - Fossil
- `base4` - Base Set 2
- `base5` - Team Rocket

**Neo Series**:
- `neo1` - Neo Genesis
- `neo2` - Neo Discovery
- `neo3` - Neo Revelation
- `neo4` - Neo Destiny

**E-Card Series**:
- `ecard1` - Expedition Base Set
- `ecard2` - Aquapolis
- `ecard3` - Skyridge

## Calculating Secret Rares

```python
secret_rares = set['total'] - set['printedTotal']
print(f"Set has {secret_rares} secret rare cards")
```

Example: Vivid Voltage
- `printedTotal`: 185
- `total`: 203
- Secret Rares: 203 - 185 = 18 cards

## Using Set Data

### Check Format Legality
```python
def is_standard_legal(set_obj):
    return 'standard' in set_obj.get('legalities', {})

def is_expanded_legal(set_obj):
    return 'expanded' in set_obj.get('legalities', {})
```

### Sort by Release Date
```python
sets.sort(key=lambda x: x['releaseDate'], reverse=True)
```

### Filter by Series
```python
sword_shield_sets = [s for s in sets if s['series'] == 'Sword & Shield']
```

### Get Set from Card
```python
# When you have a card object
set_info = card['set']
print(f"From set: {set_info['name']} ({set_info['id']})")
print(f"Released: {set_info['releaseDate']}")
```

## Set Information Timeline

### By Release Date (Newest First)
Use `orderBy=-releaseDate` when searching sets

### By Series
Group sets by their `series` field to organize chronologically

### By Legality
Filter by `legalities` to find tournament-legal sets

## See Also

- [Get a Set](get_set.md) - Fetch a single set by ID
- [Search Sets](search_sets.md) - Search for sets with queries
- [Card Object](../cards/card_object.md) - Card object structure (contains embedded set)
