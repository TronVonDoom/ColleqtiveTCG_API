# Card Image Helper - Automatic Placeholder Support

## Overview

The `CardImageHelper` class provides automatic fallback to placeholder images when card images are missing. Instead of copying placeholders to replace missing images, the system keeps track of which images exist and returns the placeholder path when needed.

## Benefits

✅ **Easy to identify missing cards** - Placeholder is separate, not mixed with actual card images
✅ **Automatic fallback** - Your code doesn't need to check if images exist
✅ **Clean organization** - Only actual downloaded images are in card folders
✅ **Single source of truth** - One placeholder image for all missing cards

## Placeholder Images

Two placeholder images are stored in `pokemontcg/pokemon-tcg-data/images/`:
- `card_back.png` - Standard Pokemon card back (small size)
- `card_back_hires.png` - High-resolution card back (large size)

## Usage

### Basic Usage

```python
from pokemontcg.image_helper import CardImageHelper

helper = CardImageHelper()

# Get image path (returns actual card or placeholder)
image_path = helper.get_card_image_path("base1", "4", "small")
# Returns: pokemontcg/pokemon-tcg-data/images/cards/base1/4.png

# For missing cards, returns placeholder
missing_path = helper.get_card_image_path("mcd14", "1", "small")
# Returns: pokemontcg/pokemon-tcg-data/images/card_back.png
```

### Check If Card Exists

```python
# Check if actual card image exists (not placeholder)
exists = helper.card_image_exists("base1", "4", "small")
# Returns: True

exists = helper.card_image_exists("mcd14", "1", "small")
# Returns: False (will use placeholder)
```

### Get All Missing Cards

```python
# Get list of all missing cards
missing = helper.get_missing_cards()

print(f"Missing small images: {len(missing['small'])}")
print(f"Missing large images: {len(missing['large'])}")

# Each entry is a tuple: (set_id, card_number, card_name)
for set_id, card_num, name in missing['small'][:5]:
    print(f"{set_id}-{card_num}: {name}")
```

## API Integration Example

```python
from flask import Flask, send_file
from pokemontcg.image_helper import CardImageHelper

app = Flask(__name__)
helper = CardImageHelper()

@app.route('/cards/<set_id>/<card_number>/image')
def get_card_image(set_id, card_number):
    """
    Get card image endpoint with automatic placeholder fallback
    """
    size = request.args.get('size', 'small')  # 'small' or 'large'
    
    # This automatically returns placeholder if image doesn't exist
    image_path = helper.get_card_image_path(set_id, card_number, size)
    
    # Optional: Add header to indicate if it's a placeholder
    is_placeholder = not helper.card_image_exists(set_id, card_number, size)
    
    response = send_file(image_path, mimetype='image/png')
    if is_placeholder:
        response.headers['X-Image-Status'] = 'placeholder'
    
    return response
```

## Missing Cards Summary

Currently missing images (~52-53 cards):
- **McDonald's Promo Sets**: mcd14, mcd15, mcd17, mcd18 (images not available on server)
- **Special Cards**: A few promotional and special edition cards
- **Percentage**: 99.7% coverage (19,597 of 19,653 cards have images)

## File Structure

```
pokemontcg/pokemon-tcg-data/
├── images/
│   ├── card_back.png           # Placeholder for small images
│   ├── card_back_hires.png     # Placeholder for large images
│   ├── cards/
│   │   ├── base1/
│   │   │   ├── 1.png          # Actual card images
│   │   │   ├── 1_hires.png
│   │   │   └── ...
│   │   └── ...
│   └── sets/
│       ├── symbols/
│       └── logos/
```

## Command Line Tools

### Check for missing images
```bash
python pokemontcg/image_helper.py
```

### Retry downloading missing images
```bash
python retry_missing_images.py
```

## Notes

- The placeholder image is the official Pokemon TCG card back
- Transparent PNG format matches all actual card images
- The helper automatically handles special characters in card numbers (/, ?)
- Both small and large placeholders have the same dimensions as actual cards
