# Pokemon TCG Database Sync Tool

A clean, organized tool for syncing Pokemon TCG API data to a local database.

## Project Structure

```
pokemon_tcg_database/
├── core/                    # Core application code
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   └── models.py           # SQLAlchemy database models
├── scripts/                # Essential utility scripts
│   ├── __init__.py
│   ├── check_progress.py   # Progress monitoring
│   └── improved_sync.py    # Enhanced sync script
├── tests/                  # Test files
│   ├── __init__.py
│   └── test_api.py         # API connectivity testing
├── docs/                   # Documentation
│   └── README.md           # Detailed documentation
├── logs/                   # Log files
│   └── sync.log           # Sync operation logs
├── database_sync.py        # Main sync script
├── requirements.txt        # Python dependencies
├── schema.sql             # Database schema (for manual PostgreSQL setup)
└── pokemon_tcg.db         # SQLite database (created after first run)
```

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the sync:
   ```bash
   python database_sync.py --full
   ```

For detailed documentation, see `docs/README.md`.