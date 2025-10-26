"""
Convert PNG images to WebP format
This script finds all .png files and converts them to .webp with quality 90
"""
import os
import sys
from pathlib import Path
from PIL import Image
import argparse

# Base directory for images
IMAGES_BASE_DIR = Path(__file__).parent.parent.parent / 'tcg-images-download' / 'pokemon' / 'cards'

# WebP quality (90 = excellent quality, ~80% size reduction)
WEBP_QUALITY = 90

def convert_png_to_webp(png_path: Path, quality: int = WEBP_QUALITY, delete_original: bool = False) -> bool:
    """Convert a single PNG file to WebP
    
    Args:
        png_path: Path to the PNG file
        quality: WebP quality (0-100, default 90)
        delete_original: Whether to delete the PNG file after conversion
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate WebP path
        webp_path = png_path.with_suffix('.webp')
        
        # Check if WebP already exists
        if webp_path.exists():
            print(f"   ⚠️  WebP already exists: {webp_path.name}")
            if delete_original and png_path.exists():
                png_path.unlink()
                print(f"   🗑️  Deleted original PNG")
            return True
        
        # Open and convert
        with Image.open(png_path) as img:
            # Save as WebP
            img.save(webp_path, 'WEBP', quality=quality, method=6)
        
        # Get file sizes for comparison
        original_size = png_path.stat().st_size
        webp_size = webp_path.stat().st_size
        savings = (1 - webp_size / original_size) * 100
        
        print(f"   ✅ Converted: {png_path.name} -> {webp_path.name}")
        print(f"      Size: {original_size/1024:.1f}KB → {webp_size/1024:.1f}KB ({savings:.0f}% smaller)")
        
        # Delete original if requested
        if delete_original:
            png_path.unlink()
            print(f"   🗑️  Deleted original PNG")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error converting {png_path.name}: {str(e)}")
        return False

def find_png_files(directory: Path, set_id: str = None) -> list:
    """Recursively find all PNG files in directory
    
    Args:
        directory: Root directory to search
        set_id: Optional set ID to filter by
    
    Returns:
        List of Path objects for PNG files
    """
    png_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip if filtering by set and this isn't the set
        if set_id and set_id not in root:
            continue
            
        for file in files:
            if file.lower().endswith('.png'):
                png_files.append(Path(root) / file)
    
    return png_files

def scan_and_report(directory: Path, set_id: str = None):
    """Scan directory and report PNG files found"""
    print(f"\n🔍 Scanning for PNG files in: {directory}")
    if set_id:
        print(f"   Filtering to set: {set_id}")
    print("=" * 80)
    
    png_files = find_png_files(directory, set_id)
    
    if not png_files:
        print("\n✅ No PNG files found!")
        return []
    
    print(f"\n📊 Found {len(png_files)} PNG files:")
    print("-" * 80)
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in png_files)
    estimated_webp_size = total_size * 0.2  # ~80% reduction at Q90
    estimated_savings = total_size - estimated_webp_size
    
    # Group by set
    by_set = {}
    for png_file in png_files:
        # Get set ID (parent's parent directory name)
        set_id = png_file.parent.parent.name
        if set_id not in by_set:
            by_set[set_id] = []
        by_set[set_id].append(png_file)
    
    for set_id in sorted(by_set.keys()):
        files = by_set[set_id]
        set_size = sum(f.stat().st_size for f in files)
        print(f"\n   {set_id}: {len(files)} files ({set_size/(1024*1024):.1f} MB)")
        for f in files[:3]:  # Show first 3
            print(f"      • {f.parent.name}/{f.name}")
        if len(files) > 3:
            print(f"      ... and {len(files) - 3} more")
    
    print("\n" + "=" * 80)
    print("💾 Size Estimates:")
    print(f"   Current (PNG): {total_size/(1024*1024):.1f} MB")
    print(f"   After (WebP Q90): {estimated_webp_size/(1024*1024):.1f} MB")
    print(f"   Space savings: {estimated_savings/(1024*1024):.1f} MB (~80%)")
    
    return png_files

def convert_all(directory: Path, quality: int = WEBP_QUALITY, 
                delete_original: bool = False, set_id: str = None):
    """Convert all PNG files to WebP
    
    Args:
        directory: Root directory to search
        quality: WebP quality (0-100)
        delete_original: Whether to delete PNG files after conversion
        set_id: Optional set ID to filter by
    """
    print("\n🔄 Starting conversion...")
    print("=" * 80)
    print(f"WebP Quality: {quality}")
    
    # Find all PNG files
    png_files = find_png_files(directory, set_id)
    
    if not png_files:
        print("\n✅ No PNG files to convert!")
        return
    
    print(f"\nConverting {len(png_files)} files...")
    if delete_original:
        print("⚠️  Original PNG files will be DELETED after conversion")
    
    success_count = 0
    fail_count = 0
    total_original_size = 0
    total_webp_size = 0
    
    for i, png_file in enumerate(png_files, 1):
        print(f"\n[{i}/{len(png_files)}] {png_file.parent.parent.name}/{png_file.parent.name}/{png_file.name}")
        
        original_size = png_file.stat().st_size
        
        if convert_png_to_webp(png_file, quality, delete_original):
            success_count += 1
            total_original_size += original_size
            
            # Get WebP size
            webp_path = png_file.with_suffix('.webp')
            if webp_path.exists():
                total_webp_size += webp_path.stat().st_size
        else:
            fail_count += 1
    
    print("\n" + "=" * 80)
    print("📊 Conversion Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📁 Total: {len(png_files)}")
    
    if success_count > 0:
        actual_savings = (1 - total_webp_size / total_original_size) * 100
        print(f"\n💾 Size Results:")
        print(f"   Original: {total_original_size/(1024*1024):.1f} MB")
        print(f"   WebP: {total_webp_size/(1024*1024):.1f} MB")
        print(f"   Saved: {(total_original_size - total_webp_size)/(1024*1024):.1f} MB ({actual_savings:.1f}%)")
    
    if delete_original and success_count > 0:
        print(f"\n   🗑️  Deleted {success_count} original PNG files")

def main():
    parser = argparse.ArgumentParser(
        description='Convert PNG images to WebP format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for PNG files (no conversion)
  python convert_png_to_webp.py --scan
  
  # Convert all PNG files (keep originals)
  python convert_png_to_webp.py --convert
  
  # Convert and delete originals
  python convert_png_to_webp.py --convert --delete
  
  # Convert with custom quality (0-100)
  python convert_png_to_webp.py --convert --quality 95
  
  # Convert specific set only
  python convert_png_to_webp.py --convert --set base1
        """
    )
    
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan for PNG files without converting'
    )
    
    parser.add_argument(
        '--convert',
        action='store_true',
        help='Convert PNG files to WebP'
    )
    
    parser.add_argument(
        '--quality',
        type=int,
        default=WEBP_QUALITY,
        help=f'WebP quality (0-100, default: {WEBP_QUALITY})'
    )
    
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete original PNG files after conversion (use with --convert)'
    )
    
    parser.add_argument(
        '--set',
        type=str,
        help='Only process files for specific set ID (e.g., base1, swsh1)'
    )
    
    parser.add_argument(
        '--dir',
        type=str,
        help='Custom directory to scan (default: tcg-images-download/pokemon/cards)'
    )
    
    args = parser.parse_args()
    
    # Validate quality
    if not 0 <= args.quality <= 100:
        print("❌ Quality must be between 0 and 100")
        sys.exit(1)
    
    # Determine directory
    directory = Path(args.dir) if args.dir else IMAGES_BASE_DIR
    
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        sys.exit(1)
    
    print("🎴 PNG to WebP Converter")
    print("=" * 80)
    print(f"Directory: {directory}")
    
    try:
        if args.scan:
            # Scan only
            scan_and_report(directory, args.set)
        
        elif args.convert:
            # Scan first
            png_files = scan_and_report(directory, args.set)
            
            if not png_files:
                return
            
            # Confirm
            print("\n" + "=" * 80)
            action = "convert and DELETE" if args.delete else "convert (keep originals)"
            response = input(f"\n❓ {action.upper()} {len(png_files)} PNG files? (y/n): ")
            
            if response.lower() == 'y':
                convert_all(directory, quality=args.quality, 
                           delete_original=args.delete, set_id=args.set)
            else:
                print("\n❌ Conversion cancelled")
        
        else:
            # No action specified - show help
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
