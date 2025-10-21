# Pokemon TCG Image Downloader

## Overview

This script downloads and organizes all Pokemon TCG images from pokemontcg.io, including:
- Card images (small and large/hi-res)
- Set symbols
- Set logos

## Directory Structure

After running the script, images will be organized as follows:

```
pokemontcg/
└── pokemon-tcg-data/
    ├── cards/
    │   └── en/
    │       ├── base1.json
    │       ├── base2.json
    │       └── ...
    ├── sets/
    │   └── en.json
    └── images/
        ├── cards/
        │   ├── base1/              # Base Set
        │   │   ├── 1.png           # Small image (card #1)
        │   │   ├── 1_hires.png     # Large image (card #1)
        │   │   ├── 2.png
        │   │   ├── 2_hires.png
        │   │   └── ...
        │   ├── base2/              # Jungle Set
        │   ├── sv1/                # Scarlet & Violet
        │   └── ...                 # 169 set folders total
        └── sets/
            ├── symbols/
            │   ├── base1_symbol.png
            │   ├── base2_symbol.png
            │   └── ...
            └── logos/
                ├── base1_logo.png
                ├── base2_logo.png
                └── ...
```

**Benefits of this structure:**
- ✅ Images organized by set (easier to find and manage)
- ✅ All data in one place (`pokemontcg/pokemon-tcg-data/`)
- ✅ Small and large versions in same folder
- ✅ Card numbers match the JSON data
- ✅ Self-contained module structure

## Usage

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

### Show Statistics
```bash
python download_images.py --stats
```

## Advanced Options

### Custom Output Directory
```bash
python download_images.py --all --dir my_images
```

### Adjust Parallel Workers
```bash
python download_images.py --all --workers 20
```
(Default: 10 workers. Increase for faster downloads if you have good bandwidth)

### Adjust Rate Limiting
```bash
python download_images.py --all --rate-limit 0.05
```
(Default: 0.1 seconds between requests. Lower = faster but more aggressive)

## Expected Results

### Download Size
- **Card images (small)**: ~18,000 images, ~500-800 MB
- **Card images (large)**: ~18,000 images, ~3-4 GB
- **Set images**: ~180 symbols + logos, ~10-20 MB
- **Total**: Approximately **4-5 GB**

### Download Time
- With 10 workers and good internet: ~30-60 minutes
- With 20 workers: ~15-30 minutes
- Depends on your internet speed and pokemontcg.io server response

## Features

✅ **Parallel Downloads**: Uses ThreadPoolExecutor for fast concurrent downloads
✅ **Rate Limiting**: Respects server resources with configurable delays
✅ **Resume Support**: Skips already downloaded images
✅ **Error Handling**: Retries failed downloads with exponential backoff
✅ **Progress Tracking**: Shows real-time download progress
✅ **Logging**: Detailed logs saved to `download_images.log`

## Requirements

Make sure you have the required package:
```bash
pip install requests
```
(Should already be in your requirements.txt)

## Troubleshooting

### Download is slow
- Increase workers: `--workers 20`
- Reduce rate limit: `--rate-limit 0.05`
- Check your internet connection

### Some images fail to download
- Check the log file: `download_images.log`
- Run the script again (it will skip existing files and retry failures)
- URLs may be temporarily unavailable

### Out of disk space
- Small images only: ~1 GB
- Skip large images if space is limited
- Use `--cards` without `--all` and modify script to skip large images

## Integration with Database

The downloaded images use the same naming convention as the database:
- Database `image_small` URL → Local `images/cards/small/{card_id}.png`
- Database `image_large` URL → Local `images/cards/large/{card_id}_hires.png`

You can update your API to serve local images instead of remote URLs.

## Notes

- Images are downloaded from pokemontcg.io CDN
- **All images are PNG format with transparent backgrounds** (perfect for overlays and UI)
- The script creates directory structure automatically
- Safe to run multiple times (skips existing files)
- Progress is logged to console and file
- Transparent backgrounds allow flexible use in any design context

## Example Run

```bash
$ python download_images.py --all

2025-10-20 23:45:12 - INFO - Created image directory structure in: images
2025-10-20 23:45:12 - INFO - ============================================================
2025-10-20 23:45:12 - INFO - Starting card image downloads
2025-10-20 23:45:12 - INFO - ============================================================
2025-10-20 23:45:13 - INFO - Processing base1.json: 102 cards
2025-10-20 23:45:14 - INFO - Processing base2.json: 130 cards
...
2025-10-20 23:45:20 - INFO - Total images to download: 36000
2025-10-20 23:45:20 - INFO - Using 10 parallel workers
2025-10-20 23:46:00 - INFO - Progress: 100/36000 images processed
...
2025-10-21 00:15:30 - INFO - ============================================================
2025-10-21 00:15:30 - INFO - Card Image Download Summary
2025-10-21 00:15:30 - INFO - ============================================================
2025-10-21 00:15:30 - INFO - Total cards: 18000
2025-10-21 00:15:30 - INFO - Small images downloaded: 18000
2025-10-21 00:15:30 - INFO - Large images downloaded: 18000
2025-10-21 00:15:30 - INFO - Failed: 0
```
