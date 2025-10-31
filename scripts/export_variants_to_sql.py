"""
Export card_variants from local SQLite to SQL file for importing to PostgreSQL
"""
import sqlite3
from pathlib import Path

def export_variants_to_sql():
    """Export card_variants table to SQL INSERT statements"""
    db_path = Path(__file__).parent.parent / "pokemontcg" / "pokemontcg.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    print(f"📂 Reading from: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get count
    cursor.execute("SELECT COUNT(*) FROM card_variants")
    total = cursor.fetchone()[0]
    print(f"📊 Found {total} variants to export")
    
    # Export file
    export_path = Path(__file__).parent.parent / "card_variants_export.sql"
    
    with open(export_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("-- Card Variants Export\n")
        f.write(f"-- Total records: {total}\n")
        f.write("-- Generated from local SQLite database\n\n")
        
        # Fetch all variants in batches
        batch_size = 1000
        offset = 0
        
        while True:
            cursor.execute("""
                SELECT card_id, variant_type, tcgplayer_product_id, 
                       market_price, low_price, mid_price, high_price, direct_low_price
                FROM card_variants
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (batch_size, offset))
            
            rows = cursor.fetchall()
            if not rows:
                break
            
            print(f"  Exporting batch {offset // batch_size + 1} ({len(rows)} rows)...")
            
            # Write INSERT statements
            for row in rows:
                card_id, variant_type, product_id, market, low, mid, high, direct_low = row
                
                # Escape single quotes
                card_id = card_id.replace("'", "''")
                variant_type = variant_type.replace("'", "''") if variant_type else 'Normal'
                
                # Build INSERT statement
                f.write(f"INSERT INTO card_variants ")
                f.write(f"(card_id, variant_type, tcgplayer_product_id, ")
                f.write(f"market_price, low_price, mid_price, high_price, direct_low_price, ")
                f.write(f"last_price_update, created_at, updated_at) VALUES ")
                f.write(f"('{card_id}', '{variant_type}', ")
                f.write(f"{product_id if product_id else 'NULL'}, ")
                f.write(f"{market if market else 'NULL'}, ")
                f.write(f"{low if low else 'NULL'}, ")
                f.write(f"{mid if mid else 'NULL'}, ")
                f.write(f"{high if high else 'NULL'}, ")
                f.write(f"{direct_low if direct_low else 'NULL'}, ")
                f.write(f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ")
                f.write(f"ON CONFLICT (card_id, variant_type) DO UPDATE SET ")
                f.write(f"market_price = EXCLUDED.market_price, ")
                f.write(f"low_price = EXCLUDED.low_price, ")
                f.write(f"mid_price = EXCLUDED.mid_price, ")
                f.write(f"high_price = EXCLUDED.high_price, ")
                f.write(f"direct_low_price = EXCLUDED.direct_low_price, ")
                f.write(f"last_price_update = CURRENT_TIMESTAMP, ")
                f.write(f"updated_at = CURRENT_TIMESTAMP;\n")
            
            offset += batch_size
    
    conn.close()
    
    print(f"\n✅ Export complete!")
    print(f"📄 File: {export_path}")
    print(f"📊 {total} variants exported")
    print(f"\n💡 To import to Railway PostgreSQL:")
    print(f"   1. Copy the SQL file to a secure location")
    print(f"   2. Connect to Railway PostgreSQL using psql or Railway CLI")
    print(f"   3. Run: \\i card_variants_export.sql")
    print(f"   OR use Railway's database import feature")


if __name__ == "__main__":
    export_variants_to_sql()
