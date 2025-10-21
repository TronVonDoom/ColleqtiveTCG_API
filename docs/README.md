# Database Setup and Data Migration Tool

This tool fetches all data from the Pokémon TCG API and stores it in your own database for use in your application.

## Features

- ✅ Fetches all cards from the API
- ✅ Fetches all sets from the API
- ✅ Stores data in local SQLite or PostgreSQL (Railway-ready)
- ✅ Automatic schema creation
- ✅ Progress tracking
- ✅ Resume capability (skip already imported data)
- ✅ Pricing data included
- ✅ Image URLs stored
- ✅ Full-text search support

## Database Schema

### Tables Created

1. **sets** - All Pokémon TCG sets
2. **cards** - All cards with complete data
3. **card_types** - Card type relationships (Fire, Water, etc.)
4. **card_subtypes** - Card subtype relationships (Basic, V, etc.)
5. **card_attacks** - Card attacks
6. **card_abilities** - Card abilities
7. **card_weaknesses** - Card weaknesses
8. **card_resistances** - Card resistances
9. **types** - Reference: All energy types
10. **subtypes** - Reference: All subtypes
11. **supertypes** - Reference: All supertypes
12. **rarities** - Reference: All rarities

## Files

- `database_sync.py` - Main sync script
- `database_schema.sql` - SQL schema for PostgreSQL
- `models.py` - SQLAlchemy ORM models
- `config.py` - Database configuration
- `requirements.txt` - Python dependencies

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Edit `config.py` to set your database connection:

```python
# For local SQLite (development)
DATABASE_URL = "sqlite:///pokemon_tcg.db"

# For PostgreSQL (Railway/production)
DATABASE_URL = "postgresql://user:password@host:port/database"
```

### 3. Run Initial Sync

```bash
python database_sync.py --full
```

This will:
1. Create all database tables
2. Fetch all reference data (types, subtypes, etc.)
3. Fetch all sets
4. Fetch all cards (this may take 30-60 minutes)

### 4. Update Data

To update with new cards/sets:

```bash
python database_sync.py --update
```

## Usage Options

```bash
# Full sync (initial import)
python database_sync.py --full

# Update only (new cards/sets since last sync)
python database_sync.py --update

# Sync specific set
python database_sync.py --set swsh4

# Sync reference data only
python database_sync.py --reference

# Sync with progress bar
python database_sync.py --full --verbose

# Resume interrupted sync
python database_sync.py --resume
```

## Railway Deployment

### 1. Create Railway PostgreSQL Database

1. Go to https://railway.app/
2. Create new project
3. Add PostgreSQL database
4. Copy the DATABASE_URL connection string

### 2. Update config.py

```python
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///pokemon_tcg.db')
```

### 3. Deploy

```bash
# Set environment variable
railway variables set DATABASE_URL="postgresql://..."

# Run migration
railway run python database_sync.py --full
```

### 4. Schedule Updates

Use Railway's Cron Jobs or GitHub Actions to run daily updates:

```yaml
# .github/workflows/update_db.yml
name: Update Pokemon TCG Database
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python database_sync.py --update
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Query Examples

After syncing, you can query your database:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Card, Set

engine = create_engine('sqlite:///pokemon_tcg.db')
Session = sessionmaker(bind=engine)
session = Session()

# Get all Charizard cards
charizards = session.query(Card).filter(Card.name.like('%Charizard%')).all()

# Get cards from a set
vivid_voltage = session.query(Set).filter_by(id='swsh4').first()
cards = session.query(Card).filter_by(set_id='swsh4').all()

# Get cards by type
fire_cards = session.query(Card).join(Card.types).filter_by(name='Fire').all()

# Get expensive cards
expensive = session.query(Card).filter(Card.market_price > 100).all()
```

## API Usage

With data in your database, you can build fast APIs:

```python
from fastapi import FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/api/cards")
def get_cards(name: str = None, limit: int = 50):
    query = session.query(Card)
    if name:
        query = query.filter(Card.name.like(f'%{name}%'))
    return query.limit(limit).all()

@app.get("/api/sets")
def get_sets():
    return session.query(Set).all()
```

## Performance

- **Initial sync**: 30-60 minutes (depends on API rate limits)
- **Database size**: ~500MB - 1GB (all cards + images URLs)
- **Query speed**: Milliseconds (vs seconds from API)
- **No rate limits**: Query your own database unlimited times

## Maintenance

### Update Pricing Data

Pricing data changes frequently. Update it separately:

```bash
python database_sync.py --update-prices
```

### Backup Database

```bash
# SQLite
cp pokemon_tcg.db pokemon_tcg_backup.db

# PostgreSQL
pg_dump DATABASE_URL > backup.sql
```

## Troubleshooting

### Rate Limit Errors

If you hit rate limits, the script will automatically retry with exponential backoff.

### Resume Failed Sync

```bash
python database_sync.py --resume
```

### Clear and Restart

```bash
python database_sync.py --reset --full
```

## Benefits

- ⚡ **Fast queries** - No API calls needed
- 💰 **Cost effective** - No rate limit concerns
- 🔍 **Complex queries** - Use SQL for advanced searches
- 📊 **Analytics** - Run aggregate queries on your data
- 🚀 **Scalable** - Deploy to Railway, Heroku, AWS, etc.
- 💾 **Offline** - Works without internet (after initial sync)

## Next Steps

1. Run initial sync: `python database_sync.py --full`
2. Deploy to Railway
3. Build your API on top of the database
4. Schedule daily updates
5. Add custom analytics and features
