# Search Sets

Search for one or many sets using query parameters.

## HTTP Request

```
GET https://api.pokemontcg.io/v2/sets
```

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | - | The search query (see syntax below) |
| `page` | integer | 1 | The page of data to access |
| `pageSize` | integer | 250 | Maximum sets to return (max: 250) |
| `orderBy` | string | - | Field(s) to order results by |
| `select` | string | (all) | Comma-delimited list of fields to return |

## Authentication

```
X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## Search Query Syntax

The `q` parameter uses the same Lucene-like syntax as the cards endpoint. See the [Search Cards](../cards/search_cards.md) documentation for detailed syntax.

### Common Set Queries

#### By Name
```
q=name:base
```

#### By Series
```
q=series:"Sword & Shield"
```

#### By Legality
```
q=legalities.standard:legal
```

#### By Release Year
```
q=releaseDate:[2020/01/01 TO 2020/12/31]
```

#### By PTCGO Code
```
q=ptcgoCode:SSH
```

## Searchable Fields

- `id` - Set ID
- `name` - Set name
- `series` - Series name
- `printedTotal` - Printed total (numeric)
- `total` - Actual total including secrets (numeric)
- `ptcgoCode` - PTCGO/PTCGL code
- `releaseDate` - Release date (YYYY/MM/DD)
- `legalities.standard` - Standard legality
- `legalities.expanded` - Expanded legality
- `legalities.unlimited` - Unlimited legality

## Ordering Data

### Common Sort Orders

```
?orderBy=releaseDate           # Oldest first
?orderBy=-releaseDate          # Newest first
?orderBy=name                  # Alphabetical A-Z
?orderBy=-name                 # Alphabetical Z-A
?orderBy=total                 # Smallest sets first
?orderBy=-total                # Largest sets first
```

## Code Samples

### Python

```python
from pokemontcgsdk import Set

# Get all sets
all_sets = Set.all()

# Filter sets
standard_sets = Set.where(q='legalities.standard:legal')

# Get specific page
sets = Set.where(page=2, pageSize=10)
```

With requests:
```python
import requests

headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}

# Get all Sword & Shield sets, newest first
params = {
    'q': 'series:"Sword & Shield"',
    'orderBy': '-releaseDate'
}

response = requests.get(
    'https://api.pokemontcg.io/v2/sets',
    headers=headers,
    params=params
)

data = response.json()
sets = data['data']

for set_data in sets:
    print(f"{set_data['name']} - {set_data['releaseDate']}")
```

### cURL

```bash
# Get all sets
curl "https://api.pokemontcg.io/v2/sets" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"

# Get Standard legal sets
curl "https://api.pokemontcg.io/v2/sets?q=legalities.standard:legal" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### JavaScript

```javascript
const headers = {
  'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
};

// Get all sets ordered by release date (newest first)
const params = new URLSearchParams({
  orderBy: '-releaseDate'
});

fetch(`https://api.pokemontcg.io/v2/sets?${params}`, { headers })
  .then(response => response.json())
  .then(result => {
    const sets = result.data;
    sets.forEach(set => {
      console.log(`${set.name} (${set.releaseDate})`);
    });
  });
```

## Sample Response

```json
{
  "data": [
    {
      "id": "base1",
      "name": "Base",
      "series": "Base",
      "printedTotal": 102,
      "total": 102,
      "legalities": {
        "unlimited": "Legal"
      },
      "ptcgoCode": "BS",
      "releaseDate": "1999/01/09",
      "updatedAt": "2020/08/14 09:35:00",
      "images": {
        "symbol": "https://images.pokemontcg.io/base1/symbol.png",
        "logo": "https://images.pokemontcg.io/base1/logo.png"
      }
    },
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
  ],
  "page": 1,
  "pageSize": 250,
  "count": 2,
  "totalCount": 123
}
```

## Query Examples

### Get Standard Legal Sets
```python
params = {'q': 'legalities.standard:legal', 'orderBy': '-releaseDate'}
response = requests.get('https://api.pokemontcg.io/v2/sets', headers=headers, params=params)
```

### Get Sets from Specific Series
```python
# Sword & Shield series
params = {'q': 'series:"Sword & Shield"', 'orderBy': 'releaseDate'}

# Sun & Moon series
params = {'q': 'series:"Sun & Moon"', 'orderBy': 'releaseDate'}

# XY series
params = {'q': 'series:XY', 'orderBy': 'releaseDate'}
```

### Get Sets Released in a Year
```python
# All 2020 sets
params = {
    'q': 'releaseDate:[2020/01/01 TO 2020/12/31]',
    'orderBy': 'releaseDate'
}

# Sets from 2015 onwards
params = {
    'q': 'releaseDate:[2015/01/01 TO *]',
    'orderBy': '-releaseDate'
}
```

### Get Sets with Large Card Counts
```python
# Sets with 200+ cards
params = {'q': 'total:[200 TO *]', 'orderBy': '-total'}

# Sets with many secret rares (difference between total and printed)
# Note: This requires client-side filtering
response = requests.get('https://api.pokemontcg.io/v2/sets', headers=headers)
sets = response.json()['data']
large_secret_sets = [s for s in sets if (s['total'] - s['printedTotal']) >= 20]
```

### Get Recent Sets
```python
import datetime

# Sets from last 2 years
two_years_ago = (datetime.datetime.now() - datetime.timedelta(days=730)).strftime('%Y/%m/%d')
params = {
    'q': f'releaseDate:[{two_years_ago} TO *]',
    'orderBy': '-releaseDate'
}
```

## Pagination

```python
def get_all_sets():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    all_sets = []
    page = 1
    
    while True:
        response = requests.get(
            f'https://api.pokemontcg.io/v2/sets?page={page}',
            headers=headers
        ).json()
        
        all_sets.extend(response['data'])
        
        # Check if we've reached the end
        if len(response['data']) < response['pageSize']:
            break
        
        page += 1
    
    return all_sets
```

## Practical Examples

### Build Set Selector UI
```python
def get_sets_by_series():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    response = requests.get(
        'https://api.pokemontcg.io/v2/sets?orderBy=-releaseDate',
        headers=headers
    )
    
    sets = response.json()['data']
    
    # Group by series
    by_series = {}
    for set_data in sets:
        series = set_data['series']
        if series not in by_series:
            by_series[series] = []
        by_series[series].append(set_data)
    
    return by_series

# Usage
sets_by_series = get_sets_by_series()
for series, sets in sets_by_series.items():
    print(f"\n{series}:")
    for s in sets:
        print(f"  - {s['name']} ({s['id']})")
```

### Check Format Rotation
```python
def get_tournament_legal_sets():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    # Get Standard legal sets
    standard_response = requests.get(
        'https://api.pokemontcg.io/v2/sets?q=legalities.standard:legal&orderBy=-releaseDate',
        headers=headers
    )
    standard_sets = standard_response.json()['data']
    
    # Get Expanded legal sets
    expanded_response = requests.get(
        'https://api.pokemontcg.io/v2/sets?q=legalities.expanded:legal&orderBy=-releaseDate',
        headers=headers
    )
    expanded_sets = expanded_response.json()['data']
    
    return {
        'standard': standard_sets,
        'expanded': expanded_sets
    }
```

### Generate Set Statistics
```python
def get_set_statistics():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    response = requests.get(
        'https://api.pokemontcg.io/v2/sets',
        headers=headers
    )
    
    sets = response.json()['data']
    
    total_cards = sum(s['total'] for s in sets)
    total_secret_rares = sum(s['total'] - s['printedTotal'] for s in sets)
    avg_cards_per_set = total_cards / len(sets)
    
    print(f"Total Sets: {len(sets)}")
    print(f"Total Cards: {total_cards}")
    print(f"Total Secret Rares: {total_secret_rares}")
    print(f"Average Cards per Set: {avg_cards_per_set:.1f}")
    
    # Largest set
    largest = max(sets, key=lambda s: s['total'])
    print(f"Largest Set: {largest['name']} ({largest['total']} cards)")
    
    # Most secret rares
    most_secrets = max(sets, key=lambda s: s['total'] - s['printedTotal'])
    secret_count = most_secrets['total'] - most_secrets['printedTotal']
    print(f"Most Secret Rares: {most_secrets['name']} ({secret_count} cards)")
```

### Build Set Timeline
```python
def create_set_timeline():
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    response = requests.get(
        'https://api.pokemontcg.io/v2/sets?orderBy=releaseDate',
        headers=headers
    )
    
    sets = response.json()['data']
    
    # Group by year
    by_year = {}
    for set_data in sets:
        year = set_data['releaseDate'][:4]
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(set_data)
    
    for year, year_sets in sorted(by_year.items()):
        print(f"\n{year} ({len(year_sets)} sets):")
        for s in year_sets:
            print(f"  {s['releaseDate']}: {s['name']}")
```

## Tips

1. **Order by release date** for chronological browsing
2. **Filter by legality** to find tournament-legal sets
3. **Group by series** for better organization
4. **Cache results** - Set data changes infrequently
5. **Use `select`** to reduce response size when you only need specific fields

## Performance Tips

### Only Request Needed Fields
```
?select=id,name,series,releaseDate
```

### Cache Set List
```python
import requests_cache

requests_cache.install_cache('sets_cache', expire_after=86400)  # 24 hours
```

## Related

- [Get a Set](get_set.md) - Get single set by ID
- [Set Object](set_object.md) - Complete field reference
- [Search Cards](../cards/search_cards.md) - Search cards by set
