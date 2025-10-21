# Pokémon TCG API - Quick Reference

Your quick-start guide to the Pokémon TCG API.

## Your API Key
```
0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## Base URL
```
https://api.pokemontcg.io/v2
```

## Authentication Header
```
X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## Rate Limits
- **With API Key**: 20,000 requests/day
- **Without API Key**: 1,000 requests/day, 30/minute max

---

## Quick Start Examples

### Get a Single Card
```bash
curl "https://api.pokemontcg.io/v2/cards/base1-4" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### Search for Cards
```bash
curl "https://api.pokemontcg.io/v2/cards?q=name:charizard" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### Get All Sets
```bash
curl "https://api.pokemontcg.io/v2/sets" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

---

## Main Endpoints

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `GET /cards` | Search cards | `/cards?q=name:pikachu` |
| `GET /cards/:id` | Get single card | `/cards/swsh4-25` |
| `GET /sets` | Search sets | `/sets?q=series:"Sword & Shield"` |
| `GET /sets/:id` | Get single set | `/sets/swsh4` |
| `GET /types` | Get all types | `/types` |
| `GET /subtypes` | Get all subtypes | `/subtypes` |
| `GET /supertypes` | Get all supertypes | `/supertypes` |
| `GET /rarities` | Get all rarities | `/rarities` |

---

## Common Query Parameters

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `q` | Search query | `q=name:charizard types:fire` |
| `page` | Page number | `page=2` |
| `pageSize` | Results per page | `pageSize=100` |
| `orderBy` | Sort results | `orderBy=-set.releaseDate` |
| `select` | Fields to return | `select=id,name,images` |

---

## Search Query Syntax

### Basic Search
```
name:charizard                    # Name contains "charizard"
types:Fire                        # Fire-type cards
hp:[150 TO *]                     # HP 150 or higher
set.id:swsh4                      # From Vivid Voltage set
```

### Operators
```
name:charizard subtypes:mega      # AND (both conditions)
(types:fire OR types:water)       # OR (either condition)
subtypes:vmax -types:water        # NOT (exclude water)
name:"venusaur v"                 # Exact phrase
name:char*                        # Wildcard
!name:charizard                   # Exact match only
```

### Ranges
```
hp:[100 TO 200]                   # Inclusive range
hp:{100 TO 200}                   # Exclusive range
hp:[* TO 100]                     # Up to 100
hp:[200 TO *]                     # 200 and above
nationalPokedexNumbers:[1 TO 151] # Original 151
```

### Nested Fields
```
set.id:swsh4                      # By set ID
set.name:"Vivid Voltage"          # By set name
attacks.name:flamethrower         # By attack name
legalities.standard:legal         # Standard legal
```

### Ordering
```
orderBy=name                      # Ascending by name
orderBy=-name                     # Descending by name
orderBy=hp,-set.releaseDate       # Multiple fields
```

---

## Python Quick Start

```python
import requests

API_KEY = '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
BASE_URL = 'https://api.pokemontcg.io/v2'
headers = {'X-Api-Key': API_KEY}

# Get a card
response = requests.get(f'{BASE_URL}/cards/base1-4', headers=headers)
card = response.json()['data']
print(card['name'])

# Search cards
params = {'q': 'name:pikachu', 'pageSize': 10}
response = requests.get(f'{BASE_URL}/cards', headers=headers, params=params)
cards = response.json()['data']

for card in cards:
    print(f"{card['name']} - {card['set']['name']}")
```

---

## Common Card Fields

```json
{
  "id": "swsh4-25",
  "name": "Charizard",
  "supertype": "Pokémon",
  "subtypes": ["Stage 2"],
  "hp": "170",
  "types": ["Fire"],
  "attacks": [...],
  "weaknesses": [...],
  "retreatCost": [...],
  "set": {...},
  "number": "25",
  "artist": "Artist Name",
  "rarity": "Rare Holo",
  "images": {
    "small": "https://images.pokemontcg.io/swsh4/25.png",
    "large": "https://images.pokemontcg.io/swsh4/25_hires.png"
  },
  "tcgplayer": {...},
  "legalities": {...}
}
```

---

## Common Set Fields

```json
{
  "id": "swsh4",
  "name": "Vivid Voltage",
  "series": "Sword & Shield",
  "printedTotal": 185,
  "total": 203,
  "legalities": {
    "standard": "Legal",
    "expanded": "Legal"
  },
  "releaseDate": "2020/11/13",
  "images": {
    "symbol": "https://images.pokemontcg.io/swsh4/symbol.png",
    "logo": "https://images.pokemontcg.io/swsh4/logo.png"
  }
}
```

---

## Image URLs

### Card Images
- **Small**: `https://images.pokemontcg.io/{setId}/{number}.png`
- **Large**: `https://images.pokemontcg.io/{setId}/{number}_hires.png`

### Set Images
- **Symbol**: `https://images.pokemontcg.io/{setId}/symbol.png`
- **Logo**: `https://images.pokemontcg.io/{setId}/logo.png`

---

## Common Set IDs

| ID | Set Name | Series |
|----|----------|--------|
| `base1` | Base Set | Base |
| `xy1` | XY | XY |
| `sm1` | Sun & Moon | Sun & Moon |
| `swsh1` | Sword & Shield | Sword & Shield |
| `swsh4` | Vivid Voltage | Sword & Shield |
| `swsh9` | Brilliant Stars | Sword & Shield |

---

## Energy Types
```
Colorless, Darkness, Dragon, Fairy, Fighting, Fire, 
Grass, Lightning, Metal, Psychic, Water
```

## Supertypes
```
Pokémon, Trainer, Energy
```

## Common Subtypes
```
Basic, Stage 1, Stage 2, EX, GX, V, VMAX, MEGA,
Item, Supporter, Stadium, Special
```

---

## Common Use Cases

### Find Standard-Legal Cards
```
q=legalities.standard:legal
```

### Find Expensive Cards
Look for `tcgplayer.prices.*.market` in results

### Get All Cards from a Set
```
q=set.id:swsh4
```

### Find Evolution Chains
```
q=name:charizard OR name:charmeleon OR name:charmander
```

### Find Cards by Artist
```
q=artist:"Ken Sugimori"
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid query) |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500+ | Server Error |

---

## Tips

1. ✅ Always use your API key for better rate limits
2. ✅ Use `select` parameter to request only needed fields
3. ✅ Cache responses when possible
4. ✅ Use pagination for large result sets
5. ✅ Add small delays between bulk requests
6. ✅ Handle 404 and rate limit errors gracefully
7. ✅ Use small images for galleries, large for details
8. ✅ Check `legalities` field for tournament-legal cards

---

## More Resources

- **Full Documentation**: See README.md
- **API Reference**: See api_reference/ folder
- **Code Examples**: See examples/code_examples.md
- **Image Guide**: See images/image_guide.md
- **Developer Portal**: https://dev.pokemontcg.io/
- **Discord**: https://discord.gg/dpsTCvg
- **GitHub**: https://github.com/PokemonTCG

---

## Quick Python Functions

```python
# Get random card
def get_random_card():
    import random
    response = requests.get(
        f'{BASE_URL}/cards',
        headers=headers,
        params={'page': random.randint(1, 100)}
    )
    cards = response.json()['data']
    return random.choice(cards) if cards else None

# Check if card is Standard legal
def is_standard_legal(card):
    return 'standard' in card.get('legalities', {})

# Get card price
def get_market_price(card):
    if 'tcgplayer' in card:
        prices = card['tcgplayer'].get('prices', {})
        for variant in prices.values():
            if 'market' in variant:
                return variant['market']
    return None
```
