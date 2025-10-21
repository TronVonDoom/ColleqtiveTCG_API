# Colleqtive TCG API# Colleqtive TCG API# Pokemon TCG Database Sync Tool



A unified API and database system for multiple Trading Card Games. Each game module is self-contained with its own data, scripts, and documentation.



## 📁 Project StructureA unified API and database for multiple Trading Card Games.A clean, organized tool for syncing Pokemon TCG API data to a local database.



```

ColleqtiveTCG_API/

│## Structure## Project Structure

├── pokemontcg/              # Pokemon TCG Module (Self-Contained)

│   ├── README.md            # Complete Pokemon TCG documentation

│   ├── config.py            # API configuration

│   ├── models.py            # Database models``````

│   ├── sync_api.py          # API sync script

│   ├── sync_github.py       # GitHub data sync scriptColleqtiveTCG_API/pokemon_tcg_database/

│   ├── image_helper.py      # Image utilities

│   ├── schema.sql           # Database schema├── pokemontcg/          # Pokemon TCG (pokemontcg.io)├── core/                    # Core application code

│   ├── pokemon_tcg.db       # SQLite database (generated)

│   ├── docs/                # Pokemon TCG documentation│   ├── models.py        # Database models│   ├── __init__.py

│   │   ├── IMAGE_DOWNLOAD.md

│   │   ├── IMAGE_PLACEHOLDER.md│   ├── config.py        # Configuration│   ├── config.py           # Configuration settings

│   │   └── IMAGE_INFORMATION.md

│   ├── logs/                # Log files (generated)│   ├── sync_api.py      # API sync script│   └── models.py           # SQLAlchemy database models

│   ├── scripts/             # Image & utility scripts

│   │   ├── download_images.py│   ├── sync_github.py   # GitHub data sync script├── scripts/                # Essential utility scripts

│   │   ├── find_missing_images.py

│   │   ├── retry_missing_images.py│   ├── pokemontcg.db    # SQLite database│   ├── __init__.py

│   │   └── check_images.py

│   └── pokemon-tcg-data/    # GitHub data repository (cloned)│   ├── pokemon-tcg-data/# Cloned GitHub data│   ├── check_progress.py   # Progress monitoring

│

├── scryfall/                # Magic: The Gathering Module (Future)│   ├── logs/            # Sync logs│   └── improved_sync.py    # Enhanced sync script

│   └── (planned - will follow same self-contained structure)

││   └── schema.sql       # Database schema├── tests/                  # Test files

├── shared/                  # Shared utilities (if needed across games)

│   └── __init__.py││   ├── __init__.py

│

├── scripts/                 # Project-level utility scripts├── scryfall/            # Magic: The Gathering (scryfall.com)│   └── test_api.py         # API connectivity testing

│   ├── check_progress.py    # Monitor sync progress

│   └── improved_sync.py     # Enhanced sync utilities│   └── (future implementation)├── docs/                   # Documentation

│

├── tests/                   # Test files││   └── README.md           # Detailed documentation

│   └── test_api.py

│├── shared/              # Shared utilities├── logs/                   # Log files

├── docs/                    # Project-level documentation

│   └── README.md│   └── (common functions)│   └── sync.log           # Sync operation logs

│

├── requirements.txt         # Python dependencies│├── database_sync.py        # Main sync script

├── REFACTORING_COMPLETE.md  # Refactoring notes

└── README.md               # This file├── scripts/             # Utility scripts├── requirements.txt        # Python dependencies

```

│   ├── check_progress.py├── schema.sql             # Database schema (for manual PostgreSQL setup)

## 🎮 Supported Games

│   └── improved_sync.py└── pokemon_tcg.db         # SQLite database (created after first run)

### ✅ Pokemon TCG (pokemontcg.io)

│```

**Status**: Fully Implemented & Self-Contained

├── tests/               # Test files

A complete module for syncing Pokemon TCG data with:

- 19,600+ cards across 169+ sets│   └── test_api.py## Quick Start

- Full database sync from API or GitHub

- Image downloading and management│

- Comprehensive documentation

└── docs/                # Documentation1. Install dependencies:

**Quick Start**:

```bash```   ```bash

cd pokemontcg

git clone https://github.com/PokemonTCG/pokemon-tcg-data.git   pip install -r requirements.txt

python sync_github.py --full

```## Games Supported   ```



**See**: `pokemontcg/README.md` for complete documentation



### 🔜 Magic: The Gathering (scryfall.com)### ✅ Pokemon TCG (pokemontcg.io)2. Run the sync:



**Status**: Planned- **Database**: `pokemontcg/pokemontcg.db`   ```bash



Will follow the same self-contained structure as Pokemon TCG module.- **Cards**: 19,653 cards across 169 sets   python database_sync.py --full



## 🚀 Quick Start- **Sync Methods**:   ```



### 1. Install Dependencies  - API: `python -m pokemontcg.sync_api --full`



```bash  - GitHub: `python -m pokemontcg.sync_github --full`For detailed documentation, see `docs/README.md`.

pip install -r requirements.txt

```### 🔜 Magic: The Gathering (scryfall.com)

- Coming soon

### 2. Work with a Game Module

## Usage

Each game has its own self-contained folder. Navigate to the game folder and follow its README:

### Pokemon TCG

**Pokemon TCG**:

```bash**Full Sync from GitHub (Fast, Reliable)**:

cd pokemontcg```bash

# See pokemontcg/README.md for full instructionspython -m pokemontcg.sync_github --full

python sync_github.py --full```

```

**Full Sync from API (When API is available)**:

## 📦 Design Philosophy: Self-Contained Modules```bash

python -m pokemontcg.sync_api --full

Each trading card game module follows these principles:```



✅ **Self-Contained**: All game-specific code, data, and documentation in one folder  **Check Progress**:

✅ **Independent Database**: Each game has its own SQLite database  ```bash

✅ **Own Scripts**: Image downloads, utilities, and helpers within the module  python scripts/check_progress.py

✅ **Complete Documentation**: Full README and docs within each module  ```

✅ **No Cross-Dependencies**: Modules don't depend on each other  

### Incremental Updates

This makes it easy to:

- Work on one game without affecting others**Update only new cards**:

- Copy a module to another project independently```bash

- Add new games without modifying existing onespython -m pokemontcg.sync_api

- Understand a game's implementation by looking at one folder```



## 🛠️ Development**Update only sets**:

```bash

### Adding a New TCG Gamepython -m pokemontcg.sync_api --sets-only

```

1. Create a new folder named after the game/API (e.g., `scryfall/`, `yugioh/`)

2. Follow the structure of `pokemontcg/`:## Setup

   ```

   newgame/1. **Install dependencies**:

   ├── README.md           # Complete documentation```bash

   ├── config.py           # API configurationpip install -r requirements.txt

   ├── models.py           # Database models```

   ├── sync_*.py           # Sync scripts

   ├── schema.sql          # Database schema2. **Clone Pokemon TCG data** (optional, for GitHub sync):

   ├── scripts/            # Utility scripts```bash

   ├── docs/               # Game-specific docscd pokemontcg

   └── logs/               # Log filesgit clone https://github.com/PokemonTCG/pokemon-tcg-data.git

   ``````

3. Implement sync logic and database models

4. Add image download scripts if needed3. **Run initial sync**:

5. Write comprehensive documentation```bash

6. Update this main READMEpython -m pokemontcg.sync_github --full

```

### Project-Level Scripts

## Database Schema

The `scripts/` folder at the root contains utilities that work across modules:

Each game has its own database with game-specific schema:

- `check_progress.py` - Monitor sync progress for any game- **Pokemon**: `pokemontcg/pokemontcg.db`

- `improved_sync.py` - Enhanced sync utilities- **Magic** (future): `scryfall/scryfall.db`



## 📚 Documentation## API Keys



- **Project Documentation**: `docs/README.md`### Pokemon TCG

- **Pokemon TCG Documentation**: `pokemontcg/README.md`Set your API key in `pokemontcg/config.py`:

- **Image Management**: `pokemontcg/docs/IMAGE_*.md````python

API_KEY = 'your-api-key-here'

## 🧪 Testing```



```bash### Magic: The Gathering

# Run all testsScryfall API is free and doesn't require an API key.

python -m pytest tests/

## Contributing

# Test API connectivity

python tests/test_api.pyWhen adding a new TCG:

```1. Create a new directory named after the API/data source

2. Implement models, config, and sync scripts

## 📊 Database Information3. Update this README



Each game module maintains its own SQLite database:## License



- **Pokemon TCG**: `pokemontcg/pokemon_tcg.db`MIT

- **Magic** (future): `scryfall/scryfall.db`

This approach ensures:
- No conflicts between games
- Easy backup and migration per game
- Simpler queries and relationships
- Independent scaling

## 🔄 Version Control

The `.gitignore` file excludes:
- `*.db` - Database files (too large for git)
- `**/logs/` - Log files
- `**/pokemon-tcg-data/` - Cloned repositories
- `**/images/` - Downloaded images

## 🤝 Contributing

1. Keep game-specific code within game folders
2. Use `shared/` only for truly common utilities
3. Document all new features
4. Follow the self-contained module pattern
5. Test thoroughly before committing

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Resources

### Pokemon TCG
- **API**: https://pokemontcg.io
- **Data Repository**: https://github.com/PokemonTCG/pokemon-tcg-data
- **Documentation**: https://docs.pokemontcg.io

### Magic: The Gathering (Planned)
- **API**: https://scryfall.com
- **Documentation**: https://scryfall.com/docs/api

---

**Note**: Each game module contains its own comprehensive README. Navigate to the module folder and read its README for detailed instructions and documentation.
