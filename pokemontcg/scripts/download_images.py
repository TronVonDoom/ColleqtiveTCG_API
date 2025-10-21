"""
Download Pokemon TCG images from pokemontcg.io
Organizes images into proper folder structure
"""
import os
import json
import requests
import logging
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pokemontcg/logs/download_images.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageDownloader:
    """Download and organize Pokemon TCG images"""
    
    def __init__(self, base_dir="pokemon-tcg-data/images", max_workers=10, rate_limit=0.1):
        self.base_dir = Path(base_dir)
        self.max_workers = max_workers
        self.rate_limit = rate_limit  # seconds between requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create directory structure
        self.cards_dir = self.base_dir / "cards"
        self.sets_symbol_dir = self.base_dir / "sets" / "symbols"
        self.sets_logo_dir = self.base_dir / "sets" / "logos"
        
        for dir_path in [self.cards_dir, self.sets_symbol_dir, self.sets_logo_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created image directory structure in: {self.base_dir}")
    
    def download_image(self, url, output_path, retry=3):
        """Download a single image with retry logic"""
        if not url:
            return None, "No URL provided"
        
        if output_path.exists():
            logger.debug(f"Already exists: {output_path.name}")
            return output_path, None
        
        for attempt in range(retry):
            try:
                time.sleep(self.rate_limit)  # Rate limiting
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Write image to file
                output_path.write_bytes(response.content)
                logger.debug(f"Downloaded: {output_path.name}")
                return output_path, None
                
            except requests.exceptions.RequestException as e:
                if attempt == retry - 1:
                    logger.warning(f"Failed to download {url}: {e}")
                    return None, str(e)
                time.sleep(1 * (attempt + 1))  # Exponential backoff
        
        return None, "Max retries exceeded"
    
    def get_image_filename(self, url):
        """Extract filename from URL"""
        if not url:
            return None
        parsed = urlparse(url)
        return Path(parsed.path).name
    
    def download_card_images(self):
        """Download all card images from JSON files"""
        logger.info("=" * 60)
        logger.info("Starting card image downloads")
        logger.info("=" * 60)
        
        cards_dir = Path("pokemon-tcg-data/cards/en")
        if not cards_dir.exists():
            logger.error(f"Cards directory not found: {cards_dir}")
            return
        
        total_cards = 0
        downloaded_small = 0
        downloaded_large = 0
        failed = 0
        skipped = 0
        
        # Collect all image URLs first
        image_tasks = []
        
        for set_file in sorted(cards_dir.glob("*.json")):
            try:
                with open(set_file, 'r', encoding='utf-8') as f:
                    cards_data = json.load(f)
                
                set_id = set_file.stem
                logger.info(f"Processing {set_file.name}: {len(cards_data)} cards")
                
                # Create set folder
                set_folder = self.cards_dir / set_id
                set_folder.mkdir(parents=True, exist_ok=True)
                
                for card in cards_data:
                    total_cards += 1
                    
                    images = card.get('images', {})
                    small_url = images.get('small')
                    large_url = images.get('large')
                    
                    # Extract card number from ID (e.g., "base1-1" -> "1")
                    card_id = card.get('id', '')
                    card_number = card.get('number', card_id.split('-')[-1] if '-' in card_id else card_id)
                    # Sanitize card number for filename
                    card_number = card_number.replace('/', '_').replace('?', 'unknown')
                    
                    if small_url:
                        filename = f"{card_number}.png"
                        output_path = set_folder / filename
                        image_tasks.append(('small', small_url, output_path))
                    
                    if large_url:
                        filename = f"{card_number}_hires.png"
                        output_path = set_folder / filename
                        image_tasks.append(('large', large_url, output_path))
            
            except Exception as e:
                logger.error(f"Error reading {set_file}: {e}")
                continue
        
        logger.info(f"Total images to download: {len(image_tasks)}")
        logger.info(f"Using {self.max_workers} parallel workers")
        
        # Download images in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.download_image, url, path): (img_type, url, path)
                for img_type, url, path in image_tasks
            }
            
            completed = 0
            for future in as_completed(futures):
                img_type, url, path = futures[future]
                try:
                    result_path, error = future.result()
                    completed += 1
                    
                    if result_path:
                        if img_type == 'small':
                            downloaded_small += 1
                        else:
                            downloaded_large += 1
                        
                        if path.exists() and completed == len(image_tasks):
                            skipped += 1
                    else:
                        failed += 1
                    
                    if completed % 100 == 0:
                        logger.info(f"Progress: {completed}/{len(image_tasks)} images processed")
                
                except Exception as e:
                    logger.error(f"Error downloading {url}: {e}")
                    failed += 1
        
        logger.info("=" * 60)
        logger.info("Card Image Download Summary")
        logger.info("=" * 60)
        logger.info(f"Total cards: {total_cards}")
        logger.info(f"Small images downloaded: {downloaded_small}")
        logger.info(f"Large images downloaded: {downloaded_large}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Images saved to: {self.base_dir}")
    
    def download_set_images(self):
        """Download all set images (symbols and logos)"""
        logger.info("=" * 60)
        logger.info("Starting set image downloads")
        logger.info("=" * 60)
        
        sets_file = Path("pokemon-tcg-data/sets/en.json")
        if not sets_file.exists():
            logger.error(f"Sets file not found: {sets_file}")
            return
        
        with open(sets_file, 'r', encoding='utf-8') as f:
            sets_data = json.load(f)
        
        logger.info(f"Found {len(sets_data)} sets")
        
        downloaded_symbols = 0
        downloaded_logos = 0
        failed = 0
        
        image_tasks = []
        
        for set_data in sets_data:
            set_id = set_data.get('id', '').replace('/', '_')
            images = set_data.get('images', {})
            
            symbol_url = images.get('symbol')
            logo_url = images.get('logo')
            
            if symbol_url:
                filename = f"{set_id}_symbol.png"
                output_path = self.sets_symbol_dir / filename
                image_tasks.append(('symbol', symbol_url, output_path))
            
            if logo_url:
                filename = f"{set_id}_logo.png"
                output_path = self.sets_logo_dir / filename
                image_tasks.append(('logo', logo_url, output_path))
        
        logger.info(f"Total set images to download: {len(image_tasks)}")
        
        # Download images in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.download_image, url, path): (img_type, url, path)
                for img_type, url, path in image_tasks
            }
            
            completed = 0
            for future in as_completed(futures):
                img_type, url, path = futures[future]
                try:
                    result_path, error = future.result()
                    completed += 1
                    
                    if result_path:
                        if img_type == 'symbol':
                            downloaded_symbols += 1
                        else:
                            downloaded_logos += 1
                    else:
                        failed += 1
                    
                    if completed % 10 == 0:
                        logger.info(f"Progress: {completed}/{len(image_tasks)} set images processed")
                
                except Exception as e:
                    logger.error(f"Error downloading {url}: {e}")
                    failed += 1
        
        logger.info("=" * 60)
        logger.info("Set Image Download Summary")
        logger.info("=" * 60)
        logger.info(f"Symbols downloaded: {downloaded_symbols}")
        logger.info(f"Logos downloaded: {downloaded_logos}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Images saved to: {self.base_dir}")
    
    def get_download_stats(self):
        """Get statistics about downloaded images"""
        total_cards_small = 0
        total_cards_large = 0
        
        # Count card images across all set folders
        if self.cards_dir.exists():
            for set_folder in self.cards_dir.iterdir():
                if set_folder.is_dir():
                    total_cards_small += len(list(set_folder.glob("*.png"))) - len(list(set_folder.glob("*_hires.png")))
                    total_cards_large += len(list(set_folder.glob("*_hires.png")))
        
        stats = {
            'cards_small': total_cards_small,
            'cards_large': total_cards_large,
            'set_symbols': len(list(self.sets_symbol_dir.glob("*.png"))) if self.sets_symbol_dir.exists() else 0,
            'set_logos': len(list(self.sets_logo_dir.glob("*.png"))) if self.sets_logo_dir.exists() else 0
        }
        
        total_size = 0
        for dir_path in [self.cards_dir, self.sets_symbol_dir, self.sets_logo_dir]:
            if dir_path.exists():
                for file in dir_path.rglob("*.png"):
                    total_size += file.stat().st_size
        
        stats['total_size_mb'] = total_size / (1024 * 1024)
        
        return stats


def main():
    parser = argparse.ArgumentParser(description='Download Pokemon TCG images')
    parser.add_argument('--cards', action='store_true', help='Download card images')
    parser.add_argument('--sets', action='store_true', help='Download set images')
    parser.add_argument('--all', action='store_true', help='Download all images')
    parser.add_argument('--dir', default='pokemon-tcg-data/images', help='Base directory for images (default: pokemon-tcg-data/images)')
    parser.add_argument('--workers', type=int, default=10, help='Number of parallel workers (default: 10)')
    parser.add_argument('--rate-limit', type=float, default=0.1, help='Seconds between requests (default: 0.1)')
    parser.add_argument('--stats', action='store_true', help='Show download statistics')
    
    args = parser.parse_args()
    
    downloader = ImageDownloader(
        base_dir=args.dir,
        max_workers=args.workers,
        rate_limit=args.rate_limit
    )
    
    if args.stats:
        stats = downloader.get_download_stats()
        print("\n" + "=" * 60)
        print("Image Download Statistics")
        print("=" * 60)
        print(f"Card images (small): {stats['cards_small']}")
        print(f"Card images (large): {stats['cards_large']}")
        print(f"Set symbols: {stats['set_symbols']}")
        print(f"Set logos: {stats['set_logos']}")
        print(f"Total disk space: {stats['total_size_mb']:.2f} MB")
        print("=" * 60)
        return
    
    start_time = time.time()
    
    if args.all or args.cards:
        downloader.download_card_images()
    
    if args.all or args.sets:
        downloader.download_set_images()
    
    if not (args.all or args.cards or args.sets):
        parser.print_help()
        return
    
    duration = time.time() - start_time
    logger.info(f"\nTotal download time: {duration:.2f} seconds")
    
    # Show final statistics
    stats = downloader.get_download_stats()
    logger.info("\n" + "=" * 60)
    logger.info("Final Statistics")
    logger.info("=" * 60)
    logger.info(f"Card images (small): {stats['cards_small']}")
    logger.info(f"Card images (large): {stats['cards_large']}")
    logger.info(f"Set symbols: {stats['set_symbols']}")
    logger.info(f"Set logos: {stats['set_logos']}")
    logger.info(f"Total disk space: {stats['total_size_mb']:.2f} MB")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
