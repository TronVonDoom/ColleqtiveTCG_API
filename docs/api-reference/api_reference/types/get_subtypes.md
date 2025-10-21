# Get Subtypes

Get all possible card subtypes available in the Pokémon TCG.

## HTTP Request

```
GET https://api.pokemontcg.io/v2/subtypes
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
from pokemontcgsdk import Subtype

# Get all subtypes
subtypes = Subtype.all()
print(subtypes)
```

With requests:
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/subtypes',
    headers=headers
)
subtypes = response.json()['data']
print(subtypes)
```

### cURL
```bash
curl "https://api.pokemontcg.io/v2/subtypes" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### JavaScript
```javascript
const headers = {
  'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
};

fetch('https://api.pokemontcg.io/v2/subtypes', { headers })
  .then(response => response.json())
  .then(result => {
    console.log(result.data);
  });
```

## Sample Response

```json
{
  "data": [
    "BREAK",
    "Baby",
    "Basic",
    "EX",
    "GX",
    "Goldenrod Game Corner",
    "Item",
    "LEGEND",
    "Level-Up",
    "MEGA",
    "Pokémon Tool",
    "Pokémon Tool F",
    "Rapid Strike",
    "Restored",
    "Rocket's Secret Machine",
    "Single Strike",
    "Special",
    "Stadium",
    "Stage 1",
    "Stage 2",
    "Supporter",
    "TAG TEAM",
    "Technical Machine",
    "V",
    "VMAX"
  ]
}
```

## Subtype Categories

### Pokémon Evolution Stages
- **Basic** - Basic Pokémon (no evolution)
- **Stage 1** - First evolution
- **Stage 2** - Second evolution
- **Restored** - Fossil Pokémon
- **Baby** - Baby Pokémon (older sets)

### Special Pokémon Types
- **EX** - Pokémon-EX cards
- **GX** - Pokémon-GX cards
- **V** - Pokémon V cards
- **VMAX** - Pokémon VMAX cards
- **MEGA** - Mega Evolution Pokémon
- **BREAK** - BREAK Evolution Pokémon
- **Level-Up** - Level-Up Pokémon (LV.X)
- **LEGEND** - LEGEND cards
- **TAG TEAM** - TAG TEAM GX cards

### Battle Styles (Sword & Shield)
- **Rapid Strike** - Rapid Strike style
- **Single Strike** - Single Strike style

### Trainer Card Types
- **Item** - Item cards
- **Supporter** - Supporter cards
- **Stadium** - Stadium cards
- **Pokémon Tool** - Tool cards to attach to Pokémon
- **Pokémon Tool F** - Tool cards for Fusion Strike
- **Technical Machine** - TM cards
- **Rocket's Secret Machine** - Team Rocket TM cards

### Energy Types
- **Special** - Special Energy cards

### Other
- **Goldenrod Game Corner** - Special trainer type

## Usage Examples

### Search for Specific Subtypes
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}

# Get all VMAX Pokémon
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=subtypes:VMAX',
    headers=headers
)
vmax_cards = response.json()['data']
```

### Search Multiple Subtypes
```python
# Get all EX, GX, or V cards
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=(subtypes:EX OR subtypes:GX OR subtypes:V)',
    headers=headers
)
special_cards = response.json()['data']
```

### Filter by Evolution Stage
```python
# Get all Stage 2 Pokémon
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=subtypes:"Stage 2"',
    headers=headers
)
stage2_cards = response.json()['data']
```

### Build Subtype Filter
```python
def categorize_subtypes():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    response = requests.get(
        'https://api.pokemontcg.io/v2/subtypes',
        headers=headers
    )
    subtypes = response.json()['data']
    
    pokemon_stages = ['Basic', 'Stage 1', 'Stage 2', 'Restored', 'Baby']
    special_pokemon = ['EX', 'GX', 'V', 'VMAX', 'MEGA', 'BREAK', 'Level-Up', 'LEGEND', 'TAG TEAM']
    trainer_types = ['Item', 'Supporter', 'Stadium', 'Pokémon Tool', 'Technical Machine']
    
    return {
        'evolution_stages': [s for s in subtypes if s in pokemon_stages],
        'special_pokemon': [s for s in subtypes if s in special_pokemon],
        'trainer_types': [s for s in subtypes if s in trainer_types],
        'other': [s for s in subtypes if s not in pokemon_stages + special_pokemon + trainer_types]
    }

categories = categorize_subtypes()
for category, items in categories.items():
    print(f"\n{category.replace('_', ' ').title()}:")
    for item in items:
        print(f"  - {item}")
```

### Count Cards by Subtype
```python
def count_cards_by_subtype():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    # Get all subtypes
    subtypes_response = requests.get(
        'https://api.pokemontcg.io/v2/subtypes',
        headers=headers
    )
    subtypes = subtypes_response.json()['data']
    
    counts = {}
    for subtype in subtypes:
        response = requests.get(
            f'https://api.pokemontcg.io/v2/cards?q=subtypes:"{subtype}"&pageSize=1',
            headers=headers
        )
        counts[subtype] = response.json()['totalCount']
    
    # Sort by count
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    print("Cards by Subtype:")
    for subtype, count in sorted_counts:
        print(f"{subtype}: {count}")

count_cards_by_subtype()
```

## Notes

- Cards can have multiple subtypes (e.g., "Basic, V")
- Subtypes vary by era and set
- Some subtypes are specific to certain sets or series
- Evolution stages (Basic, Stage 1, Stage 2) are the most common
- Modern sets feature V, VMAX, and other special subtypes
- Older sets feature EX, GX, BREAK, etc.

## Related Endpoints

- [Get Types](get_types.md) - Get all energy types
- [Get Supertypes](get_supertypes.md) - Get all card supertypes
- [Get Rarities](get_rarities.md) - Get all rarities
- [Search Cards](../cards/search_cards.md) - Search cards by subtype
