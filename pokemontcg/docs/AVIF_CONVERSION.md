# AVIF to PNG Conversion Guide

## Overview

Some Pokemon TCG card images are downloaded in AVIF format instead of PNG. AVIF is a modern image format with better compression, but PNG is more universally supported.

This script converts all AVIF images to PNG format automatically.

## Prerequisites

Install required dependencies:

```powershell
pip install Pillow pillow-avif-plugin
```

Or update all requirements:

```powershell
pip install -r requirements.txt
```

## Usage

### 1. Scan for AVIF Files

First, see what AVIF files exist:

```powershell
python pokemontcg\scripts\convert_avif_to_png.py --scan
```

**Output:**
```
🔍 Scanning for AVIF files in: tcg-images-download/pokemon/cards
================================================================================

📊 Found 42 AVIF files:
--------------------------------------------------------------------------------

   base1: 5 files
      • small/1.avif
      • small/2.avif
      • large/1.avif
      ... and 2 more

   swsh1: 12 files
      • small/1.avif
      • small/5.avif
      ... and 10 more
```

### 2. Convert Files (Keep Originals)

Convert AVIF to PNG but keep original AVIF files:

```powershell
python pokemontcg\scripts\convert_avif_to_png.py --convert
```

This will:
- ✅ Create PNG versions
- ✅ Keep original AVIF files
- ✅ Skip if PNG already exists

### 3. Convert and Delete Originals

Convert and delete AVIF files after successful conversion:

```powershell
python pokemontcg\scripts\convert_avif_to_png.py --convert --delete
```

⚠️ **Warning:** This permanently deletes AVIF files!

### 4. Convert Specific Set Only

Convert only files from a specific set:

```powershell
python pokemontcg\scripts\convert_avif_to_png.py --convert --set base1
```

## Examples

### Example 1: Safe Conversion (Recommended)

```powershell
# 1. Scan first
python pokemontcg\scripts\convert_avif_to_png.py --scan

# 2. Convert (keep originals)
python pokemontcg\scripts\convert_avif_to_png.py --convert

# 3. Verify PNGs work, then delete AVIFs
python pokemontcg\scripts\convert_avif_to_png.py --convert --delete
```

### Example 2: Quick Conversion with Cleanup

```powershell
python pokemontcg\scripts\convert_avif_to_png.py --convert --delete
```

### Example 3: Convert Single Set

```powershell
python pokemontcg\scripts\convert_avif_to_png.py --convert --set svp --delete
```

## Command Reference

| Flag | Description |
|------|-------------|
| `--scan` | Scan for AVIF files without converting |
| `--convert` | Convert AVIF files to PNG |
| `--delete` | Delete original AVIF files after conversion |
| `--set <id>` | Only process files for specific set (e.g., base1) |
| `--dir <path>` | Use custom directory instead of default |

## What It Does

1. **Finds all AVIF files** in the images directory
2. **Converts to PNG** with proper color space handling
3. **Preserves transparency** (converts to white background if needed)
4. **Optimizes PNGs** for smaller file size
5. **Reports progress** for each file
6. **Optionally deletes** original AVIF files

## File Handling

### AVIF with Alpha Channel (Transparency)
- Converted to RGB with white background
- Transparency preserved where possible

### AVIF without Alpha
- Direct conversion to PNG
- No quality loss

### Existing PNGs
- Skipped (won't overwrite)
- Original AVIF deleted if `--delete` flag used

## Performance

Typical conversion speeds:
- **Small images** (~200KB): 0.1-0.2 seconds each
- **Large images** (~2MB): 0.5-1.0 seconds each
- **100 images**: ~30-60 seconds total

## Troubleshooting

### "ModuleNotFoundError: No module named 'PIL'"

Install Pillow:
```powershell
pip install Pillow pillow-avif-plugin
```

### "cannot identify image file"

AVIF support not installed:
```powershell
pip install pillow-avif-plugin
```

### "Permission denied"

Close any programs viewing the images, then try again.

### Conversion fails on some images

- Check if file is corrupted
- Try viewing in an AVIF-compatible viewer first
- Skip problematic files and convert the rest

## Safety Notes

✅ **Safe Operations:**
- Using `--scan` (read-only)
- Using `--convert` without `--delete` (keeps originals)

⚠️ **Caution Required:**
- Using `--delete` flag (permanent deletion)
- Always test without `--delete` first
- Verify PNGs work before deleting AVIFs

## Why Convert?

**Pros of PNG:**
- Universal browser support
- Widely compatible
- Easy to work with
- Lossless compression

**Pros of AVIF:**
- Better compression (smaller files)
- Modern format
- Better quality at same file size

**When to convert:**
- Need broader compatibility
- Your system/tools don't support AVIF
- Frontend requires PNG specifically
- Consistency across image formats

## Batch Processing Tips

### Convert All Sets Gradually

```powershell
# Get list of sets with AVIF files
python pokemontcg\scripts\convert_avif_to_png.py --scan > avif_report.txt

# Convert one set at a time
python pokemontcg\scripts\convert_avif_to_png.py --convert --set base1
python pokemontcg\scripts\convert_avif_to_png.py --convert --set base2
# ... etc
```

### Process in Background

```powershell
# Run conversion in background (Windows)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\path\to\repo; python pokemontcg\scripts\convert_avif_to_png.py --convert --delete"
```

### Verify After Conversion

```powershell
# Check for remaining AVIF files
python pokemontcg\scripts\convert_avif_to_png.py --scan

# Should show "No AVIF files found!" if all converted
```

## Integration with Manager GUI

Future enhancement: Add AVIF conversion option to the ColleqtiveTCG_Manager GUI:
- Scan button in Tools menu
- Batch convert from GUI
- Progress tracking
- Visual reporting

## File Size Comparison

Typical file sizes:

| Format | Small | Large | Savings |
|--------|-------|-------|---------|
| AVIF | 50KB | 400KB | Baseline |
| PNG (our conversion) | 150KB | 1.2MB | -3x larger |
| Original PNG | 200KB | 2MB | -4x larger |

**Note:** PNGs are larger but more compatible. If disk space is a concern, keep AVIFs instead.

## Summary

Use this script to convert all AVIF images to PNG format for better compatibility. Start with `--scan` to see what you have, then use `--convert` to create PNGs. Once verified, use `--delete` to clean up the original AVIFs.

**Recommended workflow:**
1. Scan: `--scan`
2. Convert: `--convert`
3. Test your app
4. Clean up: `--convert --delete`
