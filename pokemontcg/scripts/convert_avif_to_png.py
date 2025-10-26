"""
Convert AVIF images to PNG format
This script finds all .avif files in the images directory and converts them to .png
"""
import os
import sys
from pathlib import Path
from PIL import Image
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Base directory for images
IMAGES_BASE_DIR = Path(__file__).parent.parent.parent / 'tcg-images-download' / 'pokemon' / 'cards'

def convert_avif_to_png(avif_path: Path, delete_original: bool = False) -> bool:
    """Convert a single AVIF file to PNG
    
    Args:
        avif_path: Path to the AVIF file
        delete_original: Whether to delete the AVIF file after conversion
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate PNG path
        png_path = avif_path.with_suffix('.png')
        
        # Check if PNG already exists
        if png_path.exists():
            print(f"   ⚠️  PNG already exists: {png_path.name}")
            if delete_original:
                avif_path.unlink()
                print(f"   🗑️  Deleted original AVIF")
            return True
        
        # Open and convert
        with Image.open(avif_path) as img:
            # Convert to RGB if necessary (AVIF can have alpha channel)
            if img.mode in ('RGBA', 'LA'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                else:
                    background.paste(img, mask=img.split()[1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as PNG
            img.save(png_path, 'PNG', optimize=True)
        
        print(f"   ✅ Converted: {avif_path.name} -> {png_path.name}")
        
        # Delete original if requested
        if delete_original:
            avif_path.unlink()
            print(f"   🗑️  Deleted original AVIF")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error converting {avif_path.name}: {str(e)}")
        return False

def find_avif_files(directory: Path) -> list:
    """Recursively find all AVIF files in directory
    
    Args:
        directory: Root directory to search
    
    Returns:
        List of Path objects for AVIF files
    """
    avif_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.avif'):
                avif_files.append(Path(root) / file)
    
    return avif_files

def scan_and_report(directory: Path):
    """Scan directory and report AVIF files found"""
    print(f"\n🔍 Scanning for AVIF files in: {directory}")
    print("=" * 80)
    
    avif_files = find_avif_files(directory)
    
    if not avif_files:
        print("\n✅ No AVIF files found!")
        return []
    
    print(f"\n📊 Found {len(avif_files)} AVIF files:")
    print("-" * 80)
    
    # Group by set
    by_set = {}
    for avif_file in avif_files:
        # Get set ID (parent's parent directory name)
        set_id = avif_file.parent.parent.name
        if set_id not in by_set:
            by_set[set_id] = []
        by_set[set_id].append(avif_file)
    
    for set_id in sorted(by_set.keys()):
        files = by_set[set_id]
        print(f"\n   {set_id}: {len(files)} files")
        for f in files[:5]:  # Show first 5
            print(f"      • {f.parent.name}/{f.name}")
        if len(files) > 5:
            print(f"      ... and {len(files) - 5} more")
    
    return avif_files

def convert_all(directory: Path, delete_original: bool = False, set_id: str = None):
    """Convert all AVIF files to PNG
    
    Args:
        directory: Root directory to search
        delete_original: Whether to delete AVIF files after conversion
        set_id: Optional set ID to filter by
    """
    print("\n🔄 Starting conversion...")
    print("=" * 80)
    
    # Find all AVIF files
    avif_files = find_avif_files(directory)
    
    # Filter by set if specified
    if set_id:
        avif_files = [f for f in avif_files if set_id in str(f)]
        print(f"\nFiltered to set '{set_id}': {len(avif_files)} files")
    
    if not avif_files:
        print("\n✅ No AVIF files to convert!")
        return
    
    print(f"\nConverting {len(avif_files)} files...")
    if delete_original:
        print("⚠️  Original AVIF files will be DELETED after conversion")
    
    success_count = 0
    fail_count = 0
    
    for i, avif_file in enumerate(avif_files, 1):
        print(f"\n[{i}/{len(avif_files)}] {avif_file.parent.parent.name}/{avif_file.parent.name}/{avif_file.name}")
        
        if convert_avif_to_png(avif_file, delete_original):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 80)
    print("📊 Conversion Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📁 Total: {len(avif_files)}")
    
    if delete_original and success_count > 0:
        print(f"\n   🗑️  Deleted {success_count} original AVIF files")

def main():
    parser = argparse.ArgumentParser(
        description='Convert AVIF images to PNG format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for AVIF files (no conversion)
  python convert_avif_to_png.py --scan
  
  # Convert all AVIF files (keep originals)
  python convert_avif_to_png.py --convert
  
  # Convert and delete originals
  python convert_avif_to_png.py --convert --delete
  
  # Convert specific set only
  python convert_avif_to_png.py --convert --set base1
        """
    )
    
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan for AVIF files without converting'
    )
    
    parser.add_argument(
        '--convert',
        action='store_true',
        help='Convert AVIF files to PNG'
    )
    
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete original AVIF files after conversion (use with --convert)'
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
    
    # Determine directory
    directory = Path(args.dir) if args.dir else IMAGES_BASE_DIR
    
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        sys.exit(1)
    
    print("🎴 AVIF to PNG Converter")
    print("=" * 80)
    print(f"Directory: {directory}")
    
    try:
        if args.scan:
            # Scan only
            scan_and_report(directory)
        
        elif args.convert:
            # Scan first
            avif_files = scan_and_report(directory)
            
            if not avif_files:
                return
            
            # Confirm
            print("\n" + "=" * 80)
            action = "convert and DELETE" if args.delete else "convert (keep originals)"
            response = input(f"\n❓ {action.upper()} {len(avif_files)} AVIF files? (y/n): ")
            
            if response.lower() == 'y':
                convert_all(directory, delete_original=args.delete, set_id=args.set)
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
