# Get a Set

Fetch the details of a single set by its ID.

## HTTP Request

```
GET https://api.pokemontcg.io/v2/sets/<id>
```

## URL Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `id` | string | The ID of the set | Yes |

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `select` | string | (all fields) | Comma-delimited list of fields to return |

## Authentication

```
X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## Code Samples

### Python
```python
from pokemontcgsdk import Set

# Get a specific set
set_data = Set.find('swsh1')
print(set_data.name)
```

Or with requests:
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/sets/swsh1',
    headers=headers
)
set_data = response.json()['data']
print(f"{set_data['name']} - Released {set_data['releaseDate']}")
```

### cURL
```bash
curl "https://api.pokemontcg.io/v2/sets/swsh1" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### JavaScript
```javascript
const headers = {
  'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
};

fetch('https://api.pokemontcg.io/v2/sets/swsh1', { headers })
  .then(response => response.json())
  .then(result => {
    const set = result.data;
    console.log(`${set.name} - ${set.total} cards`);
  });
```

## Sample Response

```json
{
  "data": {
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
}
```

## Response Structure

The response contains a `data` object with the complete set information. See the [Set Object](set_object.md) reference for detailed field descriptions.

## Common Set IDs

### Recent Sets
- `swsh12` - Silver Tempest
- `swsh11` - Lost Origin
- `swsh10` - Astral Radiance
- `swsh9` - Brilliant Stars
- `swsh4` - Vivid Voltage
- `swsh1` - Sword & Shield Base

### Classic Sets
- `base1` - Base Set
- `base2` - Jungle
- `base3` - Fossil
- `neo1` - Neo Genesis
- `xy1` - XY
- `sm1` - Sun & Moon

See [Set Object Reference](set_object.md) for a complete list.

## Error Responses

### Set Not Found (404)
```json
{
  "error": {
    "message": "Set not found",
    "code": 404
  }
}
```

## Examples

### Get set with only specific fields
```bash
curl "https://api.pokemontcg.io/v2/sets/base1?select=id,name,total,releaseDate" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### Check if set is Standard legal
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/sets/swsh4',
    headers=headers
)
set_data = response.json()['data']

is_standard = 'standard' in set_data.get('legalities', {})
print(f"{set_data['name']} is {'legal' if is_standard else 'not legal'} in Standard")
```

### Calculate secret rares
```python
set_data = response.json()['data']
secret_rares = set_data['total'] - set_data['printedTotal']
print(f"{set_data['name']} has {secret_rares} secret rare cards")
```

### Get all cards from a set
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}

# First get the set info
set_response = requests.get(
    'https://api.pokemontcg.io/v2/sets/swsh4',
    headers=headers
)
set_data = set_response.json()['data']

# Then get all cards from that set
cards_response = requests.get(
    f'https://api.pokemontcg.io/v2/cards?q=set.id:{set_data["id"]}',
    headers=headers
)
cards = cards_response.json()['data']

print(f"Found {len(cards)} cards from {set_data['name']}")
```

## Tips

1. **Use `select` parameter** to request only needed fields
2. **Cache set data** - Set info changes infrequently
3. **Combine with card searches** - Use `set.id` in card queries
4. **Check legalities** - Missing legality means not legal

## Related Endpoints

- [Search Sets](search_sets.md) - Get all sets or search with queries
- [Set Object Reference](set_object.md) - Complete field documentation
- [Search Cards](../cards/search_cards.md) - Search cards by set

## Use Cases

### Display Set Information
```python
def display_set_info(set_id):
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    response = requests.get(
        f'https://api.pokemontcg.io/v2/sets/{set_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        set_data = response.json()['data']
        print(f"Name: {set_data['name']}")
        print(f"Series: {set_data['series']}")
        print(f"Released: {set_data['releaseDate']}")
        print(f"Cards: {set_data['printedTotal']} + {set_data['total'] - set_data['printedTotal']} secret")
        print(f"PTCGO Code: {set_data.get('ptcgoCode', 'N/A')}")
    else:
        print(f"Set not found: {set_id}")

display_set_info('swsh4')
```

### Build Set Gallery
```python
def get_set_with_images(set_id):
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    # Get set info
    set_response = requests.get(
        f'https://api.pokemontcg.io/v2/sets/{set_id}',
        headers=headers
    )
    set_data = set_response.json()['data']
    
    # Get all card images from set
    cards_response = requests.get(
        f'https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}&select=id,name,images',
        headers=headers
    )
    cards = cards_response.json()['data']
    
    return {
        'set': set_data,
        'cards': cards
    }
```
