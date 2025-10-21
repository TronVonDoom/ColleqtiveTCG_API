# Quick Reference - Self-Contained Modules

## 🎯 What Changed?

The project has been reorganized so each card game is **completely self-contained** in its own folder.

## 📁 Old vs New Structure

### Before:
```
ColleqtiveTCG_API/
├── download_images.py         ❌ At root
├── check_images.py             ❌ At root
├── IMAGE_INFORMATION.md        ❌ At root
├── pokemon_tcg.db              ❌ At root
├── pokemontcg/
│   ├── sync_api.py
│   └── models.py
└── docs/
    ├── IMAGE_DOWNLOAD.md       ❌ Mixed docs
    └── IMAGE_PLACEHOLDER.md
```

### After:
```
ColleqtiveTCG_API/
├── pokemontcg/                 ✅ Self-contained
│   ├── README.md               ✅ Complete docs
│   ├── pokemontcg.db           ✅ Own database
│   ├── sync_api.py
│   ├── models.py
│   ├── scripts/                ✅ Own scripts
│   │   ├── download_images.py
│   │   ├── check_images.py
│   │   ├── find_missing_images.py
│   │   └── retry_missing_images.py
│   └── docs/                   ✅ Own docs
│       ├── IMAGE_DOWNLOAD.md
│       ├── IMAGE_PLACEHOLDER.md
│       └── IMAGE_INFORMATION.md
└── scryfall/                   ✅ Ready for MTG
    └── (same self-contained structure)
```

## 🚀 How to Use

### Pokemon TCG

**Navigate to the module:**
```bash
cd pokemontcg
```

**Read the documentation:**
```bash
# View main README
cat README.md

# View image docs
cat docs/IMAGE_DOWNLOAD.md
```

**Sync database:**
```bash
python sync_github.py --full
```

**Download images:**
```bash
cd scripts
python download_images.py --all
```

**Check progress (from project root):**
```bash
cd ../..
python scripts/check_progress.py
```

## 💡 Key Benefits

1. **Everything in One Place**: All Pokemon TCG code, data, and docs in `pokemontcg/`
2. **Portable**: Copy the `pokemontcg` folder to use in another project
3. **Clear**: No guessing which files belong to which game
4. **Scalable**: Easy to add more games following the same pattern
5. **Independent**: Each game module works without the others

## 📖 Documentation

Each module has its own complete README:

- **Pokemon TCG**: `pokemontcg/README.md` - Complete usage guide
- **Project Root**: `README.md` - Overview and philosophy
- **This File**: Quick reference and migration guide

## 🔄 Migration Notes

If you had scripts or commands that worked before:

**Before:**
```bash
python download_images.py --all
```

**After:**
```bash
cd pokemontcg/scripts
python download_images.py --all
```

The scripts now use relative paths from their location.

## 📦 Adding a New Game

To add Magic: The Gathering (or any game):

1. Create `scryfall/` folder (or game name)
2. Copy the structure from `pokemontcg/`
3. Implement game-specific logic
4. Each game is completely independent!

```
scryfall/
├── README.md              # Complete Scryfall docs
├── config.py              # Scryfall API config
├── models.py              # MTG card models
├── sync_scryfall.py       # Sync script
├── scryfall.db            # Own database
├── scripts/               # MTG scripts
└── docs/                  # MTG docs
```

## ✅ Checklist for Self-Contained Module

Each game module should have:

- [ ] README.md with complete documentation
- [ ] Own database file (*.db)
- [ ] config.py for API settings
- [ ] models.py for data structures
- [ ] sync_*.py for data syncing
- [ ] scripts/ folder for utilities
- [ ] docs/ folder for detailed documentation
- [ ] logs/ folder (gitignored)
- [ ] No dependencies on other game modules

## 🎓 Philosophy

> "Each card game module is a mini-project that can stand alone."

This makes the codebase:
- Easier to understand
- Simpler to maintain
- More flexible to extend
- Portable to other projects

---

For detailed information, see:
- `pokemontcg/README.md` - Pokemon TCG complete guide
- `README.md` - Project overview
- `SELF_CONTAINED_REFACTOR.md` - Detailed change log
