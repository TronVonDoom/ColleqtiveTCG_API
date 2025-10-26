"""
Delete all PNG files after WebP conversion is verified
DANGEROUS: This will permanently delete all PNG files!
Only run this after confirming WebP images work on your website.
"""
import os
import sys
from pathlib import Path
import argparse

# Base directory for images
IMAGES_BASE_DIR = Path(__file__).parent.parent.parent / 'tcg-images-download' / 'pokemon' / 'cards'

def find_png_files(directory: Path) -> list:
    """Recursively find all PNG files"""
    png_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                png_files.append(Path(root) / file)
    
    return png_files

def verify_webp_exists(png_file: Path) -> bool:
    """Check if corresponding WebP file exists"""
    webp_file = png_file.with_suffix('.webp')
    return webp_file.exists()

def scan_pngs(directory: Path):
    """Scan and report PNG files"""
    print("\n🔍 Scanning for PNG files...")
    print("=" * 80)
    
    png_files = find_png_files(directory)
    
    if not png_files:
        print("\n✅ No PNG files found!")
        return []
    
    print(f"\n📊 Found {len(png_files):,} PNG files")
    
    # Check which have WebP equivalents
    with_webp = []
    without_webp = []
    
    for png_file in png_files:
        if verify_webp_exists(png_file):
            with_webp.append(png_file)
        else:
            without_webp.append(png_file)
    
    print(f"\n✅ PNGs with WebP equivalent: {len(with_webp):,}")
    print(f"⚠️  PNGs without WebP: {len(without_webp):,}")
    
    if without_webp:
        print("\n⚠️  WARNING: Some PNG files don't have WebP equivalents:")
        for png_file in without_webp[:10]:  # Show first 10
            print(f"   • {png_file.parent.parent.name}/{png_file.parent.name}/{png_file.name}")
        if len(without_webp) > 10:
            print(f"   ... and {len(without_webp) - 10} more")
    
    # Calculate space to be freed
    total_size = sum(f.stat().st_size for f in with_webp)
    
    print("\n" + "=" * 80)
    print(f"💾 Space that will be freed: {total_size/(1024**3):.2f} GB")
    
    return with_webp, without_webp

def delete_pngs(png_files: list, force: bool = False):
    """Delete PNG files"""
    if not png_files:
        print("\n✅ No PNG files to delete!")
        return
    
    print(f"\n🗑️  Deleting {len(png_files):,} PNG files...")
    print("=" * 80)
    
    if not force:
        print("\n⚠️  WARNING: This will PERMANENTLY delete all PNG files!")
        print("⚠️  Make sure you:")
        print("   1. Have tested your website with WebP images")
        print("   2. Verified all images load correctly")
        print("   3. Have a backup (card_images_backup_*.zip)")
        
        response = input("\n❓ Are you ABSOLUTELY SURE? Type 'DELETE' to confirm: ")
        
        if response != 'DELETE':
            print("\n❌ Deletion cancelled")
            return
    
    deleted = 0
    failed = 0
    total_freed = 0
    
    for i, png_file in enumerate(png_files, 1):
        try:
            file_size = png_file.stat().st_size
            png_file.unlink()
            deleted += 1
            total_freed += file_size
            
            # Progress every 1000 files
            if i % 1000 == 0:
                print(f"   Deleted {i:,}/{len(png_files):,} files...")
                
        except Exception as e:
            print(f"   ❌ Failed to delete {png_file.name}: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 80)
    print("📊 Deletion Summary:")
    print(f"   ✅ Deleted: {deleted:,} files")
    print(f"   ❌ Failed: {failed}")
    print(f"   💾 Space freed: {total_freed/(1024**3):.2f} GB")

def main():
    parser = argparse.ArgumentParser(
        description='Delete PNG files after WebP conversion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  DANGER ZONE ⚠️

This script will PERMANENTLY delete all PNG files in the tcg-images directory!

Before running this script:
1. Test your website thoroughly with WebP images
2. Verify all images load correctly in all browsers
3. Make sure you have a backup (run backup_images.py first)

Examples:
  # Scan only (safe - no deletion)
  python delete_pngs.py --scan
  
  # Delete PNGs that have WebP equivalents (with confirmation)
  python delete_pngs.py --delete
  
  # Delete without confirmation (DANGEROUS!)
  python delete_pngs.py --delete --force
        """
    )
    
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan for PNG files without deleting'
    )
    
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete PNG files that have WebP equivalents'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt (DANGEROUS!)'
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
    
    print("🗑️  PNG Deletion Tool")
    print("=" * 80)
    print(f"Directory: {directory}")
    
    try:
        if args.scan:
            # Scan only
            scan_pngs(directory)
        
        elif args.delete:
            # Scan first
            with_webp, without_webp = scan_pngs(directory)
            
            if without_webp:
                print("\n⚠️  WARNING: Some PNG files don't have WebP equivalents!")
                print("⚠️  Only PNGs with WebP equivalents will be deleted.")
            
            if with_webp:
                delete_pngs(with_webp, args.force)
            
            if without_webp:
                print(f"\n⚠️  {len(without_webp):,} PNG files were NOT deleted (no WebP equivalent)")
        
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
