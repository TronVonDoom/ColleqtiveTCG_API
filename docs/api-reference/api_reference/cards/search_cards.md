# Search Cards

Search for one or many cards using advanced query syntax.

## HTTP Request

```
GET https://api.pokemontcg.io/v2/cards
```

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | - | The search query (see syntax below) |
| `page` | integer | 1 | The page of data to access |
| `pageSize` | integer | 250 | Maximum cards to return (max: 250) |
| `orderBy` | string | - | Field(s) to order results by |
| `select` | string | (all) | Comma-delimited list of fields to return |

## Authentication

```
X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## Search Query Syntax

The `q` parameter uses Lucene-like syntax for powerful searches.

### Keyword Matching

#### Basic Search
Search for all cards with "charizard" in the name:
```
q=name:charizard
```

#### Phrase Search
Search for exact phrase "venusaur v":
```
q=name:"venusaur v"
```

#### AND Operator
Search for "charizard" in name AND "mega" subtype:
```
q=name:charizard subtypes:mega
```

#### OR Operator
Search for "charizard" with EITHER "mega" or "vmax" subtypes:
```
q=name:charizard (subtypes:mega OR subtypes:vmax)
```

#### NOT Operator
Search for all "mega" subtypes but NOT water types:
```
q=subtypes:mega -types:water
```

### Wildcard Matching

#### Start Wildcard
Search for names starting with "char":
```
q=name:char*
```

#### Start and End Wildcard
Search for names starting with "char" and ending with "der":
```
q=name:char*der
```

### Exact Matching

Search for cards named EXACTLY "charizard" (no other words):
```
q=!name:charizard
```

### Range Searches

Range searches work with numerical fields like `hp` and `nationalPokedexNumbers`.

#### Inclusive Range
Search for original 151 Pokémon (inclusive):
```
q=nationalPokedexNumbers:[1 TO 151]
```

#### Exclusive Range
Use curly braces for exclusive ranges:
```
q=hp:{100 TO 200}
```

#### Open-Ended Ranges
Search for HP up to 100:
```
q=hp:[* TO 100]
```

Search for HP 150 or greater:
```
q=hp:[150 TO *]
```

### Nested Field Search

Use a period `.` to search nested fields.

#### Search by Set ID
```
q=set.id:sm1
```

#### Search by Attack Name
```
q=attacks.name:Spelunk
```

#### Search by Legality
Find cards banned in Standard:
```
q=legalities.standard:banned
```

Find cards legal in Expanded:
```
q=legalities.expanded:legal
```

## Searchable Fields

All fields in the card object are searchable:

### Common Fields
- `name` - Card name
- `supertype` - Pokémon, Trainer, Energy
- `subtypes` - Basic, Stage 1, EX, VMAX, etc.
- `types` - Fire, Water, Grass, etc.
- `hp` - Hit points (numeric)
- `rarity` - Common, Rare, Rare Holo, etc.
- `artist` - Artist name
- `nationalPokedexNumbers` - Pokédex numbers (numeric)

### Nested Fields
- `set.id` - Set identifier
- `set.name` - Set name
- `set.series` - Series name
- `attacks.name` - Attack name
- `attacks.damage` - Attack damage
- `abilities.name` - Ability name
- `legalities.standard` - Standard legality
- `legalities.expanded` - Expanded legality

## Ordering Data

Use `orderBy` to sort results.

### Single Field
Order by card number:
```
?orderBy=number
```

### Descending Order
Use `-` prefix for descending:
```
?orderBy=-name
```

### Multiple Fields
Order by name (ascending), then number (descending):
```
?orderBy=name,-number
```

### Common Ordering Examples
```
?orderBy=set.releaseDate          # Oldest first
?orderBy=-set.releaseDate         # Newest first
?orderBy=name                     # Alphabetical
?orderBy=hp                       # Lowest HP first
?orderBy=-hp                      # Highest HP first
?orderBy=nationalPokedexNumbers   # Pokédex order
```

## Pagination

Control pagination with `page` and `pageSize`:

```
?page=1&pageSize=100
```

Response includes pagination info:
```json
{
  "data": [...],
  "page": 1,
  "pageSize": 100,
  "count": 100,
  "totalCount": 1234
}
```

## Code Samples

### Python

```python
from pokemontcgsdk import Card

# Get all cards (auto-pages)
cards = Card.all()

# Get single page
cards = Card.where(page=1, pageSize=250)

# Filter with query
cards = Card.where(q='set.name:generations subtypes:mega')

# Order by release date
cards = Card.where(q='subtypes:mega', orderBy='-set.releaseDate')
```

With requests:
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}

# Search for Charizard cards
params = {
    'q': 'name:charizard',
    'orderBy': '-set.releaseDate',
    'pageSize': 50
}

response = requests.get(
    'https://api.pokemontcg.io/v2/cards',
    headers=headers,
    params=params
)

data = response.json()
cards = data['data']

for card in cards:
    print(f"{card['name']} - {card['set']['name']}")
```

### cURL

```bash
curl "https://api.pokemontcg.io/v2/cards?q=name:charizard%20subtypes:mega" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### JavaScript

```javascript
const headers = {
  'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
};

const params = new URLSearchParams({
  q: 'name:charizard types:fire',
  orderBy: '-set.releaseDate',
  pageSize: 50
});

fetch(`https://api.pokemontcg.io/v2/cards?${params}`, { headers })
  .then(response => response.json())
  .then(result => {
    const cards = result.data;
    cards.forEach(card => {
      console.log(`${card.name} - ${card.set.name}`);
    });
  });
```

## Sample Response

```json
{
  "data": [
    {
      "id": "g1-1",
      "name": "Venusaur-EX",
      "supertype": "Pokémon",
      "subtypes": ["Basic", "EX"],
      "hp": "180",
      "types": ["Grass"],
      "evolvesTo": ["M Venusaur-EX"],
      "rules": [
        "Pokémon-EX rule: When a Pokémon-EX has been Knocked Out, your opponent takes 2 Prize cards."
      ],
      "attacks": [
        {
          "name": "Frog Hop",
          "cost": ["Grass", "Colorless", "Colorless"],
          "convertedEnergyCost": 3,
          "damage": "40+",
          "text": "Flip a coin. If heads, this attack does 40 more damage."
        }
      ],
      "weaknesses": [
        {
          "type": "Fire",
          "value": "×2"
        }
      ],
      "retreatCost": ["Colorless", "Colorless", "Colorless"],
      "convertedRetreatCost": 3,
      "set": {
        "id": "g1",
        "name": "Generations",
        "series": "XY",
        "printedTotal": 83,
        "total": 115,
        "legalities": {
          "unlimited": "Legal",
          "expanded": "Legal"
        },
        "ptcgoCode": "GEN",
        "releaseDate": "2016/02/22",
        "updatedAt": "2020/05/01 09:00:00",
        "images": {
          "symbol": "https://images.pokemontcg.io/g1/symbol.png",
          "logo": "https://images.pokemontcg.io/g1/logo.png"
        }
      },
      "number": "1",
      "artist": "Ryo Ueda",
      "rarity": "Rare Holo EX",
      "nationalPokedexNumbers": [3],
      "legalities": {
        "unlimited": "Legal",
        "expanded": "Legal"
      },
      "images": {
        "small": "https://images.pokemontcg.io/g1/1.png",
        "large": "https://images.pokemontcg.io/g1/1_hires.png"
      }
    }
  ],
  "page": 1,
  "pageSize": 250,
  "count": 1,
  "totalCount": 1
}
```

## Query Examples

### Find Specific Pokémon
```
# Pikachu cards
q=name:pikachu

# Shiny Pokémon
q=rarity:"Rare Shiny"

# Pikachu VMAX
q=name:pikachu subtypes:vmax
```

### Filter by Type
```
# Fire-type Pokémon
q=types:fire

# Psychic OR Dark types
q=(types:psychic OR types:darkness)

# Fire-type with 200+ HP
q=types:fire hp:[200 TO *]
```

### Filter by Set
```
# Cards from Base Set
q=set.id:base1

# Cards from Sword & Shield series
q=set.series:"Sword & Shield"

# Cards from Vivid Voltage
q=set.name:"Vivid Voltage"
```

### Filter by Legality
```
# Standard legal cards
q=legalities.standard:legal

# Banned in Standard
q=legalities.standard:banned

# Expanded legal fire types
q=legalities.expanded:legal types:fire
```

### Filter by Rarity
```
# All Secret Rares
q=rarity:"Rare Secret"

# Rare Holo or better
q=(rarity:"Rare Holo" OR rarity:"Rare Ultra" OR rarity:"Rare Secret")
```

### Complex Queries
```
# Fire-type Charizards from 2020 onwards
q=name:charizard types:fire set.releaseDate:[2020/01/01 TO *]

# VMAX Pokémon with 300+ HP that are Standard legal
q=subtypes:vmax hp:[300 TO *] legalities.standard:legal

# Original 151 Pokémon that are Common or Uncommon
q=nationalPokedexNumbers:[1 TO 151] (rarity:Common OR rarity:Uncommon)
```

### Artist Search
```
# Cards by specific artist
q=artist:"Ken Sugimori"

# Cards with artist name starting with "Mitsuhiro"
q=artist:Mitsuhiro*
```

### Attack Search
```
# Cards with "Dragon" in attack name
q=attacks.name:dragon*

# Cards with 200+ damage attacks
q=attacks.damage:[200 TO *]
```

## Tips

1. **URL Encode Queries**: Remember to URL encode special characters in URLs
2. **Use Quotes**: Use quotes for phrases with spaces: `name:"venusaur v"`
3. **Test Incrementally**: Build complex queries step by step
4. **Order Matters**: Use `orderBy` for consistent pagination
5. **Limit Results**: Use `pageSize` to control response size
6. **Select Fields**: Use `select` parameter for better performance

## Performance Tips

### Only Request Needed Fields
```
?q=name:charizard&select=id,name,images,set
```

### Use Pagination Efficiently
```python
page = 1
all_cards = []

while True:
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards?q=types:fire&page={page}',
        headers=headers
    ).json()
    
    all_cards.extend(response['data'])
    
    if len(response['data']) < response['pageSize']:
        break
    
    page += 1
```

### Cache Results
```python
import requests_cache

# Cache responses for 1 hour
requests_cache.install_cache('pokemon_cache', expire_after=3600)
```

## Related

- [Get a Card](get_card.md) - Get single card by ID
- [Card Object](card_object.md) - Complete field reference
- [Get Sets](../sets/search_sets.md) - Search for sets
