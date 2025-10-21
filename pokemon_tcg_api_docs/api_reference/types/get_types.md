# Get Types

Get all possible Pokémon energy types available in the TCG.

## HTTP Request

```
GET https://api.pokemontcg.io/v2/types
```

## URL Parameters

None

## Query Parameters

None

## Authentication

```
X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## Code Samples

### Python
```python
from pokemontcgsdk import Type

# Get all types
types = Type.all()
print(types)
```

With requests:
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/types',
    headers=headers
)
types = response.json()['data']
print(types)
```

### cURL
```bash
curl "https://api.pokemontcg.io/v2/types" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### JavaScript
```javascript
const headers = {
  'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
};

fetch('https://api.pokemontcg.io/v2/types', { headers })
  .then(response => response.json())
  .then(result => {
    console.log(result.data);
  });
```

## Sample Response

```json
{
  "data": [
    "Colorless",
    "Darkness",
    "Dragon",
    "Fairy",
    "Fighting",
    "Fire",
    "Grass",
    "Lightning",
    "Metal",
    "Psychic",
    "Water"
  ]
}
```

## Available Types

| Type | Description |
|------|-------------|
| **Colorless** | Normal-type Pokémon |
| **Darkness** | Dark-type Pokémon |
| **Dragon** | Dragon-type Pokémon |
| **Fairy** | Fairy-type Pokémon (discontinued in newer sets) |
| **Fighting** | Fighting-type Pokémon |
| **Fire** | Fire-type Pokémon |
| **Grass** | Grass-type Pokémon |
| **Lightning** | Electric-type Pokémon |
| **Metal** | Steel-type Pokémon |
| **Psychic** | Psychic-type Pokémon |
| **Water** | Water-type Pokémon |

## Usage Examples

### Search Cards by Type
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}

# Get all Fire-type Pokémon
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=types:Fire',
    headers=headers
)
fire_cards = response.json()['data']
```

### Filter Multiple Types
```python
# Fire OR Water types
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=(types:Fire OR types:Water)',
    headers=headers
)
```

### Build Type Filter UI
```python
def get_cards_by_type(type_name):
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards?q=types:{type_name}',
        headers=headers
    )
    return response.json()['data']

# Get all types
types_response = requests.get(
    'https://api.pokemontcg.io/v2/types',
    headers=headers
)
all_types = types_response.json()['data']

# Allow user to select a type
for type_name in all_types:
    cards = get_cards_by_type(type_name)
    print(f"{type_name}: {len(cards)} cards")
```

## Notes

- Types represent energy types in the TCG
- Not all types appear in all sets (e.g., Fairy was discontinued)
- Dragon type was introduced later in the TCG history
- Some Pokémon cards can have multiple types

## Related Endpoints

- [Get Subtypes](get_subtypes.md) - Get all card subtypes
- [Get Supertypes](get_supertypes.md) - Get all card supertypes
- [Search Cards](../cards/search_cards.md) - Search cards by type
