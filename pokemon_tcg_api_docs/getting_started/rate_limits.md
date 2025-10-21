# Rate Limits

## Overview

Rate limits are enforced for all third-party applications and services to ensure responsive performance for all users.

## V2 Rate Limits (Current)

### With API Key
- **Default**: 20,000 requests per day
- Higher limits available upon request (contact via Discord or email)

### Without API Key
- **Daily Limit**: 1,000 requests per day
- **Per Minute**: Maximum 30 requests per minute

## V1 Rate Limits (Deprecated)

- **Throttle**: 30 requests per minute

**Note**: Version 1 of the API is officially deprecated as of August 1, 2021. Please use Version 2.

## Rationale

Rate limiting serves several purposes:

1. **Performance**: Ensures the API remains responsive for all users by minimizing computational costs
2. **Fairness**: Prevents any single user from monopolizing resources
3. **Best Practices**: Encourages developers to build efficient integrations

## Handling Rate Limit Errors

When you exceed the rate limit, you'll receive:
- **HTTP Status Code**: `429 - Too Many Requests`

## Tips for Staying Within Limits

1. **Cache responses** when possible
2. **Batch requests** efficiently
3. **Use pagination** appropriately
4. **Implement exponential backoff** when encountering rate limits
5. **Use the `select` parameter** to request only needed fields

## Requesting Higher Limits

If you need higher rate limits for your application:

1. Contact via Discord: https://discord.gg/dpsTCvg
2. Email: andrew@pokemontcg.io
3. Explain your use case and estimated needs

## Supporting the API

Consider supporting the API through:
- **Patreon**: https://www.patreon.com/pokemon_tcg_api
- **Ko-fi**: https://ko-fi.com/pokemontcg

Donations help ensure server performance meets application needs.
