# V1 to V2 Migration Guide

## Version 1 Deprecation

**Important**: Version 1 of the API is officially deprecated as of August 1, 2021. The last set available in V1 is Chilling Reigns. Please update your application to use V2.

## Major Changes

### 1. API Usage

#### API Keys
- V2 requires API keys for better rate limits
- Provide keys via `X-Api-Key` header
- Sign up at: https://dev.pokemontcg.io/

#### Query Parameters
- V2 uses a single `q` parameter for queries instead of individual field parameters
- More advanced query operators available
- Lucene-like syntax

**V1 Example:**
```
GET /v1/cards?name=charizard&types=fire
```

**V2 Example:**
```
GET /v2/cards?q=name:charizard types:fire
```

### 2. Card JSON Response Changes

| V1 Field | V2 Field | Type Change |
|----------|----------|-------------|
| `subtype` | `subtypes` | Now an array of strings |
| `ability` | `abilities` | Now an array to support multiple abilities |
| `nationalPokedexNumber` | `nationalPokedexNumbers` | Now an array (supports TAG TEAM cards) |
| `imageUrl` | `images.small` | Moved to nested object |
| `imageUrlHiRes` | `images.large` | Moved to nested object |
| `setCode` | `set.id` | Embedded in set object |
| `set` (name) | `set.name` | Embedded in set object |
| `text` | `rules` | Renamed for clarity |

#### New Fields in V2

**legalities** - Format legality information
```json
{
  "legalities": {
    "standard": "Legal",
    "expanded": "Legal",
    "unlimited": "Legal"
  }
}
```
- If a format is not present, the card is not legal (different from "Banned")
- Possible values: "Legal", "Banned"

**tcgplayer** - Pricing information from TCGPlayer
```json
{
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
      }
    }
  }
}
```

**cardmarket** - Pricing information from Cardmarket (Europe)

**flavorText** - Italicized text at bottom of cards

**evolvesTo** - Array of strings for evolution chains

**regulationMark** - Tournament legality marker (Sword & Shield onwards)

### 3. Set JSON Response Changes

| V1 Field | V2 Field | Change |
|----------|----------|--------|
| `standardLegal` | `legalities.standard` | Part of legalities object |
| `expandedLegal` | `legalities.expanded` | Part of legalities object |
| `totalCards` | `printedTotal` | Renamed |
| N/A | `total` | NEW: Includes secret rares |
| `symbolUrl` | `images.symbol` | Moved to images object |
| `logoUrl` | `images.logo` | Moved to images object |

**printedTotal** vs **total**:
- `printedTotal`: The number shown on the card
- `total`: Includes all cards (printedTotal + secret rares + alternate art)

Example:
```json
{
  "printedTotal": 202,
  "total": 216
}
```

### 4. Response Structure Changes

#### Data Wrapper
All responses now wrap data in a `data` field:

**V1:**
```json
{
  "cards": [...]
}
```

**V2:**
```json
{
  "data": [...]
}
```

This applies to all endpoints: `/cards`, `/sets`, `/types`, etc.

#### Pagination
Pagination info moved from headers to response body:

**V2 Pagination:**
```json
{
  "data": [...],
  "page": 1,
  "pageSize": 250,
  "count": 250,
  "totalCount": 1234
}
```

### 5. Data Changes

#### Breaking Changes
- **Aquapolis and Skyridge H1-H32 cards have new IDs**
  - Old format: Various inconsistent formats
  - New format: `{set-id}-{card-number}` (e.g., `ecard2-H1`, `ecard3-H32`)

#### Data Quality
- Full rebuild of all sets
- Corrections to typos
- Fixed missing attacks
- Corrected incorrect data
- More comprehensive and accurate information

## Migration Checklist

### 1. Update Base URL
```diff
- https://api.pokemontcg.io/v1/
+ https://api.pokemontcg.io/v2/
```

### 2. Add API Key Header
```python
headers = {
    'X-Api-Key': 'your-api-key-here'
}
```

### 3. Update Query Parameters
```diff
- GET /cards?name=charizard&subtypes=mega
+ GET /cards?q=name:charizard subtypes:mega
```

### 4. Update Response Parsing
```diff
- response['cards']
+ response['data']

- card['imageUrl']
+ card['images']['small']

- card['subtype']
+ card['subtypes']  # Now array

- card['ability']
+ card['abilities']  # Now array
```

### 5. Handle New Fields
```python
# Check format legality
if 'standard' in card['legalities']:
    print(f"Standard: {card['legalities']['standard']}")

# Access pricing
if 'tcgplayer' in card:
    market_price = card['tcgplayer']['prices']['normal']['market']
```

### 6. Update Pagination Logic
```python
# V2 pagination from body
response = requests.get(url, headers=headers).json()
current_page = response['page']
total_pages = response['totalCount'] // response['pageSize']
```

## Example: Complete Migration

### V1 Code
```python
response = requests.get('https://api.pokemontcg.io/v1/cards?name=charizard&subtypes=mega')
cards = response.json()['cards']

for card in cards:
    print(f"{card['name']} - {card['imageUrl']}")
    print(f"Subtype: {card['subtype']}")
```

### V2 Code
```python
headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    'https://api.pokemontcg.io/v2/cards?q=name:charizard subtypes:mega',
    headers=headers
)
data = response.json()
cards = data['data']

for card in cards:
    print(f"{card['name']} - {card['images']['small']}")
    print(f"Subtypes: {', '.join(card['subtypes'])}")
    
    # New V2 features
    if 'legalities' in card:
        print(f"Standard Legal: {'standard' in card['legalities']}")
    if 'tcgplayer' in card:
        print(f"Market Price: ${card['tcgplayer']['prices']['normal']['market']}")
```

## Need Help?

- Discord: https://discord.gg/dpsTCvg
- Email: andrew@pokemontcg.io
- Stack Overflow: https://stackoverflow.com/questions/tagged/pokemontcg
