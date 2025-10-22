"""
Script to update rarity for basic Energy cards in the Pokemon TCG database
"""
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "pokemontcg" / "pokemontcg.db"


def update_energy_card_rarity():
    """Update rarity to 'Energy' for all basic energy cards"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Find all energy cards without a rarity
        cursor.execute("""
            SELECT id, name, set_id, number, supertype, rarity
            FROM cards 
            WHERE supertype = 'Energy' 
            AND (rarity IS NULL OR rarity = '')
            ORDER BY set_id, number
        """)
        
        energy_cards = cursor.fetchall()
        
        if not energy_cards:
            print("No energy cards found without rarity.")
            conn.close()
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(energy_cards)} Energy cards without rarity")
        print(f"{'='*80}\n")
        
        # Display cards that will be updated
        for card in energy_cards:
            card_id, name, set_id, number, supertype, rarity = card
            print(f"  {set_id:>10} | {number:>4} | {name:<30}")
        
        # Confirm update
        print(f"\n{'='*80}")
        print(f"This will set rarity = 'Energy' for {len(energy_cards)} cards.")
        
        # First, ensure 'Energy' exists in the rarities table
        cursor.execute("SELECT name FROM rarities WHERE name = 'Energy'")
        if not cursor.fetchone():
            print("\nAdding 'Energy' to rarities table...")
            cursor.execute("INSERT INTO rarities (name) VALUES ('Energy')")
        
        # Update all energy cards
        print("Updating energy cards...")
        cursor.execute("""
            UPDATE cards 
            SET rarity = 'Energy'
            WHERE supertype = 'Energy' 
            AND (rarity IS NULL OR rarity = '')
        """)
        
        rows_updated = cursor.rowcount
        conn.commit()
        
        print(f"\n{'='*80}")
        print(f"✓ Successfully updated {rows_updated} energy cards!")
        print(f"{'='*80}\n")
        
        # Verify the update
        cursor.execute("""
            SELECT COUNT(*) FROM cards 
            WHERE supertype = 'Energy' AND rarity = 'Energy'
        """)
        count = cursor.fetchone()[0]
        print(f"Total energy cards with rarity 'Energy': {count}")
        
        # Check if any energy cards still lack rarity
        cursor.execute("""
            SELECT COUNT(*) FROM cards 
            WHERE supertype = 'Energy' AND (rarity IS NULL OR rarity = '')
        """)
        remaining = cursor.fetchone()[0]
        
        if remaining > 0:
            print(f"⚠ Warning: {remaining} energy cards still without rarity")
        else:
            print("✓ All energy cards now have rarity set!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error updating database: {e}")
        raise


if __name__ == "__main__":
    update_energy_card_rarity()
