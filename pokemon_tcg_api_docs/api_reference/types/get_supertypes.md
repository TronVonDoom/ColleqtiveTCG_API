# Get Supertypes

Get all possible card supertypes in the Pokémon TCG.

## HTTP Request

```
GET https://api.pokemontcg.io/v2/supertypes
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
from pokemontcgsdk import Supertype

# Get all supertypes
supertypes = Supertype.all()
print(supertypes)
```

With requests:
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/supertypes',
    headers=headers
)
supertypes = response.json()['data']
print(supertypes)
```

### cURL
```bash
curl "https://api.pokemontcg.io/v2/supertypes" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### JavaScript
```javascript
const headers = {
  'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
};

fetch('https://api.pokemontcg.io/v2/supertypes', { headers })
  .then(response => response.json())
  .then(result => {
    console.log(result.data);
  });
```

## Sample Response

```json
{
  "data": [
    "Energy",
    "Pokémon",
    "Trainer"
  ]
}
```

## Available Supertypes

| Supertype | Description |
|-----------|-------------|
| **Pokémon** | Pokémon cards that you play on the field |
| **Trainer** | Trainer cards (Items, Supporters, Stadiums, Tools, etc.) |
| **Energy** | Energy cards (Basic and Special Energy) |

## Supertype Breakdown

### Pokémon
Cards representing Pokémon creatures. These cards have:
- HP (Hit Points)
- Types (Fire, Water, Grass, etc.)
- Attacks and/or Abilities
- Weaknesses and Resistances
- Retreat Cost

### Trainer
Cards that provide various effects and support. Includes:
- **Items** - Instant effects
- **Supporters** - Powerful effects (one per turn)
- **Stadiums** - Field effects
- **Pokémon Tools** - Attachments to Pokémon
- **Technical Machines** - Special trainer cards

### Energy
Cards that provide energy to power attacks:
- **Basic Energy** - Standard energy types
- **Special Energy** - Energy with additional effects

## Usage Examples

### Search by Supertype
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}

# Get all Pokémon cards
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=supertype:Pokémon',
    headers=headers
)
pokemon_cards = response.json()['data']

# Get all Trainer cards
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=supertype:Trainer',
    headers=headers
)
trainer_cards = response.json()['data']

# Get all Energy cards
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=supertype:Energy',
    headers=headers
)
energy_cards = response.json()['data']
```

### Count Cards by Supertype
```python
def count_by_supertype():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    # Get all supertypes
    supertypes_response = requests.get(
        'https://api.pokemontcg.io/v2/supertypes',
        headers=headers
    )
    supertypes = supertypes_response.json()['data']
    
    # Count cards for each supertype
    for supertype in supertypes:
        response = requests.get(
            f'https://api.pokemontcg.io/v2/cards?q=supertype:{supertype}&pageSize=1',
            headers=headers
        )
        count = response.json()['totalCount']
        print(f"{supertype}: {count} cards")

count_by_supertype()
```

### Build Deck by Supertype Distribution
```python
def analyze_deck_composition(set_id):
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    supertypes = ['Pokémon', 'Trainer', 'Energy']
    composition = {}
    
    for supertype in supertypes:
        response = requests.get(
            f'https://api.pokemontcg.io/v2/cards?q=set.id:{set_id} supertype:{supertype}',
            headers=headers
        )
        composition[supertype] = len(response.json()['data'])
    
    total = sum(composition.values())
    print(f"Set {set_id} composition:")
    for supertype, count in composition.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {supertype}: {count} ({percentage:.1f}%)")

analyze_deck_composition('swsh4')
```

### Filter Specific Combinations
```python
# Get Fire-type Pokémon (combines supertype and type)
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=supertype:Pokémon types:Fire',
    headers=headers
)

# Get Supporter Trainers (combines supertype and subtype)
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=supertype:Trainer subtypes:Supporter',
    headers=headers
)

# Get Special Energy cards (combines supertype and subtype)
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=supertype:Energy subtypes:Special',
    headers=headers
)
```

### Get Random Card by Supertype
```python
import random

def get_random_card_by_supertype(supertype):
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    # Get total count
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards?q=supertype:{supertype}&pageSize=1',
        headers=headers
    )
    total_count = response.json()['totalCount']
    
    # Get random page
    random_page = random.randint(1, (total_count // 250) + 1)
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards?q=supertype:{supertype}&page={random_page}',
        headers=headers
    )
    cards = response.json()['data']
    
    # Return random card from page
    return random.choice(cards) if cards else None

random_pokemon = get_random_card_by_supertype('Pokémon')
print(f"Random Pokémon: {random_pokemon['name']}")
```

## Notes

- Every card has exactly one supertype
- Supertype is the highest-level categorization of cards
- Most cards in any set are Pokémon cards
- Trainer cards are the second most common
- Energy cards are typically the least numerous in sets

## Typical Set Distribution

A typical modern set might have:
- **~80-85%** Pokémon cards
- **~12-15%** Trainer cards
- **~2-5%** Energy cards

## Related Endpoints

- [Get Types](get_types.md) - Get all energy types
- [Get Subtypes](get_subtypes.md) - Get all card subtypes
- [Get Rarities](get_rarities.md) - Get all rarities
- [Search Cards](../cards/search_cards.md) - Search cards by supertype
