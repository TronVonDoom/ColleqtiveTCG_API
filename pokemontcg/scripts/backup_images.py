"""
Backup all card images to a ZIP file
This creates a timestamped backup of all images before conversion
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import zipfile

# Base directory for images
IMAGES_BASE_DIR = Path(__file__).parent.parent.parent / 'tcg-images-download' / 'pokemon' / 'cards'
BACKUP_DIR = Path(__file__).parent.parent.parent / 'backups'

def create_backup():
    """Create a ZIP backup of all card images"""
    
    # Create backup directory if it doesn't exist
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'card_images_backup_{timestamp}.zip'
    backup_path = BACKUP_DIR / backup_filename
    
    print("🎴 Card Images Backup Tool")
    print("=" * 80)
    print(f"Source: {IMAGES_BASE_DIR}")
    print(f"Backup: {backup_path}")
    print()
    
    if not IMAGES_BASE_DIR.exists():
        print(f"❌ Source directory not found: {IMAGES_BASE_DIR}")
        return False
    
    # Count files first
    print("📊 Counting files...")
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(IMAGES_BASE_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.avif', '.webp')):
                file_path = Path(root) / file
                total_files += 1
                total_size += file_path.stat().st_size
    
    print(f"   Files to backup: {total_files:,}")
    print(f"   Total size: {total_size / (1024*1024):.2f} MB")
    print()
    
    # Confirm
    response = input("❓ Create backup? (y/n): ")
    if response.lower() != 'y':
        print("❌ Backup cancelled")
        return False
    
    print("\n📦 Creating ZIP backup...")
    print("=" * 80)
    
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            files_added = 0
            
            for root, dirs, files in os.walk(IMAGES_BASE_DIR):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.avif', '.webp')):
                        file_path = Path(root) / file
                        
                        # Calculate relative path for ZIP
                        arcname = file_path.relative_to(IMAGES_BASE_DIR.parent.parent)
                        
                        # Add to ZIP
                        zipf.write(file_path, arcname)
                        files_added += 1
                        
                        # Progress update every 100 files
                        if files_added % 100 == 0:
                            print(f"   Backed up {files_added:,} / {total_files:,} files...")
        
        backup_size = backup_path.stat().st_size
        compression_ratio = (1 - backup_size / total_size) * 100
        
        print("\n" + "=" * 80)
        print("✅ Backup Complete!")
        print(f"   Files backed up: {files_added:,}")
        print(f"   Original size: {total_size / (1024*1024):.2f} MB")
        print(f"   Backup size: {backup_size / (1024*1024):.2f} MB")
        print(f"   Compression: {compression_ratio:.1f}%")
        print(f"   Saved to: {backup_path}")
        print()
        print("💡 To restore: Extract this ZIP file to the project root")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating backup: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = create_backup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
