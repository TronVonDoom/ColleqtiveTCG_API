# Get a Card

Fetch the details of a single card by its ID.

## HTTP Request

```
GET https://api.pokemontcg.io/v2/cards/<id>
```

## URL Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `id` | string | The ID of the card | Yes |

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `select` | string | (all fields) | Comma-delimited list of fields to return |

### Using `select` Parameter

Request only specific fields to reduce response size:

```
GET https://api.pokemontcg.io/v2/cards/xy1-1?select=id,name,images
```

## Authentication

Include your API key in the header:
```
X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## Code Samples

### Python
```python
from pokemontcgsdk import Card

# Get a specific card
card = Card.find('xy1-1')
print(card.name)
```

Or with requests:
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/cards/xy1-1',
    headers=headers
)
card = response.json()['data']
print(card['name'])
```

### cURL
```bash
curl "https://api.pokemontcg.io/v2/cards/xy1-1" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### JavaScript (Fetch)
```javascript
const headers = {
  'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
};

fetch('https://api.pokemontcg.io/v2/cards/xy1-1', { headers })
  .then(response => response.json())
  .then(result => {
    const card = result.data;
    console.log(card.name);
  });
```

### JavaScript (Axios)
```javascript
const axios = require('axios');

const config = {
  headers: { 'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1' }
};

axios.get('https://api.pokemontcg.io/v2/cards/xy1-1', config)
  .then(response => {
    const card = response.data.data;
    console.log(card.name);
  });
```

## Sample Response

```json
{
  "data": {
    "id": "xy1-1",
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
        "name": "Poison Powder",
        "cost": ["Grass", "Colorless", "Colorless"],
        "convertedEnergyCost": 3,
        "damage": "60",
        "text": "Your opponent's Active Pokémon is now Poisoned."
      },
      {
        "name": "Jungle Hammer",
        "cost": ["Grass", "Grass", "Colorless", "Colorless"],
        "convertedEnergyCost": 4,
        "damage": "90",
        "text": "Heal 30 damage from this Pokémon."
      }
    ],
    "weaknesses": [
      {
        "type": "Fire",
        "value": "×2"
      }
    ],
    "retreatCost": ["Colorless", "Colorless", "Colorless", "Colorless"],
    "convertedRetreatCost": 4,
    "set": {
      "id": "xy1",
      "name": "XY",
      "series": "XY",
      "printedTotal": 146,
      "total": 146,
      "legalities": {
        "unlimited": "Legal",
        "expanded": "Legal"
      },
      "ptcgoCode": "XY",
      "releaseDate": "2014/02/05",
      "updatedAt": "2020/05/01 09:00:00",
      "images": {
        "symbol": "https://images.pokemontcg.io/xy1/symbol.png",
        "logo": "https://images.pokemontcg.io/xy1/logo.png"
      }
    },
    "number": "1",
    "artist": "Eske Yoshinob",
    "rarity": "Rare Holo EX",
    "nationalPokedexNumbers": [3],
    "legalities": {
      "unlimited": "Legal",
      "expanded": "Legal"
    },
    "images": {
      "small": "https://images.pokemontcg.io/xy1/1.png",
      "large": "https://images.pokemontcg.io/xy1/1_hires.png"
    },
    "tcgplayer": {
      "url": "https://prices.pokemontcg.io/tcgplayer/xy1-1",
      "updatedAt": "2021/08/04",
      "prices": {
        "holofoil": {
          "low": 3.99,
          "mid": 7.50,
          "high": 19.99,
          "market": 6.24,
          "directLow": 5.99
        }
      }
    }
  }
}
```

## Response Structure

The response contains a `data` object with the complete card information. See the [Card Object](card_object.md) reference for detailed field descriptions.

## Common Card IDs

Card IDs follow the format: `{set-id}-{card-number}`

**Examples**:
- `base1-4` - Charizard from Base Set
- `xy1-1` - Venusaur-EX from XY
- `swsh4-25` - Charizard from Vivid Voltage
- `sm1-1` - Rowlet from Sun & Moon Base
- `dp1-1` - Turtwig from Diamond & Pearl

## Error Responses

### Card Not Found (404)
```json
{
  "error": {
    "message": "Card not found",
    "code": 404
  }
}
```

### Invalid ID Format (400)
```json
{
  "error": {
    "message": "Bad Request. Invalid card ID format.",
    "code": 400
  }
}
```

## Tips

1. **Use the `select` parameter** to request only needed fields for better performance
2. **Cache responses** when possible to reduce API calls
3. **Check for missing fields** - Not all cards have all fields (e.g., some cards don't have abilities)
4. **Handle errors gracefully** - Always check for 404 responses

## Related Endpoints

- [Search Cards](search_cards.md) - Search for multiple cards
- [Card Object Reference](card_object.md) - Complete field documentation
- [Get All Sets](../sets/search_sets.md) - List all available sets

## Examples

### Get only name and images
```bash
curl "https://api.pokemontcg.io/v2/cards/base1-4?select=name,images" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### Get card with pricing info
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/cards/swsh4-25',
    headers=headers
)
card = response.json()['data']

if 'tcgplayer' in card:
    prices = card['tcgplayer']['prices']
    if 'normal' in prices:
        print(f"Market Price: ${prices['normal']['market']}")
```

### Check format legality
```python
card = response.json()['data']

if 'legalities' in card:
    standard_legal = 'standard' in card['legalities']
    expanded_legal = 'expanded' in card['legalities']
    
    print(f"Standard: {'Legal' if standard_legal else 'Not Legal'}")
    print(f"Expanded: {'Legal' if expanded_legal else 'Not Legal'}")
```
