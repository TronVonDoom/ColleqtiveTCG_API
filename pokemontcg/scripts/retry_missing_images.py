"""
Retry downloading missing images
"""
import json
from pathlib import Path
import logging
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_image(url, output_path, retry=3):
    """Download a single image with retry logic"""
    if not url:
        return None, "No URL provided"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for attempt in range(retry):
        try:
            time.sleep(0.1)  # Rate limiting
            
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            # Write image to file
            output_path.write_bytes(response.content)
            logger.info(f"✓ Downloaded: {output_path.name}")
            return output_path, None
            
        except requests.exceptions.RequestException as e:
            if attempt == retry - 1:
                logger.warning(f"✗ Failed to download {url}: {e}")
                return None, str(e)
            time.sleep(1 * (attempt + 1))  # Exponential backoff
    
    return None, "Max retries exceeded"

def find_missing_images():
    """Find which card images are missing"""
    cards_dir = Path("pokemon-tcg-data/cards/en")
    images_small_dir = Path("images/cards/small")
    images_large_dir = Path("images/cards/large")
    
    missing_small = []
    missing_large = []
    
    for set_file in sorted(cards_dir.glob("*.json")):
        with open(set_file, 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
        
        for card in cards_data:
            card_id = card.get('id', '').replace('/', '_')
            images = card.get('images', {})
            
            if images.get('small'):
                small_path = images_small_dir / f"{card_id}.png"
                if not small_path.exists():
                    missing_small.append((images['small'], small_path))
            
            if images.get('large'):
                large_path = images_large_dir / f"{card_id}_hires.png"
                if not large_path.exists():
                    missing_large.append((images['large'], large_path))
    
    return missing_small, missing_large

def retry_missing_images():
    """Retry downloading missing images"""
    logger.info("Finding missing images...")
    missing_small, missing_large = find_missing_images()
    
    total_missing = len(missing_small) + len(missing_large)
    
    if total_missing == 0:
        logger.info("✓ No missing images! All downloads complete.")
        return
    
    logger.info(f"Found {len(missing_small)} missing small images")
    logger.info(f"Found {len(missing_large)} missing large images")
    logger.info(f"Total missing: {total_missing}")
    logger.info("\nRetrying downloads...")
    
    all_missing = missing_small + missing_large
    
    success = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(download_image, url, path): (url, path)
            for url, path in all_missing
        }
        
        for future in as_completed(futures):
            url, path = futures[future]
            try:
                result_path, error = future.result()
                if result_path:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Error downloading {url}: {e}")
                failed += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Retry complete!")
    logger.info(f"Successfully downloaded: {success}")
    logger.info(f"Failed: {failed}")
    logger.info("=" * 60)
    
    if failed > 0:
        logger.warning(f"\n{failed} images could not be downloaded.")
        logger.warning("These images do not exist on the server.")
        logger.info("\nUse the placeholder card back image for missing cards:")
        logger.info("  pokemon-tcg-data/images/card_back.png")
        logger.info("  pokemon-tcg-data/images/card_back_hires.png")

if __name__ == '__main__':
    retry_missing_images()
