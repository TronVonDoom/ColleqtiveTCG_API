"""
Helper utility to get card image paths with automatic placeholder fallback
"""
from pathlib import Path


class CardImageHelper:
    """Helper class to manage card images with placeholder support"""
    
    def __init__(self, base_dir="pokemontcg/pokemon-tcg-data/images"):
        self.base_dir = Path(base_dir)
        self.cards_dir = self.base_dir / "cards"
        self.placeholder_small = self.base_dir / "card_back.png"
        self.placeholder_large = self.base_dir / "card_back_hires.png"
    
    def get_card_image_path(self, set_id, card_number, size="small"):
        """
        Get the path to a card image, returning placeholder if not found
        
        Args:
            set_id: The set identifier (e.g., "base1", "sv1")
            card_number: The card number (e.g., "1", "25")
            size: "small" or "large"
        
        Returns:
            Path object to the image (actual card or placeholder)
        """
        if size not in ["small", "large"]:
            raise ValueError("size must be 'small' or 'large'")
        
        # Build the path to the actual card image
        suffix = "_hires" if size == "large" else ""
        card_path = self.cards_dir / set_id / f"{card_number}{suffix}.png"
        
        # Return actual card if it exists, otherwise return placeholder
        if card_path.exists():
            return card_path
        
        placeholder = self.placeholder_large if size == "large" else self.placeholder_small
        return placeholder
    
    def card_image_exists(self, set_id, card_number, size="small"):
        """
        Check if a card image exists (not placeholder)
        
        Args:
            set_id: The set identifier
            card_number: The card number
            size: "small" or "large"
        
        Returns:
            Boolean indicating if actual card image exists
        """
        suffix = "_hires" if size == "large" else ""
        card_path = self.cards_dir / set_id / f"{card_number}{suffix}.png"
        return card_path.exists()
    
    def get_missing_cards(self):
        """
        Get a list of all missing card images
        
        Returns:
            Dictionary with 'small' and 'large' lists of (set_id, card_number) tuples
        """
        import json
        
        missing = {'small': [], 'large': []}
        cards_data_dir = Path("pokemontcg/pokemon-tcg-data/cards/en")
        
        for set_file in sorted(cards_data_dir.glob("*.json")):
            with open(set_file, 'r', encoding='utf-8') as f:
                cards_data = json.load(f)
            
            set_id = set_file.stem
            
            for card in cards_data:
                card_number = card.get('number', card.get('id', '').split('-')[-1])
                card_number = card_number.replace('/', '_').replace('?', 'unknown')
                
                if not self.card_image_exists(set_id, card_number, 'small'):
                    missing['small'].append((set_id, card_number, card.get('name')))
                
                if not self.card_image_exists(set_id, card_number, 'large'):
                    missing['large'].append((set_id, card_number, card.get('name')))
        
        return missing


# Example usage
if __name__ == '__main__':
    helper = CardImageHelper()
    
    # Example: Get image path for Charizard from Base Set
    charizard_small = helper.get_card_image_path("base1", "4", "small")
    charizard_large = helper.get_card_image_path("base1", "4", "large")
    
    print("Charizard paths:")
    print(f"  Small: {charizard_small}")
    print(f"  Large: {charizard_large}")
    print(f"  Exists: {helper.card_image_exists('base1', '4')}")
    
    # Example: Try a missing card
    missing_small = helper.get_card_image_path("mcd14", "1", "small")
    print(f"\nMissing card (returns placeholder):")
    print(f"  Path: {missing_small}")
    print(f"  Exists: {helper.card_image_exists('mcd14', '1')}")
    
    # Show statistics
    missing = helper.get_missing_cards()
    print(f"\nMissing images summary:")
    print(f"  Small: {len(missing['small'])} cards")
    print(f"  Large: {len(missing['large'])} cards")
    
    if missing['small']:
        print(f"\nFirst 5 missing small images:")
        for set_id, card_num, name in missing['small'][:5]:
            print(f"  {set_id}-{card_num}: {name}")
