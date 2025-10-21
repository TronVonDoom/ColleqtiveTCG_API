# Magic: The Gathering (Scryfall.com)

This module will handle syncing and database operations for Magic: The Gathering using the Scryfall API.

## Status
🔜 **Not yet implemented**

## Future Structure

When implemented, this directory will contain:
```
scryfall/
├── models.py          # MTG-specific database models
├── config.py          # Scryfall API configuration
├── sync_api.py        # Sync from Scryfall API
├── scryfall.db        # SQLite database
├── logs/              # Sync logs
└── schema.sql         # Database schema
```

## Scryfall API

- **API Docs**: https://scryfall.com/docs/api
- **Rate Limit**: 10 requests per second
- **Authentication**: None required (free API)
- **Data**: 
  - ~25,000+ unique cards
  - Multiple printings
  - Card images (small, normal, large, art crop, border crop)
  - Prices (USD, EUR, TIX)
  - Rulings and legalities

## Implementation Notes

When implementing:
1. Use similar model structure to pokemontcg
2. Handle MTG-specific fields (mana cost, color identity, card types, etc.)
3. Support multiple printings of the same card
4. Include pricing data from TCGPlayer and Cardmarket
5. Handle double-faced/split/flip cards properly
