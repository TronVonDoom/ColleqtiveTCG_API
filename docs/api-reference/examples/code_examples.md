# Pokémon TCG API - Code Examples

Practical examples for common use cases with the Pokémon TCG API.

## Table of Contents

- [Setup and Authentication](#setup-and-authentication)
- [Basic Card Searches](#basic-card-searches)
- [Advanced Queries](#advanced-queries)
- [Working with Sets](#working-with-sets)
- [Pricing and Market Data](#pricing-and-market-data)
- [Building a Collection Tracker](#building-a-collection-tracker)
- [Performance Optimization](#performance-optimization)

## Setup and Authentication

### Python Setup
```python
import requests
import json

# Your API key
API_KEY = '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'

# Headers for all requests
headers = {
    'X-Api-Key': API_KEY
}

# Base URL
BASE_URL = 'https://api.pokemontcg.io/v2'
```

### Using the Official SDK
```bash
pip install pokemontcgsdk
```

```python
from pokemontcgsdk import Card, Set, RestClient

# Configure API key
RestClient.configure('0af3890a-ef8f-4a46-8cb6-f5e111be72f1')

# Now you can use the SDK
cards = Card.where(q='name:charizard')
```

## Basic Card Searches

### Find a Specific Card
```python
def find_card(card_id):
    """Get a single card by ID"""
    response = requests.get(
        f'{BASE_URL}/cards/{card_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Error: {response.status_code}")
        return None

# Example
charizard = find_card('base1-4')
print(f"Found: {charizard['name']}")
print(f"HP: {charizard['hp']}")
print(f"Type: {charizard['types']}")
```

### Search by Name
```python
def search_by_name(name):
    """Search for cards by name"""
    params = {
        'q': f'name:{name}',
        'orderBy': '-set.releaseDate'
    }
    
    response = requests.get(
        f'{BASE_URL}/cards',
        headers=headers,
        params=params
    )
    
    return response.json()['data']

# Example
pikachus = search_by_name('pikachu')
print(f"Found {len(pikachus)} Pikachu cards")

for card in pikachus[:5]:  # First 5
    print(f"- {card['name']} ({card['set']['name']})")
```

### Get All Cards from a Set
```python
def get_set_cards(set_id):
    """Get all cards from a specific set"""
    all_cards = []
    page = 1
    
    while True:
        params = {
            'q': f'set.id:{set_id}',
            'page': page,
            'pageSize': 250
        }
        
        response = requests.get(
            f'{BASE_URL}/cards',
            headers=headers,
            params=params
        )
        
        data = response.json()
        all_cards.extend(data['data'])
        
        # Check if we've got all cards
        if len(data['data']) < data['pageSize']:
            break
        
        page += 1
    
    return all_cards

# Example
vivid_voltage_cards = get_set_cards('swsh4')
print(f"Vivid Voltage has {len(vivid_voltage_cards)} cards")
```

## Advanced Queries

### Multi-Condition Search
```python
def advanced_search():
    """Complex search with multiple conditions"""
    params = {
        'q': 'types:Fire hp:[150 TO *] legalities.standard:legal',
        'orderBy': '-hp',
        'pageSize': 50
    }
    
    response = requests.get(
        f'{BASE_URL}/cards',
        headers=headers,
        params=params
    )
    
    return response.json()['data']

# Fire-type Standard-legal cards with 150+ HP
powerful_fire_cards = advanced_search()

for card in powerful_fire_cards[:10]:
    print(f"{card['name']}: {card['hp']} HP")
```

### Search with OR Logic
```python
def search_legendary_pokemon():
    """Find cards with legendary Pokémon"""
    params = {
        'q': '(name:Mewtwo OR name:Mew OR name:Lugia OR name:Ho-Oh)',
        'orderBy': '-set.releaseDate'
    }
    
    response = requests.get(
        f'{BASE_URL}/cards',
        headers=headers,
        params=params
    )
    
    return response.json()['data']

legendaries = search_legendary_pokemon()
print(f"Found {len(legendaries)} legendary cards")
```

### Find Rare Cards from Recent Sets
```python
def find_recent_rares():
    """Find recent rare cards"""
    import datetime
    
    # Date from 1 year ago
    one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y/%m/%d')
    
    params = {
        'q': f'set.releaseDate:[{one_year_ago} TO *] (rarity:"Rare Secret" OR rarity:"Rare Rainbow")',
        'orderBy': '-set.releaseDate'
    }
    
    response = requests.get(
        f'{BASE_URL}/cards',
        headers=headers,
        params=params
    )
    
    return response.json()['data']

recent_rares = find_recent_rares()
```

## Working with Sets

### List All Sets by Series
```python
def get_sets_by_series():
    """Organize all sets by series"""
    response = requests.get(
        f'{BASE_URL}/sets',
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
    
    # Sort each series by release date
    for series in by_series:
        by_series[series].sort(key=lambda x: x['releaseDate'])
    
    return by_series

# Example usage
sets_by_series = get_sets_by_series()

for series, sets in sorted(sets_by_series.items(), key=lambda x: x[1][0]['releaseDate']):
    print(f"\n{series}:")
    for s in sets:
        print(f"  - {s['name']} ({s['releaseDate']})")
```

### Get Standard-Legal Sets
```python
def get_standard_legal_sets():
    """Get all Standard format legal sets"""
    params = {
        'q': 'legalities.standard:legal',
        'orderBy': '-releaseDate'
    }
    
    response = requests.get(
        f'{BASE_URL}/sets',
        headers=headers,
        params=params
    )
    
    return response.json()['data']

standard_sets = get_standard_legal_sets()
print("Current Standard Format Sets:")
for s in standard_sets:
    print(f"- {s['name']} ({s['id']})")
```

## Pricing and Market Data

### Get Card Market Price
```python
def get_card_price(card_id):
    """Get current market price for a card"""
    response = requests.get(
        f'{BASE_URL}/cards/{card_id}',
        headers=headers
    )
    
    if response.status_code != 200:
        return None
    
    card = response.json()['data']
    
    prices = {}
    
    # TCGPlayer prices (USD)
    if 'tcgplayer' in card and 'prices' in card['tcgplayer']:
        for variant, price_data in card['tcgplayer']['prices'].items():
            if 'market' in price_data:
                prices[f'tcgplayer_{variant}'] = price_data['market']
    
    # Cardmarket prices (EUR)
    if 'cardmarket' in card and 'prices' in card['cardmarket']:
        cm_prices = card['cardmarket']['prices']
        if 'averageSellPrice' in cm_prices:
            prices['cardmarket_avg'] = cm_prices['averageSellPrice']
    
    return {
        'name': card['name'],
        'set': card['set']['name'],
        'prices': prices,
        'updated': card.get('tcgplayer', {}).get('updatedAt', 'Unknown')
    }

# Example
price_info = get_card_price('swsh4-25')
print(f"{price_info['name']} prices:")
for variant, price in price_info['prices'].items():
    print(f"  {variant}: ${price:.2f}")
```

### Find Most Expensive Cards
```python
def find_most_expensive_cards(min_price=100, limit=10):
    """Find the most expensive cards"""
    response = requests.get(
        f'{BASE_URL}/cards',
        headers=headers,
        params={'pageSize': 250}
    )
    
    cards = response.json()['data']
    expensive_cards = []
    
    for card in cards:
        if 'tcgplayer' not in card:
            continue
        
        prices = card['tcgplayer'].get('prices', {})
        for variant, price_data in prices.items():
            market_price = price_data.get('market', 0)
            if market_price >= min_price:
                expensive_cards.append({
                    'name': card['name'],
                    'set': card['set']['name'],
                    'variant': variant,
                    'price': market_price,
                    'rarity': card.get('rarity', 'Unknown')
                })
    
    # Sort by price
    expensive_cards.sort(key=lambda x: x['price'], reverse=True)
    
    return expensive_cards[:limit]

# Find cards worth $100+
expensive = find_most_expensive_cards(min_price=100)
for card in expensive:
    print(f"{card['name']} ({card['set']}) - ${card['price']:.2f}")
```

## Building a Collection Tracker

### Track Collection Progress
```python
class CollectionTracker:
    def __init__(self):
        self.owned_cards = set()  # Set of card IDs
        
    def add_card(self, card_id):
        """Add a card to collection"""
        self.owned_cards.add(card_id)
    
    def get_set_completion(self, set_id):
        """Calculate completion percentage for a set"""
        # Get all cards in set
        response = requests.get(
            f'{BASE_URL}/cards',
            headers=headers,
            params={'q': f'set.id:{set_id}'}
        )
        
        all_cards = response.json()['data']
        total_cards = len(all_cards)
        
        # Count owned cards
        owned_count = sum(1 for card in all_cards if card['id'] in self.owned_cards)
        
        return {
            'set_id': set_id,
            'total': total_cards,
            'owned': owned_count,
            'percentage': (owned_count / total_cards * 100) if total_cards > 0 else 0
        }
    
    def missing_cards(self, set_id):
        """Get list of missing cards from a set"""
        response = requests.get(
            f'{BASE_URL}/cards',
            headers=headers,
            params={'q': f'set.id:{set_id}'}
        )
        
        all_cards = response.json()['data']
        missing = [card for card in all_cards if card['id'] not in self.owned_cards]
        
        return missing

# Example usage
tracker = CollectionTracker()

# Add some cards
tracker.add_card('swsh4-1')
tracker.add_card('swsh4-2')
tracker.add_card('swsh4-25')

# Check completion
completion = tracker.get_set_completion('swsh4')
print(f"Vivid Voltage: {completion['owned']}/{completion['total']} ({completion['percentage']:.1f}%)")

# Get missing cards
missing = tracker.missing_cards('swsh4')
print(f"\nMissing {len(missing)} cards:")
for card in missing[:5]:
    print(f"- {card['name']} ({card['number']})")
```

## Performance Optimization

### Caching Responses
```python
import requests_cache
from datetime import timedelta

# Install cache
requests_cache.install_cache(
    'pokemon_cache',
    expire_after=timedelta(hours=24)
)

# Now requests are automatically cached for 24 hours
response = requests.get(f'{BASE_URL}/sets', headers=headers)
# Subsequent identical requests will use cache
```

### Batch Processing with Pagination
```python
def get_all_cards_efficiently(query):
    """Efficiently paginate through all results"""
    all_cards = []
    page = 1
    
    while True:
        params = {
            'q': query,
            'page': page,
            'pageSize': 250,  # Max page size
            'select': 'id,name,images,set'  # Only fields you need
        }
        
        response = requests.get(
            f'{BASE_URL}/cards',
            headers=headers,
            params=params
        )
        
        data = response.json()
        cards = data['data']
        
        if not cards:
            break
        
        all_cards.extend(cards)
        print(f"Fetched page {page}: {len(cards)} cards")
        
        # Check if done
        if len(cards) < 250:
            break
        
        page += 1
    
    return all_cards
```

### Request Only Needed Fields
```python
def get_card_images_only(set_id):
    """Get only card images to reduce bandwidth"""
    params = {
        'q': f'set.id:{set_id}',
        'select': 'id,name,images'  # Only these fields
    }
    
    response = requests.get(
        f'{BASE_URL}/cards',
        headers=headers,
        params=params
    )
    
    return response.json()['data']

# Much faster and less data transfer
cards = get_card_images_only('swsh4')
```

## Error Handling

### Robust Request Function
```python
import time

def make_request_with_retry(url, max_retries=3, backoff=2):
    """Make request with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited
                wait_time = backoff ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif response.status_code == 404:
                print("Resource not found")
                return None
            else:
                print(f"Error {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            time.sleep(backoff ** attempt)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    print("Max retries exceeded")
    return None
```

## Complete Example: Card Price Tracker

```python
import requests
import json
from datetime import datetime

class PriceTracker:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'X-Api-Key': api_key}
        self.base_url = 'https://api.pokemontcg.io/v2'
    
    def track_card(self, card_id):
        """Get current price and save to history"""
        response = requests.get(
            f'{self.base_url}/cards/{card_id}',
            headers=self.headers
        )
        
        if response.status_code != 200:
            return None
        
        card = response.json()['data']
        
        # Extract price
        price = None
        if 'tcgplayer' in card:
            prices = card['tcgplayer'].get('prices', {})
            if 'normal' in prices and 'market' in prices['normal']:
                price = prices['normal']['market']
        
        # Create price record
        record = {
            'timestamp': datetime.now().isoformat(),
            'card_id': card_id,
            'name': card['name'],
            'set': card['set']['name'],
            'price': price
        }
        
        return record
    
    def track_multiple(self, card_ids):
        """Track multiple cards"""
        results = []
        for card_id in card_ids:
            record = self.track_card(card_id)
            if record:
                results.append(record)
            time.sleep(0.1)  # Rate limiting courtesy
        
        return results

# Usage
tracker = PriceTracker('0af3890a-ef8f-4a46-8cb6-f5e111be72f1')

# Track some valuable cards
watch_list = ['base1-4', 'swsh4-25', 'xy1-1']
prices = tracker.track_multiple(watch_list)

for record in prices:
    print(f"{record['name']}: ${record['price']}")
```

## See Also

- [API Reference](../api_reference/cards/search_cards.md)
- [Authentication Guide](../getting_started/authentication.md)
- [Rate Limits](../getting_started/rate_limits.md)
