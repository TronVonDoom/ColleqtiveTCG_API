"""
Populate card_variants table on Railway PostgreSQL database
Uses environment variable DATABASE_URL for connection
"""
import asyncio
import json
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pokemontcg.tcgplayer_proxy import get_tcgplayer_products, get_tcgplayer_prices

# Check for psycopg2
try:
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)


async def populate_variants_for_set_pg(db_url: str, set_id: str, group_id: int, set_name: str):
    """
    Populate variants for all cards in a specific set (PostgreSQL version)
    """
    print(f"\n📦 Processing set: {set_name} (set_id={set_id}, group_id={group_id})")
    
    # Connect to PostgreSQL database
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
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
            WHERE set_id = %s
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
        
        variants_to_insert = []
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
            
            card_has_variants = False
            
            # Process each matching product as a variant
            for product in matching_products:
                product_id = product['productId']
                pricing = price_map.get(product_id)
                
                # Get variant type from pricing subTypeName
                variant_type = pricing.get('subTypeName', 'Normal') if pricing else 'Normal'
                
                # Skip if we don't have pricing
                if not pricing:
                    continue
                
                # Add to batch
                variants_to_insert.append((
                    card_id,
                    variant_type,
                    product_id,
                    product.get('url'),
                    pricing.get('marketPrice'),
                    pricing.get('lowPrice'),
                    pricing.get('midPrice'),
                    pricing.get('highPrice'),
                    pricing.get('directLowPrice')
                ))
                card_has_variants = True
            
            if card_has_variants:
                cards_with_variants += 1
        
        # Batch insert variants
        if variants_to_insert:
            execute_batch(cursor, """
                INSERT INTO card_variants 
                (card_id, variant_type, tcgplayer_product_id, tcgplayer_url,
                 market_price, low_price, mid_price, high_price, direct_low_price,
                 last_price_update, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (card_id, variant_type) DO UPDATE SET
                    market_price = EXCLUDED.market_price,
                    low_price = EXCLUDED.low_price,
                    mid_price = EXCLUDED.mid_price,
                    high_price = EXCLUDED.high_price,
                    direct_low_price = EXCLUDED.direct_low_price,
                    last_price_update = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, variants_to_insert, page_size=100)
            
            conn.commit()
            print(f"  ✅ Added {len(variants_to_insert)} variants for {cards_with_variants} cards")
        else:
            print(f"  ⚠️ No variants to add")
        
    except Exception as e:
        print(f"  ❌ Error processing set {set_id}: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return 0
    finally:
        conn.close()
    
    return len(variants_to_insert)


async def main():
    """Main entry point"""
    # Get DATABASE_URL from environment
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ DATABASE_URL environment variable not set")
        print("   Set it with your Railway PostgreSQL connection string:")
        print("   export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
        return
    
    print(f"📂 Using database: {db_url[:30]}...{db_url[-20:]}")
    
    # Load TCGplayer set mapping from frontend project
    mapping_path = Path("C:/Users/TronVonDoom/Documents/GitHub/ColleqtiveTCG/data/pokemon/tcgplayer-set-mapping.json")
    
    if not mapping_path.exists():
        print(f"❌ Set mapping not found at {mapping_path}")
        return
    
    print(f"📂 Using set mapping: {mapping_path}")
    
    with open(mapping_path, 'r') as f:
        set_mapping = json.load(f)
    
    print(f"📋 Found {len(set_mapping)} sets with TCGplayer mapping")
    
    # Ask user which sets to process
    print("\nOptions:")
    print("  1. Process all sets")
    print("  2. Process specific set")
    print("  3. Process top 10 most recent sets")
    print("  4. Process specific range (e.g., sets 1-50)")
    
    choice = input("\nEnter choice (1-4) [default: 3]: ").strip() or "3"
    
    sets_to_process = []
    
    if choice == "1":
        # Process all sets
        sets_to_process = [(set_id, data['tcgplayerGroupId'], data['setName']) 
                          for set_id, data in set_mapping.items()]
    elif choice == "2":
        # Process specific set
        print("\nAvailable sets:")
        for i, (set_id, data) in enumerate(list(set_mapping.items())[:20]):
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
    elif choice == "4":
        # Process range
        start = int(input("Start index (0-based): ").strip())
        end = int(input("End index (exclusive): ").strip())
        sets_to_process = [(set_id, data['tcgplayerGroupId'], data['setName']) 
                          for set_id, data in list(set_mapping.items())[start:end]]
    else:
        print("❌ Invalid choice")
        return
    
    print(f"\n🚀 Starting variant population for {len(sets_to_process)} set(s)...")
    print(f"   Target: Railway PostgreSQL database")
    
    confirm = input(f"\n⚠️  This will modify your PRODUCTION database. Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    total_variants = 0
    for set_id, group_id, set_name in sets_to_process:
        variants = await populate_variants_for_set_pg(db_url, set_id, group_id, set_name)
        total_variants += variants
        
        # Small delay to avoid overwhelming the API
        await asyncio.sleep(0.5)
    
    print(f"\n✅ COMPLETE! Added {total_variants} total variants across {len(sets_to_process)} sets")
    print(f"\n💡 Next step:")
    print(f"   Test PDF generation with Master Set enabled in your frontend")


if __name__ == "__main__":
    asyncio.run(main())
