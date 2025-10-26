"""
Convert PNG images to WebP format with PARALLEL PROCESSING
This script uses multiple CPU cores to convert images much faster
"""
import os
import sys
from pathlib import Path
from PIL import Image
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time

# Base directory for images
IMAGES_BASE_DIR = Path(__file__).parent.parent.parent / 'tcg-images-download' / 'pokemon' / 'cards'

# WebP quality (90 = excellent quality, ~80% size reduction)
WEBP_QUALITY = 90

# Number of parallel workers (adjust based on your CPU cores)
MAX_WORKERS = 8

# Thread-safe counters
stats_lock = Lock()
stats = {
    'success': 0,
    'failed': 0,
    'skipped': 0,
    'total_original_size': 0,
    'total_webp_size': 0
}

def convert_png_to_webp(png_path: Path, quality: int = WEBP_QUALITY, delete_original: bool = False) -> dict:
    """Convert a single PNG file to WebP
    
    Returns:
        dict with status and size info
    """
    try:
        # Generate WebP path
        webp_path = png_path.with_suffix('.webp')
        
        # Check if WebP already exists
        if webp_path.exists():
            result = {
                'status': 'skipped',
                'path': png_path,
                'message': 'WebP already exists'
            }
            if delete_original and png_path.exists():
                png_path.unlink()
                result['message'] += ' (deleted PNG)'
            return result
        
        # Get original size
        original_size = png_path.stat().st_size
        
        # Open and convert
        with Image.open(png_path) as img:
            # Save as WebP
            img.save(webp_path, 'WEBP', quality=quality, method=6)
        
        # Get WebP size
        webp_size = webp_path.stat().st_size
        
        # Delete original if requested
        if delete_original:
            png_path.unlink()
        
        return {
            'status': 'success',
            'path': png_path,
            'original_size': original_size,
            'webp_size': webp_size,
            'deleted': delete_original
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'path': png_path,
            'error': str(e)
        }

def find_png_files(directory: Path, set_id: str = None) -> list:
    """Recursively find all PNG files in directory"""
    png_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip if filtering by set and this isn't the set
        if set_id and set_id not in root:
            continue
            
        for file in files:
            if file.lower().endswith('.png'):
                png_files.append(Path(root) / file)
    
    return png_files

def update_stats(result: dict):
    """Thread-safe stats update"""
    with stats_lock:
        if result['status'] == 'success':
            stats['success'] += 1
            stats['total_original_size'] += result['original_size']
            stats['total_webp_size'] += result['webp_size']
        elif result['status'] == 'failed':
            stats['failed'] += 1
        elif result['status'] == 'skipped':
            stats['skipped'] += 1

def print_progress(completed: int, total: int, start_time: float):
    """Print progress with ETA"""
    elapsed = time.time() - start_time
    if completed > 0:
        rate = completed / elapsed
        remaining = total - completed
        eta_seconds = remaining / rate if rate > 0 else 0
        eta_minutes = eta_seconds / 60
        
        # Calculate current stats
        with stats_lock:
            success = stats['success']
            failed = stats['failed']
            skipped = stats['skipped']
            
        print(f"\r   Progress: {completed:,}/{total:,} ({completed/total*100:.1f}%) | "
              f"✅ {success} ❌ {failed} ⏭️ {skipped} | "
              f"Rate: {rate:.1f}/s | ETA: {eta_minutes:.1f}m", end='', flush=True)

def convert_all_parallel(directory: Path, quality: int = WEBP_QUALITY, 
                        delete_original: bool = False, set_id: str = None,
                        max_workers: int = MAX_WORKERS):
    """Convert all PNG files to WebP using parallel processing"""
    
    print("\n🔄 Starting parallel conversion...")
    print("=" * 80)
    print(f"WebP Quality: {quality}")
    print(f"Parallel Workers: {max_workers}")
    
    # Find all PNG files
    png_files = find_png_files(directory, set_id)
    
    if not png_files:
        print("\n✅ No PNG files to convert!")
        return
    
    print(f"\nConverting {len(png_files):,} files...")
    if delete_original:
        print("⚠️  Original PNG files will be DELETED after conversion")
    
    # Reset stats
    stats['success'] = 0
    stats['failed'] = 0
    stats['skipped'] = 0
    stats['total_original_size'] = 0
    stats['total_webp_size'] = 0
    
    start_time = time.time()
    completed = 0
    failed_files = []
    
    # Process files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(convert_png_to_webp, png_file, quality, delete_original): png_file
            for png_file in png_files
        }
        
        # Process completed tasks
        for future in as_completed(future_to_file):
            result = future.result()
            update_stats(result)
            completed += 1
            
            # Track failures
            if result['status'] == 'failed':
                failed_files.append((result['path'], result.get('error', 'Unknown error')))
            
            # Print progress every 10 files
            if completed % 10 == 0 or completed == len(png_files):
                print_progress(completed, len(png_files), start_time)
    
    # Final newline after progress
    print()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("📊 Conversion Summary:")
    print(f"   ✅ Successful: {stats['success']:,}")
    print(f"   ❌ Failed: {stats['failed']:,}")
    print(f"   ⏭️  Skipped: {stats['skipped']:,}")
    print(f"   📁 Total: {len(png_files):,}")
    print(f"   ⏱️  Time: {elapsed/60:.1f} minutes ({elapsed/len(png_files):.2f}s per file)")
    
    if stats['success'] > 0:
        actual_savings = (1 - stats['total_webp_size'] / stats['total_original_size']) * 100
        print(f"\n💾 Size Results:")
        print(f"   Original: {stats['total_original_size']/(1024*1024):.1f} MB")
        print(f"   WebP: {stats['total_webp_size']/(1024*1024):.1f} MB")
        print(f"   Saved: {(stats['total_original_size'] - stats['total_webp_size'])/(1024*1024):.1f} MB ({actual_savings:.1f}%)")
    
    if delete_original and stats['success'] > 0:
        print(f"\n   🗑️  Deleted {stats['success']:,} original PNG files")
    
    # Show failed files
    if failed_files:
        print(f"\n⚠️  Failed conversions ({len(failed_files)}):")
        for file_path, error in failed_files[:10]:  # Show first 10
            print(f"   • {file_path.name}: {error}")
        if len(failed_files) > 10:
            print(f"   ... and {len(failed_files) - 10} more")

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
    
    print(f"\n📊 Found {len(png_files):,} PNG files:")
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
    
    print(f"\n   Sets: {len(by_set)}")
    for set_id in sorted(by_set.keys())[:10]:  # Show first 10
        files = by_set[set_id]
        set_size = sum(f.stat().st_size for f in files)
        print(f"   {set_id}: {len(files)} files ({set_size/(1024*1024):.1f} MB)")
    
    if len(by_set) > 10:
        print(f"   ... and {len(by_set) - 10} more sets")
    
    print("\n" + "=" * 80)
    print("💾 Size Estimates:")
    print(f"   Current (PNG): {total_size/(1024*1024):.1f} MB")
    print(f"   After (WebP Q90): {estimated_webp_size/(1024*1024):.1f} MB")
    print(f"   Space savings: {estimated_savings/(1024*1024):.1f} MB (~80%)")
    
    return png_files

def main():
    parser = argparse.ArgumentParser(
        description='Convert PNG images to WebP format (PARALLEL VERSION)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for PNG files (no conversion)
  python convert_png_to_webp_parallel.py --scan
  
  # Convert all PNG files with 8 workers (keep originals)
  python convert_png_to_webp_parallel.py --convert
  
  # Convert with 16 workers for faster processing
  python convert_png_to_webp_parallel.py --convert --workers 16
  
  # Convert and delete originals
  python convert_png_to_webp_parallel.py --convert --delete
  
  # Convert specific set only
  python convert_png_to_webp_parallel.py --convert --set base1
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
        '--workers',
        type=int,
        default=MAX_WORKERS,
        help=f'Number of parallel workers (default: {MAX_WORKERS})'
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
    
    print("🎴 PNG to WebP Converter (PARALLEL)")
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
            response = input(f"\n❓ {action.upper()} {len(png_files):,} PNG files? (y/n): ")
            
            if response.lower() == 'y':
                convert_all_parallel(directory, quality=args.quality, 
                                    delete_original=args.delete, set_id=args.set,
                                    max_workers=args.workers)
            else:
                print("\n❌ Conversion cancelled")
        
        else:
            # No action specified - show help
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        with stats_lock:
            print(f"\n📊 Partial Results:")
            print(f"   ✅ Successful: {stats['success']:,}")
            print(f"   ❌ Failed: {stats['failed']:,}")
            print(f"   ⏭️  Skipped: {stats['skipped']:,}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
