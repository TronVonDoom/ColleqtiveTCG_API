"""
Script to find cards without a Rarity field in the Pokemon TCG database
"""
import sqlite3
from pathlib import Path
import json

# Database path
DB_PATH = Path(__file__).parent / "pokemontcg" / "pokemontcg.db"


def check_missing_rarity():
    """Find all cards that don't have a rarity value"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find cards where rarity is NULL or empty string
        cursor.execute("""
            SELECT 
                id, 
                name, 
                set_id, 
                number, 
                supertype,
                rarity
            FROM cards 
            WHERE rarity IS NULL OR rarity = ''
            ORDER BY set_id, number
        """)
        
        missing_rarity_cards = cursor.fetchall()
        
        if not missing_rarity_cards:
            print("✓ All cards have a rarity value!")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(missing_rarity_cards)} cards WITHOUT a rarity value:")
        print(f"{'='*80}\n")
        
        # Group by set for better readability
        cards_by_set = {}
        for card in missing_rarity_cards:
            set_id = card['set_id']
            if set_id not in cards_by_set:
                cards_by_set[set_id] = []
            cards_by_set[set_id].append({
                'id': card['id'],
                'name': card['name'],
                'number': card['number'],
                'supertype': card['supertype'],
                'rarity': card['rarity']
            })
        
        # Display results grouped by set
        for set_id, cards in sorted(cards_by_set.items()):
            print(f"\nSet: {set_id} ({len(cards)} cards)")
            print("-" * 80)
            for card in cards:
                rarity_display = "NULL" if card['rarity'] is None else f"'{card['rarity']}'"
                print(f"  • {card['number']:>4} | {card['name']:<40} | {card['supertype']:<15} | Rarity: {rarity_display}")
        
        # Summary statistics
        print(f"\n{'='*80}")
        print("SUMMARY:")
        print(f"{'='*80}")
        print(f"Total cards without rarity: {len(missing_rarity_cards)}")
        print(f"Number of sets affected: {len(cards_by_set)}")
        
        # Get total card count for percentage
        cursor.execute("SELECT COUNT(*) FROM cards")
        total_cards = cursor.fetchone()[0]
        percentage = (len(missing_rarity_cards) / total_cards) * 100
        print(f"Percentage of cards without rarity: {percentage:.2f}%")
        
        # Save to JSON file for further analysis
        output_data = {
            'total_missing': len(missing_rarity_cards),
            'total_cards': total_cards,
            'percentage': round(percentage, 2),
            'sets_affected': len(cards_by_set),
            'cards_by_set': cards_by_set
        }
        
        output_file = Path(__file__).parent / "missing_rarity_report.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nDetailed report saved to: {output_file}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")
        raise


if __name__ == "__main__":
    check_missing_rarity()
