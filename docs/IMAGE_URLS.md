# Card Image URL Structure - Hostinger Implementation

## Base URL
```
https://lime-goat-951061.hostingersite.com/pokemon-tcg-data
```

## Card Images

### Format
- **Set ID**: Lowercase set identifier (e.g., `sv2`, `base1`)
- **Card Number**: Integer without leading zeros (e.g., `10` not `010`)

### Small Image
```
{BASE_URL}/images/cards/{set_id}/{number}.png
```

**Example**: Snover 010/193 from sv2
```
https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/cards/sv2/10.png
```

### Large/Hi-Res Image
```
{BASE_URL}/images/cards/{set_id}/{number}_hires.png
```

**Example**: Snover 010/193 from sv2
```
https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/cards/sv2/10_hires.png
```

## Set Images

### Set Symbol
```
{BASE_URL}/images/sets/symbols/{set_id}_symbol.png
```

**Example**: Base Set symbol
```
https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/sets/symbols/base1_symbol.png
```

### Set Logo
```
{BASE_URL}/images/sets/logos/{set_id}_logo.png
```

**Example**: Base Set logo
```
https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/sets/logos/base1_logo.png
```

## Placeholder/Missing Image

### Pokemon Card Back
```
{BASE_URL}/images/card_back.png
```

**Full URL**:
```
https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/card_back.png
```

**Usage**: Display this when:
- Card image is missing/404
- Card data is incomplete
- Image fails to load

## API Response Structure

### Card Object
```json
{
  "id": "sv2-10",
  "name": "Snover",
  "number": "10",
  "set_id": "sv2",
  "images": {
    "small": "https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/cards/sv2/10.png",
    "large": "https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/cards/sv2/10_hires.png"
  }
}
```

### Set Object
```json
{
  "id": "base1",
  "name": "Base Set",
  "images": {
    "symbol": "https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/sets/symbols/base1_symbol.png",
    "logo": "https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/sets/logos/base1_logo.png"
  }
}
```

## API Endpoints

### Card Image Redirect
```
GET /cards/{card_id}/image/{size}
```
- `card_id`: Format like `sv2-10` or `base1-4`
- `size`: Either `small` or `large`

**Example**:
```
GET /cards/sv2-10/image/small
→ Redirects to: https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/cards/sv2/10.png
```

### Card Back Placeholder
```
GET /card-back
```

**Example**:
```
GET /card-back
→ Redirects to: https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/card_back.png
```

### Set Image Redirects
```
GET /sets/{set_id}/symbol
GET /sets/{set_id}/logo
```

**Examples**:
```
GET /sets/base1/logo
→ Redirects to: https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/sets/logos/base1_logo.png
```

## Frontend Implementation

### JavaScript Example
```javascript
// Get card from API
const card = await fetch('https://your-railway-api.up.railway.app/cards/sv2-10').then(r => r.json());

// Use images directly
const imgElement = document.createElement('img');
imgElement.src = card.data.images.small;

// With error fallback to card back
imgElement.onerror = () => {
  imgElement.src = 'https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/card_back.png';
};
```

### React Example
```jsx
function CardImage({ card }) {
  const [imgSrc, setImgSrc] = useState(card.images.small);
  
  const handleError = () => {
    setImgSrc('https://lime-goat-951061.hostingersite.com/pokemon-tcg-data/images/card_back.png');
  };
  
  return (
    <img 
      src={imgSrc} 
      alt={card.name}
      onError={handleError}
    />
  );
}
```

## Key Implementation Notes

1. **Card numbers are normalized**: Leading zeros are automatically stripped
   - Database stores: `"010"`
   - URL uses: `10`

2. **No CORS issues**: All images hosted on your Hostinger domain

3. **Automatic fallback**: If `set_id` or `number` is missing, API returns card_back.png URLs

4. **Railway deployment**: Changes auto-deploy when pushed to GitHub

5. **Image paths**: All paths use `/images/` prefix after base URL
