# Get Rarities

Get all possible card rarities available in the Pokémon TCG.

## HTTP Request

```
GET https://api.pokemontcg.io/v2/rarities
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
from pokemontcgsdk import Rarity

# Get all rarities
rarities = Rarity.all()
print(rarities)
```

With requests:
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/rarities',
    headers=headers
)
rarities = response.json()['data']
print(rarities)
```

### cURL
```bash
curl "https://api.pokemontcg.io/v2/rarities" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### JavaScript
```javascript
const headers = {
  'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
};

fetch('https://api.pokemontcg.io/v2/rarities', { headers })
  .then(response => response.json())
  .then(result => {
    console.log(result.data);
  });
```

## Sample Response

```json
{
  "data": [
    "Amazing Rare",
    "Common",
    "LEGEND",
    "Promo",
    "Rare",
    "Rare ACE",
    "Rare BREAK",
    "Rare Holo",
    "Rare Holo EX",
    "Rare Holo GX",
    "Rare Holo LV.X",
    "Rare Holo Star",
    "Rare Holo V",
    "Rare Holo VMAX",
    "Rare Prime",
    "Rare Prism Star",
    "Rare Rainbow",
    "Rare Secret",
    "Rare Shining",
    "Rare Shiny",
    "Rare Shiny GX",
    "Rare Ultra",
    "Uncommon"
  ]
}
```

## Rarity Tiers

### Common Rarities (Most Frequent)

#### Common
- Most basic rarity
- Usually makes up bulk of a set
- Circle symbol on older cards
- Common symbol on modern cards

#### Uncommon
- Slightly less common than Common
- Diamond symbol on older cards
- Uncommon symbol on modern cards

### Standard Rare Rarities

#### Rare
- Standard rare cards
- Star symbol
- Non-holographic

#### Rare Holo
- Holographic rare cards
- Star symbol with holographic effect
- Traditional holofoil pattern

### Special Rare Variants

#### Rare Holo EX
- Pokémon-EX cards
- Holographic with special artwork

#### Rare Holo GX
- Pokémon-GX cards
- Full art or regular GX cards

#### Rare Holo V
- Pokémon V cards
- Modern special cards

#### Rare Holo VMAX
- Pokémon VMAX cards
- Evolution of V cards

#### Rare Holo LV.X
- Level-Up Pokémon cards
- Diamond & Pearl era

#### Rare Holo Star
- Star Pokémon (★)
- Ultra rare in older sets

### Ultra Rare Rarities

#### Rare Ultra
- Ultra rare cards
- Often full art cards
- Very collectible

#### Rare Rainbow
- Rainbow rare cards
- Special holographic pattern
- Some of the most valuable cards

#### Rare Secret
- Secret rare cards
- Card number exceeds set's printed total
- Gold cards, alternate arts, etc.

### Special Rarities

#### Amazing Rare
- Special rarity introduced in Sword & Shield
- Unique holographic pattern

#### Rare BREAK
- BREAK Evolution cards
- XY era mechanic

#### Rare Prime
- Prime Pokémon cards
- HeartGold & SoulSilver era

#### Rare Prism Star
- Prism Star cards (◇)
- Limited to one per deck

#### Rare Shining / Rare Shiny
- Shining/Shiny Pokémon
- Special artwork variants

#### Rare Shiny GX
- Shiny GX Pokémon
- Hidden Fates subset

#### Rare ACE
- ACE SPEC cards
- Black & White era

#### LEGEND
- LEGEND cards
- Two-card sets that combine

#### Promo
- Promotional cards
- Not from standard sets

## Usage Examples

### Search by Rarity
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}

# Get all Secret Rare cards
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=rarity:"Rare Secret"',
    headers=headers
)
secret_rares = response.json()['data']
```

### Search Multiple Rarities
```python
# Get all ultra rare cards (Rainbow, Secret, Ultra)
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=(rarity:"Rare Rainbow" OR rarity:"Rare Secret" OR rarity:"Rare Ultra")',
    headers=headers
)
ultra_rares = response.json()['data']
```

### Count Cards by Rarity
```python
def count_by_rarity():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    # Get all rarities
    rarities_response = requests.get(
        'https://api.pokemontcg.io/v2/rarities',
        headers=headers
    )
    rarities = rarities_response.json()['data']
    
    counts = {}
    for rarity in rarities:
        response = requests.get(
            f'https://api.pokemontcg.io/v2/cards?q=rarity:"{rarity}"&pageSize=1',
            headers=headers
        )
        counts[rarity] = response.json()['totalCount']
    
    # Sort by count
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    print("Cards by Rarity:")
    for rarity, count in sorted_counts:
        print(f"{rarity}: {count}")

count_by_rarity()
```

### Get Most Valuable Rarities
```python
def get_expensive_cards_by_rarity(rarity, min_price=50):
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards?q=rarity:"{rarity}"',
        headers=headers
    )
    cards = response.json()['data']
    
    expensive_cards = []
    for card in cards:
        if 'tcgplayer' in card and 'prices' in card['tcgplayer']:
            for price_type, prices in card['tcgplayer']['prices'].items():
                if 'market' in prices and prices['market'] >= min_price:
                    expensive_cards.append({
                        'name': card['name'],
                        'set': card['set']['name'],
                        'price': prices['market']
                    })
                    break
    
    return sorted(expensive_cards, key=lambda x: x['price'], reverse=True)

expensive_secrets = get_expensive_cards_by_rarity('Rare Secret', min_price=100)
for card in expensive_secrets[:10]:  # Top 10
    print(f"{card['name']} ({card['set']}): ${card['price']}")
```

### Analyze Set Rarity Distribution
```python
def analyze_set_rarities(set_id):
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}',
        headers=headers
    )
    cards = response.json()['data']
    
    rarity_counts = {}
    for card in cards:
        rarity = card.get('rarity', 'Unknown')
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
    
    print(f"Rarity distribution for set {set_id}:")
    for rarity, count in sorted(rarity_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {rarity}: {count}")

analyze_set_rarities('swsh4')
```

### Build Collection Tracker
```python
def track_collection_by_rarity():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    # Define target rarities for collection
    target_rarities = ['Rare Holo', 'Rare Ultra', 'Rare Rainbow', 'Rare Secret']
    
    collection_goals = {}
    for rarity in target_rarities:
        response = requests.get(
            f'https://api.pokemontcg.io/v2/cards?q=rarity:"{rarity}" legalities.standard:legal',
            headers=headers
        )
        total = response.json()['totalCount']
        collection_goals[rarity] = total
    
    print("Standard-Legal Collection Goals:")
    for rarity, count in collection_goals.items():
        print(f"{rarity}: 0/{count} cards")

track_collection_by_rarity()
```

## Rarity Value Hierarchy (Generally)

From most to least valuable (typically):

1. **Rare Secret** / **Rare Rainbow** - Highest value
2. **Rare Ultra**
3. **Rare Holo VMAX** / **Rare Holo V**
4. **Rare Holo GX** / **Rare Holo EX**
5. **Amazing Rare** / **Rare Shiny**
6. **Rare Holo**
7. **Rare**
8. **Uncommon**
9. **Common** - Lowest value

**Note**: Actual value varies greatly by specific card, popularity, and playability.

## Notes

- Rarity affects pull rates from booster packs
- Secret Rares have card numbers beyond the set's printed total
- Some rarities are era-specific (e.g., BREAK, Prime)
- Promo cards have their own rarity designation
- Rainbow Rares are typically the most valuable variants

## Related Endpoints

- [Get Types](get_types.md) - Get all energy types
- [Get Subtypes](get_subtypes.md) - Get all card subtypes
- [Get Supertypes](get_supertypes.md) - Get all card supertypes
- [Search Cards](../cards/search_cards.md) - Search cards by rarity
