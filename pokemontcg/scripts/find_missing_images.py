"""
Find missing images and retry downloading them
"""
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_missing_images():
    """Find which card images are missing"""
    cards_dir = Path("pokemon-tcg-data/cards/en")
    images_base_dir = Path("pokemon-tcg-data/images/cards")
    
    missing_small = []
    missing_large = []
    total_cards = 0
    
    for set_file in sorted(cards_dir.glob("*.json")):
        with open(set_file, 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
        
        set_id = set_file.stem
        set_images_dir = images_base_dir / set_id
        
        for card in cards_data:
            total_cards += 1
            card_id = card.get('id', '')
            
            # Extract card number from ID
            card_number = card.get('number', card_id.split('-')[-1] if '-' in card_id else card_id)
            card_number = card_number.replace('/', '_').replace('?', 'unknown')
            
            images = card.get('images', {})
            
            if images.get('small'):
                small_path = set_images_dir / f"{card_number}.png"
                if not small_path.exists():
                    missing_small.append({
                        'id': card_id,
                        'url': images['small'],
                        'path': small_path
                    })
            
            if images.get('large'):
                large_path = set_images_dir / f"{card_number}_hires.png"
                if not large_path.exists():
                    missing_large.append({
                        'id': card_id,
                        'url': images['large'],
                        'path': large_path
                    })
    
    logger.info(f"Total cards in dataset: {total_cards}")
    logger.info(f"Missing small images: {len(missing_small)}")
    logger.info(f"Missing large images: {len(missing_large)}")
    
    if missing_small:
        logger.info("\nMissing small images:")
        for item in missing_small[:10]:  # Show first 10
            logger.info(f"  {item['id']}")
        if len(missing_small) > 10:
            logger.info(f"  ... and {len(missing_small) - 10} more")
    
    if missing_large:
        logger.info("\nMissing large images:")
        for item in missing_large[:10]:  # Show first 10
            logger.info(f"  {item['id']}")
        if len(missing_large) > 10:
            logger.info(f"  ... and {len(missing_large) - 10} more")
    
    return missing_small, missing_large

if __name__ == '__main__':
    find_missing_images()
