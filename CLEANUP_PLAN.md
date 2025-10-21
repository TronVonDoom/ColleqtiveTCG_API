# Backend API Cleanup Plan

## Issues Found:
1. ❌ Duplicate folders: `pokemontcg/` and `pokemon_tcg_database/`
2. ❌ Multiple database files in different locations
3. ❌ Documentation scattered (root + pokemon_tcg_api_docs/)
4. ❌ Unused `src/` folder structure
5. ❌ Log files in root
6. ❌ Loose `__init__.py` in root

## Proposed Structure:

```
ColleqtiveTCG_API/
├── .git/
├── .gitignore
├── README.md
├── requirements.txt
├── runtime.txt
├── Procfile
│
├── docs/                      # All documentation
│   ├── api-reference/         # API docs
│   ├── setup/
│   └── deployment/
│
├── pokemontcg/                # Main Pokemon TCG module
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── api.py
│   ├── sync_api.py
│   ├── sync_github.py
│   ├── schema.sql
│   ├── image_helper.py
│   ├── scripts/
│   ├── data/                  # Database and data files
│   │   ├── pokemontcg.db
│   │   └── pokemon-tcg-data/  # Cloned GitHub data
│   └── logs/
│
├── scripts/                   # Project-level utilities
│   ├── check_progress.py
│   └── improved_sync.py
│
├── tests/
│   ├── test_api.py
│   └── test_*.py
│
└── scryfall/                  # Future MTG module
    └── README.md
```

## Actions to Take:

### 1. Consolidate Pokemon TCG Code
- [ ] Merge `pokemon_tcg_database/` into `pokemontcg/`
- [ ] Remove duplicate files
- [ ] Update import paths

### 2. Organize Documentation
- [ ] Move `pokemon_tcg_api_docs/` → `docs/api-reference/`
- [ ] Move deployment docs to `docs/deployment/`
- [ ] Keep only main README in root

### 3. Clean Database Files
- [ ] Keep only `pokemontcg/data/pokemontcg.db`
- [ ] Update `.gitignore` for database location
- [ ] Remove duplicates

### 4. Remove Unused Files
- [ ] Delete `src/` folder (unused structure)
- [ ] Remove `__init__.py` from root
- [ ] Move `sync.log` to `pokemontcg/logs/`
- [ ] Remove duplicate markdown files

### 5. Update .gitignore
```
# Database files
*.db
**/data/*.db

# Logs
**/logs/*.log
sync.log

# Cloned data
**/pokemon-tcg-data/

# Python
__pycache__/
*.pyc
.pytest_cache/
venv/
.env

# IDE
.vscode/
.idea/
```

## Commands to Execute:

```powershell
# Will be provided after confirmation
```
