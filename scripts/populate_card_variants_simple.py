"""
Simplified variant population script
Populates card_variants table using the API's existing get_card_variants endpoint
"""
import asyncio
import sqlite3
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pokemontcg.tcgplayer_proxy import get_card_variants


async def populate_variants_simple(db_path: str, sample_limit: int = 10):
    """
    Simple approach: Populate variants for a sample of cards
    """
    print(f"📂 Using database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure card_variants table exists (SQLite version)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id TEXT NOT NULL,
            variant_type TEXT NOT NULL,
            tcgplayer_product_id INTEGER UNIQUE,
            tcgplayer_url TEXT,
            market_price REAL,
            low_price REAL,
            mid_price REAL,
            high_price REAL,
            direct_low_price REAL,
            is_available INTEGER DEFAULT 1,
            last_price_update TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(card_id, variant_type),
            FOREIGN KEY (card_id) REFERENCES cards(id)
        )
    """)
    conn.commit()
    
    print(f"✅ Ensured card_variants table exists")
    
    # Get a sample of recent cards to populate variants for
    cursor.execute("""
        SELECT c.id, c.name, c.number, s.id as set_id, s.name as set_name
        FROM cards c
        JOIN sets s ON c.set_id = s.id
        ORDER BY c.synced_at DESC
        LIMIT ?
    """, (sample_limit,))
    
    cards = cursor.fetchall()
    
    if not cards:
        print("❌ No cards found in database")
        conn.close()
        return
    
    print(f"\n📋 Found {len(cards)} cards to process")
    print(f"   This is a sample. To process all cards, modify sample_limit parameter.\n")
    
    # For each card, we need to find the TCGplayer group ID
    # This requires the set mapping which might not be in the database
    # Let's try a different approach - use the TCGplayer URL from existing cards
    
    variants_added = 0
    cards_with_variants = 0
    
    for card_id, card_name, card_number, set_id, set_name in cards:
        print(f"Processing: {card_name} ({set_name}) #{card_number}")
        
        # Try to extract group_id from existing tcgplayer_url in the card
        cursor.execute("SELECT tcgplayer_url FROM cards WHERE id = ?", (card_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            print(f"  ⚠️  No TCGplayer URL found - skipping")
            continue
        
        tcgplayer_url = result[0]
        
        # Extract group ID from URL if possible
        # Example URL: https://prices.pokemontcg.io/tcgplayer/sv7-1
        #  or: https://www.tcgplayer.com/product/...
        
        # For now, skip this - we'll need the mapping file or API endpoint
        print(f"  ⚠️  TCGplayer group ID extraction not implemented yet")
        print(f"     URL: {tcgplayer_url[:80]}...")
        
    conn.close()
    
    print(f"\n✅ Processed {len(cards)} cards")
    print(f"   Added {variants_added} variants for {cards_with_variants} cards")
    
    print("\n💡 Next steps:")
    print("   The database needs TCGplayer group IDs to fetch variants.")
    print("   Options:")
    print("   1. Add a set mapping table/column with TCGplayer group IDs")
    print("   2. Use the frontend's tcgplayer-set-mapping.json file")
    print("   3. Manually add variants for key sets")


async def main():
    """Main entry point"""
    db_path = Path(__file__).parent.parent / "pokemontcg" / "pokemontcg.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    await populate_variants_simple(str(db_path), sample_limit=50)


if __name__ == "__main__":
    asyncio.run(main())
