# Errors

## Overview

The Pokémon TCG API uses conventional HTTP response codes to indicate the success or failure of an API request.

## HTTP Status Code Summary

| Status Code | Meaning | Description |
|------------|---------|-------------|
| **200** | OK | Everything worked as expected |
| **400** | Bad Request | The request was unacceptable, often due to an incorrect query string parameter |
| **402** | Request Failed | The parameters were valid but the request failed |
| **403** | Forbidden | The user doesn't have permissions to perform the request |
| **404** | Not Found | The requested resource doesn't exist |
| **429** | Too Many Requests | The rate limit has been exceeded |
| **500** | Server Error | Something went wrong on the server |
| **502** | Bad Gateway | Something went wrong on the server |
| **503** | Service Unavailable | Something went wrong on the server |
| **504** | Gateway Timeout | Something went wrong on the server |

## Status Code Ranges

- **2xx**: Success - The request was successful
- **4xx**: Client Error - There was an error with your request
- **5xx**: Server Error - There was an error on the API's servers

## Sample Error Response

```json
{
  "error": {
    "message": "Bad Request. Your request is either malformed, or is missing one or more required fields.",
    "code": 400
  }
}
```

## Common Error Scenarios

### 400 - Bad Request
**Causes:**
- Malformed query string
- Invalid query syntax
- Missing required parameters

**Example:**
```
GET /v2/cards?q=name:char*zard AND invalid:syntax
```

### 404 - Not Found
**Causes:**
- Invalid card ID
- Invalid set ID
- Non-existent resource

**Example:**
```
GET /v2/cards/invalid-id-123
```

### 429 - Too Many Requests
**Causes:**
- Exceeded daily rate limit
- Exceeded per-minute rate limit

**Solution:**
- Implement exponential backoff
- Use API key for higher limits
- Contact support for increased limits

### 500/502/503/504 - Server Errors
**Causes:**
- Temporary server issues
- Database problems
- Maintenance

**Solution:**
- Retry after a short delay
- Implement exponential backoff
- Check API status on Discord

## Error Handling Best Practices

### 1. Check Status Codes
```python
response = requests.get('https://api.pokemontcg.io/v2/cards/xy1-1', headers=headers)

if response.status_code == 200:
    data = response.json()
    # Process data
elif response.status_code == 404:
    print("Card not found")
elif response.status_code == 429:
    print("Rate limit exceeded")
else:
    print(f"Error: {response.status_code}")
```

### 2. Implement Retry Logic
```python
import time

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

### 3. Log Errors
Always log error responses for debugging:
```python
if response.status_code != 200:
    print(f"Error {response.status_code}: {response.json()}")
```

## Getting Help

If you encounter persistent errors:

1. Check your query syntax
2. Verify your API key is valid
3. Review the documentation for the endpoint
4. Ask on Discord: https://discord.gg/dpsTCvg
5. Search Stack Overflow: https://stackoverflow.com/questions/tagged/pokemontcg
