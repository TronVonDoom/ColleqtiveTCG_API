"""
Populate card_variants table from TCGCSV data
Uses existing tcgplayer_proxy endpoints to fetch variant data
"""
import asyncio
import sqlite3
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pokemontcg.tcgplayer_proxy import get_tcgplayer_products, get_tcgplayer_prices


async def populate_variants_for_set(db_path: str, set_id: str, group_id: int, set_name: str):
    """
    Populate variants for all cards in a specific set
    """
    print(f"\n📦 Processing set: {set_name} (set_id={set_id}, group_id={group_id})")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure card_variants table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id TEXT NOT NULL,
            variant_type TEXT NOT NULL,
            tcgplayer_product_id INTEGER,
            market_price REAL,
            low_price REAL,
            mid_price REAL,
            high_price REAL,
            direct_low_price REAL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (card_id) REFERENCES cards(id),
            UNIQUE(card_id, variant_type)
        )
    """)
    conn.commit()
    
    try:
        # Fetch TCGplayer products and prices
        print(f"  📥 Fetching products from TCGCSV...")
        products_response = await get_tcgplayer_products(group_id)
        products = products_response.get('results', [])
        
        print(f"  📥 Fetching prices from TCGCSV...")
        prices_response = await get_tcgplayer_prices(group_id)
        prices = prices_response.get('results', [])
        
        if not products:
            print(f"  ⚠️ No products found for group {group_id}")
            conn.close()
            return 0
        
        # Create price lookup
        price_map = {p['productId']: p for p in prices}
        
        print(f"  ✅ Found {len(products)} products, {len(prices)} with pricing")
        
        # Get all cards from this set in our database
        cursor.execute("""
            SELECT id, name, number FROM cards 
            WHERE set_id = ?
        """, (set_id,))
        our_cards = cursor.fetchall()
        
        print(f"  💾 Found {len(our_cards)} cards in our database")
        
        # Helper function to normalize names
        def normalize_name(name):
            return name.lower().replace('-', ' ').replace("'", "").replace('.', '').strip()
        
        # Create product lookup by normalized name
        products_by_name = {}
        for product in products:
            # Extract base card name (before any dash)
            base_name = normalize_name(product['name'].split('-')[0].strip())
            if base_name not in products_by_name:
                products_by_name[base_name] = []
            products_by_name[base_name].append(product)
        
        variants_added = 0
        cards_with_variants = 0
        
        # Process each card
        for card_id, card_name, card_number in our_cards:
            normalized_name = normalize_name(card_name)
            
            # Find matching products
            matching_products = products_by_name.get(normalized_name, [])
            
            if not matching_products:
                # Try fuzzy match (contains)
                matching_products = []
                for prod_name, prods in products_by_name.items():
                    if normalized_name in prod_name or prod_name in normalized_name:
                        matching_products.extend(prods)
            
            if not matching_products:
                continue
            
            card_variants = []
            
            # Process each matching product as a variant
            for product in matching_products:
                product_id = product['productId']
                pricing = price_map.get(product_id)
                
                # Get variant type from pricing subTypeName
                variant_type = pricing.get('subTypeName', 'Normal') if pricing else 'Normal'
                
                # Skip if we don't have pricing
                if not pricing:
                    continue
                
                # Prepare variant data
                variant = {
                    'card_id': card_id,
                    'variant_type': variant_type,
                    'tcgplayer_product_id': product_id,
                    'market_price': pricing.get('marketPrice'),
                    'low_price': pricing.get('lowPrice'),
                    'mid_price': pricing.get('midPrice'),
                    'high_price': pricing.get('highPrice'),
                    'direct_low_price': pricing.get('directLowPrice')
                }
                
                card_variants.append(variant)
            
            # Insert variants for this card
            if card_variants:
                for variant in card_variants:
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO card_variants 
                            (card_id, variant_type, tcgplayer_product_id, 
                             market_price, low_price, mid_price, high_price, direct_low_price,
                             last_updated)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (
                            variant['card_id'],
                            variant['variant_type'],
                            variant['tcgplayer_product_id'],
                            variant['market_price'],
                            variant['low_price'],
                            variant['mid_price'],
                            variant['high_price'],
                            variant['direct_low_price']
                        ))
                        variants_added += 1
                    except sqlite3.Error as e:
                        print(f"    ❌ Error inserting variant for {card_name}: {e}")
                
                cards_with_variants += 1
        
        conn.commit()
        print(f"  ✅ Added {variants_added} variants for {cards_with_variants} cards")
        
    except Exception as e:
        print(f"  ❌ Error processing set {set_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
    
    return variants_added


async def main():
    """Main entry point"""
    # Database path (try both locations)
    db_path = Path(__file__).parent.parent / "pokemontcg" / "pokemontcg.db"
    if not db_path.exists():
        db_path = Path(__file__).parent.parent / "pokemontcg" / "pokemon_tcg.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("   This script needs to be run on the Railway deployment or with a local database")
        return
    
    print(f"📂 Using database: {db_path}")
    
    # Load TCGplayer set mapping from frontend project
    mapping_path = Path(__file__).parent.parent.parent / "ColleqtiveTCG" / "data" / "pokemon" / "tcgplayer-set-mapping.json"
    
    if not mapping_path.exists():
        # Try alternate path (in case script is run from different location)
        mapping_path = Path("C:/Users/TronVonDoom/Documents/GitHub/ColleqtiveTCG/data/pokemon/tcgplayer-set-mapping.json")
    
    if not mapping_path.exists():
        print(f"❌ Set mapping not found at {mapping_path}")
        print("   Looking for: ColleqtiveTCG/data/pokemon/tcgplayer-set-mapping.json")
        return
    
    print(f"📂 Using set mapping: {mapping_path}")
    
    with open(mapping_path, 'r') as f:
        set_mapping = json.load(f)
    
    print(f"📋 Found {len(set_mapping)} sets with TCGplayer mapping")
    
    # Ask user which sets to process
    print("\nOptions:")
    print("  1. Process all sets")
    print("  2. Process specific set  ")
    print("  3. Process top 10 most recent sets")
    
    choice = input("\nEnter choice (1-3) [default: 3]: ").strip() or "3"
    
    sets_to_process = []
    
    if choice == "1":
        # Process all sets
        sets_to_process = [(set_id, data['tcgplayerGroupId'], data['setName']) 
                          for set_id, data in set_mapping.items()]
    elif choice == "2":
        # Process specific set
        print("\nAvailable sets:")
        for i, (set_id, data) in enumerate(list(set_mapping.items())[:20]):  # Show first 20
            print(f"  {set_id}: {data['setName']}")
        if len(set_mapping) > 20:
            print(f"  ... (and {len(set_mapping) - 20} more)")
        
        set_id = input("\nEnter set ID: ").strip()
        if set_id in set_mapping:
            data = set_mapping[set_id]
            sets_to_process = [(set_id, data['tcgplayerGroupId'], data['setName'])]
        else:
            print(f"❌ Set {set_id} not found")
            return
    elif choice == "3":
        # Process first 10 sets (most recent)
        sets_to_process = [(set_id, data['tcgplayerGroupId'], data['setName']) 
                          for set_id, data in list(set_mapping.items())[:10]]
    else:
        print("❌ Invalid choice")
        return
    
    print(f"\n🚀 Starting variant population for {len(sets_to_process)} set(s)...")
    
    total_variants = 0
    for set_id, group_id, set_name in sets_to_process:
        variants = await populate_variants_for_set(str(db_path), set_id, group_id, set_name)
        total_variants += variants
        
        # Small delay to avoid overwhelming the API
        await asyncio.sleep(0.5)
    
    print(f"\n✅ COMPLETE! Added {total_variants} total variants across {len(sets_to_process)} sets")
    print("\n💡 Next steps:")
    print("  1. Deploy updated API to Railway")
    print("  2. Test PDF generation with Master Set enabled")


if __name__ == "__main__":
    asyncio.run(main())
