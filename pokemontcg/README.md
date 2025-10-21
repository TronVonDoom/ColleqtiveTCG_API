# Pokemon TCG API Module

A complete, self-contained module for syncing and managing Pokemon TCG data from pokemontcg.io.

## 📁 Project Structure

```
pokemontcg/
├── __init__.py
├── README.md              # This file
├── config.py              # API configuration
├── models.py              # Database models
├── schema.sql             # Database schema
├── sync_api.py            # Sync from pokemontcg.io API
├── sync_github.py         # Sync from GitHub repository
├── image_helper.py        # Image handling utilities
├── pokemon_tcg.db         # SQLite database (generated)
│
├── docs/                  # Documentation
│   ├── IMAGE_DOWNLOAD.md
│   ├── IMAGE_PLACEHOLDER.md
│   └── IMAGE_INFORMATION.md
│
├── logs/                  # Log files (generated)
│   ├── sync.log
│   └── download_images.log
│
├── scripts/               # Utility scripts
│   ├── download_images.py      # Download card and set images
│   ├── find_missing_images.py  # Check for missing images
│   ├── retry_missing_images.py # Retry failed image downloads
│   └── check_images.py         # Verify image integrity
│
└── pokemon-tcg-data/      # GitHub data repository (cloned)
    ├── cards/
    │   └── en/            # Card data JSON files
    ├── sets/
    │   └── en.json        # Set data
    └── images/            # Downloaded images (generated)
        ├── cards/         # Card images by set
        └── sets/          # Set symbols and logos
```

## 🚀 Quick Start

### 1. Install Dependencies

From the **pokemontcg** folder:
```bash
cd pokemontcg
pip install -r ../requirements.txt
```

### 2. Clone Pokemon TCG Data Repository

```bash
git clone https://github.com/PokemonTCG/pokemon-tcg-data.git
```

### 3. Sync Data to Database

**Option A: Sync from GitHub (Recommended - Fast & Reliable)**
```bash
python sync_github.py --full
```

**Option B: Sync from API**
```bash
python sync_api.py --full
```

### 4. Download Images (Optional)

```bash
cd scripts
python download_images.py --all
```

## 📊 Database Operations

### Full Sync
Syncs all sets and cards from scratch:
```bash
python sync_github.py --full
```

### Incremental Update
Updates only new cards and sets:
```bash
python sync_github.py
```

### Sync Only Sets
```bash
python sync_api.py --sets-only
```

### Check Sync Progress
From the project root:
```bash
python scripts/check_progress.py
```

## 🖼️ Image Management

All image scripts should be run from the **pokemontcg/scripts** folder:

```bash
cd pokemontcg/scripts
```

### Download All Images
```bash
python download_images.py --all
```

### Download Only Card Images
```bash
python download_images.py --cards
```

### Download Only Set Images
```bash
python download_images.py --sets
```

### Check Download Statistics
```bash
python download_images.py --stats
```

### Find Missing Images
```bash
python find_missing_images.py
```

### Retry Failed Downloads
```bash
python retry_missing_images.py
```

### Advanced Options
```bash
# Increase parallel workers for faster downloads
python download_images.py --all --workers 20

# Adjust rate limiting (seconds between requests)
python download_images.py --all --rate-limit 0.05

# Custom image directory
python download_images.py --all --dir custom/path/to/images
```

## 📝 Configuration

### API Key Setup

Edit `config.py` to add your API key:
```python
API_KEY = 'your-api-key-here'
```

Get a free API key at: https://pokemontcg.io/

### Database Configuration

The module uses SQLite by default. The database file is created at:
```
pokemontcg/pokemon_tcg.db
```

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

- **IMAGE_DOWNLOAD.md** - Comprehensive guide to image downloading
- **IMAGE_PLACEHOLDER.md** - Using placeholder images for missing cards
- **IMAGE_INFORMATION.md** - Image data structure and organization

## 🗄️ Database Schema

The database includes the following main tables:

- **sets** - Pokemon TCG set information
- **cards** - Individual card data with all attributes
- **types** - Pokemon types
- **subtypes** - Card subtypes
- **supertypes** - Card supertypes
- **rarities** - Card rarities
- **sync_status** - Sync operation tracking

View the full schema in `schema.sql`.

## 🔧 Module Usage

### As a Python Module

```python
from pokemontcg import models, config
from pokemontcg.sync_github import sync_all_data

# Sync data
sync_all_data()

# Query database
import sqlite3
conn = sqlite3.connect('pokemontcg/pokemon_tcg.db')
cursor = conn.cursor()

# Get all sets
cursor.execute("SELECT * FROM sets")
sets = cursor.fetchall()

# Get cards from a specific set
cursor.execute("SELECT * FROM cards WHERE set_id = ?", ('base1',))
cards = cursor.fetchall()

conn.close()
```

## 📈 Statistics

After syncing, the database typically contains:
- **169+ sets** across all eras (Base Set through Scarlet & Violet)
- **19,600+ cards** with complete data
- **Image library** of 39,000+ card images (small + large)
- **Set assets** including symbols and logos

## 🛠️ Troubleshooting

### Database Issues

If you encounter database errors:
```bash
# Delete and recreate
rm pokemon_tcg.db
python sync_github.py --full
```

### Image Download Issues

If images fail to download:
```bash
cd scripts
python find_missing_images.py  # Check what's missing
python retry_missing_images.py  # Retry failed downloads
```

### GitHub Repository Issues

If the pokemon-tcg-data folder is missing or corrupted:
```bash
rm -rf pokemon-tcg-data
git clone https://github.com/PokemonTCG/pokemon-tcg-data.git
```

## 🔄 Keeping Data Updated

To keep your local database synchronized with the latest Pokemon TCG releases:

1. **Update the GitHub repository** (weekly):
   ```bash
   cd pokemon-tcg-data
   git pull origin master
   cd ..
   ```

2. **Run incremental sync**:
   ```bash
   python sync_github.py
   ```

3. **Download new images**:
   ```bash
   cd scripts
   python download_images.py --all
   ```

## 📦 Self-Contained Module

This module is completely self-contained with:
- ✅ All dependencies managed via parent `requirements.txt`
- ✅ Own database and data files
- ✅ Own scripts and utilities
- ✅ Own documentation
- ✅ No external dependencies on parent project

The module can be copied and used independently in other projects.

## 🤝 Contributing

When making changes to this module:
1. Keep all Pokemon TCG-specific code within this folder
2. Update documentation in `docs/` folder
3. Test sync operations before committing
4. Update this README with any new features

## 📄 License

This module follows the parent project's MIT License.

---

**Pokemon TCG Data Source**: https://github.com/PokemonTCG/pokemon-tcg-data  
**Pokemon TCG API**: https://pokemontcg.io
