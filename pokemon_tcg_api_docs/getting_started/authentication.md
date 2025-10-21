# Authentication

## Overview

The Pokémon TCG API uses API keys to authenticate requests. You can use the API without an API key, but your rate limits will be significantly reduced.

## Your API Key
```
0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## How to Authenticate

Provide your API key in the `X-Api-Key` header for all requests:

```http
X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1
```

## Example Requests

### Using cURL
```bash
curl "https://api.pokemontcg.io/v2/cards" \
  -H "X-Api-Key: 0af3890a-ef8f-4a46-8cb6-f5e111be72f1"
```

### Using Python
```python
import requests

headers = {
    'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
}

response = requests.get('https://api.pokemontcg.io/v2/cards', headers=headers)
data = response.json()
```

### Using JavaScript (Fetch)
```javascript
fetch('https://api.pokemontcg.io/v2/cards', {
  headers: {
    'X-Api-Key': '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Important Notes

- **Keep your API key secure!** Do not share it publicly or commit it to public repositories
- All API requests must be made over HTTPS
- Requests without authentication will still work but with drastically reduced rate limits
- If your API key is compromised, generate a new one at the [Developer Portal](https://dev.pokemontcg.io/)

## Rate Limits

- **With API Key**: 20,000 requests per day (default)
- **Without API Key**: 1,000 requests per day, maximum 30 per minute

For higher rate limits, contact the API team via Discord or email.
