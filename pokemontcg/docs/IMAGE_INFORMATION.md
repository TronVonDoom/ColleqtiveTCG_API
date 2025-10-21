# Pokemon TCG Card Images Information

## Summary

✅ **Good news!** Your sync script already extracts and stores Pokemon card images from the GitHub data.

## Available Images

Each Pokemon card in the dataset includes **two image sizes**:

### 1. Small Image
- **Format**: PNG
- **Size**: Standard resolution (~245x342 pixels typically)
- **URL Pattern**: `https://images.pokemontcg.io/{set_id}/{card_number}.png`
- **Example**: `https://images.pokemontcg.io/base1/1.png`
- **Use Case**: Thumbnails, lists, previews

### 2. Large Image (Hi-Res)
- **Format**: PNG
- **Size**: High resolution (~734x1024 pixels typically)
- **URL Pattern**: `https://images.pokemontcg.io/{set_id}/{card_number}_hires.png`
- **Example**: `https://images.pokemontcg.io/base1/1_hires.png`
- **Use Case**: Detailed views, zooming, printing

## Image Storage

Images are stored as **URLs** (not downloaded locally) in two database columns:
- `image_small` - Small image URL
- `image_large` - Large/hi-res image URL

## Sample Image Data

Here are examples from the Base Set:

```
Card: Alakazam (base1-1)
  Small: https://images.pokemontcg.io/base1/1.png
  Large: https://images.pokemontcg.io/base1/1_hires.png

Card: Blastoise (base1-2)
  Small: https://images.pokemontcg.io/base1/2.png
  Large: https://images.pokemontcg.io/base1/2_hires.png

Card: Chansey (base1-3)
  Small: https://images.pokemontcg.io/base1/3.png
  Large: https://images.pokemontcg.io/base1/3_hires.png
```

## Current Status

### ✅ Already Implemented
- Image URLs are extracted from JSON files
- Image URLs are stored in the database schema
- The sync script (`pokemontcg/sync_github.py`) processes images automatically
- Both small and large image URLs are captured

### What Happens During Sync
When you run the sync script, it:
1. Reads card data from JSON files in `pokemontcg/pokemon-tcg-data/cards/en/`
2. Extracts the `images` object from each card
3. Stores `images.small` → `card.image_small`
4. Stores `images.large` → `card.image_large`

See lines 449-451 in `pokemontcg/sync_github.py`:
```python
# Images
images = card_data.get('images', {})
card.image_small = images.get('small')
card.image_large = images.get('large')
```

## Total Available Images

Based on your database sync:
- **~18,000+ cards** with images
- All cards from Base Set (1999) through Scarlet & Violet series (2025)
- Promo sets, McDonald's sets, and special collections included

## Image Hosting

Images are hosted by **pokemontcg.io** CDN:
- Reliable and fast delivery
- No need to download and store images locally
- Always up-to-date
- Free to use (part of the Pokemon TCG API ecosystem)

## Next Steps - Options

### Option 1: Just Use the URLs (Recommended)
- Images are already in your database
- Reference them directly in your API/UI
- No additional storage needed
- Example API response:
  ```json
  {
    "id": "base1-1",
    "name": "Alakazam",
    "image_small": "https://images.pokemontcg.io/base1/1.png",
    "image_large": "https://images.pokemontcg.io/base1/1_hires.png"
  }
  ```

### Option 2: Download Images Locally
If you want to download and host images yourself:
- **Pros**: Full control, offline access, custom optimization
- **Cons**: ~5-10 GB storage needed, bandwidth for downloads, maintenance
- **Not recommended** unless you have specific requirements

### Option 3: Create Image Proxy/Cache
Create a caching layer:
- Fetch from pokemontcg.io on first request
- Cache locally for performance
- Best of both worlds

## Verification

To verify images are synced, run:
```bash
python -c "import sqlite3; conn = sqlite3.connect('pokemon_tcg.db'); c = conn.cursor(); c.execute('SELECT COUNT(*) FROM cards WHERE image_small IS NOT NULL'); print(f'Cards with images: {c.fetchone()[0]}'); conn.close()"
```

## Image Examples You Can View Now

Try opening these URLs in your browser:
- https://images.pokemontcg.io/base1/4.png (Charizard!)
- https://images.pokemontcg.io/base1/4_hires.png (Charizard Hi-Res)
- https://images.pokemontcg.io/sv1/1.png (Recent Scarlet & Violet)
- https://images.pokemontcg.io/cel25/25.png (Special Pikachu)

## Recommendation

✅ **The image URLs are already available!** 

When you run your sync script, all image URLs will be automatically populated in the database. You can immediately start using them in your API or application without any additional work.

The images are professionally hosted, fast, and reliable. Unless you have a specific reason to download and self-host them, using the URLs directly is the best approach.
