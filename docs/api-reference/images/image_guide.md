# Image Information and URLs

Complete guide to accessing and using Pokémon TCG card images from the API.

## Image Types

### Card Images

The API provides two sizes of card images:

#### Small Images
- **URL Format**: `https://images.pokemontcg.io/{setId}/{number}.png`
- **Usage**: Thumbnails, lists, small previews
- **Size**: Lower resolution, smaller file size
- **Example**: `https://images.pokemontcg.io/swsh4/25.png`

#### Large Images (High-Res)
- **URL Format**: `https://images.pokemontcg.io/{setId}/{number}_hires.png`
- **Usage**: Detailed views, zoomed displays, printing
- **Size**: Higher resolution, larger file size
- **Example**: `https://images.pokemontcg.io/swsh4/25_hires.png`

### Set Images

#### Set Symbol
- **URL Format**: `https://images.pokemontcg.io/{setId}/symbol.png`
- **Usage**: Small icon representing the set
- **Example**: `https://images.pokemontcg.io/swsh4/symbol.png`

#### Set Logo
- **URL Format**: `https://images.pokemontcg.io/{setId}/logo.png`
- **Usage**: Full branded logo for the set
- **Example**: `https://images.pokemontcg.io/swsh4/logo.png`

## Accessing Images from Card Objects

### Card Image Structure

```json
{
  "id": "swsh4-25",
  "name": "Charizard",
  "images": {
    "small": "https://images.pokemontcg.io/swsh4/25.png",
    "large": "https://images.pokemontcg.io/swsh4/25_hires.png"
  }
}
```

### Set Image Structure

```json
{
  "id": "swsh4",
  "name": "Vivid Voltage",
  "images": {
    "symbol": "https://images.pokemontcg.io/swsh4/symbol.png",
    "logo": "https://images.pokemontcg.io/swsh4/logo.png"
  }
}
```

## Code Examples

### Python - Download Card Image

```python
import requests
from PIL import Image
from io import BytesIO

def download_card_image(card_id, size='large'):
    """Download and save a card image"""
    # Get card data
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards/{card_id}',
        headers=headers
    )
    
    card = response.json()['data']
    image_url = card['images'][size]
    
    # Download image
    img_response = requests.get(image_url)
    img = Image.open(BytesIO(img_response.content))
    
    # Save image
    filename = f"{card['id']}_{size}.png"
    img.save(filename)
    print(f"Saved {filename}")
    
    return img

# Example usage
image = download_card_image('swsh4-25', size='large')
```

### Python - Display Card in Jupyter Notebook

```python
from IPython.display import Image, display

def show_card(card_id):
    """Display card image in Jupyter notebook"""
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards/{card_id}',
        headers=headers
    )
    
    card = response.json()['data']
    image_url = card['images']['small']
    
    print(f"{card['name']} - {card['set']['name']}")
    display(Image(url=image_url))

# Show a card
show_card('base1-4')
```

### Python - Batch Download Set Images

```python
import requests
import os
from time import sleep

def download_set_images(set_id, output_dir='cards'):
    """Download all card images from a set"""
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all cards from set
    response = requests.get(
        f'https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}',
        headers=headers
    )
    
    cards = response.json()['data']
    print(f"Downloading {len(cards)} cards from set {set_id}...")
    
    for i, card in enumerate(cards):
        # Download small image
        img_url = card['images']['small']
        img_response = requests.get(img_url)
        
        # Save with card number as filename
        filename = f"{card['set']['id']}_{card['number']}.png"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(img_response.content)
        
        print(f"Downloaded {i+1}/{len(cards)}: {card['name']}")
        
        # Be nice to the server
        sleep(0.1)
    
    print("Download complete!")

# Download all Vivid Voltage cards
download_set_images('swsh4', output_dir='vivid_voltage_cards')
```

### JavaScript - Display Card Image

```javascript
async function displayCard(cardId) {
  const headers = {
    'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
  };
  
  // Fetch card data
  const response = await fetch(
    `https://api.pokemontcg.io/v2/cards/${cardId}`,
    { headers }
  );
  
  const data = await response.json();
  const card = data.data;
  
  // Create image element
  const img = document.createElement('img');
  img.src = card.images.small;
  img.alt = card.name;
  img.title = `${card.name} - ${card.set.name}`;
  
  // Add to page
  document.getElementById('card-container').appendChild(img);
}

// Display Charizard
displayCard('base1-4');
```

### HTML - Card Gallery

```html
<!DOCTYPE html>
<html>
<head>
    <title>Pokémon Card Gallery</title>
    <style>
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        
        .card-item {
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .card-item:hover {
            transform: scale(1.05);
        }
        
        .card-item img {
            width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .card-name {
            margin-top: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="card-grid" id="cardGrid"></div>
    
    <script>
        async function loadCards() {
            const headers = {
                'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
            };
            
            const response = await fetch(
                'https://api.pokemontcg.io/v2/cards?q=set.id:swsh4&pageSize=50',
                { headers }
            );
            
            const data = await response.json();
            const grid = document.getElementById('cardGrid');
            
            data.data.forEach(card => {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'card-item';
                cardDiv.innerHTML = `
                    <img src="${card.images.small}" alt="${card.name}">
                    <div class="card-name">${card.name}</div>
                `;
                
                // Click to view large image
                cardDiv.onclick = () => {
                    window.open(card.images.large, '_blank');
                };
                
                grid.appendChild(cardDiv);
            });
        }
        
        loadCards();
    </script>
</body>
</html>
```

### Python - Create Image Mosaic

```python
from PIL import Image
import requests
from io import BytesIO
import math

def create_card_mosaic(card_ids, columns=5):
    """Create a mosaic of multiple cards"""
    headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
    
    images = []
    
    # Download all card images
    for card_id in card_ids:
        response = requests.get(
            f'https://api.pokemontcg.io/v2/cards/{card_id}',
            headers=headers
        )
        card = response.json()['data']
        
        # Download small image
        img_response = requests.get(card['images']['small'])
        img = Image.open(BytesIO(img_response.content))
        images.append(img)
    
    # Calculate mosaic dimensions
    rows = math.ceil(len(images) / columns)
    
    # Get dimensions from first image
    card_width, card_height = images[0].size
    
    # Create blank canvas
    mosaic_width = card_width * columns
    mosaic_height = card_height * rows
    mosaic = Image.new('RGB', (mosaic_width, mosaic_height), (255, 255, 255))
    
    # Paste cards
    for idx, img in enumerate(images):
        row = idx // columns
        col = idx % columns
        x = col * card_width
        y = row * card_height
        mosaic.paste(img, (x, y))
    
    # Save
    mosaic.save('card_mosaic.png')
    print(f"Created mosaic with {len(images)} cards")
    
    return mosaic

# Create mosaic of Charizard cards
charizard_ids = ['base1-4', 'base2-4', 'neo1-4', 'ex3-105']
mosaic = create_card_mosaic(charizard_ids, columns=2)
```

## Image Caching Best Practices

### Cache Images Locally

```python
import os
import hashlib

def get_cached_image(image_url, cache_dir='image_cache'):
    """Download image with local caching"""
    # Create cache directory
    os.makedirs(cache_dir, exist_ok=True)
    
    # Generate cache filename from URL
    url_hash = hashlib.md5(image_url.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{url_hash}.png")
    
    # Check if cached
    if os.path.exists(cache_path):
        print(f"Using cached image")
        return Image.open(cache_path)
    
    # Download and cache
    print(f"Downloading image...")
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img.save(cache_path)
    
    return img

# Usage
card_id = 'swsh4-25'
headers = {'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'}
response = requests.get(
    f'https://api.pokemontcg.io/v2/cards/{card_id}',
    headers=headers
)
card = response.json()['data']

# This will cache the image
img = get_cached_image(card['images']['large'])
```

## Image URL Patterns

### Constructing URLs Manually

If you know the set ID and card number, you can construct URLs without an API call:

```python
def build_image_url(set_id, card_number, size='large'):
    """Build image URL from set ID and card number"""
    if size == 'large':
        return f"https://images.pokemontcg.io/{set_id}/{card_number}_hires.png"
    else:
        return f"https://images.pokemontcg.io/{set_id}/{card_number}.png"

# Example
url = build_image_url('swsh4', '25', 'large')
print(url)  # https://images.pokemontcg.io/swsh4/25_hires.png
```

## Image Specifications

### Card Images

| Attribute | Small | Large |
|-----------|-------|-------|
| **Format** | PNG | PNG |
| **Typical Width** | ~245px | ~734px |
| **Typical Height** | ~342px | ~1024px |
| **File Size** | 50-200 KB | 200-800 KB |
| **Aspect Ratio** | 2.5:3.5 (approx) | 2.5:3.5 (approx) |

### Set Symbols and Logos

| Attribute | Symbol | Logo |
|-----------|--------|------|
| **Format** | PNG | PNG |
| **Typical Size** | Small icon | Larger branded image |
| **Background** | Usually transparent | Varies |

## Tips

1. **Use small images for galleries** to reduce bandwidth and load times
2. **Use large images for detailed views** when users click on a card
3. **Cache images locally** when building apps to reduce API load
4. **Respect rate limits** when downloading multiple images
5. **Add delays between downloads** (100-200ms) to be server-friendly
6. **Handle missing images gracefully** - some older cards may have broken image links

## Common Issues

### Image Not Found (404)
- Check that the card ID and set ID are correct
- Some very old or promo cards may have missing images
- Verify the URL format matches the expected pattern

### Slow Loading
- Use small images for initial loads
- Implement lazy loading for galleries
- Cache images when possible
- Use CDN or proxy for better performance

## Related

- [Card Object](../api_reference/cards/card_object.md) - Complete card structure
- [Set Object](../api_reference/sets/set_object.md) - Complete set structure
- [Code Examples](code_examples.md) - More programming examples
